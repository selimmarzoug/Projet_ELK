# 🔗 Guide Détaillé - Étape 3 : Tests d'Intégration

## 📚 Qu'est-ce qu'un Test d'Intégration ?

### Différence Tests Unitaires vs Tests d'Intégration

| Aspect | Test Unitaire | Test d'Intégration |
|--------|---------------|-------------------|
| **Isolation** | Fonction isolée (mock) | Plusieurs composants |
| **Services** | Simulés (fake) | Réels (Docker) |
| **Vitesse** | Rapide (< 1s) | Plus lent (1-5s) |
| **Dépendances** | Aucune | Elasticsearch, MongoDB, Redis |
| **Objectif** | Logique correcte | Communication entre services |

### Exemple Concret

```python
# ❌ TEST UNITAIRE (mock - rapide mais pas réaliste)
@pytest.mark.unit
@patch('webapp.app.es')  # ← FAUX Elasticsearch
def test_search_mock(mock_es):
    mock_es.search.return_value = {'hits': {'total': {'value': 0}}}
    # Pas de vraie connexion, juste simulation

# ✅ TEST D'INTÉGRATION (réel - lent mais fiable)
@pytest.mark.integration
def test_search_real():
    es = Elasticsearch(['http://localhost:9200'])  # ← VRAI Elasticsearch
    result = es.search(index='logs-*', body={'query': {'match_all': {}}})
    # Vraie connexion, vrais résultats
```

---

## 🎯 Étape par Étape - Comment Faire

### **Étape 3.1 : Démarrer les Services Docker**

#### Commandes à exécuter :

```bash
# 1. Aller dans le dossier du projet
cd /home/selim/Bureau/ProjetELK

# 2. Démarrer TOUS les services
docker compose up -d

# 3. Vérifier que tout est UP et HEALTHY
docker compose ps

# Vous devez voir :
# NAME            STATUS
# elasticsearch   Up (healthy)
# mongodb         Up (healthy)
# redis           Up (healthy)
# kibana          Up (healthy)
# logstash        Up
# webapp          Up
```

#### Si un service n'est pas healthy :

```bash
# Voir les logs du service
docker compose logs elasticsearch
docker compose logs mongodb
docker compose logs redis

# Redémarrer un service
docker compose restart elasticsearch
```

---

### **Étape 3.2 : Comprendre le Fichier de Tests**

J'ai créé `tests/test_integration.py` avec **4 classes** :

#### **Classe 1 : TestRealElasticsearch**
Tests avec le VRAI Elasticsearch

```python
def test_elasticsearch_is_running():
    # Vérifie que ES est accessible
    es = Elasticsearch(['http://localhost:9200'])
    health = es.cluster.health()
    assert health is not None

def test_elasticsearch_can_index_document():
    # Indexe un vrai document
    es.index(index='test', document={'message': 'test'})

def test_elasticsearch_can_search():
    # Fait une vraie recherche
    result = es.search(index='test', body={'query': {'match_all': {}}})
```

#### **Classe 2 : TestRealMongoDB**
Tests avec le VRAI MongoDB

```python
def test_mongodb_is_running():
    # Vérifie connexion
    client = MongoClient('mongodb://admin:changeme@localhost:27017/')
    client.admin.command('ping')

def test_mongodb_can_insert_document():
    # Insère un vrai document
    collection.insert_one({'filename': 'test.csv'})

def test_mongodb_can_query_documents():
    # Fait une vraie requête
    count = collection.count_documents({'status': 'success'})
```

#### **Classe 3 : TestRealRedis**
Tests avec le VRAI Redis

```python
def test_redis_is_running():
    # Vérifie connexion
    r = redis.Redis(host='localhost', port=6379, password='changeme')
    r.ping()

def test_redis_can_set_and_get():
    # SET et GET réels
    r.set('key', 'value')
    value = r.get('key')

def test_redis_expiration():
    # Test expiration réelle
    r.setex('temp', 2, 'value')  # Expire après 2 secondes
    time.sleep(3)
    assert r.exists('temp') == 0
```

#### **Classe 4 : TestEndToEndFlows**
Tests de flux complets (TODO - à compléter plus tard)

---

### **Étape 3.3 : Exécuter les Tests d'Intégration**

#### Commande simple :

```bash
cd /home/selim/Bureau/ProjetELK

# Exécuter UNIQUEMENT les tests d'intégration
python3 -m pytest tests/test_integration.py -v
```

#### Commande détaillée :

```bash
# Avec marker (recommandé)
python3 -m pytest tests/ -m integration -v

# Avec output des prints
python3 -m pytest tests/test_integration.py -v -s

# Un seul test
python3 -m pytest tests/test_integration.py::TestRealElasticsearch::test_elasticsearch_is_running -v
```

---

### **Étape 3.4 : Interpréter les Résultats**

#### ✅ Si tout passe (résultat attendu) :

```
tests/test_integration.py::TestRealElasticsearch::test_elasticsearch_is_running PASSED
tests/test_integration.py::TestRealElasticsearch::test_elasticsearch_can_index_document PASSED
tests/test_integration.py::TestRealMongoDB::test_mongodb_is_running PASSED
tests/test_integration.py::TestRealRedis::test_redis_is_running PASSED

======================== 12 passed in 3.45s ========================
```

