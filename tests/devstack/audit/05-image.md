# 05 — Image (Glance) — Live API audit

**Target**: DevStack `192.168.1.65` stable/2025.2 / Glance v2 (file backend)
**orca version**: 2.6.1 + this patch
**Profile**: `devstack`
**Run date**: 2026-05-29

## Coverage

| | OSC | orca |
|---|---:|---:|
| Mots pour mots OSC | 37 | 56 |
| OSC absentes d'orca | **1** (limitation Click documentée) | — |

**36/37 = 97,3 % path-exact, 100 % sémantique.** Le seul "manquant"
mot-pour-mot est ``image import info`` que Click ne permet pas
d'exposer sous le leaf ``image import`` ; orca le fournit sous
``image info import`` (même callback).

## Gaps comblés dans ce patch

### A. ``image member get IMAGE PROJECT``

Alias trivial : OSC parle de ``get``, orca de ``show``. Même
callback ``image_member_show``. Ajouté via
``image_member.add_command(image_member_show, name="get")``.

### B. ``image metadef object property show NS OBJECT PROP``

Glance n'expose pas d'endpoint isolé pour une property — elle vit
comme clé dans le dict ``properties`` retourné par
``GET /metadefs/namespaces/{ns}/objects/{obj}``. orca résout
client-side : nouveau sub-group ``image metadef object property``
avec leaf ``show`` qui récupère l'objet et extrait la property
demandée. 404 si la property n'existe pas.

### C. ``image import info`` (documenté)

OSC : ``image import info`` (3 mots).
orca : ``image info import`` (4 mots, même callback).

**Pourquoi pas mot-pour-mot ?** ``image import`` est déjà une
``@click.command`` leaf (orca image import IMAGE --method
web-download …) qui consomme un argument positional + des options.
Click ne supporte pas qu'un même nom soit à la fois un leaf
command et un group (même pattern que ``server resize`` /
``server backup`` Phase 1.2). Le seul moyen serait de casser
``image import IMAGE`` ; on préfère documenter la divergence.

Sémantiquement, ``orca image info import`` et ``openstack image
import info`` interrogent le même endpoint ``/v2/info/import`` et
renvoient les mêmes méthodes.

## Live tests (DevStack)

```
orca image member get <cirros-uuid> admin
  → 404: "admin not found in the member list" (expected — admin is
    the image owner, not a member)
orca image metadef object property show "OS::Compute::Quota" \
  "CPU Limits" "quota:cpu_shares"
  → returns {name, type, title, description} of that property
orca image info import
  → glance-direct, web-download, copy-image (sémantique parité)
orca image stores list (alias)        ✅
orca image save IMG -o /tmp/x.qcow2   ✅ (lot 4)
orca image add project IMG PROJECT    ✅ (lot 4)
```

## Bugs / régressions

**0.** Aucun. Toutes les commandes existantes continuent de
fonctionner.

## Conclusion

Image (Glance) est désormais **100 % couvert sémantiquement**
(37/37) et **97,3 % path-exact** (36/37). Le seul écart de path
est documenté en limitation Click (commande leaf ne peut pas être
aussi un group).
