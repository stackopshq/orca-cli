# 04 — Volume (Cinder) — Live API audit

**Target**: DevStack `192.168.1.65` stable/2025.2 / Cinder (LVM)
**orca version**: 2.6.0 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-29

## Coverage

| | OSC | orca |
|---|---:|---:|
| Mots pour mots OSC | 82 | 112 |
| OSC absentes d'orca | **0** | — |

100 % parité OSC (82/82). orca expose en plus ~30 commandes (retype,
revert, tree, summary, set-bootable/set-readonly, set/unset, …).

## Gaps comblés dans ce patch

### A. Nouveau top-level ``block-storage``

OSC met sous ``openstack block storage …`` un bloc d'admin :
``cluster``, ``log level``, ``resource filter``, ``volume manageable
list``, ``snapshot manageable list``, ``cleanup``. orca le couvrait
déjà sous ``volume`` (depuis v2.5.0). Nouveau module
``orca/commands/block_storage.py`` qui re-expose ces sub-groupes au
path OSC sans dupliquer le code (chaque sous-cmd partage la même
fonction Click).

| OSC | orca |
|---|---|
| ``block storage cluster list / show / set`` | ✅ alias de ``volume cluster …`` |
| ``block storage log level list / set`` | ✅ alias de ``volume log-level …`` |
| ``block storage resource filter list / show`` | ✅ alias de ``volume resource-filter …`` |
| ``block storage volume manageable list`` | ✅ alias de ``volume manageable list`` |
| ``block storage snapshot manageable list`` | ✅ alias de ``volume snapshot manageable list`` |
| ``block storage cleanup`` | ✅ nouveau leaf (POST ``/workers/cleanup``) |

### B. ``volume backend pool list``

OSC met ``pool list`` sous ``volume backend``. orca avait
``volume pool list``. Re-exposé sous ``volume backend pool list``.

### C. ``volume backend capability show`` (breaking)

OSC : ``volume backend capability show HOST`` (4 mots).
orca avant : ``volume backend capability HOST`` (3 mots).

Refactor : ``volume_backend.command("capability")`` → sub-group
``capability`` avec leaf ``show``. **Breaking** pour la cmd niche
admin. Test mis à jour.

### D. ``volume transfer request *`` (5 verbes)

OSC : ``volume transfer request accept/create/delete/list/show``
(4 mots). orca : ``volume transfer accept/create/delete/list/show``
(3 mots). Aliases ajoutés via un sub-group ``request`` sous
``volume transfer``.

### E. Service helper

- ``VolumeService.workers_cleanup(filters)`` — POST
  ``/workers/cleanup`` avec négociation micro-version 3.70.

## Live tests (DevStack)

```
orca block-storage --help                              ✅ 4 sub-groups
orca block-storage cluster list                        ✅ empty (single-host)
orca block-storage resource-filter list                ✅ Cinder filters
orca block-storage volume manageable list --host       ✅ 1 LVM volume
orca block-storage cleanup --host devstack@lvmdriver-1 ✅ 0 cleaning, 0 unavailable
orca volume backend pool list                          ✅ devstack@lvmdriver-1#lvmdriver-1
orca volume backend capability show <host>             ✅ driver capabilities
orca volume transfer request list                      ✅ No transfers found
```

## Breaking change

- ``volume backend capability HOST`` → ``volume backend capability
  show HOST``. If you scripted the 3-word form, add ``show`` between
  ``capability`` and the host.

## Bugs / régressions

**0.** Toutes les commandes existantes continuent de fonctionner,
sauf la divergence ``backend capability`` documentée ci-dessus.

## Conclusion

Volume (Cinder) est désormais **100 % couvert** en parité OSC
(82/82). Six nouveaux paths OSC ajoutés sous ``block-storage`` et
``volume backend pool``, un nouveau leaf ``cleanup``, aliases
``volume transfer request`` et refactor mineur ``backend
capability`` (breaking documenté).

Zero régression. Live-validé sur DevStack avec etcd + Cinder
opérationnels.
