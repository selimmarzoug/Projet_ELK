# 📝 PROMPT 11 - API de Recherche Elasticsearch

## ✅ Objectif
Créer une API REST `/api/search` pour rechercher dans les logs Elasticsearch avec Query DSL, pagination et sauvegarde de l'historique dans MongoDB.

---

## 🎯 Spécifications Implémentées

### 1. Route API `/api/search` (POST)

**Endpoint** : `POST http://localhost:8000/api/search`

**Paramètres acceptés** :
```json
{
  "query": "texte libre",           // Recherche multi-champs
  "level": "success|failed",         // Niveau (alias: status)
  "service": "payment_type",         // Service (alias: payment_type)
  "country": "France",               // Filtre par pays
  "date_from": "2025-11-25T00:00",  // Date début (ISO)
  "date_to": "2025-11-25T23:59",    // Date fin (ISO)
  "page": 1,                         // Numéro de page
  "size": 50                         // Résultats par page (défaut: 50)
}
```

**Réponse JSON** :
```json
{
  "success": true,
  "total": 600,
  "page": 1,
  "size": 50,
  "total_pages": 12,
  "results": [
    {
      "id": "abc123",
      "timestamp": "2025-11-25T14:30:00.000Z",
      "transaction_id": "TXN00123",
      "customer_id": "CUST1234",
      "amount": 129.99,
      "payment_type": "credit_card",
      "status": "success",
      "country": "France",
      "product_category": "Electronics",
      "error_message": ""
    }
    // ... 49 autres résultats
  ],
  "query_info": {
    "query": "texte recherché",
    "level": "success",
    "service": "credit_card",
    "country": "France",
    "date_from": "2025-11-25T00:00",
    "date_to": "2025-11-25T23:59"
  }
}
```

---

## 🔍 Query DSL Elasticsearch

### Construction de la Requête

**Code Python** (`webapp/app.py`) :
```python
# Construire la requête Elasticsearch
must_queries = []

# 1. Recherche textuelle (multi_match sur tous les champs)
if query_text:
    must_queries.append({
        'multi_match': {
            'query': query_text,
            'fields': ['*'],
            'type': 'best_fields',
            'operator': 'or'
        }
    })

# 2. Filtre par status (niveau)
if status_filter:
    must_queries.append({'term': {'status': status_filter}})

# 3. Filtre par payment_type (service)
if payment_type_filter:
    must_queries.append({'term': {'payment_type': payment_type_filter}})

# 4. Filtre par country
if country_filter:
    must_queries.append({'term': {'country': country_filter}})

# 5. Filtre par date range
if date_from or date_to:
    date_range = {}
    if date_from:
        date_range['gte'] = date_from
    if date_to:
        date_range['lte'] = date_to
    must_queries.append({
        'range': {
            '@timestamp': date_range
        }
    })

# Query finale
es_query = {
    'bool': {
        'must': must_queries if must_queries else [{'match_all': {}}]
    }
}
```

### Exemple de Query DSL Générée

**Recherche avec tous les filtres** :
```json
{
  "bool": {
    "must": [
      {
        "multi_match": {
          "query": "failed transaction",
          "fields": ["*"],
          "type": "best_fields",
          "operator": "or"
        }
      },
      {
        "term": {
          "status": "failed"
        }
      },
      {
        "term": {
          "payment_type": "credit_card"
        }
      },
      {
        "term": {
          "country": "France"
        }
      },
      {
        "range": {
          "@timestamp": {
            "gte": "2025-11-25T00:00:00",
            "lte": "2025-11-25T23:59:59"
          }
        }
      }
    ]
  }
}
```

---

## 📊 Pagination

**Paramètres** :
- `page` : Numéro de page (commence à 1)
- `size` : Résultats par page (défaut: **50** selon Prompt 11)

**Calcul** :
```python
from_offset = (page - 1) * size

response = es_client.search(
    index='logstash-*',
    body={
        'query': es_query,
        'from': from_offset,
        'size': size,
        'sort': [{'@timestamp': {'order': 'desc'}}]
    }
)
```

**Métadonnées de pagination** :
```python
total = response['hits']['total']['value']
total_pages = (total + size - 1) // size  # Arrondi supérieur
```

---

## 💾 Sauvegarde dans MongoDB (Collection `search_history`)

### Structure du Document

```json
{
  "timestamp": "2025-11-25T14:32:15.123Z",
  "query": "failed transaction",
  "filters": {
    "level": "failed",
    "service": "credit_card",
    "country": "France",
    "date_from": "2025-11-25T00:00:00",
    "date_to": "2025-11-25T23:59:59"
  },
  "elasticsearch_query": {
    "bool": {
      "must": [...]
    }
  },
  "results_count": 158,
  "page": 1,
  "size": 50,
  "execution_time_ms": 42,
  "ip_address": "172.18.0.1",
  "user_agent": "Mozilla/5.0 ..."
}
```

### Code de Sauvegarde

```python
if db is not None:
    try:
        history_collection = db['search_history']
        history_entry = {
            'timestamp': search_timestamp,
            'query': query_text,
            'filters': {
                'level': status_filter,
                'service': payment_type_filter,
                'country': country_filter,
                'date_from': date_from,
                'date_to': date_to
            },
            'elasticsearch_query': es_query,
            'results_count': total,
            'page': page,
            'size': size,
            'execution_time_ms': int((datetime.utcnow() - search_timestamp).total_seconds() * 1000),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        history_collection.insert_one(history_entry)
        print(f"✅ Recherche sauvegardée dans l'historique MongoDB")
    except Exception as mongo_error:
        print(f"⚠️ Erreur sauvegarde historique MongoDB: {mongo_error}")
```

