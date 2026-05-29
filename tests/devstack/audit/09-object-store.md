# 09 — Object Store (Swift) — Live API audit

**Target**: DevStack `192.168.1.65` / Swift
**orca version**: 2.6.1 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-29

## Coverage

| | OSC | orca |
|---|---:|---:|
| Mots pour mots OSC | 17 | 31 |
| OSC absentes d'orca | **0** | — |

100 % parité OSC (17/17). orca expose 14 commandes utilitaires
supplémentaires (``stats``, ``tree``, ``download``, …).

## Gaps comblés

### A. ``object create`` alias

OSC : ``object create`` = Swift PUT object. orca : ``object upload``.
Ajout d'un alias ``object.add_command(object_upload, name="create")``
sans dupliquer le code.

### B. Nouveau top-level ``object-store``

OSC met l'admin Swift sous ``openstack object store …``. orca
expose ``object account …`` (3 mots). Module
``orca/commands/object_store_alias.py`` qui re-expose
``account set/show/unset`` au path OSC 4-mots.

Override ajouté dans ``main.py`` :
``"object_store_alias": ["object-store"]``.

## Live tests (DevStack)

```
orca object-store account show         ✅ Container-Count=1, Bytes-Used=0
orca container list                    ✅ volumebackups
orca object create / object upload     ✅ (same callback, OSC alias)
```

## Bugs / régressions

**0.** Pas de breaking change.

## Conclusion

Object Store (Swift) est désormais **100 % couvert** en parité
OSC (17/17). Deux ajouts triviaux (alias ``object create`` +
nouveau top-level ``object-store``).
