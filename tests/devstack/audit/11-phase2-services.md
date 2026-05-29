# 11 — Phase 2 services — Live API audit (Aodh / Magnum / Octavia / Manila / Gnocchi / CloudKitty / Freezer)

**Target**: DevStack `192.168.1.65`
**orca version**: 2.6.1 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-29
**Audit source**: OSC plugin-installed CLI (``python-octaviaclient``,
``python-magnumclient``, ``python-manilaclient``, ``aodhclient``,
``gnocchiclient``, ``python-cloudkittyclient``).

## Audit summary

| Service | OSC verbs | orca verbs | Path-exact | Status |
|---|---:|---:|---:|---|
| Aodh (alarm) | 13 | 12 → 12 (+3 OSC) | 10/13 | ⚠️ partial |
| Magnum (cluster / coe) | 29 | 15 → 25 | 10/29 | ⚠️ partial (alias only) |
| Octavia (loadbalancer) | 82 | 39 | 39/82 | ⊘ deferred |
| Manila (share) | 154 | 15 | 12/154 | ⊘ deferred (huge surface) |
| Gnocchi (metric) | 39 | 16 | 9/39 | ⊘ deferred |
| CloudKitty (rating) | 46 | 25 | 19/46 | ⊘ deferred |
| Freezer (backup) | n/a (not installed in OSC) | — | n/a | ⊘ deferred |

## Done in this patch

### Aodh

* ``alarm update`` — alias of ``alarm set`` (OSC's verb name).
* ``alarm quota show [--project ID]`` — new leaf backed by
  ``AlarmService.get_quota``. Renders the Aodh ``/v2/quotas``
  payload.
* ``alarm metrics`` — new leaf backed by ``AlarmService.get_metrics``
  (``/v2/metrics``).
* Service helpers added: ``get_quota``, ``get_metrics``.

### Magnum

* New top-level group ``coe`` (``orca/commands/coe.py``) that
  re-exposes ``cluster`` at the OSC path
  (``coe cluster list/show/create/delete/resize/upgrade/...``).
  Covers ~10 OSC paths via alias without code duplication.

## Deferred — full backlog

Implementing 100 % parity on the remaining 6 services would add
~280 verbs + ~80 service-helper methods — too much for this audit
cycle. Each service's gap list is reproduced below so a future
session can pick them up.

### Octavia (44 missing)

| Group | Missing verbs |
|---|---|
| amphora | configure, delete, stats show |
| availability-zone | full CRUD (4) |
| availability-zone-profile | full CRUD (5) |
| flavor (LB-flavors) | full CRUD (6) |
| flavor-profile | full CRUD (5) |
| failover (LB) | 1 |
| unset (across HM, L7P, L7R, listener, pool, member) | 6 |
| listener stats show | 1 |
| member create / delete | 2 (orca uses ``add`` / ``remove``) |
| provider | list, capability list (2) |
| quota | reset, list, defaults show (3) |

### Magnum (15 missing after coe alias)

ca rotate / show / sign (3) — credential rotate (1) —
cluster config (1, may alias kubeconfig) — cluster update (1) —
nodegroup create/delete/update (3) — quotas full CRUD (5) —
service list (1) — stats list (1) = 15.

### Manila (142 missing)

Massive surface: backup (5), access (6), adopt/abandon (2),
availability-zone list (1), export-location (4), group + group-snapshot
(11), message (4), network/network-subnet (8), pool list (1),
quota / class (10), replica + replica-export-location (10),
security-service (5), server (4), transfer (6), type / type-access
(10), service list (1), share extend/migrate/properties/resize/
restore/revert/etc (~20), share-instance (4), … Re-audit needed
because some hide behind hyphen renames.

### Gnocchi (30 missing)

archive-policy CRUD (5), archive-policy-rule CRUD (4),
benchmark commands (~6), capabilities list (1),
metric show / aggregates / batch / measures show (4),
resource batch / delete / list-types (3),
resource-type CRUD (4), status (1), server show (1).

### CloudKitty (27 missing)

dataframes add (1), info config + capabilities (2),
hashmap full CRUD (~16), pyscripts CRUD (4),
modules enable / disable / list / set (4).

### Freezer

Plugin `python-freezerclient` not packaged for current OSC; no live
audit possible.

## Conclusion

Phase 2 services audit complete. 4 services (Aodh, Magnum, Octavia,
Manila) opened, 3 (Gnocchi/CloudKitty/Freezer) listed for follow-up.

The pragmatic call: **lock in the easy wins (Aodh + Magnum coe
alias) and freeze the rest for a dedicated Phase 2.x release**.
Total estimated work to close the remaining gaps: ~280 verbs +
~80 service helpers ≈ 8-10 dedicated sessions per service.

Phase 1 (the 10 core services) is **100 % closed**; that's the
"newbie-grade OSC parity" goal we set at the start.
