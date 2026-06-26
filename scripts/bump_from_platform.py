#!/usr/bin/env python3
"""Bump the chart to match an exact KubeVoIP platform ref."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "kubevoip"


class LiteralString(str):
    pass


def literal_string_representer(dumper: yaml.Dumper, data: LiteralString) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.SafeDumper.add_representer(LiteralString, literal_string_representer)


def version_from_ref(ref: str) -> str:
    match = re.fullmatch(r"v(?P<version>\d+\.\d+\.\d+)", ref)
    if not match:
        raise SystemExit(f"platform ref must look like vX.Y.Z, got {ref!r}")
    return match.group("version")


def write_yaml(path: Path, data: object) -> None:
    data = preserve_multiline_strings(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def preserve_multiline_strings(data: object) -> object:
    if isinstance(data, dict):
        return {key: preserve_multiline_strings(value) for key, value in data.items()}
    if isinstance(data, list):
        return [preserve_multiline_strings(value) for value in data]
    if isinstance(data, str) and "\n" in data:
        return LiteralString(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform-ref", required=True)
    parser.add_argument("--platform-dir", default="_platform")
    args = parser.parse_args()

    version = version_from_ref(args.platform_ref)
    platform_dir = ROOT / args.platform_dir
    platform_crd = platform_dir / "config" / "crd" / "platform-crds.yaml"
    chart_crd = CHART / "crds" / "platform-crds.yaml"

    if not platform_crd.exists():
        raise SystemExit(f"missing platform CRD source: {platform_crd}")

    chart_yaml = CHART / "Chart.yaml"
    chart = yaml.safe_load(chart_yaml.read_text(encoding="utf-8"))
    chart["version"] = version
    chart["appVersion"] = version
    write_yaml(chart_yaml, chart)

    values_yaml = CHART / "values.yaml"
    values = yaml.safe_load(values_yaml.read_text(encoding="utf-8"))
    values["image"]["tag"] = args.platform_ref
    write_yaml(values_yaml, values)

    shutil.copyfile(platform_crd, chart_crd)


if __name__ == "__main__":
    main()
