# 🧪 Tests Automatisés - ProjetELK

## 📋 Vue d'ensemble

Suite de tests complète pour le projet ELK incluant :
- ✅ Tests unitaires
- ✅ Tests d'intégration  
- ✅ Coverage de code
- ✅ CI/CD avec GitHub Actions

---

## 🏗️ Structure des Tests

```
tests/
├── __init__.py                 # Package tests
├── conftest.py                 # Configuration pytest et fixtures
├── test_health.py              # Tests endpoint /health
├── test_upload.py              # Tests upload de fichiers
├── test_search.py              # Tests recherche de logs
└── test_redis_cache.py         # Tests cache Redis
```

---

## 📦 Installation

### Dépendances de test

```bash
# Option 1 : Via requirements-dev.txt
pip install -r requirements-dev.txt

# Option 2 : Installation manuelle
pip install pytest pytest-cov pytest-flask pytest-mock
```

---

## 🚀 Exécution des Tests

### Tous les tests

```bash
pytest tests/
```

### Tests spécifiques

```bash
# Tests unitaires uniquement
pytest tests/ -m unit

# Tests d'intégration uniquement
pytest tests/ -m integration

# Tests d'une classe spécifique
pytest tests/test_health.py::TestHealthEndpoint

# Un seul test
pytest tests/test_health.py::TestHealthEndpoint::test_health_endpoint_exists
```

### Avec coverage

```bash
# Coverage HTML (génère htmlcov/)
pytest tests/ --cov=webapp --cov-report=html

# Coverage dans le terminal
pytest tests/ --cov=webapp --cov-report=term-missing

# Les deux
pytest tests/ --cov=webapp --cov-report=html --cov-report=term
```

### Mode verbose

```bash
# Affichage détaillé
pytest tests/ -v

# Affichage très détaillé
pytest tests/ -vv

# Avec output des prints
pytest tests/ -s
```

---

## 🏷️ Markers (Tags)

Les tests sont organisés par markers :

```python
@pytest.mark.unit          # Tests unitaires rapides
@pytest.mark.integration   # Tests d'intégration
@pytest.mark.api           # Tests d'API REST
@pytest.mark.db            # Tests avec bases de données
@pytest.mark.slow          # Tests lents
```

### Utilisation

```bash
# Exécuter tests unitaires
pytest -m unit

# Exécuter tests API
pytest -m api

# Exécuter tests SANS les lents
pytest -m "not slow"

# Combiner markers
pytest -m "unit and api"
```

---

## 📊 Coverage Attendu

| Module | Coverage Minimum | Status |
|--------|------------------|---------|
| `webapp/app.py` | 70% | 🔴 En cours |
| `webapp/database.py` | 70% | 🟡 24% |
| `webapp/routes/auth.py` | 60% | 🔴 0% |
| `webapp/models/user.py` | 60% | 🔴 0% |
| **TOTAL** | **70%** | 🔴 7% |

---

## 🔧 Configuration pytest

Le fichier `pytest.ini` contient la configuration :

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --tb=short
    --cov=webapp
    --cov-report=html
    --cov-report=term-missing
```

---

## 🧪 Fixtures Disponibles

Définies dans `conftest.py` :

### Fixtures de base

```python
@pytest.fixture
def app():
    """Instance Flask app configurée pour les tests"""
    
@pytest.fixture
def client(app):
    """Client de test Flask"""
    
@pytest.fixture
def auth_client(client):
    """Client authentifié"""
```

### Fixtures de fichiers

```python
@pytest.fixture
def sample_csv_file(tmp_path):
    """Fichier CSV de test"""
    
@pytest.fixture
def sample_json_file(tmp_path):
    """Fichier JSON de test"""
```

### Fixtures de mock

```python
@pytest.fixture
def mock_elasticsearch(mocker):
    """Mock d'Elasticsearch"""
    
@pytest.fixture
def mock_redis(mocker):
    """Mock de Redis"""
    
@pytest.fixture
def mock_mongodb(mocker):
    """Mock de MongoDB"""