**Signification :** Les services Docker fonctionnent correctement !

#### ⚠️ Si des tests sont skippés :

```
tests/test_integration.py::TestRealElasticsearch::test_elasticsearch_is_running SKIPPED
Reason: Elasticsearch non disponible: Connection refused
```

**Signification :** Le service n'est pas démarré ou pas accessible.

**Solution :**
```bash
# Vérifier les services
docker compose ps

# Redémarrer si nécessaire
docker compose restart elasticsearch

# Attendre quelques secondes
sleep 10

# Relancer les tests
python3 -m pytest tests/test_integration.py -v
```

#### ❌ Si des tests échouent :

```
tests/test_integration.py::TestRealMongoDB::test_mongodb_can_insert_document FAILED
AssertionError: Insert failed
```

**Signification :** Il y a un problème avec le service.

**Solution :**
```bash
# Voir les logs
docker compose logs mongodb

# Redémarrer le service
docker compose restart mongodb
```

---

## 🧪 Exercice Pratique

### **Exercice 1 : Tester Elasticsearch**

```bash
# 1. Démarrer les services
docker compose up -d

# 2. Attendre 30 secondes que ES soit prêt
sleep 30

# 3. Lancer le test
python3 -m pytest tests/test_integration.py::TestRealElasticsearch::test_elasticsearch_is_running -v -s

# Résultat attendu :
# ✅ Elasticsearch status: green
# PASSED
```

### **Exercice 2 : Tester MongoDB**

```bash
# Lancer les tests MongoDB
python3 -m pytest tests/test_integration.py::TestRealMongoDB -v -s

# Résultat attendu :
# ✅ MongoDB est accessible
# ✅ Document inséré : 67...
# ✅ Trouvé 3 documents
# 3 PASSED
```

### **Exercice 3 : Tester Redis**

```bash
# Lancer les tests Redis
python3 -m pytest tests/test_integration.py::TestRealRedis -v -s

# Résultat attendu :
# ✅ Redis est accessible
# ✅ SET et GET fonctionnent
# ✅ Expiration fonctionne
# 3 PASSED
```

---

## 🎯 Checklist Étape 3

Cochez au fur et à mesure :

- [ ] **3.1** Services Docker démarrés (`docker compose up -d`)
- [ ] **3.2** Services healthy (`docker compose ps`)
- [ ] **3.3** Fichier `test_integration.py` créé
- [ ] **3.4** Tests Elasticsearch passent
- [ ] **3.5** Tests MongoDB passent
- [ ] **3.6** Tests Redis passent
- [ ] **3.7** Tous les tests d'intégration passent

---

## 🚀 Commandes Rapides Résumé

```bash
# 1. Démarrer services
docker compose up -d

# 2. Vérifier services
docker compose ps

# 3. Lancer tous les tests d'intégration
python3 -m pytest tests/ -m integration -v

# 4. Lancer un service spécifique
python3 -m pytest tests/test_integration.py::TestRealElasticsearch -v

# 5. Voir les logs si problème
docker compose logs elasticsearch
docker compose logs mongodb
docker compose logs redis
```

---

## ❓ Questions Fréquentes

### Q1 : Les tests sont skippés, pourquoi ?

**R :** Les services Docker ne sont pas démarrés.

```bash
# Solution
docker compose up -d
sleep 30  # Attendre que les services soient prêts
python3 -m pytest tests/test_integration.py -v
```

### Q2 : "Connection refused" error ?

**R :** Le service n'est pas accessible.

```bash
# Vérifier le port
docker compose ps
# Si le conteneur est DOWN, redémarrer
docker compose restart elasticsearch
```

### Q3 : Tests très lents ?

**R :** Normal ! Les tests d'intégration sont plus lents que les tests unitaires.
- Tests unitaires : < 1s
- Tests d'intégration : 1-5s par test

### Q4 : Différence avec tests unitaires ?

**R :**
- **Unitaires** : Rapides, mocks, isolation → Pour développement
- **Intégration** : Lents, services réels → Pour validation finale

---

## 📊 Résultat Attendu

Après l'étape 3, vous devriez avoir :

```
tests/test_integration.py ... 12 tests

TestRealElasticsearch
  ✅ test_elasticsearch_is_running
  ✅ test_elasticsearch_can_index_document  
  ✅ test_elasticsearch_can_search

TestRealMongoDB
  ✅ test_mongodb_is_running
  ✅ test_mongodb_can_insert_document
  ✅ test_mongodb_can_query_documents

TestRealRedis
  ✅ test_redis_is_running
  ✅ test_redis_can_set_and_get
  ✅ test_redis_expiration

TestEndToEndFlows
  ⏩ test_full_upload_flow (skipped - TODO)
  ⏩ test_full_search_flow (skipped - TODO)

TestPerformance
  ✅ test_elasticsearch_bulk_indexing

======================== 10 passed, 2 skipped ========================
```

---

**Est-ce que c'est plus clair maintenant ? 😊**

Voulez-vous qu'on exécute ensemble les tests d'intégration ?
