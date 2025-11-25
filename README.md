# ProjetELK - Stack Monitoring & WebApp Flask

## 📚 Description
Stack de monitoring de logs basée sur **Elasticsearch / Logstash / Kibana (ELK)** complétée par **MongoDB**, **Redis** et une application **Flask**.

## 🧱 Services (docker-compose)
| Service | Port Host | Image | Persistance | Notes |
|---------|-----------|-------|-------------|-------|
| Elasticsearch | 9200 | elasticsearch:8.11.3 | Volume `elasticsearch_data` | Mode single-node, sécurité désactivée |
| Kibana | 5601 | kibana:8.11.3 | - | Se connecte à Elasticsearch sans credentials |
| Logstash | 5044 / 9600 | logstash:8.11.3 | Volume `logstash_data` + pipeline mount | Pipeline dans `./pipeline/logstash.conf` |
| MongoDB | 27017 | mongo:7.0 | Volumes `mongodb_data`, `mongodb_config` | Auth root via variables .env |
| Redis | 6379 | redis:7.2-alpine | Volume `redis_data` | Mot de passe via .env |
| WebApp Flask | 8000 | build local | Montage code `./webapp` | Route `/` -> "Hello ELK!" |
| Mongo Express | 8081 | mongo-express:1.0.2-18 | - | UI web MongoDB (basic auth via .env) |

## 🌐 Endpoints principaux
- Webapp: http://localhost:8000/
- **Upload Interface**: http://localhost:8000/upload
- Elasticsearch: http://localhost:9200/
- Kibana: http://localhost:5601/
- MongoDB: mongodb://admin:<password>@localhost:27017/
- Redis: redis://:REDIS_PASSWORD@localhost:6379
- Mongo Express (UI): http://localhost:8081/

## 📤 Module d'Upload de Fichiers

### Interface Web
Accédez à http://localhost:8000/upload pour uploader des fichiers CSV ou JSON.

**Fonctionnalités :**
- ✅ Drag & drop ou sélection de fichier
- ✅ Validation des extensions (.csv, .json)
- ✅ Barre de progression d'upload
- ✅ Aperçu des 10 premières lignes
- ✅ Stockage des métadonnées dans MongoDB
- ✅ Ingestion automatique par Logstash

### Upload via API (curl)
```bash
# Upload un fichier CSV
curl -X POST -F "file=@test_logs.csv" http://localhost:8000/upload

# Upload un fichier JSON
curl -X POST -F "file=@test_logs.json" http://localhost:8000/upload
```

**Réponse JSON :**
```json
{
  "success": true,
  "file_id": "69258f89087369731aad7241",
  "filename": "test2.csv",
  "type": "csv",
  "size": 187,
  "upload_date": "2025-11-25T11:14:17.126729",
  "mongodb_stored": true,
  "headers": ["timestamp", "level", "message", "user"],
  "preview": [
    ["2025-11-25 12:00:00", "INFO", "Application started", "admin"],
    ["2025-11-25 12:00:05", "DEBUG", "Configuration loaded", "system"]
  ]
}
```

### Stockage
- **Fichiers**: Volume Docker `uploads_data` monté sur `/data/uploads/`
- **Métadonnées**: Collection MongoDB `files` dans la base `logsdb`

**Schéma MongoDB :**
```javascript
{
  "_id": ObjectId("69258f89087369731aad7241"),
  "filename": "test2.csv",
  "original_filename": "test2.csv",
  "size": 187,
  "type": "csv",
  "upload_date": ISODate("2025-11-25T11:14:17.126Z"),
  "filepath": "/data/uploads/test2.csv",
  "status": "uploaded"
}
```

### Vérifier les uploads
```bash
# Lister les fichiers uploadés
docker compose exec webapp ls -lh /data/uploads/

# Voir les métadonnées dans MongoDB
docker compose exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin --eval "db.getSiblingDB('logsdb').files.find().pretty()"
```

## 🔌 Healthchecks
- Elasticsearch: `_cluster/health`
- Webapp: `/` (HTTP 200)
- Kibana: `/api/status`
- MongoDB / Redis: healthcheck interne Docker

## 📂 Structure clé
```
ProjetELK/
  docker-compose.yml
  Dockerfile
  requirements.txt
  .env / .env.example
  webapp/
    app.py
    routes/
    models/
    utils/
    templates/
    static/
  pipeline/
    logstash.conf
```

## 🛠 Logstash Multi-Pipeline Configuration

