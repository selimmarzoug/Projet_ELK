# 🌐 URLs & Endpoints - ProjetELK

## 📱 Application Web (Port 8000)

### Pages Principales (Authentification Requise)
| URL | Description | Icône |
|-----|-------------|-------|
| http://localhost:8000/ | Dashboard principal avec statistiques | 🏠 |
| http://localhost:8000/upload | Upload de fichiers CSV/JSON | ☁️ |
| http://localhost:8000/search | Recherche avancée dans les logs | 🔍 |
| http://localhost:8000/health-dashboard | Monitoring système ⭐ NOUVEAU | 💚 |

### Authentification
| URL | Description | Méthode |
|-----|-------------|---------|
| http://localhost:8000/login | Page de connexion | GET/POST |
| http://localhost:8000/register | Page d'inscription | GET/POST |
| http://localhost:8000/logout | Déconnexion | GET |

### API Endpoints
| URL | Description | Auth | Format |
|-----|-------------|------|--------|
| http://localhost:8000/health | Health check des services | ❌ Non | JSON |
| http://localhost:8000/api/search | Recherche dans les logs | ✅ Oui | JSON |
| http://localhost:8000/api/search/history | Historique des recherches | ✅ Oui | JSON |

---

## 🔍 Elasticsearch (Port 9200)

### Endpoints Principaux
```bash
# Santé du cluster
http://localhost:9200/_cluster/health

# Liste des indices
http://localhost:9200/_cat/indices?v

# Statistiques du cluster
http://localhost:9200/_cluster/stats?pretty

# Info du nœud
http://localhost:9200/

# Recherche dans tous les index logstash
http://localhost:9200/logstash-*/_search

# Compter les documents
http://localhost:9200/logstash-*/_count
```

---

## 📊 Kibana (Port 5601)

### Pages Principales
| URL | Description |
|-----|-------------|
| http://localhost:5601 | Page d'accueil Kibana |
| http://localhost:5601/app/discover | Discover - Explorer les données |
| http://localhost:5601/app/dashboards | Dashboards - Visualisations |
| http://localhost:5601/app/canvas | Canvas - Présentations |
| http://localhost:5601/app/management/kibana/dataViews | Data Views (Index Patterns) |

### URLs Utiles
```bash
# Discover avec filtre de temps
http://localhost:5601/app/discover#/?_g=(time:(from:'2026-01-02T00:00:00.000Z',to:'2026-01-02T23:59:59.999Z'))

# Créer un nouveau dashboard
http://localhost:5601/app/dashboards#/create

# Stack Management
http://localhost:5601/app/management

# Dev Tools Console
http://localhost:5601/app/dev_tools#/console
```

---

## 🗄️ MongoDB (Port 27017)

### Connexion
```bash
# URI de connexion
mongodb://admin:changeme@localhost:27017

# Via mongosh
mongosh "mongodb://admin:changeme@localhost:27017" --authenticationDatabase admin

# Via application Python
from pymongo import MongoClient
client = MongoClient('mongodb://admin:changeme@mongodb:27017')
db = client['logsdb']
```

### Collections
- `users` - Comptes utilisateurs
- `files` - Métadonnées des fichiers uploadés
- `search_history` - Historique des recherches

---

## 🌿 Mongo Express (Port 8081)

### Interface Web MongoDB
```bash
# URL
http://localhost:8081

# Credentials
Username: meadmin
Password: mechangeme
```

---

## 🔴 Redis (Port 6379)

### Connexion
```bash
# Via redis-cli
redis-cli -h localhost -p 6379 -a changeme

# URI de connexion
redis://:changeme@localhost:6379

# Via application Python
import redis
r = redis.Redis(host='localhost', port=6379, password='changeme', db=0)
```

---

## 🔧 Logstash (Ports 5044, 9600)

### Endpoints
```bash
# API Node Stats
http://localhost:9600/_node/stats?pretty

# API Node Info
http://localhost:9600/_node?pretty

# Pipeline Stats
http://localhost:9600/_node/stats/pipelines?pretty

# Hot Threads
http://localhost:9600/_node/hot_threads
```

---

## 🧪 Tests Rapides

### Tester tous les services
```bash
# Webapp
curl http://localhost:8000/health | jq

# Elasticsearch
curl http://localhost:9200/_cluster/health | jq

# Kibana
curl http://localhost:5601/api/status | jq

# Logstash
curl http://localhost:9600/_node/stats | jq
```

### Upload un fichier
```bash
# Via curl (nécessite une session authentifiée)
curl -X POST -F "file=@test_today_2026.csv" \
  http://localhost:8000/upload
```

---

## 📝 Notes Importantes

### Authentification
- ✅ **Webapp** : Connexion requise pour accéder aux pages
- ❌ **Elasticsearch** : Pas de sécurité (mode dev)
- ❌ **Kibana** : Pas de sécurité (mode dev)
- ✅ **MongoDB** : Username/password requis
- ✅ **Redis** : Password requis
- ✅ **Mongo Express** : Basic auth

### Ports Utilisés
- **8000** : Flask WebApp
- **5601** : Kibana
- **9200** : Elasticsearch HTTP
- **9300** : Elasticsearch Transport
- **5044** : Logstash Beats
- **9600** : Logstash API
- **27017** : MongoDB
- **6379** : Redis
- **8081** : Mongo Express

### Volumes Docker
```bash
# Lister les volumes
docker volume ls

# Volumes du projet
- elasticsearch_data
- logstash_data
- mongodb_data
- mongodb_config
- redis_data
- uploads_data
```

---

## 🚀 Workflows Courants

### 1. Premier démarrage
```bash
# Lancer la stack
docker compose up -d

# Attendre que tout démarre (30-60 secondes)
docker compose ps

# Créer un compte utilisateur
# Ouvrir http://localhost:8000 dans le navigateur
```

### 2. Upload et visualisation
```bash
# 1. Se connecter à l'application
# 2. Aller sur http://localhost:8000/upload
# 3. Uploader test_today_2026.csv
# 4. Attendre 15 secondes (Logstash traite le fichier)
# 5. Voir les stats sur http://localhost:8000/
# 6. Explorer dans Kibana http://localhost:5601
```

### 3. Monitoring
```bash
# Health Dashboard visuel
http://localhost:8000/health-dashboard

# API Health JSON
curl http://localhost:8000/health | jq
```

---

**Dernière mise à jour** : 2 janvier 2026
