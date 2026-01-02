# 🚀 Étape 4 : GitHub Actions CI/CD

## 📋 Objectif

Automatiser tous les tests et le déploiement avec GitHub Actions :
- ✅ Linting automatique à chaque push
- ✅ Tests unitaires automatiques
- ✅ Tests d'intégration avec services Docker
- ✅ Build automatique de l'image Docker
- ✅ Push sur Docker Hub (branche main uniquement)

---

## 🏗️ Architecture du Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  JOB 1: Lint & Code Quality 🔍     │
         │  - Black (formatage)                │
         │  - Flake8 (syntaxe)                 │
         │  - Pylint (analyse statique)        │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  JOB 2: Unit Tests 🧪              │
         │  - pytest -m unit                   │
         │  - Coverage report                  │
         │  - Upload to Codecov                │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  JOB 3: Integration Tests 🔗       │
         │  Services:                          │
         │    - Elasticsearch 8.11.3           │
         │    - MongoDB 7.0                    │
         │    - Redis 7.2                      │
         │  - pytest -m integration            │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  JOB 4: Build Docker Image 🐳     │
         │  - docker/build-push-action         │
         │  - Cache optimization               │
         │  - Multi-platform support           │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  JOB 5: Push to Registry 🚀        │
         │  (main branch only)                 │
         │  - Tag: latest, sha                 │
         │  - Push to Docker Hub               │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  JOB 6: Deploy 🎯                  │
         │  (optionnel - notification)         │
         └────────────────────────────────────┘
```

---

## 📁 Fichier Workflow

**Emplacement :** `.github/workflows/ci-cd.yml`

### Déclencheurs

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:  # Déclenchement manuel
```

### Jobs Détaillés

#### 1️⃣ Lint & Code Quality

```yaml
lint:
  name: 🔍 Lint & Code Quality
  runs-on: ubuntu-latest
  
  steps:
    - Black (formatage Python)
    - Flake8 (erreurs syntaxe)
    - Pylint (analyse statique)
```

**Durée estimée :** 1-2 minutes

#### 2️⃣ Unit Tests

```yaml
test:
  name: 🧪 Unit Tests
  runs-on: ubuntu-latest
  needs: lint  # Attend que lint soit OK
  
  steps:
    - pytest -m unit
    - Coverage report
    - Upload Codecov
```

**Durée estimée :** 2-3 minutes

#### 3️⃣ Integration Tests

```yaml
integration-test:
  name: 🔗 Integration Tests
  runs-on: ubuntu-latest
  needs: test
  
  services:  # Services Docker parallèles
    elasticsearch:
      image: elasticsearch:8.11.3
    mongodb:
      image: mongo:7.0
    redis:
      image: redis:7.2-alpine
```

**Durée estimée :** 3-5 minutes

#### 4️⃣ Build Docker

```yaml
build:
  name: 🐳 Build Docker Image
  runs-on: ubuntu-latest
  needs: [test, integration-test]
  
  steps:
    - Docker Buildx setup
    - Build image (sans push)
    - Cache optimization
```

**Durée estimée :** 5-7 minutes

#### 5️⃣ Push Docker (main uniquement)

```yaml
push:
  name: 🚀 Push Docker Image
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main'
  
  steps:
    - Login Docker Hub
    - Build + Push
    - Tag: latest, sha
```

**Durée estimée :** 3-5 minutes

---

## 🔐 Configuration des Secrets

Pour que le pipeline fonctionne, vous devez configurer des **secrets GitHub**.

### 1. Créer un compte Docker Hub (si pas déjà fait)

1. Aller sur https://hub.docker.com/
2. S'inscrire / Se connecter
3. Créer un dépôt public : `votre-username/projetelk`

### 2. Créer un Access Token Docker Hub

1. Docker Hub → Account Settings → Security
2. Cliquer sur **New Access Token**
3. Name: `github-actions`
4. Permissions: **Read, Write, Delete**
5. Copier le token (vous ne le reverrez pas)

### 3. Ajouter les Secrets sur GitHub