```

---

## 📝 Exemples de Tests

### Test unitaire simple

```python
@pytest.mark.unit
def test_allowed_file_csv():
    """Test que les fichiers CSV sont autorisés"""
    from webapp.app import allowed_file
    assert allowed_file('test.csv') is True
```

### Test avec mock

```python
@pytest.mark.unit
@patch('webapp.app.es')
def test_search_with_mock(mock_es, client):
    """Test recherche avec Elasticsearch mocké"""
    mock_es.search.return_value = {'hits': {'total': {'value': 0}}}
    response = client.get('/api/search?query=test')
    assert response.status_code == 200
```

### Test d'intégration

```python
@pytest.mark.integration
@pytest.mark.db
def test_upload_saves_to_mongodb(auth_client, sample_csv_file):
    """Test upload avec MongoDB réel"""
    with open(sample_csv_file, 'rb') as f:
        response = auth_client.post('/upload', data={'file': f})
    assert response.status_code == 200
```

---

## 🤖 CI/CD avec GitHub Actions

### Workflow automatique

Le fichier `.github/workflows/ci-cd.yml` exécute :

1. **Linting** (flake8, pylint, black)
2. **Tests unitaires** avec coverage
3. **Tests d'intégration** avec services Docker
4. **Build** de l'image Docker
5. **Push** sur Docker Hub (main seulement)
6. **Deploy** (optionnel)

### Déclenchement

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

### Secrets requis

Dans GitHub Settings > Secrets :

```
DOCKER_USERNAME=votre_username
DOCKER_PASSWORD=votre_token
```

### Badge de status

Ajoutez dans votre README.md :

```markdown
![CI/CD](https://github.com/votre-username/ProjetELK/workflows/CI%2FCD%20Pipeline/badge.svg)
```

---

## 📈 Amélioration du Coverage

### Étapes recommandées

1. **Identifier les zones non testées**
   ```bash
   pytest --cov=webapp --cov-report=html
   open htmlcov/index.html
   ```

2. **Ajouter des tests pour les fonctions critiques**
   - Endpoints API
   - Fonctions de validation
   - Logique métier

3. **Tester les cas limites**
   - Fichiers vides
   - Formats invalides
   - Erreurs réseau
   - Timeout

4. **Tester les erreurs**
   - Exceptions
   - Status codes 4xx/5xx
   - Déconnexions

---

## 🐛 Debugging des Tests

### Test qui échoue

```bash
# Afficher la stack trace complète
pytest tests/test_health.py -vv --tb=long

# S'arrêter au premier échec
pytest tests/ -x

# Entrer en mode debug
pytest tests/ --pdb
```

### Problèmes courants

1. **Import errors**
   ```bash
   # Vérifier PYTHONPATH
   export PYTHONPATH=$PWD:$PYTHONPATH
   pytest tests/
   ```

2. **Services non disponibles**
   ```bash
   # Démarrer les services
   docker-compose up -d elasticsearch mongodb redis
   pytest tests/ -m integration
   ```

3. **Fixtures manquantes**
   ```bash
   # Lister les fixtures disponibles
   pytest --fixtures
   ```

---

## ✅ Checklist Avant PR

- [ ] Tous les tests passent
- [ ] Coverage > 70%
- [ ] Pas de warning flake8
- [ ] Code formaté avec black
- [ ] Nouveaux tests ajoutés pour nouvelles fonctionnalités
- [ ] Documentation mise à jour

---

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Flask](https://pytest-flask.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## 🎯 Objectifs de Coverage

**Pour atteindre 20/20 (Module K) :**

- ✅ Tests unitaires : > 70% coverage
- ✅ Tests d'intégration : Tous les flux critiques
- ✅ CI/CD : Pipeline GitHub Actions complet
- ✅ Quality gates : Linting + Tests
- ✅ Documentation : Complète

**Status actuel : 7% → Objectif : 70%+**

---

Dernière mise à jour : 2 janvier 2026