### Architecture
Le projet utilise une **configuration multi-pipeline** pour traiter simultanément différents types de fichiers :
- **CSV Pipeline** (`csv-logs`) : Ingestion de fichiers CSV avec parsing automatique
- **JSON Pipeline** (`json-logs`) : Ingestion de fichiers JSON Lines

Configuration définie dans `pipeline/pipelines.yml` :
```yaml
- pipeline.id: csv-logs
  path.config: "/usr/share/logstash/pipeline/csv-pipeline.conf"
  pipeline.workers: 1
  pipeline.batch.size: 125

- pipeline.id: json-logs
  path.config: "/usr/share/logstash/pipeline/json-pipeline.conf"
  pipeline.workers: 1
  pipeline.batch.size: 125
```

### CSV Pipeline (`pipeline/csv-pipeline.conf`)
✅ **Fonctionnel et testé**

```conf
input {
  file {
    path => "/data/uploads/*.csv"
    start_position => "beginning"
    sincedb_path => "/usr/share/logstash/data/sincedb_csv"
    mode => "read"
    file_completed_action => "log"
    file_completed_log_path => "/usr/share/logstash/data/completed_csv.log"
    codec => plain
  }
}

filter {
  csv {
    separator => ","
    autodetect_column_names => true
    autogenerate_column_names => true
  }
  
  if [timestamp] {
    date {
      match => ["timestamp", "ISO8601", "yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd'T'HH:mm:ss'Z'", "yyyy-MM-dd'T'HH:mm:ssZ"]
      target => "@timestamp"
      remove_field => ["timestamp"]
    }
  }
  
  mutate {
    add_field => {
      "source_type" => "csv"
      "source_file" => "%{[log][file][path]}"
      "ingestion_timestamp" => "%{@timestamp}"
    }
  }
  
  if [level] {
    mutate { uppercase => ["level"] }
  }
  
  mutate {
    remove_field => ["host", "event"]
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "logstash-csv-%{+YYYY.MM.dd}"
    data_stream => false
  }
  
  stdout {
    codec => rubydebug { metadata => true }
  }
}
```

**Format CSV attendu :**
```csv
timestamp,level,message,user
2025-11-25 12:00:00,INFO,Application started,admin
2025-11-25 12:00:05,DEBUG,Configuration loaded,system
2025-11-25 12:00:10,ERROR,Connection timeout,service
```

### JSON Pipeline (`pipeline/json-pipeline.conf`)
⚠️ **Nécessite format JSON Lines** (une ligne JSON par événement)

```conf
input {
  file {
    path => "/data/uploads/*.json"
    start_position => "beginning"
    sincedb_path => "/usr/share/logstash/data/sincedb_json"
    mode => "read"
    file_completed_action => "log"
    file_completed_log_path => "/usr/share/logstash/data/completed_json.log"
    codec => "json_lines"
  }
}

filter {
  json {
    source => "message"
    target => "parsed_json"
    skip_on_invalid_json => true
  }
  
  ruby {
    code => "
      parsed = event.get('parsed_json')
      if parsed.is_a?(Hash)
        parsed.each { |k, v| event.set(k, v) }
      end
    "
  }
  
  if [timestamp] {
    date {
      match => ["timestamp", "ISO8601", "yyyy-MM-dd'T'HH:mm:ss'Z'", "yyyy-MM-dd'T'HH:mm:ssZ", "yyyy-MM-dd HH:mm:ss"]
      target => "@timestamp"
      remove_field => ["timestamp"]
    }
  }
  
  mutate {
    add_field => {
      "source_type" => "json"
      "source_file" => "%{[log][file][path]}"
      "ingestion_timestamp" => "%{@timestamp}"
    }
  }
  
  if [level] {
    mutate { uppercase => ["level"] }
  }
  
  if [message] and [message] =~ /ERROR|WARN|INFO|DEBUG/ {
    grok {
      match => {
        "message" => [
          "%{LOGLEVEL:extracted_level}",
          ".*%{LOGLEVEL:extracted_level}.*"
        ]
      }
      pattern_definitions => {
        "LOGLEVEL" => "(ERROR|WARN|WARNING|INFO|DEBUG|TRACE|FATAL)"
      }
      tag_on_failure => []
    }
  }
  
  mutate {
    remove_field => ["host", "event"]
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "logstash-json-%{+YYYY.MM.dd}"
    data_stream => false
  }
  
  stdout {
    codec => rubydebug { metadata => true }
  }
}
```

