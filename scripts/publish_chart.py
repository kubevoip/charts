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
    args = parser.parse_args()

    version = chart_version()
    site = ROOT / args.site_dir
    dist = ROOT / args.dist_dir
    packages = site / "packages"
    package_name = f"kubevoip-{version}.tgz"
    new_package = dist / package_name
    hosted_package = packages / package_name

    dist.mkdir(parents=True, exist_ok=True)
    packages.mkdir(parents=True, exist_ok=True)
    (site / "CNAME").write_text("charts.kubevoip.com\n", encoding="utf-8")

    run("helm", "package", str(CHART), "--destination", str(dist))

    if not new_package.exists():
        raise SystemExit(f"helm package did not create {new_package}")

    if hosted_package.exists():
        existing_digest = sha256(hosted_package)
        new_digest = sha256(new_package)
        if existing_digest == new_digest:
            print(f"kubevoip {version} already published with matching digest; no-op")
            return
        if extracted_contents_match(hosted_package, new_package):
            print(f"kubevoip {version} already published with matching content; no-op")
            return
        raise SystemExit("version already published with different content")

    shutil.copyfile(new_package, hosted_package)
    run("helm", "repo", "index", str(packages), "--url", args.url)
    shutil.move(str(packages / "index.yaml"), site / "index.yaml")


if __name__ == "__main__":
    main()
