# KubeVoIP

The canonical KubeVoIP README lives in the main platform repository:

https://github.com/kubevoip/kubevoip#readme

KubeVoIP is a Kubernetes operator for SIP platforms. It runs Kamailio gateways,
RTPengine media relays, SIP users, dial policies, provider-neutral trunks, and
Asterisk application pods, with runtime data stored in PostgreSQL.

## Prerequisites

- Kubernetes cluster with Helm 3.
- A namespace for KubeVoIP resources.
- A PostgreSQL database for production use.
- UDP `LoadBalancer` support or equivalent routing for SIP and RTP services.

The chart installs KubeVoIP CRDs as cluster-scoped resources. Each Helm release
watches only its installation namespace.

## Install

```bash
helm repo add kubevoip https://charts.kubevoip.com
helm repo update
helm upgrade --install kubevoip kubevoip/kubevoip \
  --namespace telephony --create-namespace
```

To install a specific version:

```bash
helm upgrade --install kubevoip kubevoip/kubevoip \
  --version 0.6.7 \
  --namespace telephony --create-namespace
```

The same chart is also published to GHCR OCI:

```bash
helm upgrade --install kubevoip oci://ghcr.io/kubevoip/charts/kubevoip \
  --version 0.6.7 \
  --namespace telephony --create-namespace
```

## Configuration

The chart deploys the KubeVoIP operator and lets the operator reconcile SIP
platform resources in the release namespace. Artifact Hub renders the full
values reference from the chart's `values.schema.json`. Common values include:

| Value | Description |
| --- | --- |
| `image.repository` | Operator image repository. |
| `image.tag` | Operator image tag. Defaults to the matching platform release. |
| `operator.replicas` | Number of operator pods. |
| `operator.highAvailability.enabled` | Enables Kopf active/passive peering. |
| `asteriskImage.repository` | Asterisk runtime image repository. |
| `kamailioImage.repository` | Kamailio runtime image repository. |
| `rtpengineImage.repository` | RTPengine runtime image repository. |
| `serviceAccount.create` | Creates a service account for the operator. |
| `rbac.create` | Creates operator RBAC resources. |

Enable operator failover HA with multiple replicas:

```bash
helm upgrade --install kubevoip kubevoip/kubevoip \
  --namespace telephony --create-namespace \
  --set operator.highAvailability.enabled=true \
  --set operator.replicas=3
```

This improves controller availability only. Configure SIP gateways, media
relays, Asterisk workers, and PostgreSQL separately for platform HA.

## Next Steps

Use the KubeVoIP CLI to create a demo platform or initialize resources for your
own PostgreSQL database:

```bash
uvx kubevoip -n telephony init
```

For the full walkthrough, API reference, networking guidance, and production
database notes, see the KubeVoIP README and documentation.

## Links

- Website: https://kubevoip.com
- Main README: https://github.com/kubevoip/kubevoip#readme
- Documentation: https://docs.kubevoip.com
- Source: https://github.com/kubevoip/kubevoip
- Chart source: https://github.com/kubevoip/charts
- Issues: https://github.com/kubevoip/kubevoip/issues

## License

MIT
