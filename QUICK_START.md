# 🚀 Quick Start Guide - ProjetELK

## Démarrage rapide

### 1. Lancer la stack complète
```bash
docker compose up -d
```

### 2. Vérifier que tout fonctionne
```bash
# Elasticsearch
curl http://localhost:9200/_cluster/health

# Kibana
curl http://localhost:5601/api/status

# WebApp
curl http://localhost:8000/

# MongoDB (via Mongo Express)
# Ouvrir http://localhost:8081 dans le navigateur
# Login: meadmin / mechangeme
```

### 3. Uploader un fichier de logs

**Via l'interface web:**
- Ouvrir http://localhost:8000/upload
- Glisser-déposer un fichier CSV ou JSON
- Voir l'aperçu et confirmer

**Via curl:**
```bash
# Créer un fichier CSV de test
cat > test.csv << 'CSV'
timestamp,level,message,user
2025-11-25 14:00:00,INFO,User login,alice
2025-11-25 14:00:05,ERROR,Connection failed,bob
2025-11-25 14:00:10,WARNING,High CPU usage,system
CSV

# Uploader
curl -X POST -F "file=@test.csv" http://localhost:8000/upload
```

### 4. Vérifier l'ingestion dans Elasticsearch
```bash
# Attendre 10 secondes que Logstash traite le fichier
sleep 10

# Lister les indices
curl "http://localhost:9200/_cat/indices?v" | grep logstash

# Compter les documents
curl "http://localhost:9200/logstash-csv-*/_count?pretty"

# Rechercher les logs ERROR
curl "http://localhost:9200/logstash-csv-*/_search?pretty&size=5&q=level:ERROR"
```

### 5. Visualiser dans Kibana
1. Ouvrir http://localhost:5601
2. Menu → Stack Management → Index Patterns
3. Créer pattern: `logstash-csv-*`
4. Choisir `@timestamp` comme champ de temps
5. Menu → Discover → Sélectionner le pattern
6. Explorer les logs!

## 📁 Formats de fichiers supportés

### CSV
```csv
timestamp,level,message,user
2025-11-25 12:00:00,INFO,Application started,admin
2025-11-25 12:00:05,ERROR,Connection timeout,service
```

### JSON Lines (une ligne = un objet JSON)
```json
{"timestamp":"2025-11-25T12:00:00Z","level":"info","message":"Service started"}
{"timestamp":"2025-11-25T12:00:05Z","level":"error","message":"Database error"}
```

## 🔧 Commandes utiles

### Docker
```bash
# Voir les logs en temps réel
docker compose logs -f logstash

# Redémarrer un service
docker compose restart webapp

# Arrêter la stack
docker compose down

# Arrêter et supprimer les volumes
docker compose down -v
```

### Logstash
```bash
# Forcer le retraitement des fichiers
docker compose exec logstash rm -f /usr/share/logstash/data/sincedb_*
docker compose restart logstash

# Vérifier les pipelines actifs
docker compose logs logstash | grep "Pipeline started"
```

### MongoDB
```bash
# Accéder au shell MongoDB
docker compose exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin

# Voir les fichiers uploadés
docker compose exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin --eval "db.getSiblingDB('logsdb').files.find().pretty()"
```

### Elasticsearch
```bash
# Santé du cluster
curl http://localhost:9200/_cluster/health?pretty

# Lister tous les indices
curl http://localhost:9200/_cat/indices?v

# Supprimer un index
curl -X DELETE http://localhost:9200/logstash-csv-2025.11.25
```

## 🐛 Dépannage

### Logstash ne traite pas les fichiers
1. Vérifier que les fichiers sont dans `/data/uploads/`:
   ```bash
   docker compose exec logstash ls -lh /data/uploads/
   ```

2. Vérifier les logs Logstash:
   ```bash
   docker compose logs --tail=100 logstash | grep -i error
   ```

3. Forcer le retraitement:
   ```bash
   docker compose exec logstash rm -f /usr/share/logstash/data/sincedb_*
   docker compose restart logstash
   ```

### MongoDB connection refused
1. Vérifier que MongoDB est démarré:
   ```bash
   docker compose ps mongodb
   ```

2. Vérifier les credentials dans `.env`:
   ```bash
   cat .env | grep MONGO
   ```

### Elasticsearch cluster red/yellow
1. Vérifier les logs:
   ```bash
   docker compose logs elasticsearch | tail -50
   ```

2. Mode single-node est normal en yellow (pas de réplicas)

## 📚 Documentation complète
Voir `README.md` pour la documentation complète.

---
**Projet ELK Stack - Monitoring de Logs**
