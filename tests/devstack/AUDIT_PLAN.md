# orca — Live API audit plan (DevStack-driven)

## Goal

Validate every primary command in the orca CLI tree against a real
OpenStack API. The output is a per-service report
(`tests/devstack/audit/NN-<service>.md`) listing each command, the
scenario covered, the result, and any bug discovered (with the patch
commit that addresses it).

We will not pass for newbies in front of the OpenStack community:
**CRUD round-trips with assertions**, not smoke `--help` runs.

## Coverage policy

For every command we cover at least one of:

- **CRUD** — `create` → `show` → `set` / mutation → `delete`, with
  assertion on the round-trip body / state.
- **List with filter** — both empty result and non-empty path, with
  at least one filter exercised.
- **Action verb** — for non-CRUD verbs (pause, lock, evacuate,
  failover, etc.) we trigger the action and assert the resulting
  state via `show`.
- **Edge case** — at least one `--force`, `--wait`, or format
  switch where it changes behaviour.

For each command, in the per-service report:

| Symbol | Meaning |
|---|---|
| ✅ | tested live, passes |
| ❌ | tested live, fails (bug — link to patch commit) |
| ⊘ | skipped (driver / extension absent — documented) |
| ➖ | inapplicable in this env (e.g. multi-cell admin on a single-node DevStack) |

## Test target

- DevStack `sysadmin@192.168.1.65` (Ubuntu 24.04, stable/2025.2,
  OVN networking, LVM Cinder)
- `~/.orca/config.yaml` profile `devstack`
- All resources prefixed `audit-<service>-<run-id>` for traceability
  and cleanup
- Cleanup is mandatory at the end of every scenario; on test
  failure, log the orphans for follow-up

## Phase 1 — services already active on DevStack

| # | Service (orca top-level)           | Primary cmds | DevStack state              | Prereqs           |
|---|------------------------------------|-------------:|-----------------------------|-------------------|
| 1 | identity (Keystone)                |          ~60 | ✅ enabled                   | none              |
| 2 | compute (Nova) — server/flavor/... |          ~70 | ✅ enabled                   | external network (ext-net already created last session) |
| 3 | network (Neutron)                  |          ~88 | ✅ + metering, segment_range, port_forwarding (activated in previous session) | OVN: ndp-proxy / l3-conntrack-helper / local-ip = ⊘ |
| 4 | volume (Cinder)                    |          ~84 | ✅ enabled (LVM)             | etcd must be up   |
| 5 | image (Glance)                     |          ~47 | ✅ enabled                   | none              |
| 6 | dns (Designate)                    |          ~28 | ✅ enabled                   | none              |
| 7 | placement                          |          ~29 | ✅ enabled                   | none              |
| 8 | orchestration (Heat / stack)       |          ~34 | ✅ enabled                   | needs a network for resource templates |
| 9 | object-store (Swift)               |          ~17 | ✅ enabled                   | none              |
|10 | key-manager (Barbican)             |          ~20 | ✅ enabled                   | none              |

## Phase 2 — services to enable on DevStack

| # | Service                | Plugin to enable in `local.conf`              | Cost   |
|---|------------------------|-----------------------------------------------|--------|
| 11 | load-balancer (Octavia) | `enable_plugin octavia https://opendev.org/openstack/octavia` + `enable_service o-api o-cw o-hk o-hm` | ~5min restart |
| 12 | container_infra (Magnum) | `enable_plugin magnum https://opendev.org/openstack/magnum` | ~10min (driver image) |
| 13 | backup (Freezer)        | `enable_plugin freezer https://opendev.org/openstack/freezer` | ~5min |
| 14 | share (Manila)          | `enable_plugin manila https://opendev.org/openstack/manila` + LVM driver | ~10min |
| 15 | alarm (Aodh)            | `enable_plugin aodh https://opendev.org/openstack/aodh` | ~5min |
| 16 | metric (Gnocchi)        | `enable_plugin gnocchi https://github.com/gnocchixyz/gnocchi` | ~5min |
| 17 | rating (CloudKitty)     | `enable_plugin cloudkitty https://opendev.org/openstack/cloudkitty` (depends on Gnocchi) | ~10min |

## Phase 3 — bilan global

Consolidated report at `tests/devstack/audit/00-summary.md`:

- Total commands tested vs total commands in orca
- Bugs found, classified by severity, with the patch commit
- Services not testable on DevStack — escalate to external clouds
  (Infomaniak, Sharktech)

## Method

1. **One service at a time.** Setup env → exhaustive live tests →
   cleanup → write the report → commit the report.
2. **Bugs found are fixed in the same session**, with a separate
   commit (`fix(<service>): ...`) and a unit-test addition. The
   per-service report references the fix commit hash.
3. **DevStack is a shared resource** — no destructive admin ops
   (no service flag flips without recording the diff, no `--purge`).
4. **The cleanup helper** uses prefixed names so a failed test
   leaves obvious orphans we can grep.

## Tracking

- Task list (`TaskList`): one task per phase, one per Phase 1 service.
- Per-service report committed when complete.
- Bug fix commits referenced from the report.

## When external cloud needed

Some flows are impossible on this DevStack instance:

- True replication failover (volume / Cinder) — needs second backend.
- Real Octavia amphora provisioning at scale.
- OIDC federation (real IdP) — needs Infomaniak / Sharktech.
- Quota stress tests beyond the LVM cap (10 volumes max).

These will be called out in the per-service report as "**Phase 4
escalation**" and grouped at the end for a separate session against
a real public cloud.
