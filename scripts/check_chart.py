#!/usr/bin/env python3
"""Validate chart metadata and CRD YAML for CI."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "kubevoip"
REPOSITORY_METADATA = ROOT / "artifacthub-repo.yml"


def main() -> None:
    chart = yaml.safe_load((CHART / "Chart.yaml").read_text(encoding="utf-8"))
    values = yaml.safe_load((CHART / "values.yaml").read_text(encoding="utf-8"))
    version = chart["version"]

    if chart["appVersion"] != version:
        raise SystemExit(f"appVersion {chart['appVersion']} does not match chart version {version}")

    expected_tag = f"v{version}"
    actual_tag = values["image"]["tag"]
    if actual_tag != expected_tag:
        raise SystemExit(f"operator image tag {actual_tag} does not match {expected_tag}")
    if chart.get("icon") != "https://raw.githubusercontent.com/kubevoip/kubevoip/main/assets/logo.png":
        raise SystemExit("Chart.yaml icon must point to the PNG logo for Artifact Hub")

    require_artifacthub_metadata(chart)

    for path in sorted((CHART / "crds").glob("*.yaml")):
        docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        if not docs or any(doc is None for doc in docs):
            raise SystemExit(f"{path} did not parse as non-empty YAML documents")


def require_artifacthub_metadata(chart: dict[str, object]) -> None:
    for name in ("README.md", "LICENSE"):
        if not (CHART / name).is_file():
            raise SystemExit(f"chart package is missing {name}")

    annotations = chart.get("annotations")
    if not isinstance(annotations, dict):
        raise SystemExit("Chart.yaml is missing Artifact Hub annotations")

    expected_annotations = {
        "artifacthub.io/category": "networking",
        "artifacthub.io/operator": "true",
        "artifacthub.io/operatorCapabilities": "Basic Install",
        "artifacthub.io/license": "MIT",
    }
    for key, expected in expected_annotations.items():
        actual = annotations.get(key)
        if actual != expected:
            raise SystemExit(f"Chart.yaml annotation {key} must be {expected!r}, got {actual!r}")

    links = yaml.safe_load(str(annotations.get("artifacthub.io/links", "")))
    if not isinstance(links, list):
        raise SystemExit("Chart.yaml annotation artifacthub.io/links must be a YAML list")
    link_names = {link.get("name") for link in links if isinstance(link, dict)}
    for required in ("website", "documentation", "source", "support"):
        if required not in link_names:
            raise SystemExit(f"Chart.yaml artifacthub.io/links is missing {required}")

    metadata = yaml.safe_load(REPOSITORY_METADATA.read_text(encoding="utf-8"))
    owners = metadata.get("owners") if isinstance(metadata, dict) else None
    if not isinstance(owners, list) or not owners:
        raise SystemExit("artifacthub-repo.yml must include at least one owner")
    for owner in owners:
        if not isinstance(owner, dict) or not owner.get("name") or not owner.get("email"):
            raise SystemExit("artifacthub-repo.yml owners must include name and email")


if __name__ == "__main__":
    main()
