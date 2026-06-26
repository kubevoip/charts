# Release Status During Migration

Platform and chart releases are intentionally decoupled by a reviewed PR.

The platform release `vX.Y.Z` publishes the operator image first. The chart bump
PR then updates the chart to `X.Y.Z`, copies CRDs from the exact platform tag,
and publishes the chart only after the PR merges.

Users may see an operator image tag before the matching Helm chart appears.
Until the chart repository has published at least one accepted release to both
classic Helm and OCI, `kubevoip/kubevoip` remains the fallback release path.

Do not cut over if any of these are true:

- classic Helm publishing works but OCI publishing fails;
- OCI publishing works but `charts.kubevoip.com`, DNS, or Pages fails;
- the chart installs but CRDs do not match the platform tag exactly;
- historical packages or `index.yaml` entries are not preserved across reruns.
