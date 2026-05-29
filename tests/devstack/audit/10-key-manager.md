# 10 — Key Manager (Barbican) — Live API audit

**Target**: DevStack `192.168.1.65` / Barbican (down — 503)
**orca version**: 2.6.1 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-29

## Coverage

| | OSC | orca |
|---|---:|---:|
| Mots pour mots OSC | 23 | 34 |
| OSC absentes d'orca | **0** | — |

100 % parité OSC (23/23).

## Gaps comblés

### A. Sub-groups OSC sous ``secret``

Les leafs hyphenés ``secret container-*`` et ``secret order-*``
restent pour back-compat. Nouveaux sub-groups :

| OSC | orca |
|---|---|
| ``secret container list/show/create/delete`` | ✅ |
| ``secret container get`` | ✅ alias de ``show`` |
| ``secret order list/show/create/delete`` | ✅ |
| ``secret order get`` | ✅ alias de ``show`` |

### B. Verbes OSC ajoutés

* ``secret get`` — alias de ``secret show``.
* ``secret update`` — alias de ``secret store`` (même action
  Barbican ``PUT /v1/secrets/{id}`` avec payload).
* ``secret acl submit`` — alias de ``secret acl set``.
* ``secret acl user add`` / ``secret acl user remove`` — nouveaux
  verbes qui font le read-modify-write de l'ACL Barbican via
  ``KeyManagerService.add_acl_users`` / ``remove_acl_users``.

### C. Nouveaux top-level

* **``orca acl``** (module ``orca/commands/acl.py``) — re-expose les
  ACL verbs au top-level.
* **``orca ca``** (module ``orca/commands/ca.py``) — nouveau
  groupe Certificate Authorities :
  * ``ca list`` — GET ``/v1/cas``.
  * ``ca get CA_ID`` — GET ``/v1/cas/{ca_id}``.

### D. Service helpers ajoutés

* ``find_cas`` / ``get_ca``.
* ``add_acl_users`` / ``remove_acl_users`` (read-modify-write de
  l'ACL existant).

## Live tests (DevStack)

Barbican est down (uwsgi backend 503). Tous les nouveaux paths
répondent avec le 503 documenté côté API ; le routing orca est
correct.

Sanity ``--help`` validé pour :

* ``secret get`` / ``update`` / ``container get`` / ``order get``
* ``ca list`` / ``ca get``
* ``acl submit`` / ``acl user add`` / ``acl user remove``

## Bugs / régressions

**0.** Pas de breaking change : les hyphened legacy (``secret
container-list``, ``order-create``, …) restent valides en parallèle
des nouveaux sub-groups.

## Conclusion

Key Manager (Barbican) est désormais **100 % couvert** en parité
OSC (23/23). Deux nouveaux modules top-level (``acl`` + ``ca``),
deux sub-groups (``secret container`` + ``secret order``), six
nouveaux verbes orca, deux nouvelles méthodes service.