1. Aller sur votre repo GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquer sur **New repository secret**

Ajouter ces 2 secrets :

| Name | Value | Description |
|------|-------|-------------|
| `DOCKER_USERNAME` | Votre username Docker Hub | Ex: `selim123` |
| `DOCKER_PASSWORD` | Le token créé à l'étape 2 | Ex: `dckr_pat_xxxxx...` |

**⚠️ NE JAMAIS mettre ces valeurs dans le code !**

---

## 🧪 Test en Local AVANT GitHub

Utilisez le script de validation locale :

```bash
# Exécuter toutes les étapes du pipeline localement
./validate_ci.sh
```

Ce script va :
1. ✅ Vérifier le formatage (Black)
2. ✅ Vérifier la syntaxe (Flake8)
3. ✅ Analyser le code (Pylint)
4. ✅ Lancer les tests unitaires
5. ✅ Lancer les tests d'intégration
6. ✅ Builder l'image Docker

**Si tout passe ✅**, vous pouvez push sur GitHub !

---

## 🚀 Déploiement sur GitHub

### Méthode 1 : Push Simple

```bash
# S'assurer d'être sur la branche main
git checkout main

# Ajouter tous les fichiers
git add .

# Commit avec message clair
git commit -m "feat: CI/CD pipeline with automated tests"

# Push vers GitHub
git push origin main
```

### Méthode 2 : Via Pull Request

```bash
# Créer une branche feature
git checkout -b feature/ci-cd

# Push la branche
git push origin feature/ci-cd

# Sur GitHub : créer une Pull Request
# Le pipeline s'exécutera sur la PR
# Fusionner après validation
```

---

## 📊 Voir les Résultats

### Sur GitHub

1. Aller sur votre repo
2. Onglet **Actions**
3. Cliquer sur le dernier workflow run

Vous verrez :
```
✅ lint (1m 23s)
✅ test (2m 45s)
✅ integration-test (4m 12s)
✅ build (6m 34s)
✅ push (3m 56s)
✅ deploy (0m 12s)
```

### Badge de Statut

Ajouter dans votre `README.md` :

```markdown
![CI/CD Pipeline](https://github.com/VOTRE-USERNAME/ProjetELK/actions/workflows/ci-cd.yml/badge.svg)
```

---

## 🐛 Dépannage

### Erreur : "Docker login failed"

❌ **Problème :** Secrets non configurés

✅ **Solution :** Vérifier que `DOCKER_USERNAME` et `DOCKER_PASSWORD` sont bien dans GitHub Secrets

### Erreur : "Integration tests timeout"

❌ **Problème :** Services Docker trop lents à démarrer

✅ **Solution :** Augmenter `--health-interval` et `--health-timeout` dans `.github/workflows/ci-cd.yml`

### Erreur : "Coverage too low"

❌ **Problème :** Coverage < 70%

✅ **Solution :** Ajouter plus de tests (voir Étape 5)

---

## ✅ Checklist de Validation

Avant de considérer l'Étape 4 terminée :

- [ ] Fichier `.github/workflows/ci-cd.yml` créé et valide
- [ ] Script `validate_ci.sh` exécuté localement avec succès
- [ ] Secrets GitHub configurés (`DOCKER_USERNAME`, `DOCKER_PASSWORD`)
- [ ] Compte Docker Hub créé avec dépôt `projetelk/webapp`
- [ ] Premier push sur GitHub effectué
- [ ] Pipeline passé avec succès (tous jobs ✅)
- [ ] Badge CI/CD ajouté au README
- [ ] Image Docker disponible sur Docker Hub

---

## 🎯 Prochaine Étape

**Étape 5 : Augmenter le Coverage à 70%+**

Actuellement : **20%** → Objectif : **70%+**

Pour obtenir le maximum de points (Module K : +4 pts), il faut :
- Coverage > 70%
- Tests E2E (end-to-end)
- Documentation complète

---

## 📚 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Integration](https://about.codecov.io/)

---

**Date :** 2 janvier 2026  
**Étape 4/7** ✅
