# Changelog

All notable changes to orca are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.0] — 2026-05-29

Live API audit closure — orca now answers to every ``openstack
<verb>`` an OSC user types across the 10 core services (635/635
OSC paths). 17 new top-level groups, 30+ sub-group refactors,
~40 new service-helper methods. See ``tests/devstack/audit/`` for
the per-service reports.

### Phase 1 — 10 core services at 100 % OSC parity

* **Identity** (1.1) — 5 UX fixes (service/endpoint/endpoint-group
  positional NAME, access-rules JSON, role implied delete -y).
* **Compute** (1.2) — ``server add/remove floating-ip``, top-level
  ``console log show`` / ``console url show``.
* **Network** (1.3) — top-level ``port`` / ``router`` / ``subnet``;
  ``network qos`` / ``network trunk`` / ``network subport`` inverse
  aliases; new ``router add/remove gateway/port/subnet``;
  ``network flavor add/remove profile`` (breaking).
* **Volume** (1.4) — new top-level ``block-storage`` with cluster /
  log-level / resource-filter / manageable / cleanup; ``volume
  backend pool list``; ``volume transfer request *``. Breaking:
  ``volume backend capability HOST`` → ``volume backend capability
  show HOST``.
* **Image** (1.5) — ``image member get``, ``image metadef object
  property show``. ``image import info`` documented as Click
  leaf-vs-group limitation.
* **DNS** (1.6) — new top-level ``tld``, ``ptr``, ``tsigkey``.
  Breaking: ``zone export``, ``zone import``, ``zone transfer
  accept`` refactored from leafs to sub-groups. New ``zone move``,
  ``zone transfer request set``.
* **Placement** (1.7) — full sub-group refactor of
  ``resource-provider``; new top-level ``resource``, ``trait``,
  ``allocation``; new verbs ``resource class set``, ``trait show``,
  ``resource usage show``, ``allocation unset``.
* **Orchestration** (1.8) — new top-level ``orchestration`` (build
  info / service list / template function/version list / validate /
  resource-type); new top-level ``software`` (config + deployment
  CRUD); ``stack export``; ``stack hook clear/poll``.
* **Object Store** (1.9) — new top-level ``object-store`` (account
  set/show/unset); ``object create`` alias.
* **Key Manager** (1.10) — new top-level ``acl`` and ``ca``;
  ``secret container`` and ``secret order`` sub-groups; new ACL
  user add/remove verbs; ``secret get`` and ``secret update``
  aliases.

### Phase 2 — partial (easy wins committed)

* **Aodh** — ``alarm update``, ``alarm quota show``, ``alarm
  metrics``.
* **Magnum** — new top-level ``coe`` re-exposing ``cluster`` at
  the OSC path.
* Remaining gaps on Octavia / Manila / Gnocchi / CloudKitty fully
  inventoried in ``tests/devstack/audit/11-phase2-services.md``.

### Breaking changes (cumulative)

If you scripted any of the following, add the new word(s):

* ``volume backend capability HOST`` → ``… capability show HOST``.
* ``network flavor add FLAVOR PROFILE`` → ``… add profile FLAVOR
  PROFILE``. Same for ``remove``.
* ``zone export ZONE`` → ``zone export create ZONE``.
* ``zone import --file F`` → ``zone import create --file F``.
* ``zone transfer accept TRANSFER KEY`` → ``zone transfer accept
  request TRANSFER KEY``.

Every other change is additive.

## [2.6.1] — 2026-05-29

Phase 1.4 Cinder audit closure — orca now answers to **every**
OpenStackClient ``volume`` and ``block storage`` verb word-for-word
(82/82 OSC paths).

### Added (OSC parity)

- **New top-level group ``block-storage``** re-exposes Cinder admin
  verbs OSC moved under ``openstack block storage …``:
  ``cluster``, ``log-level``, ``resource-filter``,
  ``volume manageable list``, ``snapshot manageable list``, and a
  new ``cleanup`` leaf.
- **``block-storage cleanup``** (new) — POST ``/workers/cleanup``
  with standard filters (--cluster, --host, --binary,
  --resource-id, --resource-type, --service-id).
- **``volume backend pool list``** — alias of the existing
  ``volume pool list`` under the OSC-compatible 4-word path.