**Format JSON Lines attendu :**
```json
{"timestamp":"2025-11-25T12:10:00Z","level":"info","message":"Service started","service":"api"}
{"timestamp":"2025-11-25T12:10:05Z","level":"error","message":"Database ERROR occurred","service":"db"}
{"timestamp":"2025-11-25T12:10:10Z","level":"warning","message":"High memory WARNING detected","service":"monitor"}
```

### 📊 Vérifier l'ingestion

**Lister les indices :**
```bash
curl -s http://localhost:9200/_cat/indices?v | grep logstash
```

**Compter les documents CSV :**
```bash
curl -s "http://localhost:9200/logstash-csv-*/_count?pretty"
```

**Rechercher dans les logs CSV :**
```bash
curl -s -X GET "http://localhost:9200/logstash-csv-*/_search?pretty&size=5&q=level:ERROR"
```

**Exemple de document indexé :**
```json
{
  "_index": "logstash-csv-2025.11.25",
  "_id": "kFi4upoBo8sA3KWOsjoZ",
  "_source": {
    "user": "admin",
    "@version": "1",
    "log": {
      "file": {
        "path": "/data/uploads/test2.csv"
      }
    },
    "source_type": "csv",
    "ingestion_timestamp": "2025-11-25T12:00:00.000Z",
    "@timestamp": "2025-11-25T12:00:00.000Z",
    "message": "Application started",
    "source_file": "/data/uploads/test2.csv",
    "level": "INFO"
  }
}
```

### 🔍 Debugging Logstash

**Voir les logs en temps réel :**
```bash
docker compose logs -f logstash
```

**Vérifier que les pipelines sont démarrés :**
```bash
docker compose logs logstash | grep "Pipeline started"
```

**Vérifier le sincedb (fichiers traités) :**
```bash
docker compose exec logstash cat /usr/share/logstash/data/sincedb_csv
docker compose exec logstash cat /usr/share/logstash/data/sincedb_json
```

**Forcer le retraitement des fichiers :**
```bash
docker compose exec logstash rm -f /usr/share/logstash/data/sincedb_*
docker compose restart logstash
```

## � Index Template Elasticsearch

### Template `logs-template`
Un index template est configuré pour tous les indices `logstash-*` avec des mappings optimisés :

```json
{
  "index_patterns": ["logstash-*"],
  "priority": 200,
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "index.refresh_interval": "5s"
    },
    "mappings": {
      "properties": {
        "timestamp": { "type": "date" },
        "@timestamp": { "type": "date" },
        "level": { "type": "keyword" },
        "message": { 
          "type": "text",
          "fields": {
            "keyword": { "type": "keyword" }
          }
        },
        "service": { "type": "keyword" },
        "ip": { "type": "ip" },
        "ip_address": { "type": "ip" },
        "user": { "type": "keyword" },
        "source_type": { "type": "keyword" },
        "source_file": { "type": "keyword" }
      }
    }
  }
}
```

**Fichier**: `logs-template.json`

### Créer/Mettre à jour le template
```bash
curl -X PUT "http://localhost:9200/_index_template/logs-template" \
  -H 'Content-Type: application/json' \
  -d @logs-template.json
```

### Vérifier le template
```bash
# Lister tous les templates
curl "http://localhost:9200/_index_template?pretty"

# Voir un template spécifique
curl "http://localhost:9200/_index_template/logs-template?pretty"
```

### Vérifier qu'un index utilise le template
```bash
# Voir le mapping d'un index
curl "http://localhost:9200/logstash-csv-2025.11.25/_mapping?pretty"
```

### Types de champs configurés

| Champ | Type | Description | Exemple de requête |
|-------|------|-------------|-------------------|
| `timestamp` / `@timestamp` | `date` | Date du log | Recherche par plage de dates |
| `level` | `keyword` | Niveau de log (INFO, ERROR, etc.) | Filtrage exact : `level:ERROR` |
| `message` | `text` + `keyword` | Message du log, analysé pour recherche full-text | Recherche texte : `message:authentication` |
| `service` | `keyword` | Nom du service | Agrégation par service |
| `ip` / `ip_address` | `ip` | Adresse IP | Range : `ip:[192.168.0.0 TO 192.168.255.255]` |
| `user` | `keyword` | Utilisateur | Filtrage : `user:alice` |

### Exemples de requêtes avancées

**Recherche par range IP (CIDR) :**
```bash
curl -X GET "http://localhost:9200/logstash-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "ip": {
        "gte": "192.168.0.0",
        "lte": "192.168.255.255"
      }
    }
  }
}'
```