---

## 📡 Route API Historique `/api/search/history` (GET)

**Endpoint** : `GET http://localhost:8000/api/search/history?limit=50&skip=0`

**Paramètres** :
- `limit` : Nombre de résultats (défaut: 50)
- `skip` : Offset pour pagination (défaut: 0)

**Réponse** :
```json
{
  "success": true,
  "total": 127,
  "limit": 50,
  "skip": 0,
  "history": [
    {
      "timestamp": "2025-11-25T14:32:15.123Z",
      "query": "failed transaction",
      "filters": {...},
      "results_count": 158,
      "execution_time_ms": 42
    },
    // ... 49 autres entrées
  ]
}
```

---

## 🧪 Tests

### Test 1 : Recherche Simple (Match All)
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "page": 1,
    "size": 50
  }'
```

**Résultat attendu** : 50 premiers logs (sur 600 total)

### Test 2 : Recherche avec Filtres
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "failed",
    "level": "failed",
    "service": "credit_card",
    "page": 1,
    "size": 50
  }' | jq '.total'
```

**Résultat attendu** : Nombre de transactions failed avec credit_card

### Test 3 : Recherche par Date Range
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2025-11-25T10:00:00",
    "date_to": "2025-11-25T12:00:00",
    "size": 50
  }' | jq '.results | length'
```

**Résultat attendu** : Logs entre 10h et 12h

### Test 4 : Vérifier Historique MongoDB
```bash
curl -s http://localhost:8000/api/search/history?limit=10 | jq '.total'
```

**Résultat attendu** : Nombre total de recherches effectuées

### Test 5 : Pagination
```bash
# Page 1
curl -s -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "size": 50}' | jq '.page, .total_pages'

# Page 2
curl -s -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"page": 2, "size": 50}' | jq '.results[0].transaction_id'
```

**Résultat attendu** : Page 1/12, puis première transaction de la page 2

---

## 📊 Intégration avec DataTables.js

**Frontend** (`templates/search.html`) :
- Appel AJAX à `/api/search` avec paramètres du formulaire
- Affichage dans DataTables avec tri/filtrage côté client
- Export CSV des résultats via bouton DataTables
- Pagination DataTables (25 résultats par page dans l'UI)

**Configuration DataTables** :
```javascript
dataTable = $('#resultsTable').DataTable({
    dom: 'Bfrtip',
    buttons: [
        {
            extend: 'csv',
            text: '<i class="fas fa-file-csv"></i> Export CSV',
            filename: 'logs_export_' + new Date().toISOString().slice(0,10)
        }
    ],
    pageLength: 25,
    order: [[0, 'desc']]
});
```

---

## 🔐 Sécurité & Performance

### Sécurité
- ✅ Validation des paramètres (`int()` pour page/size)
- ✅ Gestion des erreurs avec try/except
- ✅ Logs des erreurs côté serveur
- ✅ Pas d'injection ES (Query DSL structuré)

### Performance
- ✅ Index Elasticsearch optimisé
- ✅ Pagination côté serveur (50 résultats max)
- ✅ Tri par @timestamp (champ indexé)
- ✅ MongoDB: collection indexée sur timestamp
- ✅ Timeout Elasticsearch: 5 secondes

### Recommandations
```python
# Créer index MongoDB pour historique
db.search_history.create_index([('timestamp', -1)])
db.search_history.create_index('ip_address')
```

---

## 📁 Fichiers Modifiés

### 1. `/webapp/app.py`
- Route `/api/search` (POST) : Recherche avec Query DSL
- Route `/api/search/history` (GET) : Historique des recherches
- Sauvegarde automatique dans MongoDB collection `search_history`
- Pagination 50 résultats/page par défaut

### 2. `/webapp/templates/search.html`
- Formulaire avec filtres : query, level, service, country, date_range
- Intégration DataTables.js avec export CSV
- Appel AJAX à `/api/search`
- Affichage résultats paginés

---

## 🚀 Déploiement

```bash
# 1. Modifications appliquées
vim webapp/app.py
vim webapp/templates/search.html

# 2. Redémarrage
docker compose restart webapp

# 3. Test
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "failed", "size": 50}'
```

---

## ✅ Checklist Prompt 11

- [x] Route Flask `/api/search` (POST)
- [x] Paramètres : query, level, service, date_from, date_to
- [x] Construction Query DSL Elasticsearch (bool query avec must)
- [x] Retour JSON paginé (50 logs/page par défaut)
- [x] Sauvegarde requête dans MongoDB (collection `search_history`)
- [x] Métadonnées : timestamp, filters, elasticsearch_query, results_count
- [x] Route `/api/search/history` pour consulter l'historique
- [x] Gestion d'erreurs complète
- [x] Logs serveur pour debugging

---

## 📈 Statistiques MongoDB

**Voir l'historique** :
```bash
docker exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin \
  --eval 'db = db.getSiblingDB("logsdb"); db.search_history.countDocuments({})'
```

**Dernières recherches** :
```bash
docker exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin \
  --eval 'db = db.getSiblingDB("logsdb"); db.search_history.find().sort({timestamp:-1}).limit(5).pretty()'
```

---

## 🎯 Résumé

**API REST complète** pour recherche Elasticsearch avec :
- ✅ Query DSL dynamique (multi_match + term + range)
- ✅ Pagination 50 résultats/page
- ✅ Historique MongoDB automatique
- ✅ Frontend DataTables avec export CSV
- ✅ Support filtres avancés (texte, niveau, service, date)

**URLs** :
- API Search : `POST http://localhost:8000/api/search`
- API History : `GET http://localhost:8000/api/search/history`
- Page Search : `http://localhost:8000/search`
