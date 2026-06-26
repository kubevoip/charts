# KubeVoIP Helm Charts

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/kubevoip)](https://artifacthub.io/packages/search?repo=kubevoip)

This repository owns KubeVoIP Helm chart source and, after the migration cutover,
publishes the chart to:

- Classic Helm: `https://charts.kubevoip.com`
- OCI: `oci://ghcr.io/kubevoip/charts/kubevoip`

## Migration source of truth

During the migration, chart source may temporarily exist in both
`kubevoip/kubevoip` and `kubevoip/charts`.

`kubevoip/charts` becomes the publishing source of truth only after the first
successful chart release has published to both `charts.kubevoip.com` and GHCR
OCI and the acceptance checks pass. Until then, `kubevoip/kubevoip` remains the
fallback release path.

## Version policy

For now, chart and platform versions stay aligned:

- chart version `X.Y.Z`
- chart `appVersion` `X.Y.Z`
- default operator image tag `vX.Y.Z`

Do not introduce independent chart versions until there is a real support need.

## Hosted chart repository

The `main` branch is authoritative for chart source and workflows.

The `gh-pages` branch is authoritative for hosted Helm repository artifacts:

- `index.yaml`
- `packages/*.tgz`
- future `packages/*.prov` or signing artifacts
- `CNAME`

Historical packages and index entries are retained indefinitely unless a version
is intentionally deprecated.

## OCI compatibility

The intended OCI install URL remains:

```bash
oci://ghcr.io/kubevoip/charts/kubevoip
```

At migration time, that GHCR package is public and linked to
`kubevoip/kubevoip`. Before cutover, grant `kubevoip/charts` write access to the
existing package in GitHub Packages settings, then verify the chart repo can
publish to the same path. If that cannot be made to work, document explicit OCI
migration commands before changing user-facing install docs.