**Agrégation par service :**
```bash
curl -X GET "http://localhost:9200/logstash-*/_search?pretty&size=0" -H 'Content-Type: application/json' -d'
{
  "aggs": {
    "services": {
      "terms": {
        "field": "service",
        "size": 10
      }
    }
  }
}'
```

**Filtrage multi-critères :**
```bash
curl -X GET "http://localhost:9200/logstash-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "message": "error" }},
        { "term": { "level": "ERROR" }},
        { "range": { "@timestamp": { "gte": "now-1h" }}}
      ]
    }
  }
}'
```

## �🚀 Démarrage
```bash
# Construire l'image webapp
docker compose build webapp

# Lancer toute la stack
docker compose up -d

# Vérifier état
curl -s http://localhost:9200/_cluster/health
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:5601/api/status
curl -s http://localhost:8000/
```

### Lancer seulement MongoDB ou Mongo Express
```bash
# Lancer MongoDB seul
docker compose up -d mongodb

# Lancer Mongo Express (UI) seul
docker compose up -d mongo-express
```

## 🧪 Développement local (sans Docker)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python webapp/app.py
```

## 🔐 Variables (.env)
```
ELASTIC_USERNAME=elastic (non utilisé quand sécurité off)
ELASTIC_PASSWORD=changeme (supprimé côté compose)
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=changeme
MONGO_DATABASE=logsdb
REDIS_PASSWORD=changeme
FLASK_ENV=development
MONGO_EXPRESS_USERNAME=meadmin
MONGO_EXPRESS_PASSWORD=mechangeme
```
Adapter les mots de passe avant production.

## 🗄️ MongoDB: connexions rapides

Depuis l'hôte (si `mongosh` installé) :
```bash
mongosh "mongodb://admin:changeme@localhost:27017/logsdb?authSource=admin"
```

Depuis le conteneur (pas besoin d'installer `mongosh` en local) :
```bash
docker compose exec mongodb mongosh -u "$MONGO_ROOT_USERNAME" -p "$MONGO_ROOT_PASSWORD" --authenticationDatabase admin
```

Créer un utilisateur applicatif (optionnel) :
```javascript
use logsdb
db.createUser({ user: "appuser", pwd: "app_pass_123", roles: [{ role: "readWrite", db: "logsdb" }] })
```

Connexion ensuite :
```bash
mongosh "mongodb://appuser:app_pass_123@localhost:27017/logsdb"
```

## 🖥️ Mongo Express (UI)

- URL: http://localhost:8081
- Identifiants (par défaut):
  - Utilisateur: `meadmin`
  - Mot de passe: `mechangeme`

Changer les identifiants dans `.env`, puis :
```bash
docker compose up -d --force-recreate mongo-express
```

## ✅ Actions déjà réalisées

### Infrastructure
- ✅ Docker-compose avec 7 services (Elasticsearch, Kibana, Logstash, MongoDB, Redis, Flask WebApp, Mongo Express)
- ✅ Volumes persistants pour toutes les données
- ✅ Network bridge `elk_net` pour communication inter-services
- ✅ Politique de restart `unless-stopped` pour démarrage automatique au boot
- ✅ Healthchecks pour Elasticsearch, Kibana, MongoDB, WebApp

### Configuration Logstash
- ✅ Multi-pipeline avec `pipelines.yml`
- ✅ CSV Pipeline fonctionnel (csv-pipeline.conf) avec parsing automatique
- ✅ JSON Pipeline configuré (json-pipeline.conf) pour JSON Lines
- ✅ Volume `/data/uploads` monté en lecture seule
- ✅ Sincedb tracking pour éviter les doublons
- ✅ Output vers Elasticsearch avec indices datés

### Application Flask
- ✅ Interface d'upload avec drag & drop
- ✅ Validation des fichiers (CSV/JSON uniquement)
- ✅ Preview des 10 premières lignes
- ✅ Stockage des métadonnées dans MongoDB
- ✅ API REST pour upload programmatique
- ✅ Connexion MongoDB avec authentification
- ✅ Barre de progression d'upload

### Tests & Validation
- ✅ Upload CSV testé avec succès (3 documents indexés)
- ✅ Vérification de l'indexation dans Elasticsearch
- ✅ Vérification des métadonnées dans MongoDB
- ✅ Parsing des timestamps et normalisation des niveaux de log

### Résolutions de problèmes
- ✅ Correction erreur Kibana (username superuser interdit avec security disabled)
- ✅ Fix permission Logstash `file_completed_log_path`
- ✅ Correction index Elasticsearch (data_stream conflict)
- ✅ Fix interpolation des champs ECS (log.file.path)
- ✅ Nettoyage des credentials inutiles

## � Prompt 8 — Configuration Kibana Dashboard E-Commerce

### Fichiers créés
- ✅ **ecommerce_transactions.csv** : 100 transactions e-commerce avec timestamps, montants, types de paiement, statuts (success/failed)
- ✅ **KIBANA_SETUP_GUIDE.md** : Guide complet pas à pas pour la configuration Kibana
- ✅ **kibana_setup.sh** : Script de vérification des services et affichage des étapes
- ✅ **export_kibana_dashboard.sh** : Script automatique d'export du dashboard

### Étapes de configuration

#### 1. Upload des données
```bash
# Le fichier ecommerce_transactions.csv contient 100 transactions
# Uploadez-le via l'interface web : http://localhost:8000/upload
```

#### 2. Créer l'index pattern dans Kibana
1. Ouvrez Kibana : http://localhost:5601
2. Menu ☰ → Management → Stack Management → Data Views
3. Create data view :
   - Name: `Logs Pattern`
   - Index pattern: `logstash-*`
   - Timestamp field: `@timestamp`

#### 3. Créer les 3 visualisations

**Visualisation 1 : Transactions par Heure**
- Type : Area/Line Chart
- Axe Y : Count
- Axe X : Date Histogram (@timestamp, intervalle 1h)
- Nom : `E-Commerce - Transactions par Heure`

**Visualisation 2 : Top 10 des Erreurs**
- Type : Horizontal Bar Chart
- Filtre : status=failed
- Axe Y : Count
- Axe X : Terms (error_message.keyword, top 10)
- Nom : `E-Commerce - Top 10 Erreurs`

**Visualisation 3 : Répartition par Type de Paiement**
- Type : Pie Chart (Donut)
- Slice size : Count
- Split slices : Terms (payment_type.keyword)
- Nom : `E-Commerce - Répartition Paiements`

#### 4. Créer le dashboard
1. Menu ☰ → Dashboard → Create dashboard
2. Add from library → Sélectionner les 3 visualisations
3. Organiser le layout (transactions en haut, 2 autres en bas)
4. Save : `E-Commerce Logs Dashboard`

#### 5. Exporter le dashboard
```bash
# Méthode 1 : Via l'interface Kibana
# Stack Management → Saved Objects → Sélectionner les objets → Export

