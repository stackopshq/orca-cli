# orca

OpenStack Rich Command-line Alternative — a unified, batteries-included
CLI for managing OpenStack cloud infrastructure.

## What is orca?

`orca` is a drop-in alternative to `python-openstackclient` (OSC).
It manages virtual machines, networks, load balancers, secrets,
Kubernetes clusters, metrics, DNS, object storage, identity, and
more through one consistent interface — with extras OSC doesn't
have.

**100 % OSC parity** on the 10 core services (635/635 verbs).
If you have OSC muscle memory, `alias openstack=orca` and you're
done. See [Coming from OSC](from-osc.md) for the handful of
differences and orca-exclusive commands.

## Highlights

- **80+ top-level command groups** covering Keystone, Nova, Neutron,
  Cinder, Glance, Swift, Heat, Designate, Barbican, Placement,
  Octavia, Magnum, Manila, Gnocchi, Aodh, CloudKitty, Freezer,
  Federation, and admin top-levels (`block-storage`,
  `object-store`, `orchestration`, `software`, `coe`, …).
- **635/635 OSC verbs** answered word-for-word on the 10 core
  services (99,4 % path-exact + 4 documented Click leaf-vs-group
  divergences).
- **Typed service layer** — every resource flows through a
  `*Service` class with `TypedDict` models, catching field-name
  typos at mypy time.
- **Rich terminal output** — coloured tables, trees, progress
  bars (Rich).
- **Multi-account profiles** — named profiles, `clouds.yaml` and
  `OS_*` env var support, transparent token caching.
- **Shell auto-completion** — Bash, Zsh, Fish, with per-profile
  resource caching for IDs and names.
- **Orca-exclusive commands** — `overview`, `find`, `audit`,
  `cleanup`, `watch`, `doctor`, `diff`, `clone`, `bulk`,
  `port-forward`, `inspect`, `tree`, `topology`, … see
  [Coming from OSC](from-osc.md).

## Supported services

| Service | Top-level command(s) | Backend |
|---|---|---|
| Compute | `server`, `flavor`, `keypair`, `aggregate`, `hypervisor`, `availability-zone`, `compute-service`, `server-group`, `event`, `usage`, `console` | Nova |
| Image | `image` | Glance |
| Block Storage | `volume`, `block-storage`, `backup` | Cinder, Freezer |
| Object Storage | `container`, `object`, `object-store` | Swift |
| Network | `network`, `port`, `router`, `subnet`, `floating-ip`, `security-group`, `qos`, `subnet-pool`, `trunk`, `address-group`, `address-scope`, `ip-availability`, `local-ip`, `extension` | Neutron |
| Load Balancer | `loadbalancer` | Octavia |
| DNS | `zone`, `recordset`, `tld`, `ptr`, `tsigkey` | Designate |
| Orchestration | `stack`, `orchestration`, `software` | Heat |
| Clusters | `cluster`, `coe` | Magnum |
| Shared File Systems | `share` | Manila |
| Metrics & Alarms | `metric`, `alarm` | Gnocchi, Aodh |
| Rating | `rating` | CloudKitty |
| Placement | `placement`, `resource`, `trait`, `allocation` | Placement |
| Secrets | `secret`, `acl`, `ca` | Barbican |
| Identity | `user`, `project`, `domain`, `role`, `group`, `policy`, `credential`, `application-credential`, `access-rule`, `trust`, `token`, `auth`, `endpoint`, `endpoint-group`, `region`, `service`, `limit`, `registered-limit`, `versions` | Keystone |
| Federation | `identity-provider`, `federation-protocol`, `mapping`, `service-provider` | Keystone |
| Utilities | `ip`, `limits`, `quota`, `catalog`, `completion` | — |
| Orca-exclusive | `overview`, `find`, `audit`, `cleanup`, `watch`, `doctor`, `export`, `profile`, `setup` | — |

## Quick start

```bash
pip install orca-openstackclient
orca setup           # interactive credential setup
orca server list     # list your VMs
```

If you're coming from OSC, jump to [Coming from OSC](from-osc.md)
for a one-page tour of the differences and the orca-exclusive
commands.

For full installation, profile management, and shell completion
setup, see [Getting Started](getting-started.md). For per-command
documentation generated directly from the running CLI, see the
[Command Reference](commands/index.md).
