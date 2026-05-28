# 02 — Compute (Nova) — Live API audit

**Target**: DevStack `192.168.1.65` stable/2025.2 / Nova micro-version 2.79
**orca version**: 2.5.2 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-28
**Run ID prefix**: `audit-c-<unix-ts>`

## Coverage summary

orca already covered the bulk of the Nova surface (server CRUD,
flavor CRUD, keypair, aggregate add/remove/cache, hypervisor list/show/
usage/stats, compute-service list/set/delete, server group, server
event, server migration list/show/abort/force-complete/confirm/revert).
This pass focused on the **gaps** identified against OSC.

| OSC command | orca path before | orca path after |
|---|---|---|
| `server add floating ip` | ⊘ missing | ✅ `server add floating-ip SERVER IP` |
| `server remove floating ip` | ⊘ missing | ✅ `server remove floating-ip SERVER IP` |
| `console log show` | only as `server console log` | ✅ top-level `console log show` |
| `console url show` | only as `server console url` | ✅ top-level `console url show` |
| `server resize confirm/revert` | as `server migration confirm/revert` | ➖ kept as `server migration confirm/revert` |

## Bugs / regressions found

**None.** All existing compute commands round-trip cleanly.

## Live tests of the new commands (audit-c-1780002190)

CRUD sequence:

```
orca flavor list                                       ✅ debug-flavor
orca image list                                        ✅ orca-live-cirros
orca network list                                      ✅ private, ext-net
orca server create --name audit-c-1780002190-vm        ✅ ACTIVE in 16 s
  --image orca-live-cirros --flavor debug-flavor
  --network private --wait
orca console log show <vm>                             ✅ cirros boot log
orca console url show <vm>                             ✅ novnc URL
orca floating-ip create --network <ext-net-uuid>       ✅ 172.24.4.186 allocated
orca network router create audit-router                ✅ created
  --external-network <ext-net-uuid>
orca network router add interface <router>             ✅
  --subnet-id <private-subnet>
orca server add floating-ip <vm> 172.24.4.186          ✅ associated (by IP)
orca server remove floating-ip <vm> 172.24.4.186       ✅ disassociated (by IP)
orca server add floating-ip <vm> <fip-uuid>            ✅ associated (by UUID)
orca server remove floating-ip <vm> <fip-uuid>         ✅ disassociated (by UUID)
orca server delete <vm> --yes                          ✅
orca floating-ip delete <fip-uuid> --yes               ✅
orca network router remove interface ... ; delete      ✅
```

## Design choice — `server resize confirm/revert`

OSC exposes the Nova ``confirmResize`` / ``revertResize`` actions
under ``openstack server resize confirm SERVER`` and
``openstack server resize revert SERVER``. orca uses
``orca server migration confirm SERVER`` / ``orca server migration
revert SERVER`` (same Nova action, semantically equivalent).

Click does not support a single name as both a leaf command (``server
resize SERVER --flavor X``) and a group (``server resize confirm/
revert``), so the OSC three-word form would require dropping
``server resize SERVER --flavor`` — too disruptive. The OSC parity
is therefore documented as a divergence in
[`feedback_audit_ux_divergences_osc`](../../../.claude/projects/-home-kallioli-Projects-orca-cli/memory/feedback_audit_ux_divergences_osc.md).

## UX findings carried over to Phase 1.3 (network)

- `orca network router create` rejects `--external-gateway` (OSC
  flag name); orca uses `--external-network`. Noted for the network
  consistency pass.

## Conclusion

Compute (Nova) is **production-grade live** on orca 2.5.2 + this
patch. Two genuine OSC-parity gaps closed (`server add/remove
floating-ip`) and two convenience aliases added (top-level `console
log show` / `console url show`). Zero regressions, zero 5xx.
