# Artifact Hub Publishing

KubeVoIP is listed on Artifact Hub from the classic Helm repository:

```text
https://charts.kubevoip.com
```

Repository metadata is published to:

```text
https://charts.kubevoip.com/artifacthub-repo.yml
```

## Verified Publisher

Verified publisher is controlled by `artifacthub-repo.yml`. The file must
include the Artifact Hub repository ID and an owner email that matches the
Artifact Hub account or organization membership.

## Official Status

Official status is granted manually by Artifact Hub. Request it only after the
repository is verified and Artifact Hub has processed a chart package that
includes a README.

Use the Artifact Hub official status issue template:

```text
https://github.com/artifacthub/hub/issues/new?template=official-status.yml
```

KubeVoIP should request repository-level official status because the chart
installs KubeVoIP itself and the repository contains only official KubeVoIP
packages.

## Signed Packages

Signed status requires Helm provenance files. KubeVoIP chart packages are signed
with:

```text
KubeVoIP Chart Signing <hello@kubevoip.com>
Fingerprint: 9C70EA83B762C2C97292207DAD39B317609DC2CE
Public key: https://raw.githubusercontent.com/kubevoip/charts/main/keys/kubevoip-chart-signing.asc
```

The publish workflow signs packages when all of these GitHub Actions settings
exist in `kubevoip/charts`:

- Repository variable `CHART_SIGNING_KEY`: a substring of the signing key UID,
  such as `hello@kubevoip.com`.
- Repository secret `CHART_SIGNING_KEYRING_BASE64`: base64-encoded legacy GPG
  secret keyring usable by `helm package --sign --keyring`.
- Repository secret `CHART_SIGNING_PASSPHRASE`: passphrase for the signing key.

The chart advertises the key to Artifact Hub with this annotation in
`charts/kubevoip/Chart.yaml`:

```yaml
artifacthub.io/signKey: |
  fingerprint: 9C70EA83B762C2C97292207DAD39B317609DC2CE
  url: https://raw.githubusercontent.com/kubevoip/charts/main/keys/kubevoip-chart-signing.asc
```

The next chart release will publish both `packages/kubevoip-X.Y.Z.tgz` and
`packages/kubevoip-X.Y.Z.tgz.prov`. Artifact Hub will detect the provenance
file and mark the package as signed.

## Values Schema

The chart includes `charts/kubevoip/values.schema.json`. Helm validates this
schema during `helm lint`, `helm template`, `helm install`, and `helm upgrade`.
Artifact Hub uses the same schema to render a values reference for the package.
