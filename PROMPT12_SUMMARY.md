# 📊 Prompt 12 - Configuration MongoDB et Redis

## 🎯 Objectif
Créer un module Python centralisé (`database.py`) pour gérer les connexions MongoDB et Redis avec:
- Configuration via variables d'environnement
- Tests de connexion au démarrage
- Gestion d'erreurs robuste
- Health check monitoring
- Fonctions utilitaires d'accès

## 📁 Fichiers Modifiés/Créés

### 1. `/webapp/database.py`
Module principal de gestion des connexions aux bases de données.

#### Classes Principales

**`DatabaseConfig`**
- Configuration centralisée des variables d'environnement
- MongoDB: `MONGO_URI`, `MONGO_DB_NAME`, `MONGO_TIMEOUT`
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`

**`MongoDBConnection`**
- Gestion de la connexion MongoDB via PyMongo
- Méthodes: `connect()`, `get_collection()`, `health_check()`, `close()`
- Test automatique de connexion avec `ping()`

**`RedisConnection`**
- Gestion de la connexion Redis via redis-py
- Méthodes: `connect()`, `get_client()`, `health_check()`, `close()`
- Décodage automatique UTF-8

**`DatabaseManager`**
- Gestionnaire global des connexions
- Initialisation centralisée: `connect_all()`
- Health check global: `health_check_all()`
- Fermeture propre: `close_all()`

#### Fonctions Utilitaires

```python
init_databases() -> bool
# Initialise toutes les connexions (à appeler au démarrage)

get_mongodb_db() -> Database
# Retourne l'instance de la base MongoDB

get_mongodb_collection(name: str) -> Collection
# Retourne une collection MongoDB spécifique

get_redis_client() -> redis.Redis
# Retourne le client Redis

health_check() -> Dict[str, Any]
# Effectue un health check complet
```

### 2. `/webapp/app.py`
Intégration du module database dans l'application Flask.

#### Modifications

```python
# Import du module
from database import (
    init_databases, 
    get_mongodb_db, 
    get_redis_client, 
    health_check as db_health_check
)

# Initialisation au démarrage
db_status = init_databases()
db = get_mongodb_db()
redis_client = get_redis_client()
files_collection = db['files'] if db is not None else None
```

#### Nouvelle Route `/health`

Endpoint de monitoring retournant le statut de tous les services:

```json
{
  "status": "healthy",
  "timestamp": "2025-11-25T16:36:45.038259",
  "services": {
    "mongodb": {
      "status": "connected",
      "healthy": true,
      "database": "logsdb",
      "collections": ["files", "search_history"],
      "documents": 22,
      "size_mb": 0.01
    },
    "redis": {
      "status": "connected",
      "healthy": true,
      "version": "7.2.12",
      "connected_clients": 1,
      "used_memory_mb": 0.92,
      "total_keys": 0
    },
    "elasticsearch": {
      "status": "healthy",
      "details": {
        "cluster_name": "docker-cluster",
        "status": "yellow",
        "number_of_nodes": 1
      }
    }
  }
}
```

### 3. `docker-compose.yml`
Configuration des variables d'environnement pour le service webapp.

```yaml
environment:
  - MONGO_URI=mongodb://${MONGO_ROOT_USERNAME}:${MONGO_ROOT_PASSWORD}@mongodb:27017
  - MONGO_DB_NAME=${MONGO_DATABASE:-logsdb}
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_PASSWORD=${REDIS_PASSWORD:-changeme}
```

### 4. `.env`
Variables d'environnement ajoutées:

```bash
# MongoDB
MONGO_URI=mongodb://admin:changeme@mongodb:27017
MONGO_DB_NAME=logsdb

# Redis (variables déjà existantes, configuration clarifiée)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=changeme
```

## 🧪 Tests

### Test Standalone du Module

```bash
docker exec webapp python database.py
```

**Sortie attendue:**
```
🚀 Initialisation des connexions aux bases de données
✅ MongoDB connecté - Base: logsdb
✅ Redis connecté - DB: 0
✅ Toutes les connexions établies avec succès

📊 HEALTH CHECK
📦 MongoDB: connected, 2 collections, 22 documents
💾 Redis: connected, version 7.2.12, 0 keys

🧪 TEST DES OPÉRATIONS
✅ MongoDB insert test: OK
✅ MongoDB delete test: OK
✅ Redis set/get test: OK
✅ Redis delete test: OK
```

### Test Health Check API

```bash
curl http://localhost:8000/health | python -m json.tool
```

### Test dans l'Application

```python
# Récupérer une collection MongoDB
from database import get_mongodb_collection
files_col = get_mongodb_collection('files')
count = files_col.count_documents({})

# Utiliser Redis
from database import get_redis_client
redis = get_redis_client()
redis.set('key', 'value', ex=60)
value = redis.get('key')
```

## ✅ Résultats

### Statut des Connexions

```
✅ MongoDB: Connecté (logsdb)
   - Collections: files, search_history
   - Documents: 22
   - Taille: 0.01 MB

