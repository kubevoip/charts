#!/usr/bin/env python3
"""Validate chart metadata and CRD YAML for CI."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "kubevoip"


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

    for path in sorted((CHART / "crds").glob("*.yaml")):
        docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        if not docs or any(doc is None for doc in docs):
            raise SystemExit(f"{path} did not parse as non-empty YAML documents")


if __name__ == "__main__":
    main()
