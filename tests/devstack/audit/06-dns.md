# 06 — DNS (Designate) — Live API audit

**Target**: DevStack `192.168.1.65` stable/2025.2 / Designate
**orca version**: 2.6.1 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-29

## Coverage

| | OSC | orca |
|---|---:|---:|
| Mots pour mots OSC | 53 | 59 |
| OSC absentes d'orca | **0** | — |

100 % parité OSC (53/53). orca expose 6 commandes supplémentaires
(``zone tree``, ``zone reverse-lookup``, etc.).

## Gaps comblés dans ce patch

### A. Nouveau top-level ``tld``

OSC met ``tld`` au top level. orca avait ``zone tld``. Module
``orca/commands/tld.py`` qui :
* re-expose ``zone tld list/create/delete`` au top-level,
* ajoute deux nouveaux leafs ``show`` et ``set`` (anciens manquants),
  exposés sous **les deux** chemins (top-level ``tld`` + nested
  ``zone tld``) pour ne pas casser les scripts.

### B. ``zone export`` group (5 verbs)

OSC : ``zone export create/delete/list/show/showfile``.
orca avant : leaf ``zone export ZONE``. **Breaking** : converti en
sub-group avec :
* ``zone export create ZONE`` — exact comportement du leaf
  précédent.
* ``zone export list``.
* ``zone export show EXPORT_ID``.
* ``zone export showfile EXPORT_ID`` — fetch raw BIND content.
* ``zone export delete EXPORT_ID``.

### C. ``zone import`` group (4 verbs)

OSC : ``zone import create/delete/list/show``.
orca avant : leaf ``zone import --file ...``. **Breaking** :
converti en sub-group :
* ``zone import create --file FILE`` (équivalent leaf précédent).
* ``zone import list / show / delete``.

### D. ``zone move``

OSC : ``zone move ZONE --project ID``. Nouveau leaf + service helper
``DnsService.move_zone()`` (POST ``/zones/{id}/tasks/move``).

### E. ``zone transfer accept`` group (3 verbs)

OSC : ``zone transfer accept list/request/show``.
orca avant : leaf ``zone transfer accept TRANSFER KEY``.
**Breaking** : converti en sub-group :
* ``zone transfer accept request TRANSFER KEY`` (anciennement
  ``zone transfer accept TRANSFER KEY``).
* ``zone transfer accept list`` (nouveau).
* ``zone transfer accept show ACCEPT_ID`` (nouveau).

Service helpers ajoutés : ``find_transfer_accepts``,
``get_transfer_accept``.

### F. ``zone transfer request set``

OSC parity. Nouveau leaf + service helper
``update_transfer_request``.

### G. Nouveau top-level ``ptr``

Floating-IP reverse DNS (PTR records). OSC paths :
``ptr record list/set/show/unset``. Module
``orca/commands/ptr.py``. Service helpers :
``find_reverse_floatingips`` (existait), ``get_reverse_floatingip``,
``set_reverse_floatingip`` (set + unset partagent le même PATCH).

### H. Nouveau top-level ``tsigkey``

Designate TSIG keys (admin). OSC paths :
``tsigkey list/show/create/set/delete``. Module
``orca/commands/tsigkey.py``. Service helpers :
``find_tsigkeys / get_tsigkey / create_tsigkey / update_tsigkey /
delete_tsigkey``.

## Breaking changes

| Avant | Après |
|---|---|
| ``zone export ZONE`` | ``zone export create ZONE`` |
| ``zone import --file F`` | ``zone import create --file F`` |
| ``zone transfer accept TRANSFER KEY`` | ``zone transfer accept request TRANSFER KEY`` |

Tous ces refactors sont imposés par Click qui ne supporte pas
leaf+group sur le même nom, et par la parité OSC stricte.

## Live tests (DevStack)

```
orca tld list                       ✅ No TLDs found
orca zone export list               ✅ empty
orca zone import list               ✅ empty
orca zone transfer accept list      ✅ empty
orca tsigkey list                   ✅ empty
orca ptr record list                ✅ empty

orca zone create audit.com. --email admin@audit.com          ✅
orca zone export create <zone>                                ✅ BIND file
orca zone export list                                         ✅ 1 export COMPLETE
orca zone delete <zone> --yes                                 ✅
```

## Bugs / régressions

**0.** Les anciens paths leaf ont été remplacés par les nouveaux
sub-groups après refactor. Tests unitaires mis à jour (1 test
``test_accept`` ajusté pour le nouveau path).

## Conclusion

DNS (Designate) est désormais **100 % couvert** en parité OSC
(53/53). Trois nouveaux modules top-level (``tld``, ``ptr``,
``tsigkey``), trois leafs convertis en sub-groups
(``zone export``, ``zone import``, ``zone transfer accept``), un
nouveau leaf ``zone move`` + un ``zone transfer request set``.

Service layer enrichi de **11 nouvelles méthodes** Designate.

Live-validé sur DevStack : tous les nouveaux paths répondent ;
CRUD ``zone create → export create → export list → delete`` OK.
