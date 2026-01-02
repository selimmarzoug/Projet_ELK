# 🔐 Configuration des Secrets GitHub - Guide Complet

## 📋 Vue d'ensemble

Pour que le pipeline CI/CD fonctionne sur GitHub Actions, vous devez configurer 2 secrets :

| Secret | Description | Exemple |
|--------|-------------|---------|
| `DOCKER_USERNAME` | Votre nom d'utilisateur Docker Hub | `selim123` |
| `DOCKER_PASSWORD` | Token d'accès Docker Hub | `dckr_pat_xxxxx...` |

---

## 🐳 Étape 1 : Créer un compte Docker Hub

### Si vous n'avez PAS de compte Docker Hub :

1. Aller sur https://hub.docker.com/
2. Cliquer sur **Sign Up**
3. Remplir le formulaire :
   - Username : `votreusername` (ex: `selim-projet-elk`)
   - Email : votre email
   - Password : mot de passe sécurisé
4. Vérifier votre email
5. Se connecter

### Si vous AVEZ déjà un compte :

1. Se connecter sur https://hub.docker.com/
2. Passer à l'étape 2

---

## 🔑 Étape 2 : Créer un Access Token

⚠️ **NE PAS utiliser votre mot de passe Docker Hub directement !**  
Utilisez un **Access Token** pour plus de sécurité.

### Créer le token :

1. Une fois connecté sur Docker Hub
2. Cliquer sur votre avatar (en haut à droite)
3. **Account Settings**
4. Onglet **Security**
5. Cliquer sur **New Access Token**

### Configurer le token :

```
Access Token Description: github-actions-projetelk
Access permissions: Read, Write, Delete
```

6. Cliquer sur **Generate**
7. **COPIER LE TOKEN IMMÉDIATEMENT** (exemple: `dckr_pat_AbCd1234...`)

⚠️ **IMPORTANT :** Vous ne pourrez plus voir ce token après fermeture !

---

## 📦 Étape 3 : Créer un Repository Docker Hub

1. Sur Docker Hub, cliquer sur **Repositories**
2. Cliquer sur **Create Repository**
3. Configurer :
   ```
   Repository Name: projetelk-webapp
   Visibility: Public (pour éviter les frais)
   Description: Application Flask pour monitoring et analyse de logs
   ```
4. Cliquer sur **Create**

Votre image sera disponible sur : `votreusername/projetelk-webapp`

---

## 🔐 Étape 4 : Ajouter les Secrets sur GitHub

### Pré-requis

Votre projet doit être sur GitHub. Si ce n'est pas encore fait :

```bash
# Initialiser git (si pas déjà fait)
git init

# Créer un repo sur GitHub (via interface web)
# Puis :
git remote add origin https://github.com/VOTRE-USERNAME/ProjetELK.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Ajouter les secrets

1. Aller sur votre repo GitHub : `https://github.com/VOTRE-USERNAME/ProjetELK`
2. Cliquer sur **⚙️ Settings** (onglet en haut)
3. Dans le menu latéral gauche : **Secrets and variables** → **Actions**
4. Cliquer sur **New repository secret**

#### Secret 1 : DOCKER_USERNAME

```
Name: DOCKER_USERNAME
Secret: votreusername
```

Exemple : `selim-projet-elk`

Cliquer sur **Add secret**

#### Secret 2 : DOCKER_PASSWORD

```
Name: DOCKER_PASSWORD
Secret: dckr_pat_AbCd1234...
```

(Le token copié à l'étape 2)

Cliquer sur **Add secret**

### ✅ Vérification

Vous devriez voir :

```
Repository secrets

DOCKER_USERNAME        Updated 1 minute ago
DOCKER_PASSWORD        Updated 1 minute ago
```

---

## 🔄 Étape 5 : Modifier le workflow (si nécessaire)

Si votre username Docker Hub est **différent** de `projetelk`, modifier le fichier :

`.github/workflows/ci-cd.yml`

```yaml
env:
  PYTHON_VERSION: '3.8'
  DOCKER_IMAGE: VOTRE-USERNAME/projetelk-webapp  # ← Modifier ici
```

Exemple :
```yaml
  DOCKER_IMAGE: selim123/projetelk-webapp
```

---

## 🧪 Étape 6 : Tester en Local

Avant de push sur GitHub, tester localement :

```bash
# Test de connexion Docker Hub
docker login -u VOTRE-USERNAME

# Entrer votre token quand demandé
# Si ça marche : "Login Succeeded"

# Test de build
docker build -t VOTRE-USERNAME/projetelk-webapp:test .

# Test de push
docker push VOTRE-USERNAME/projetelk-webapp:test
```

Si tout fonctionne → vous êtes prêt pour GitHub !

---

## 🚀 Étape 7 : Premier Push sur GitHub

```bash
# S'assurer que tout est commité
git add .
git commit -m "feat: CI/CD pipeline with Docker Hub integration"

# Push sur la branche main
git push origin main
```

### Observer le workflow

1. Aller sur GitHub → onglet **Actions**
2. Vous verrez le workflow s'exécuter en temps réel
3. Après 10-15 minutes, tous les jobs devraient être ✅

---

## 🎯 Vérifier le Résultat

### Sur GitHub Actions

```
✅ lint (1m 23s)
✅ test (2m 45s)
✅ integration-test (4m 12s)
✅ build (6m 34s)
✅ push (3m 56s)
✅ deploy (0m 12s)
```

### Sur Docker Hub

1. Aller sur https://hub.docker.com/
2. **Repositories** → `projetelk-webapp`
3. Vous devriez voir :
   ```
   latest     2 minutes ago    234 MB
   sha-abc123 2 minutes ago    234 MB
   ```

---

## 🐛 Dépannage Fréquent

### Erreur : "Access denied"

❌ **Problème :** Token invalide ou expiré

✅ **Solution :**
1. Créer un nouveau token sur Docker Hub
2. Mettre à jour le secret `DOCKER_PASSWORD` sur GitHub

### Erreur : "Invalid reference format"

❌ **Problème :** Nom d'image incorrect

✅ **Solution :**
- Format correct : `username/repo:tag`
- Vérifier `DOCKER_IMAGE` dans `ci-cd.yml`

### Erreur : "Secret not found"

❌ **Problème :** Secrets mal configurés

✅ **Solution :**
1. Settings → Secrets → Actions
2. Vérifier que les noms sont EXACTEMENT :
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`

---

## ✅ Checklist Complète

- [ ] Compte Docker Hub créé
- [ ] Access Token généré et copié
- [ ] Repository `projetelk-webapp` créé sur Docker Hub
- [ ] Secret `DOCKER_USERNAME` ajouté sur GitHub
- [ ] Secret `DOCKER_PASSWORD` ajouté sur GitHub
- [ ] Variable `DOCKER_IMAGE` ajustée dans `ci-cd.yml`
- [ ] Test de connexion Docker Hub local réussi
- [ ] Premier push sur GitHub effectué
- [ ] Workflow GitHub Actions passé avec succès
- [ ] Image visible sur Docker Hub

---

## 📚 Liens Utiles

- **Docker Hub :** https://hub.docker.com/
- **GitHub Secrets :** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Docker Login Action :** https://github.com/docker/login-action

---

**Date :** 2 janvier 2026  
**Document :** Configuration Secrets GitHub
