#!/usr/bin/env python3
"""Prepare gh-pages chart repository updates with idempotency checks."""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "kubevoip"
REPOSITORY_METADATA = ROOT / "artifacthub-repo.yml"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def chart_version() -> str:
    chart = yaml.safe_load((CHART / "Chart.yaml").read_text(encoding="utf-8"))
    return str(chart["version"])


def chart_metadata() -> dict[str, object]:
    return yaml.safe_load((CHART / "Chart.yaml").read_text(encoding="utf-8"))


def extracted_contents_match(left: Path, right: Path) -> bool:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        left_dir = root / "left"
        right_dir = root / "right"
        left_dir.mkdir()
        right_dir.mkdir()

        with tarfile.open(left, "r:gz") as archive:
            archive.extractall(left_dir, filter="data")
        with tarfile.open(right, "r:gz") as archive:
            archive.extractall(right_dir, filter="data")

        comparison = filecmp.dircmp(left_dir, right_dir)
        return dirs_match(comparison)


def dirs_match(comparison: filecmp.dircmp[str]) -> bool:
    if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
        return False
    return all(dirs_match(child) for child in comparison.subdirs.values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", default="site")
    parser.add_argument("--dist-dir", default="dist")
    parser.add_argument("--url", default="https://charts.kubevoip.com/packages")
    parser.add_argument("--sign", action="store_true")
    parser.add_argument("--sign-key")
    parser.add_argument("--sign-keyring")
    parser.add_argument("--sign-passphrase-file")
    args = parser.parse_args()

    version = chart_version()
    site = ROOT / args.site_dir
    dist = ROOT / args.dist_dir
    packages = site / "packages"
    package_name = f"kubevoip-{version}.tgz"
    new_package = dist / package_name
    new_provenance = dist / f"{package_name}.prov"
    hosted_package = packages / package_name

    dist.mkdir(parents=True, exist_ok=True)
    packages.mkdir(parents=True, exist_ok=True)
    (site / "CNAME").write_text("charts.kubevoip.com\n", encoding="utf-8")
    metadata_changed = sync_repository_metadata(site)

    package_args = ["helm", "package", str(CHART), "--destination", str(dist)]
    if args.sign:
        if not args.sign_key or not args.sign_keyring or not args.sign_passphrase_file:
            raise SystemExit("--sign requires --sign-key, --sign-keyring, and --sign-passphrase-file")
        package_args.extend(
            [
                "--sign",
                "--key",
                args.sign_key,
                "--keyring",
                args.sign_keyring,
                "--passphrase-file",
                args.sign_passphrase_file,
            ]
        )
    run(*package_args)

    if not new_package.exists():
        raise SystemExit(f"helm package did not create {new_package}")
    if args.sign and not new_provenance.exists():
        raise SystemExit(f"helm package did not create {new_provenance}")

    if hosted_package.exists():
        index_changed = sync_index_metadata(site, chart_metadata())
        provenance_changed = sync_provenance(new_provenance, packages / new_provenance.name)
        existing_digest = sha256(hosted_package)
        new_digest = sha256(new_package)
        if existing_digest == new_digest:
            if metadata_changed or index_changed or provenance_changed:
                print(f"kubevoip {version} already published; repository metadata changed")
                return
            print(f"kubevoip {version} already published with matching digest; no-op")
            return
        if extracted_contents_match(hosted_package, new_package):
            if metadata_changed or index_changed or provenance_changed:
                print(f"kubevoip {version} already published; repository metadata changed")
                return
            print(f"kubevoip {version} already published with matching content; no-op")
            return
        if metadata_changed or index_changed or provenance_changed:
            print(
                f"kubevoip {version} already published with different content; "
                "publishing repository metadata only"
            )
            return
        raise SystemExit("version already published with different content")

    shutil.copyfile(new_package, hosted_package)
    sync_provenance(new_provenance, packages / new_provenance.name)
    run("helm", "repo", "index", str(packages), "--url", args.url)
    shutil.move(str(packages / "index.yaml"), site / "index.yaml")


def sync_repository_metadata(site: Path) -> bool:
    destination = site / "artifacthub-repo.yml"
    if not REPOSITORY_METADATA.exists():
        if destination.exists():
            destination.unlink()
            return True
        return False

    changed = not destination.exists() or not filecmp.cmp(REPOSITORY_METADATA, destination, shallow=False)
    shutil.copyfile(REPOSITORY_METADATA, destination)
    return changed


def sync_index_metadata(site: Path, chart: dict[str, object]) -> bool:
    index_path = site / "index.yaml"
    if not index_path.exists():
        return False

    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, dict):
        return False

    entries = index.get("entries")
    if not isinstance(entries, dict):
        return False

    chart_name = str(chart["name"])
    versions = entries.get(chart_name)
    if not isinstance(versions, list):
        return False

    for entry in versions:
        if not isinstance(entry, dict) or str(entry.get("version")) != str(chart["version"]):
            continue

        changed = False
        for key in (
            "annotations",
            "apiVersion",
            "appVersion",
            "description",
            "home",
            "icon",
            "keywords",
            "sources",
            "type",
        ):
            if chart.get(key) is not None and entry.get(key) != chart[key]:
                entry[key] = chart[key]
                changed = True

        if changed:
            index_path.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
        return changed

    return False


def sync_provenance(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    changed = not destination.exists() or not filecmp.cmp(source, destination, shallow=False)
    shutil.copyfile(source, destination)
    return changed


if __name__ == "__main__":
    main()