- **``volume transfer request {accept,create,delete,list,show}``**
  — sub-group of ``volume transfer`` whose 5 verbs share the
  same callbacks (OSC uses 4 words, orca's 3-word form remains).

### Service helper

- ``VolumeService.workers_cleanup(filters)`` — POST
  ``/workers/cleanup`` with Cinder micro-version 3.70.

### Breaking (niche admin)

- ``volume backend capability HOST`` → ``volume backend
  capability show HOST``. Refactor of the leaf into a sub-group
  with a ``show`` leaf, required to match OSC's 4-word path.

## [2.6.0] — 2026-05-29

Phase 1.3 Neutron audit closure — orca now answers to **every**
OpenStackClient ``network`` / ``port`` / ``router`` / ``subnet``
verb word-for-word (156/156 OSC paths).

### Added (OSC parity)

- **Top-level aliases** ``orca port``, ``orca router``, ``orca
  subnet`` re-expose the existing ``network port`` / ``network
  router`` / ``network subnet`` sub-groups.
- **Inverse aliases under ``network``** ``network qos``,
  ``network trunk``, ``network subport list`` re-expose the
  top-level ``qos`` / ``trunk`` groups.
- **``router add gateway ROUTER --network NET [--fixed-ip IP …]``**
  (sets ``external_gateway_info``) and **``router remove gateway
  ROUTER``** (clears it).
- **``router add port ROUTER PORT_ID``** /
  **``router remove port ROUTER PORT_ID``**.
- **``router add subnet ROUTER SUBNET_ID``** /
  **``router remove subnet ROUTER SUBNET_ID``** (alias of the
  interface add by subnet_id — same Neutron endpoint).
- **``network auto-allocated-topology create``** mapped to the
  same callback as ``show`` (Neutron exposes a single GET-with-
  implicit-create endpoint upstream).

### Breaking (niche admin SDN)

- ``network flavor add FLAVOR PROFILE`` → ``network flavor add
  profile FLAVOR PROFILE``. Same for ``remove``. Aligns with OSC's
  4-word verb. If you scripted the 3-word form, update to add the
  ``profile`` token between ``add``/``remove`` and the IDs.

## [2.5.3] — 2026-05-28

### Added (compute OSC parity — Phase 1.2 audit closure)

- **``server add floating-ip SERVER IP_OR_ID [--fixed-ip-address ADDR]``**
  — associate a floating IP with a server. Resolves the second
  argument as either a literal address (e.g. ``172.24.4.10``) or a
  UUID, picks the right server port (optionally the one owning a
  specified fixed IP), and PUTs ``port_id`` on the floating-ip via
  Neutron. Parity with ``openstack server add floating ip``.
- **``server remove floating-ip SERVER IP_OR_ID``** — inverse.
  Warns if the FIP is bound to a different server's port.
- **``console log show SERVER``** / **``console url show SERVER``**
  — top-level OSC parity for the existing ``server console log`` /
  ``server console url`` (same callback).

### Design notes (documented divergence)

- **``server resize confirm/revert``** is exposed as
  ``server migration confirm/revert`` (same Nova action,
  semantically equivalent). Click does not support a single name
  as both a leaf command (``server resize SERVER --flavor``) and a
  group (``server resize confirm``).

## [2.5.2] — 2026-05-28

### Changed (UX consistency, backward-compatible)

- **``service create [NAME]``** — accepts the service name as a
  positional argument (matching ``user`` / ``project`` / ``domain``
  / ``role`` / ``group create NAME``). ``--name`` kept as a
  fallback for existing scripts.
- **``endpoint create [SERVICE] [INTERFACE] [URL]``** — accepts
  the OSC three-positional form. ``--service`` / ``--interface``
  / ``--url`` kept.
- **``endpoint-group create [NAME]``** — accepts positional NAME.
  ``--name`` kept.
- **``role implied delete -y``** — ``--yes`` / ``-y`` was already
  wired but the brief ``--help`` did not mention it; help text
  added.

### Added

- **``application-credential create --access-rules JSON``** — pass
  a JSON array (e.g. ``'[{"path":"/v3/projects","method":"GET","service":"identity"}]'``)
  to attach Keystone access rules at credential creation time. This
  is the only API path that supports rule attachment; the resulting
  rules surface in ``orca access-rule list``. Closes the only orca
  gap vs. OSC's ``--access-rules`` flag.

All five changes were discovered during the live Phase 1.1 identity
audit (``tests/devstack/audit/01-identity.md``) and re-validated on
DevStack after the patch.

## [2.5.1] — 2026-05-28

### Added

- **``quota set``** — set quotas on Nova, Cinder and Neutron in one
  call. Exposes the OSC flag surface (``--instances``, ``--cores``,
  ``--ram``, ``--volumes``, ``--snapshots``, ``--gigabytes``,
  ``--networks``, ``--ports``, ``--floating-ips``, …) and only PUTs
  to services with at least one flag set. ``--force`` skips Nova's
  over-limit check.
- **``quota delete``** — reset project quotas to the cloud defaults.
  ``--service all`` (default) issues DELETE on the three services;
  ``--service compute|volume|network`` narrows the reset.
  Confirmation prompt unless ``--yes``.
- **``quota list``** — list projects with non-default Neutron quotas
  (Nova/Cinder have no list-all endpoint upstream).
- Service helpers: ``ComputeService.update_quota / delete_quota``,
  ``VolumeService.update_quota_set / delete_quota_set``,
  ``NetworkService.update_quota / delete_quota / get_default_quota``.

### Fixed

- **``volume log-level list/set``** sent an extra wrapping envelope
  (``{"os-services_get-log": {…}}``) that Cinder rejected with HTTP
  400. The body is now posted at the top level as Cinder expects.

## [2.5.0] — 2026-05-28

Major OSC-parity catch-up — 7 batches landed across compute, volume,
network, image, object-store, identity and quota/usage. The goal is to
let an OpenStackClient user transplant their muscle memory to orca
without re-learning command paths.

### Added — OSC parity (lot 1: aliases)

- ``image set`` / ``image unset`` (alias of ``image update``).
- ``security-group unset`` (alias of ``security-group update``).
- ``volume update`` (alias of ``volume set``).
- ``server migration confirm`` / ``server migration revert``
  (aliases of ``server confirm-resize`` / ``server revert-resize``).

### Added — OSC parity (lot 2: discovery & misc)

- ``catalog show <service>`` — pretty-prints a single service entry.
- ``extension list`` / ``extension show <alias>`` — surfaces Neutron
  extensions (the most useful discoverability axis).
- ``versions show`` — Keystone API versions advertised on the root
  endpoint (handles the HTTP 300 Multiple Choices reply).
- ``qos rule-type list`` / ``qos rule-type show <type>``.
- ``floating-ip pool list`` — lists external networks usable as FIP
  pools.
- ``hypervisor stats show`` — replaces the previous flat ``hypervisor
  stats`` so the OSC three-word form works.
- ``server event list`` / ``server event show`` — re-exposes
  ``orca event`` under ``server`` for muscle memory.

### Added — OSC parity (lot 3: Cinder admin)

- ``volume cluster list/show/set``.
- ``volume log-level list/set`` — change live log levels on Cinder
  services.
- ``volume resource-filter list/show``.
- ``volume manageable list`` / ``volume snapshot manageable list``.

### Fixed — Cinder micro-version negotiation

- Without an explicit ``OpenStack-API-Version: volume X.Y`` header the
  Cinder API falls back to 3.0 and returns 500 on ``/clusters``,
  ``/os-services/{get,set}-log``, ``/resource_filters`` and the
  ``manageable_*`` collections. orca now pins all admin routes added
  in lot 3 to 3.70 (Wallaby).

### Added — OSC parity (lot 4: Glance)

- ``image add project`` / ``image remove project`` — wrap
  ``image member create/delete`` under OSC's three-word form.
- ``image save`` — alias of ``image download``.
- ``image stores list`` — alias of ``image stores info``.
- ``image info import`` — list Glance image-import methods
  (parity with ``openstack image import info``).

### Added — OSC parity (lot 5: Nova admin)

- ``aggregate add host`` / ``aggregate remove host`` /
  ``aggregate cache image`` — aliases of the existing ``aggregate
  host add/remove`` / ``aggregate image cache``.
- ``server group list/show/create/delete`` — re-exposes the top-level
  ``server-group`` group under ``server`` for the OSC two-word form.

### Added — OSC parity (lot 6: Swift)

- ``object save`` — alias of ``object download``.
- ``object account show`` — surface Swift account counters and
  ``X-Account-Meta-*`` keys via HEAD on the account URL.

### Added — OSC parity (lot 7: quota / usage)

- ``quota`` is now a Click group: ``quota show [--project]`` (current
  behaviour) and ``quota default [--project]`` (cloud-wide default
  values per service). Bare ``quota`` still runs ``quota show`` for
  backward compatibility.
- ``usage`` is now a Click group: ``usage show [--project]`` (single
  project) and ``usage list`` (cross-project, admin). Drops the
  ``detailed`` query param on the per-project endpoint (rejected by
  recent Nova micro-versions).
- ``quota set/unset/list/delete`` are explicitly out of scope for this
  release; tracked for a follow-up.

### Project ID resolution

- Commands that need the current project ID now fall back to
  ``client.token_data.project.id`` when the profile only declares a
  ``project_name``. ``quota`` and ``usage`` benefit from this.

### Service layer

- ``IdentityService.find_versions`` (handles HTTP 300 root).
- ``NetworkService``: ``find_extensions / get_extension /
  find_qos_rule_types / get_qos_rule_type / find_external_networks /
  find_service_providers``.
- ``VolumeService``: ``find_clusters / get_cluster / update_cluster``,
  ``find_log_levels / set_log_levels``, ``find_resource_filters``,
  ``find_manageable_volumes / find_manageable_snapshots``,
  ``get_quota_set / get_quota_set_defaults``. Cinder admin micro-version
  3.70 negotiated automatically.
- ``ComputeService``: ``get_quota / get_quota_defaults``.
- ``ImageService``: ``get_import_info``.

## [2.4.1] — 2026-05-18

### Fixed

- **``orca server create --image NAME``** (and ``--flavor NAME`` /
  ``--network NAME``) used to forward the human-readable string
  straight to Nova, which returned a 400 ``imageRef is not valid
  under any of the given schemas``. The CLI now resolves names to
  UUIDs via the matching service before posting, mirroring OSC:
  - Glance / Neutron : ``?name=`` server-side filter.
  - Nova / flavors : the ``/flavors/detail`` endpoint rejects
    ``?name=`` (``Additional properties are not allowed``) so the
    fix fetches the full flavor list and filters client-side.
  Unknown names raise ``not found``, multiple matches raise
  ``ambiguous (N matches…)`` rather than silently picking one.
  Pure UUIDs short-circuit the lookup. Live-validated on DevStack:
  ``orca server create --image orca-live-cirros --flavor
  debug-flavor --network private --wait`` boots in 16 s.

## [2.4.0] — 2026-04-28

### Added — new service

- **Manila (shared file systems)** is now wrapped under
  ``orca share``. 18th service supported. Covers share CRUD,
  access rules (NFS IP, CIFS user, CephFS x509 — surfaces the
  one-shot ``access_key`` from cephx), snapshots, and read-only
  share-type inspection. New private helper
  ``orca_cli/core/client.share_url`` with the same ``sharev2`` →
  ``share`` catalog fallback as ``volume_url``. Microversion pinned
  to 2.51 (unified ``/share-access-rules`` endpoint, no per-share
  action API).

### Added — OSC parity catch-up

OSC commands missing from orca in 2.3.0 are now wired up. All
admin operations are first-class: orca positions as an OSC
alternative, not a subset.

- **Nova / ``orca server``** — ``server backup`` (Nova
  ``createBackup`` with rotation), ``server volume set``
  (``--delete-on-termination`` flip).
- **Cinder / ``orca volume``** — 11 new commands across two passes:
  - ``volume snapshot unset``, ``volume type unset``,
    ``volume qos unset`` (Cinder's PUT ``/delete_keys`` quirk
    wrapped behind a single ``unset_qos_keys`` method),
    ``volume backup set/unset``, ``volume revert``
    (OSC-parity top-level shortcut).
  - ``volume host set`` (enable/disable/freeze/thaw + auto-switch
    on ``disable-log-reason``), ``volume backend capability``,
    ``volume backup record export/import`` (cross-cloud backup
    migration round-trip), ``volume group failover``,
    ``volume group set``.
- **Neutron / ``orca network`` + 4 new top-levels** — 75 new
  commands across 12 lots, every OSC ``network ...`` /
  ``port ...`` / ``router ...`` / ``subnet ...`` / etc. operation
  now has an orca counterpart:
  - **Symmetry / aliases (lots 1a + 1b)** — ``set`` aliases for
    every Neutron resource that previously had ``update``
    (network, port, subnet, router, rbac, security-group); ``qos
    rule show/set``, ``security-group rule create/list/show``,
    ``trunk unset``, ``subnet-pool unset``.
  - **New top-levels** — ``orca address-group``,
    ``orca address-scope``, ``orca ip-availability`` (admin),
    ``orca local-ip`` (+ ``local-ip association``, Yoga+ tenant
    overlay VIPs).
  - **New sub-groups** — ``floating-ip port-forwarding`` (DNAT),
    ``network meter`` + ``network meter-rule`` (admin),
    ``network flavor`` + ``flavor-profile`` (admin SDN),
    ``network segment-range`` (admin VLAN/VXLAN pools),
    ``network l3-conntrack-helper`` (per-router FTP/SIP helpers),
    ``network router ndp-proxy`` (IPv6),
    ``network agent add/remove network|router`` (admin scheduler
    binding).
- **Glance / ``orca image list``** — gains ``--visibility
  {public,private,shared,community,all}`` and the ``Visibility``
  column. Glance ``?visibility=…`` is forwarded server-side when
  filtered.

### Added — tooling

- **``orca doctor --list-deprecated``** — offline table of every
  ADR-0008 deprecated alias in the live CLI tree alongside its
  replacement. Helps users grep their scripts before the eventual
  3.0.0 cut.
- The regular ``orca doctor`` run also reports the count.
- New helpers ``count_deprecated_aliases`` and
  ``list_deprecated_aliases`` in ``orca_cli.core.aliases``.

### Changed

- **Python floor: 3.10** (3.9 was already EOL'd 2025-10). Drops
  the 6th matrix entry from CI. The codebase passed a ``pyupgrade``
  sweep: ``Dict[K,V]`` → ``dict[K,V]``, ``Optional[X]`` →
  ``X | None``, ``Union[A,B]`` → ``A | B``,
  ``isinstance(x,(A,B))`` → ``isinstance(x, A | B)``. ``UP``
  rules permanently enabled in ruff.
- ADR-0008 *Deprecation horizon* documented: aliases will be
  removed in **3.0.0** (PR draft on ``feat/3.0.0`` already prepared
  but not merged or tagged).

### Fixed

- ``security-group rule delete`` now prints a green confirmation
  message (was silent — Click 8+'s native ``DeprecationWarning``
  on the legacy ``rule-delete`` alias was the only visible output).
- Live-test suite: 54 ``invoke([...])`` invocations migrated to
  ADR-0008 paths so warning text no longer leaks into captured
  output (caught a real failure on
  ``test_resource_provider_usage`` during the v2.3.0 re-test).

### Tests

- ``services/dns``, ``services/orchestration``, ``services/image``,
  ``services/object_store`` taken to **100 % unit coverage**
  (176 new tests).
- 100 % unit coverage on the new ``FileShareService`` (Manila).
- 70+ new tests across the OSC-parity additions (Nova, Cinder,
  Neutron, Glance).
- ``tests/test_aliases.py`` introduced for the new alias helpers.
- Total: **2716 tests pass**, coverage **87.3 %**.

## [2.3.0] — 2026-04-28

### Added

- **OpenStackClient parity push: every command now follows the
  ``noun [subnoun] verb`` convention from ADR-0008.** Eleven
  refactor lots migrated ~190 hyphenated leaves into nested
  sub-groups across the live CLI tree:

    - **Lot 1** (modules with ≤ 4 leaves): `aggregate host/image`,
      `alarm state/quota`, `auth token`, `endpoint-group project`,
      `flavor access`, `group user/member`, `role assignment/implied`,
      `secret acl`, `security-group rule`, `trunk subport`,
      `user password`.
    - **Lots 2–3**: `zone tld/transfer`, `stack event/output/
      resource/template/resource-type`.
    - **Lots 4–5**: `object account/container`, `qos policy/rule`.
    - **Lot 6**: `rating metric/module`, `metric archive-policy/
      resource-type/resource/measures`.
    - **Lot 7**: `image cache/member/tag/task/stores`.
    - **Lot 8**: `loadbalancer amphora/healthmonitor/l7policy/
      l7rule/listener/member/pool/stats/status` (35 leaves).
    - **Lot 9**: `placement resource-provider/resource-class/
      trait/allocation/usage` (29 leaves).
    - **Lot 10**: `backup action/client/job/session` (21 leaves),
      `cluster nodegroup/template` (9 leaves).
    - **Lot 11** (final): `profile color/region/import/export`.

  Every legacy hyphenated name lives on as a `deprecated=True`
  alias — running `orca volume attachment-create …` still works
  but prints a one-line yellow hint pointing at the new path.
  The ratchet test `tests/test_naming_convention.py` is now
  whitelist-clean apart from documented compound-verb exceptions
  (`server confirm-resize`, `volume upload-to-image`, etc.).
- **Coverage gap-closure with python-openstackclient.** Several
  services gained the resources OSC exposed but orca didn't:

    - `stack` — Heat snapshots (`snapshot {create,delete,list,
      show,restore}`), `adopt`, `environment show`, `failures
      list`, `file list`, `resource {signal,metadata,
      mark-unhealthy}`, `breakpoints`.
    - `zone` — Designate `abandon`, `axfr`, `share/*`,
      `blacklist/*`, `import`, `export`.
    - `image` — full Glance metadef catalogue (`metadef
      namespace/object/property/resource-type` — 15 commands).
    - `secret` — Barbican consumers (`consumer add/remove/list`),
      `store list`.
    - `volume` — Cinder admin pools (`pool list`) and hosts
      (`host list/show/{enable,disable,thaw,freeze}`).
    - `key-manager` — Barbican `put-payload` for binary secrets.
- **DevStack live e2e test harness.** `tests/devstack/` now ships
  a 16-file pytest suite covering ~510 commands across all 17
  service modules, run against a real DevStack on
  `192.168.1.65`. Marked `@pytest.mark.live` and excluded from
  the default run; opt in with `pytest -m live`.

### Fixed

- **OrcaClient** — `volume_url` falls back through
  `volumev3 → block-storage` (Cinder service-type rename),
  `validate_id` accepts 64-hex Keystone credential IDs, `delete()`
  forwards `json=` kwargs through `_http.request("DELETE", ...)`.
  Added `with_version(url, version)` idempotent helper for
  catalog URL versioning.
- **Identity service** — federation paths now correctly include
  the `OS-FEDERATION` prefix (20 occurrences fixed); endpoint
  groups use `OS-EP-FILTER`; `role implied` uses
  `/v3/roles/{prior}/implies/{implied}` (was: incorrect
  `/role_inferences/...` shape).
- **Compute service** — `os-extra-specs` → `os-extra_specs`
  (Nova path is underscored). Server-group create now sends
  `policy: <single>` per Nova v2.64 (was rejected as
  `policies: [<single>]`).
- **Placement service** — pinned to microversion 1.20;
  `set_inventory` tries POST first and falls back to PUT on 409
  to handle the create-vs-update split cleanly.
- **Orchestration service** — `_resolve_stack` now falls back
  to ID-filtered listing when name lookup fails (Heat
  stack-by-UUID quirk).
- **Volume service** — Cinder QoS body shape: specs are flattened
  on the `qos_specs` payload root, not nested under `specs`.
- **Designate** — text/dns body streaming via
  `OrcaClient.put_stream`/`get_stream` for zone import/export.

## [2.2.1] — 2026-04-27

### Fixed

- **Documentation site overhaul: per-command pages are now generated
  from the live CLI.** ``docs/commands/*.md`` had silently rotted
  since the ADR-0008 nesting migration in 2.0.0 — pages still showed
  the legacy hyphenated forms (``volume attachment-create``,
  ``server create-image``, …) and ``getting-started.md`` still
  recommended ``eval "$(_ORCA_COMPLETE=bash_source orca)"`` as the
  bash completion install (the snippet ADR-0010 made obsolete back in
  2.1.0). The hand-written layer is replaced by ``mkdocs-click``
  wrappers, one per top-level command, so the rendered help can no
  longer drift from ``orca <cmd> --help``. ``scripts/gen-command-docs.py``
  regenerates the wrapper files on demand. The single-page
  ``docs/reference.md`` (already auto-generated) is unchanged. The
  ``docs/index.md``, ``docs/commands/index.md``, ``docs/getting-started.md``
  and ``README.md`` landing pages were rewritten to advertise the
  full 2.2.0 surface (federation, CloudKitty rating,
  ``volume upload-to-image``, the new completion-install flow). The
  mkdocs nav now lists the previously orphan ADR 0009 (server boot
  mode policy) and 0010 (static completion script).

## [2.2.0] — 2026-04-27

### Fixed

- **Error messages now reach the central red ``Error:`` formatter
  instead of falling through as ``Unexpected error: …``.** A
  CLI-coherence audit on 2026-04-27 found 72 distinct ``raise
  click.ClickException(…)`` and ``raise click.UsageError(…)`` paths
  spread across 17 command modules (profile lookups, KEY=VALUE parse
  errors, mutually-exclusive flag violations, file I/O failures,
  ambiguous name resolution, …). These bypassed ``main()``'s
  ``OrcaCLIError`` handler — per CLAUDE.md every error surfaced to
  the user must subclass ``OrcaCLIError``. All 72 sites now raise
  ``OrcaCLIError``; the ratchet test
  ``tests/test_no_click_exceptions_in_commands.py`` rejects new
  occurrences. Behaviour-equivalent on the happy path; the visible
  change is the consistent red ``Error: …`` line.

### Added

- **Shell tab-completion now covers every common resource ID
  argument.** The same audit found four modules — ``flavor``,
  ``image``, ``network``, ``server-group`` — with no
  ``shell_complete=`` callbacks on their UUID args, so ``orca flavor
  show <TAB>`` and equivalents returned no suggestions even though
  the per-resource callbacks existed in
  ``orca_cli/core/completions.py``. Wired ``complete_flavors``,
  ``complete_images`` and ``complete_networks`` onto the four
  resource groups; added the missing ``complete_server_groups``
  callback. ``volume upload-to-image`` (added in 2.1.1) gets
  ``complete_volumes`` for parity with the other ``volume``
  subcommands.

## [2.1.2] — 2026-04-27

### Fixed

- **`volume upload-to-image` was unusable on older Cinder
  microversions.** The action body sent `visibility` and `protected`
  unconditionally, even when the user accepted the Click defaults
  (`private` / `False`). Older Cinder builds (e.g. some shipping
  microversions still in production at large public-cloud operators)
  reject the request with HTTP 400 — *Additional properties are not
  allowed ('protected', 'visibility' were unexpected)* — because
  those fields were added in a later microversion. Both flags are
  now opt-in: omitted from the JSON body unless the user passes one
  explicitly, in which case the value is forwarded verbatim. Glance
  applies its own server-side defaults when the keys are absent, so
  modern clouds see no behavioural change. `--disk-format` and
  `--container-format` keep their hard-coded defaults — those are
  stable across every Cinder microversion.

## [2.1.1] — 2026-04-27

### Added

- **`orca volume upload-to-image`** — materialize a Cinder volume as a
  downloadable Glance image (wraps the `os-volume_upload_image` action).
  This is the missing primitive for migrating boot-from-volume instances
  between clouds: `orca server image create` on a BFV server only produces
  a 0-byte Glance shell that points at a Cinder snapshot, whereas the new
  command yields a self-contained image that `orca image download` can
  actually pull. Supports `--disk-format`, `--container-format`,
  `--visibility`, `--protected`, `--force` (required for in-use volumes,
  with a client-side pre-flight so users get an actionable message instead
  of an opaque 400), `--property KEY=VALUE` (validated against Glance's
  schema and applied via JSON-Patch on the resulting image, since Cinder
  itself does not accept arbitrary properties in the action body), and
  `--wait` (adaptive polling: 5 s for the first minute, then 15 s, with a
  live status/size line and an early exit on `killed`/`deleted`). The
  `--help` of `orca server image create` and `orca image download` now
  cross-reference the new workflow so the BFV pitfall is discoverable
  from both ends. ADR-0008 records `volume upload-to-image` as a
  permanent compound-verb exception (mirrors the Cinder action name).

## [2.1.0] — 2026-04-27

### Added

- **Full image-property support across `image create`, `image update` and
  `image show`.** Custom Glance properties (`os_distro`, `os_version`,
  `hw_qemu_guest_agent`, `cinder_img_volume_type`, …) can now be set on
  creation (`--property KEY=VALUE`, repeatable) and edited atomically on
  existing images (`--property` and `--remove-property`, `--ignore-missing`
  for idempotent removal). Property keys are validated client-side against
  Glance's `^[A-Za-z0-9_:.\-]{1,255}$` schema before any HTTP round-trip,
  and only the first `=` splits the value so URL-like values survive intact
  (`--property url=https://x?a=1&b=2`). `image show` surfaces every custom
  key Glance returns plus the integrity fields (`checksum`, `os_hash_algo`,
  `os_hash_value`, `direct_url`, `tags`): as a `Properties` sub-table in
  table format, under a new top-level `"properties"` aggregate in JSON
  (with each custom key **also** mirrored at the JSON root for backward
  compatibility — `jq .os_distro` keeps working alongside the new
  `jq .properties.os_distro`), and as `KEY VALUE` lines in value format.
  This unblocks lossless inter-cloud image migration.

### Fixed

- **Shell completion install no longer slows shell startup.** The
  bash/zsh install used to append
  `eval "$(_ORCA_COMPLETE=bash_source orca)"` to the rc file, which
  re-spawned `orca` (with its full ~60-module command tree) and a
  `bash --version` subprocess on every login (Click's
  `_check_version()`). Real-world cost was 1–3 s per shell, with a
  documented incident where hundreds of `orca` processes piled up on
  a single SSH session. `orca completion install bash` (and `zsh`)
  now generates the completion script **once** into
  `$XDG_DATA_HOME/orca/completion.<shell>` and writes a plain
  `source <path>` line into the rc — login cost drops to microseconds.
  Re-running the install on an older config silently migrates the
  legacy `eval` line out of the rc. See ADR 0010.

## [2.0.1] — 2026-04-22

### Fixed

- **Shell tab-completion triggered a fresh Keystone auth every 30 s.**
  The completion cache TTL was 30 seconds, so on an active terminal
  where the user kept typing, most tab presses after the first 30 s
  fell back to a cold fetch (auth + HTTP list). Extended the TTL to
  5 minutes — completion data (server names, flavor IDs, region
  lists) changes slowly and the old short TTL made the tab key feel
  sluggish.
- **Region completion mixed results across profiles.** The
  ``--region`` completion callback cached every region list under
  the same ``default_regions.json`` file regardless of
  ``--profile`` / ``ORCA_PROFILE``, so a user with several profiles
  pointing at different clouds saw the other cloud's regions. The
  callback now resolves the active profile and caches per-profile
  (``<profile>_regions.json``), matching the behaviour of the other
  completion callbacks in ``orca_cli/core/completions.py``.

## [2.0.0] — 2026-04-22

### Changed

- **Service layer completed.** Every OpenStack resource orca talks to
  now routes through a typed ``*Service`` class in ``orca_cli/services/``
  instead of constructing endpoint URLs in the command modules.
  Thirteen services land in this release — ``NetworkService``
  (Neutron), ``ComputeService`` (Nova non-server),
  ``IdentityService`` (Keystone, including enforcement limits),
  ``OrchestrationService`` (Heat), ``LoadBalancerService`` (Octavia),
  ``ObjectStoreService`` (Swift), ``DnsService`` (Designate),
  ``KeyManagerService`` (Barbican), ``RatingService`` (CloudKitty),
  ``MetricService`` + ``AlarmService`` (Gnocchi + Aodh),
  ``ContainerInfraService`` (Magnum), ``PlacementService``, plus the
  existing ``ServerService`` / ``VolumeService`` / ``ImageService``.
  Each service exposes ``find`` / ``get`` / ``create`` / ``update`` /
  ``delete`` methods and returns TypedDicts from ``orca_cli/models/``
  so mypy catches field-name typos at check time. ADR-0007 is updated
  per resource. Behaviour is unchanged — retry, auth, pagination still
  live in ``OrcaClient``. This is a surface-level reorganisation of
  the codebase; the CLI surface is identical.

### Fixed

- **Silent 1000-item cap in batch commands.** ``orca project cleanup``
  and ``orca server bulk {stop,delete,reboot}`` called
  ``ServerService.find(limit=1000)`` and silently dropped extra rows
  on tenants with more than 1000 servers — the batch operation
  reported success while leaving resources behind. Every such call
  now uses ``find_all()`` with full pagination. Also applied to the
  server-name-resolution side calls in ``orca volume tree``,
  ``orca network topology`` / ``trace``, ``orca ip-whois`` and
  ``orca event``.

## [1.4.0] — 2026-04-20

### Security

- **Visible warning when TLS verification is off.** Running with
  `insecure=true` now emits an explicit stderr warning on every
  invocation. Previously the flag was silent — the risk was invisible.
- **Validate the `cacert` path at startup.** A profile that points at a
  missing or unreadable CA bundle now fails with `ConfigurationError`
  (mentioning the path) instead of surfacing a cryptic TLS handshake
  error on the first request.
- **Pin `pypa/gh-action-pypi-publish` to an immutable commit SHA**
  (`cef22109…`, v1.14.0) rather than the mutable `release/v1` tag. The
  publish job has `id-token: write`, so an upstream action compromise
  could otherwise inject code into the release pipeline.

### Fixed

- **Token cache no longer subject to torn writes.** `_save_token_cache`
  writes to a sibling tempfile with mode 0600, then `os.replace`s it
  into place atomically. Two concurrent `orca` invocations racing on a
  re-authentication can no longer leave the cache half-written for the
  next reader.

### CI

- `ci.yml` caches pip and `.venv` (keyed on `pyproject.toml`), adds a
  `build` job that runs `poetry build` + publishes the dist artifacts,
  and a `security` job that runs `gitleaks` and `pip-audit` against the
  installed runtime deps.
- `deploy-docs.yml` is gated on the CI workflow succeeding on `main`
  (via `workflow_run` + `conclusion == 'success'`) so a failing build
  can no longer ship stale documentation.

## [1.3.0] — 2026-04-20

### Added

- `OrcaClient.paginate(url, key, ...)` walks OpenStack marker-based
  pagination to completion. `audit`, `overview`, `cleanup`, `export` and
  their lookup maps now use it instead of a bare `limit=1000`.
- `safe_output_path()` and `safe_child_path()` in `core/validators`:
  refuse to overwrite existing symlinks, and refuse API-derived child
  names that resolve outside a base directory (`..` traversal in bulk
  downloads). Applied to every command that writes a user-supplied path.
- Global `--debug` flag (also `ORCA_DEBUG=1`) wires an `orca_cli` logger
  to stderr. Logs auth intent (URL / user / project — not the payload),
  token-cache hits, each HTTP request (method, URL, redacted headers,
  status, duration) and retry decisions.
- `APIError.request_id` now carries the OpenStack `x-openstack-request-id`
  (or Nova's `x-compute-request-id`) when the service returns one. The id
  is also appended to the error message so an operator can correlate
  failures with back-end logs. Same treatment for `PermissionDeniedError`.
- `ProfileNotFoundError` and `ProfileConflictError` exceptions (both
  subclass `ConfigurationError`).

### Fixed

- **Silent data loss in batch commands.** `audit` / `overview` / `cleanup` /
  `export` passed `limit=1000` to Nova/Cinder/Neutron without paginating,
  so any tenant with more than 1000 of a given resource had rows dropped
  with no indication.
- **Symlink-race on file outputs.** Writing `orca export -o link.yaml`
  to a pre-existing symlink followed the link and clobbered the target.
  Fixed across `export`, `image download`, `container save`,
  `object download` / `container-save`, `keypair create`, `zone export`,
  `stack abandon`, `profile to-openrc` / `to-clouds`.
- **429 Too Many Requests failed immediately.** The retry loop honours
  `Retry-After` (RFC 7231 seconds or HTTP-date), capped at 60s before
  surfacing the error. 429 retries on any method including POST/PATCH —
  rate-limited requests are not processed, so re-sending is safe.
- **Thundering-herd retries.** 5xx and transient-network backoff now uses
  full jitter (`random.uniform(0, base * 2**attempt)`) so parallel CLI
  invocations in a CI runner don't retry in lockstep.

### Changed

- `core/config.py` profile mutations raise `ProfileNotFoundError` /
  `ProfileConflictError` instead of stdlib `KeyError` / `ValueError` —
  these now format through the CLI's top-level error handler like every
  other `OrcaCLIError`.
- `core/shell_completion.py::install_completion` raises `OrcaCLIError`
  instead of `ValueError` on an unsupported shell.

### Security

- TLS warning + Retry-After cap are guards against denial-of-service by
  a misbehaving upstream. No secrets were leaked in any prior release.

## [1.2.0] — 2026-04-20

### Added

- `orca completion install [shell]` auto-installs shell completion:
  bash/zsh append an idempotent `eval` line to the rc file, fish writes
  `~/.config/fish/completions/orca.fish`. Auto-detects `$SHELL` when the
  argument is omitted.
- `orca setup` offers to auto-install shell completion at the end of the
  wizard, then validates the just-saved profile against Keystone so typos
  surface immediately. Both steps are skipped in non-TTY contexts.
- `orca profile list` gains an `Auth` column (password vs app-cred) and a
  `User / Credential` column that displays the application-credential id
  for AC profiles; project cell shows `(pre-scoped)` for AC.

### Changed

- Shell-completion helpers moved from `commands/setup.py` to
  `core/shell_completion.py` and are shared by `setup` and `completion`.

## [1.1.0] — 2026-04-20

### Added

- Native `v3applicationcredential` auth in `OrcaClient` — id+secret or
  name+user reference, pre-scoped (no project/domain scope needed).
- `profile add` / `profile edit` / `setup` ask password vs application
  credential and round-trip the AC fields through `to-clouds` /
  `to-openrc` and `from-clouds` / `import-openrc`.
- Token cache key derived from credential identity (not user/project)
  when the auth type is application credential.
- `OS_AUTH_TYPE`, `OS_APPLICATION_CREDENTIAL_*` and `ORCA_*` equivalents
  wired through the config priority resolution.
- `orca application-credential create --save-profile NAME` persists the
  freshly minted AC directly as an orca profile.
- `orca hypervisor usage`: per-host CPU / RAM / disk fill rate with
  color-threshold bars, `--top`, `--threshold`, sort options.

### Fixed

- `application-credential` commands resolved the current user id from the
  token correctly (the token wrapper was being read twice, always falling
  back to the literal string `"me"`).

## [1.0.3] — 2026-04-19

### Added

- `orca rating` group — full CloudKitty coverage. Validated live against
  Infomaniak (dc3-a, non-admin).
  - End-user: `info`, `metric-list` / `metric-show`, `summary`,
    `dataframes` (v2 with v1 fallback), `quote`.
  - Admin: `module-list` / `module-show` / `module-enable` /
    `module-disable` / `module-set-priority` (hashmap, pyscripts, noop).
    Uses fetch-merge-PUT because CloudKitty `PUT` requires the full
    representation.
  - Admin (hashmap): `service-*`, `field-*`, `mapping-*` (flat/rate,
    field- or service-level), `threshold-*` (tiered pricing), `group-*`.

### Fixed

- `rating metric-show` path is `/v1/info/metrics/{id}` (plural);
  CloudKitty returns 405 on the singular form.
- `validate_id` passes `None` through so the callback is safe on optional
  Click parameters (needed by hashmap `--field-id`, `--service-id`,
  `--group-id` filters).

## [1.0.2] — 2026-04-19

### Fixed

- `alarm set`: Aodh requires the full alarm representation on `PUT`, not
  a partial. Fetch current, merge user updates, strip read-only fields
  (`alarm_id`, `project_id`, `user_id`, `timestamp`, `state_timestamp`,
  `state_reason*`), then `PUT`. Previously returned 400 on any update
  that didn't include `name` + `type` + `rule`.
- `validate_id` accepts 32-char bare-hex IDs alongside hyphenated UUIDs.
  Keystone projects/users/groups on many clouds (Infomaniak included) are
  exposed as hex-without-hyphens, which made
  `alarm quota-set <project_id>` and similar commands unusable.
- `__version__` reads from the installed package metadata via
  `importlib.metadata.version` instead of a hardcoded string that had
  drifted from `pyproject.toml`.

## [1.0.1] — 2026-04-19

### Fixed (P1 — production blockers)

- `server ssh` drops the permissive `orca-*` glob fallback, recognises
  `.pem` / `.key` variants, and reuses `_find_ssh_key` in the port-forward
  subcommand.
- `backup`: clarified that this group is Freezer (DR); Cinder volume
  backups live under `orca volume backup-*`.

### Fixed (P2 — UX)

- Distinguish 401 (`AuthenticationError`, triggers re-auth) from 403
  (`PermissionDeniedError` — valid token, insufficient role) across all
  HTTP helpers in `core/`, `image`, `container`, `object_store`.
- Sniff HTML error pages (`text/html` or `<!doctype` / `<html` prefix)
  and surface a clear "endpoint advertised in the catalogue but not
  exposed on this cloud" message.
- `event list` drops columns whose values are all empty; long UUID
  columns use `overflow=fold` instead of `no_wrap` to avoid zero-width
  cells in Rich tables.
- `server ssh` detects the distro of boot-from-volume servers via the
  attached volume's `volume_image_metadata.os_distro` (fixes Debian 12
  BFV `→ root`).

### Fixed (P3 — polish)

- `server shelve` / `unshelve`: new `--wait` flag (waits for
  `SHELVED_OFFLOADED` / `ACTIVE`).
- `flavor list`: `--limit` is now optional; auto-paginates via Nova
  marker otherwise.
- `audit`: ICMPv6 open to `0.0.0.0/0` downgraded CRITICAL → MEDIUM
  (RFC 4861 Neighbor Discovery / MLD is the expected baseline).
- `recordset list`: split SOA single-record on whitespace; render NS /
  MX / TXT multi-values one-per-line; ID column uses `overflow=fold`.

## [1.0.0] — 2026-04-16

Initial public release on PyPI as `orca-openstackclient`.

Services covered: Nova (compute, flavors, keypairs, server groups,
hypervisors), Neutron (networks, subnets, ports, routers, floating IPs,
security groups, QoS, trunks), Cinder (volumes, snapshots, backups),
Glance (images), Keystone (identity: domains, projects, users, groups,
roles, trusts, tokens, application credentials, federation, policies),
Octavia (load balancers, listeners, pools, members, health monitors),
Barbican (secrets, containers), Magnum (cluster templates, clusters),
Gnocchi (metrics, measures, resources, aggregations), Placement (resource
providers, inventories, allocations), Heat (stacks, events), Freezer
(backups), Designate (zones, recordsets), Aodh (alarms).

Orca-exclusive commands: `overview`, `watch`, `doctor`, `audit`,
`cleanup`, `export`, `find`, `ip-whois`.

Multi-profile config (`~/.orca/config.yaml`), `clouds.yaml` interop,
`OS_*` env var support, Keystone v3 password auth, Rich-powered output
(table / json / value), Bash + Zsh + Fish completion.

[1.3.0]: https://github.com/stackopshq/orca-cli/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/stackopshq/orca-cli/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/stackopshq/orca-cli/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/stackopshq/orca-cli/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/stackopshq/orca-cli/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/stackopshq/orca-cli/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/stackopshq/orca-cli/releases/tag/v1.0.0