# Méthode 2 : Via script automatique
./export_kibana_dashboard.sh
```

### Commandes de vérification

```bash
# Lancer le script de setup (affiche toutes les infos)
./kibana_setup.sh

# Vérifier les données indexées
curl -s 'http://localhost:9200/logstash-*/_count' | jq

# Voir les transactions échouées
curl -s -X POST 'http://localhost:9200/logstash-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match":{"status":"failed"}},"size":5}' | jq '.hits.hits[]._source'

# Agrégation par type de paiement
curl -s -X POST 'http://localhost:9200/logstash-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{"size":0,"aggs":{"payment_types":{"terms":{"field":"payment_type.keyword"}}}}' | jq '.aggregations'
```

### Documentation
Pour le guide complet avec captures d'écran et instructions détaillées :
```bash
cat KIBANA_SETUP_GUIDE.md
```

### Données E-Commerce
Le fichier CSV contient :
- **100 transactions** du 25 novembre 2025 (8h00-17h45)
- **Statuts** : 75 success, 25 failed
- **Types de paiement** : credit_card, paypal, debit_card, bank_transfer
- **Catégories** : Electronics, Clothing, Sports, Food, Home, Beauty, Books
- **Pays** : France, Germany, Italy, Spain, Belgium
- **Erreurs** : Payment declined, Card validation failed, Network timeout, Payment gateway error, Card expired

---

## 🔜 Idées futures
- Activer sécurité Elasticsearch (API Keys / service account)
- Ajouter Filebeat ou Metricbeat
- Alertes Kibana sur taux d'erreur élevé
- Tests automatisés (PyTest) pour la webapp
- Intégration CI (GitHub Actions)

## 📎 Liens utiles
- Elasticsearch Docs: https://www.elastic.co/guide/index.html
- Kibana Docs: https://www.elastic.co/guide/en/kibana/current/index.html
- Logstash Docs: https://www.elastic.co/guide/en/logstash/current/index.html
- Flask: https://flask.palletsprojects.com/
- PyMongo: https://pymongo.readthedocs.io/
- Redis Python: https://redis-py.readthedocs.io/

---
Bon monitoring !
