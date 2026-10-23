# HANDOFF — orca-cli
_Mis à jour : 2026-10-23 15:40_

## Objectif
Remplacer les workflows GitHub Actions (`.github/workflows/` : ci.yml, deploy-docs.yml,
publish.yml) par une CI GitLab : lint + tests, doc sur GitLab Pages
(`docs.orca.stackops.ch`), publication PyPI d'`orca-openstackclient` par Trusted Publishing.

## État
- [x] Lecture du dépôt et des workflows GitHub ; baseline locale verte sur `main`
      (ruff, mypy, 2752 tests, couverture 85,11 % pour un seuil à 85 %, `mkdocs build --strict`)
- [x] Branche `ci/gitlab-ci` + MR draft
- [ ] Plan de CI proposé à Kevin, en attente de validation
- [ ] Écriture de `.gitlab-ci.yml`
- [ ] Premier pipeline vert sur la MR
- [ ] Job `pages` exécuté sur `main` (après merge par Kevin) → prévenir gitlab-admin (certificat)
- [ ] Redirection `gh-pages` (GitHub) vers docs.orca.stackops.ch

## Prochaine étape
Attendre la validation du plan par Kevin (voir la description de la MR), puis écrire `.gitlab-ci.yml`.

## Blocages / questions pour Kevin
- Validation du plan de CI et des points ouverts (voir MR).
- Trusted publisher à déclarer sur pypi.org : namespace `stackopsplatform/products`,
  projet `orca-cli`, fichier `.gitlab-ci.yml`, environnement `pypi`.

## Demandes inter-sessions ouvertes
- Reçue de **gitlab-admin** (23/10) : écrire la CI ; le prévenir (1) après le premier push
  (branche + MR) pour vérifier le miroir GitHub, (2) quand `pages` a tourné sur `main`.
  Tout réglage côté projet (tags protégés, environnement `pypi`…) passe par gitlab-admin.

## Notes
- Projet GitLab 88002825, privé ; Pages en accès public ; runners partagés actifs ;
  aucun tag protégé ni environnement au 23/10.
- Miroir push GitLab → GitHub `stackopshq/orca-cli` (toutes branches et tags).
- La couverture est juste au-dessus du seuil (85,11 %) : un ajout non testé peut casser la CI.
- Pas de `poetry.lock` dans le dépôt : les dépendances sont résolues à chaque job.
- Branche `feat/3.0.0` (MR !10) : branche de Kevin, ne pas y toucher.
