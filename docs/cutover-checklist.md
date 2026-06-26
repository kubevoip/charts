# Chart Repository Cutover Checklist

Do not mark `kubevoip/charts` as the publishing source of truth until every item
passes.

## Required setup

- `charts.kubevoip.com` points to GitHub Pages for `kubevoip/charts`.
- GitHub Pages serves the `gh-pages` branch from `/`.
- The existing GHCR package `ghcr.io/kubevoip/charts/kubevoip` grants write
  access to the `kubevoip/charts` repository workflows.
- The platform repo has a GitHub App configured with access to dispatch
  `kubevoip/charts`.
- Platform secrets are set:
  - `CHARTS_APP_ID`
  - `CHARTS_APP_PRIVATE_KEY`

## Acceptance commands

Use a clean Helm cache:

```bash
export HELM_REPOSITORY_CACHE="$(mktemp -d)"
export HELM_REPOSITORY_CONFIG="$(mktemp)"
helm repo add kubevoip https://charts.kubevoip.com
helm repo update
helm search repo kubevoip/kubevoip --versions
```

Verify classic Helm:

```bash
helm upgrade --install kubevoip kubevoip/kubevoip \
  --version X.Y.Z \
  --namespace telephony --create-namespace
```

Verify OCI:

```bash
helm upgrade --install kubevoip oci://ghcr.io/kubevoip/charts/kubevoip \
  --version X.Y.Z \
  --namespace telephony --create-namespace
```

Verify CRD sync:

```bash
diff -u _platform/config/crd/platform-crds.yaml charts/kubevoip/crds/platform-crds.yaml
```

## Escape hatch

Do not cut over if any of these are true:

- classic Helm publishing works but OCI publishing fails;
- OCI publishing works but `charts.kubevoip.com`, DNS, or Pages fails;
- the chart installs but CRDs do not match the platform tag exactly;
- historical packages or `index.yaml` entries are not preserved across reruns.

Until all checks pass, `kubevoip/kubevoip` remains the fallback release path.
