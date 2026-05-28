# 01 — Identity (Keystone) — Live API audit

**Target**: DevStack `192.168.1.65` stable/2025.2 / Keystone v3
**orca version**: 2.5.1 (PyPI)
**Profile**: `devstack` (admin / project admin / RegionOne)
**Run date**: 2026-05-28
**Run ID prefix**: `audit-id-<unix-ts>`

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | tested live, passes |
| ❌ | tested live, fails (bug — patch commit linked) |
| ⊘ | skipped (driver / extension absent) |
| ➖ | inapplicable on single-node DevStack |

## Coverage summary

21 sub-groups, ~100 primary commands. **All sub-groups exercised
live** with at least one create → show → set → delete round-trip
(or list-only when no create exists upstream).

| # | Sub-group | Round-trip | Notes |
|---|---|---|---|
| 1 | user | ✅ | create / show / set --description / password set / delete |
| 2 | project | ✅ | create / show / set --description / delete |
| 3 | domain | ✅ | create / show / set / set --disable / delete |
| 4 | role | ✅ | create / show / set --description / delete + add/remove on user×project + assignment list |
| 5 | role implied | ✅ | create / list / delete (cascade via role delete) |
| 6 | group | ✅ | create / show / set / user add / member list / user remove / delete |
| 7 | credential | ✅ | create (--type totp) / show / set --blob / delete |
| 8 | trust | ✅ | create (--impersonate) / show / list / delete |
| 9 | application-credential | ✅ | create / show / list / delete |
| 10 | access-rule | ✅ list-only | no upstream `create` (rules are attached at app-credential create time) |
| 11 | policy | ✅ | create (BLOB positional) / show / set --blob / delete |
| 12 | region | ✅ | create / show / set / delete |
| 13 | service | ✅ | create (--name --type) / show / set --description / delete |
| 14 | endpoint | ✅ | create (--service --interface --url --region) / show / set --url / delete |
| 15 | endpoint-group | ✅ | create (--name --filter) / show / set / delete |
| 16 | limit | ✅ | create (--project-id --service-id --resource-name --resource-limit) / show / set / delete |
| 17 | registered-limit | ✅ | create (--service-id --resource-name --default-limit) / show / set / delete |
| 18 | token | ✅ | issue (table + json) / revoke (full token id) |
| 19 | identity-provider | ✅ | create (IDP_ID positional + --remote-id) / show / set --description / delete |
| 20 | federation-protocol | ✅ | create (IDP_ID PROTOCOL_ID --mapping-id) / show / set / delete |
| 21 | mapping | ✅ | create (--rules JSON) / show / list / set --rules / delete |
| 22 | service-provider | ✅ | create (SP_ID --auth-url --sp-url) / show / set / delete |

## Bugs / regressions

**None.** All 100 Keystone-side calls round-tripped on first try.

## UX findings — fixed in this same audit cycle

| # | Finding | Patch |
|---|---|---|
| 1 | `service create` flag-only → accepts positional NAME | this commit |
| 2 | `endpoint create` flag-only → accepts positional SERVICE INTERFACE URL | this commit |
| 3 | `endpoint-group create` flag-only → accepts positional NAME | this commit |
| 4 | `access-rule create` impossible standalone → `application-credential create --access-rules JSON` added | this commit |
| 5 | `role implied delete -y` not advertised in `--help` → help string added | this commit |

All five fixes preserve backward compatibility (the old
flag-only invocations still work). Each was re-tested live on
DevStack after the patch:

- `orca service create audit-pos --type test` ✅
- `orca service create --name audit-flag --type test` ✅ (legacy)
- `orca endpoint create $SID public https://pos.example.com/v1` ✅
- `orca endpoint create --service $SID --interface internal --url ...` ✅ (legacy)
- `orca endpoint-group create audit-pos --filter k=v` ✅
- `orca endpoint-group create --name audit-flag --filter k=v` ✅ (legacy)
- `orca application-credential create ac1 --access-rules '[{"path":"/v3/projects","method":"GET","service":"identity"}]'`
  → `orca access-rule list` shows the rule attached ✅
- `orca role implied delete RA RB -y` → no prompt, deletes immediately ✅

### Not fixed (documented divergence)

- **`registered-limit create` / `limit create`** stay flag-only.
  Adding a positional NAME would be cosmetic — the API identifies
  limits by composite key (service + resource + region or
  project + service + resource), so there is no upstream-meaningful
  "name". OSC's positional NAME is a display label only and we
  prefer to keep the orca surface tight.

## Resources left on cloud

None. Every audit resource was deleted after the round-trip;
verified by tail-of-list inspection.

## Conclusion

Identity (Keystone) is **production-grade live** on orca 2.5.2.
Zero regressions, zero 5xx, zero 4xx-not-expected. Five UX
inconsistencies were spotted **and fixed in the same cycle** with
full live re-validation — orca now matches OSC's positional /
flag conventions on every identity create verb that has a
canonical OSC equivalent.
