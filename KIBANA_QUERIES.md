# 🔍 Elasticsearch & Kibana - Exemples de Requêtes

## Requêtes Elasticsearch via cURL

### 1. Recherche basique

```bash
# Tous les logs ERROR
curl "http://localhost:9200/logstash-*/_search?pretty&q=level:ERROR"

# Recherche full-text dans message
curl "http://localhost:9200/logstash-*/_search?pretty&q=message:connection"

# Par service spécifique
curl "http://localhost:9200/logstash-*/_search?pretty&q=service:database-service"
```

### 2. Recherche par range d'IP

```bash
# IPs dans le range 192.168.x.x
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

# IPs dans le réseau 10.0.0.0/24
curl -X GET "http://localhost:9200/logstash-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "ip": "10.0.0.0/24"
    }
  }
}'
```

### 3. Recherche multi-critères (bool query)

```bash
# ERROR des dernières 24h contenant "timeout"
curl -X GET "http://localhost:9200/logstash-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "level": "ERROR" }},
        { "match": { "message": "timeout" }},
        { "range": { "@timestamp": { "gte": "now-24h" }}}
      ]
    }
  }
}'

# Logs d'un service spécifique, excluant INFO
curl -X GET "http://localhost:9200/logstash-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "service": "database-service" }}
      ],
      "must_not": [
        { "term": { "level": "INFO" }}
      ]
    }
  }
}'
```

### 4. Agrégations

```bash
# Compter logs par service
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

# Compter logs par niveau
curl -X GET "http://localhost:9200/logstash-*/_search?pretty&size=0" -H 'Content-Type: application/json' -d'
{
  "aggs": {
    "levels": {
      "terms": {
        "field": "level"
      }
    }
  }
}'

# Histogram par heure
curl -X GET "http://localhost:9200/logstash-*/_search?pretty&size=0" -H 'Content-Type: application/json' -d'
{
  "aggs": {
    "logs_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "1h"
      }
    }
  }
}'

# Top utilisateurs
curl -X GET "http://localhost:9200/logstash-*/_search?pretty&size=0" -H 'Content-Type: application/json' -d'
{
  "aggs": {
    "top_users": {
      "terms": {
        "field": "user",
        "size": 5
      }
    }
  }
}'
```

### 5. Statistiques

```bash
# Stats sur nombre de logs par service
curl -X GET "http://localhost:9200/logstash-*/_search?pretty&size=0" -H 'Content-Type: application/json' -d'
{
  "aggs": {
    "services": {
      "terms": {
        "field": "service"
      },
      "aggs": {
        "levels": {
          "terms": {
            "field": "level"
          }
        }
      }
    }
  }
}'
```

## Configuration Kibana

### 1. Créer un Index Pattern

1. Ouvrir Kibana: http://localhost:5601
2. Menu → **Stack Management** → **Index Patterns**
3. Cliquer **Create index pattern**
4. Pattern: `logstash-*`
5. Time field: `@timestamp`
6. Cliquer **Create index pattern**

### 2. Discover - Requêtes KQL

```
# Recherche basique
level: ERROR

# Recherche avec wildcard
message: *timeout*

# ET logique
level: ERROR AND service: database-service

# OU logique
level: ERROR OR level: WARNING

# Négation
NOT level: INFO

# Range de dates
@timestamp >= "2025-11-25T00:00:00" AND @timestamp <= "2025-11-25T23:59:59"

# Recherche dans IP
ip: 192.168.*

# Combinaison complexe
(level: ERROR OR level: WARNING) AND service: *-service AND NOT user: system
```

### 3. Visualisations suggérées

#### Pie Chart - Répartition par niveau
- **Metrics**: Count
- **Buckets**: Split slices → Terms → Field: `level`

#### Vertical Bar - Logs par service
- **Y-axis**: Count
- **X-axis**: Terms → Field: `service`

#### Line Chart - Timeline des logs
- **Y-axis**: Count
- **X-axis**: Date Histogram → Field: `@timestamp` → Interval: Auto

#### Data Table - Top utilisateurs
- **Metrics**: Count
- **Buckets**: Split rows → Terms → Field: `user` → Size: 10

#### Tag Cloud - Services
- **Tags**: Terms → Field: `service`

#### Heat Map - Services x Niveaux
- **Y-axis**: Terms → Field: `service`
- **X-axis**: Terms → Field: `level`
- **Dot size**: Count

### 4. Dashboard Example

Créer un dashboard avec:
1. **Metric**: Total de logs (Count)
2. **Metric**: Nombre d'erreurs (Filter: level:ERROR)
3. **Pie**: Répartition par niveau
4. **Bar**: Top 10 services
5. **Line**: Timeline des dernières 24h
6. **Table**: Derniers logs ERROR

### 5. Filtres Kibana

Ajoutez des filtres permanents:
- **Field**: `level` → **Operator**: `is` → **Value**: `ERROR`
- **Field**: `@timestamp` → **Operator**: `is between` → Last 7 days
- **Field**: `service` → **Operator**: `is one of` → database-service, api-service

## Alertes (Kibana Alerting)

### Créer une alerte sur logs ERROR

1. Menu → **Stack Management** → **Rules and Connectors**
2. **Create rule**
3. **Index threshold**:
   - Index: `logstash-*`
   - Threshold: Count > 10
   - Time window: Last 5 minutes
   - Group by: `service`
   - Filter: `level:ERROR`
4. Configurer notification (email, webhook, etc.)

## Scripts utiles

```bash
# Compter les logs par jour
for date in $(seq 20 25); do
  count=$(curl -s "http://localhost:9200/logstash-csv-2025.11.$date/_count" | grep -o '"count":[0-9]*' | cut -d: -f2)
  echo "2025-11-$date: $count logs"
done

# Exporter les logs ERROR en JSON
curl -s "http://localhost:9200/logstash-*/_search?q=level:ERROR&size=100" > errors.json

# Supprimer les vieux indices (>30 jours)
curl -X DELETE "http://localhost:9200/logstash-*-2025.10.*"
```

## Optimisation des requêtes

1. **Utiliser des filtres** (term, range) plutôt que des queries (match) quand possible
2. **Limiter la taille** avec `size` parameter
3. **Désactiver _source** si seuls les agrégations comptent: `"_source": false`
4. **Utiliser des filtres cached**: Les term queries sont automatiquement cachées
5. **Index pattern spécifique**: `logstash-csv-2025.11.25` vs `logstash-*`

---
📊 **Explorez vos logs avec puissance!**