✅ Redis: Connecté (DB 0)
   - Version: 7.2.12
   - Mémoire: 0.92 MB
   - Clients: 1

✅ Elasticsearch: Connecté (docker-cluster)
   - Status: yellow
   - Nodes: 1
```

### Logs de Démarrage

```
2025-11-25 16:36:33 - database - INFO - 🔌 Connexion à MongoDB: mongodb:27017
2025-11-25 16:36:33 - database - INFO - ✅ MongoDB connecté - Base: logsdb
2025-11-25 16:36:33 - database - INFO - 🔌 Connexion à Redis: redis:6379
2025-11-25 16:36:33 - database - INFO - ✅ Redis connecté - DB: 0
2025-11-25 16:36:33 - database - INFO - ✅ Toutes les connexions établies avec succès
```

## 🔧 Configuration

### Variables d'Environnement Supportées

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | `mongodb://admin:changeme@mongodb:27017` | URI de connexion MongoDB |
| `MONGO_DB_NAME` | `logsdb` | Nom de la base de données |
| `MONGO_TIMEOUT` | `5000` | Timeout en ms |
| `REDIS_HOST` | `redis` | Hostname Redis |
| `REDIS_PORT` | `6379` | Port Redis |
| `REDIS_DB` | `0` | Numéro de base Redis |
| `REDIS_PASSWORD` | `None` | Mot de passe Redis |
| `REDIS_DECODE_RESPONSES` | `true` | Décodage UTF-8 auto |
| `REDIS_SOCKET_TIMEOUT` | `5` | Timeout socket |
| `DB_MAX_RETRIES` | `3` | Tentatives de reconnexion |
| `DB_RETRY_DELAY` | `2` | Délai entre tentatives (s) |

## 🐛 Problèmes Résolus

### 1. Port Redis Dupliqué
**Problème:** `REDIS_HOST=redis:6379` contenait le port  
**Solution:** Séparé en `REDIS_HOST=redis` et `REDIS_PORT=6379`

### 2. Comparaison Database MongoDB
**Problème:** `if db:` lève NotImplementedError  
**Solution:** Utiliser `if db is not None:`

### 3. Variables d'Environnement Manquantes
**Problème:** `MONGO_URI` non définie dans .env  
**Solution:** Ajouté dans `.env` et `docker-compose.yml`

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│             Flask Application (app.py)          │
└─────────────────┬───────────────────────────────┘
                  │
                  │ import database
                  ▼
┌─────────────────────────────────────────────────┐
│         database.py (DatabaseManager)           │
├─────────────────┬───────────────┬───────────────┤
│ MongoDBConnection│ RedisConnection│ Config       │
└─────────┬────────┴──────┬────────┴───────────────┘
          │               │
          ▼               ▼
    ┌─────────┐     ┌─────────┐
    │ MongoDB │     │  Redis  │
    │  :27017 │     │  :6379  │
    └─────────┘     └─────────┘
```

## 🚀 Utilisation

### Démarrage
Les connexions sont initialisées automatiquement au démarrage de Flask.

### Accès aux Bases
```python
# MongoDB
db = get_mongodb_db()
collection = db['ma_collection']

# Ou directement
collection = get_mongodb_collection('ma_collection')

# Redis
redis = get_redis_client()
redis.set('key', 'value')
```

### Health Check
```bash
# HTTP
curl http://localhost:8000/health

# Python
health = health_check()
print(health['mongodb']['status'])
```

## 📝 Logs

Le module utilise le logger Python standard avec format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Niveaux:
- `INFO`: Connexions réussies, opérations normales
- `WARNING`: Tentatives de reconnexion
- `ERROR`: Échecs de connexion

## ✨ Fonctionnalités

✅ Connexions centralisées MongoDB et Redis  
✅ Configuration via variables d'environnement  
✅ Tests de connexion automatiques au démarrage  
✅ Gestion d'erreurs robuste avec logging  
✅ Health check monitoring complet  
✅ Fonctions utilitaires pour accès rapide  
✅ Mode standalone pour tests  
✅ Endpoint API `/health` pour supervision  
✅ Support des timeouts et reconnexions  
✅ Documentation et logs détaillés  

## 🎓 Bonnes Pratiques Implémentées

1. **Singleton Pattern**: Instance globale `db_manager`
2. **Configuration externalisée**: Variables d'environnement
3. **Defensive Programming**: Vérifications `is not None`
4. **Logging structuré**: Niveaux INFO/WARNING/ERROR
5. **Health Checks**: Monitoring continu
6. **Graceful Shutdown**: Fermeture propre des connexions
7. **Documentation**: Docstrings complètes
8. **Tests**: Mode standalone intégré

---

**Status:** ✅ **Prompt 12 Complété avec Succès**  
**Date:** 25 novembre 2025  
**Auteur:** Selim Marzoug
