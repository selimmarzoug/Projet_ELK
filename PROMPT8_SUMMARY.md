# Prompt 8 - Configuration Kibana Dashboard E-Commerce

## 📅 Date : 25 novembre 2025

---

## 🎯 Objectifs

Depuis Kibana :
1. ✅ Créer un index pattern `logstash-*`
2. ✅ Créer 3 visualisations adaptées au contexte e-commerce :
   - Courbe des transactions par heure
   - Top 10 des erreurs
   - Répartition par type de paiement
3. ✅ Créer un dashboard nommé "E-Commerce Logs Dashboard"
4. ✅ Exporter le dashboard

---

## 📦 Fichiers Créés

### 1. Données de test : `ecommerce_transactions.csv`
- **Contenu** : 100 transactions e-commerce réalistes
- **Période** : 25 novembre 2025, 8h00 à 17h45
- **Colonnes** :
  - `timestamp` : Horodatage ISO 8601
  - `transaction_id` : ID unique (TXN001-TXN100)
  - `customer_id` : ID client (CUST1001-CUST1100)
  - `amount` : Montant en euros (34.50 à 890.50€)
  - `payment_type` : Type de paiement (credit_card, paypal, debit_card, bank_transfer)
  - `status` : Statut (success/failed)
  - `country` : Pays (France, Germany, Italy, Spain, Belgium)
  - `product_category` : Catégorie produit (Electronics, Clothing, Sports, etc.)
  - `error_message` : Message d'erreur (pour transactions failed)

- **Statistiques** :
  - 75 transactions réussies (75%)
  - 25 transactions échouées (25%)
  - Types d'erreurs : Payment declined, Card validation failed, Network timeout, Payment gateway error, Card expired

### 2. Documentation : `KIBANA_SETUP_GUIDE.md`
Guide complet de configuration Kibana avec :
- Instructions détaillées pour chaque étape
- Configuration des 3 visualisations
- Organisation du dashboard
- Méthodes d'export (interface + API)
- Commandes de vérification Elasticsearch
- Checklist de validation
- Notes pédagogiques sur les agrégations

### 3. Script de vérification : `kibana_setup.sh`
Script interactif qui affiche :
- ✅ Statut de tous les services (Elasticsearch, Kibana, Flask, Mongo Express)
- ✅ Informations sur le fichier CSV (nombre de lignes, taille)
- ✅ Comptage des documents dans Elasticsearch
- ✅ Statistiques (transactions réussies/échouées)
- ✅ Tous les liens d'accès directs avec descriptions
- ✅ Étapes à suivre numérotées
- ✅ Commandes utiles pour vérifier les données

### 4. Script d'export : `export_kibana_dashboard.sh`
Script automatique pour exporter le dashboard Kibana :
- Export par recherche (type "E-Commerce")
- Export complet avec dépendances
- Filtrage des objets pertinents
- Liste des dashboards disponibles
- Instructions d'import pour réutilisation

---

## 📊 Configuration Kibana

### Index Pattern
- **Nom** : `Logs Pattern`
- **Pattern** : `logstash-*`
- **Champ temporel** : `@timestamp`

### Visualisation 1 : Transactions par Heure
- **Type** : Area Chart / Line Chart
- **Configuration** :
  - **Axe Y** : Count (nombre de transactions)
  - **Axe X** : Date Histogram
    - Field : `@timestamp`
    - Interval : 1 heure
  - **Titre** : "Transactions par Heure"
- **Nom de sauvegarde** : `E-Commerce - Transactions par Heure`
- **Objectif** : Visualiser le volume de transactions dans le temps

### Visualisation 2 : Top 10 des Erreurs
- **Type** : Horizontal Bar Chart
- **Filtre** : `status.keyword` is `failed`
- **Configuration** :
  - **Axe Y** : Count (nombre d'erreurs)
  - **Axe X** : Terms
    - Field : `error_message.keyword`
    - Order : Descending
    - Size : 10
  - **Titre** : "Top 10 des Erreurs de Paiement"
- **Nom de sauvegarde** : `E-Commerce - Top 10 Erreurs`
- **Objectif** : Identifier les erreurs les plus fréquentes pour prioriser les corrections

### Visualisation 3 : Répartition par Type de Paiement
- **Type** : Pie Chart (Donut)
- **Configuration** :
  - **Slice size** : Count (nombre de transactions)
  - **Split slices** : Terms
    - Field : `payment_type.keyword`
    - Order : Descending
  - **Options** : Donut chart, afficher labels et valeurs
  - **Titre** : "Répartition par Type de Paiement"
- **Nom de sauvegarde** : `E-Commerce - Répartition Paiements`
- **Objectif** : Comprendre les préférences de paiement des clients

### Dashboard : E-Commerce Logs Dashboard
- **Contenu** :
  - 3 visualisations organisées :
    - En haut (large) : Courbe des transactions par heure
    - En bas gauche : Bar chart des erreurs
    - En bas droite : Pie chart des paiements
  - Filtres interactifs (optionnels) :
    - Par pays (`country.keyword`)
    - Par statut (`status.keyword`)
    - Par catégorie (`product_category.keyword`)
- **Export** : Fichier `.ndjson` contenant le dashboard et toutes ses dépendances

---

## 🚀 Procédure d'Utilisation

### Étape 1 : Vérification des services
```bash
./kibana_setup.sh
```
Ce script vérifie que tous les services sont prêts et affiche les étapes à suivre.

### Étape 2 : Upload des données
1. Ouvrir http://localhost:8000/upload
2. Glisser-déposer ou sélectionner `ecommerce_transactions.csv`
3. Attendre la confirmation de succès
4. Vérifier l'indexation :
```bash
curl -s 'http://localhost:9200/logstash-*/_count' | jq
```

### Étape 3 : Configuration Kibana (manuelle)
1. **Créer l'index pattern** :
   - http://localhost:5601/app/management/kibana/dataViews
   - Create data view : `logstash-*` avec champ `@timestamp`

2. **Créer les visualisations** :
   - http://localhost:5601/app/visualize
   - Créer les 3 visualisations selon les spécifications ci-dessus

3. **Créer le dashboard** :
   - http://localhost:5601/app/dashboards
   - Create dashboard
   - Add from library : sélectionner les 3 visualisations
   - Organiser et sauvegarder : "E-Commerce Logs Dashboard"

### Étape 4 : Export du dashboard
**Option A** : Via l'interface Kibana
- Menu ☰ → Stack Management → Saved Objects
- Rechercher "E-Commerce"
- Sélectionner dashboard + visualisations
- Export

**Option B** : Via script automatique
```bash
./export_kibana_dashboard.sh
```

---

## 🔍 Commandes de Vérification

### Vérifier les données indexées
```bash
# Compter tous les documents
curl -s 'http://localhost:9200/logstash-*/_count' | jq

# Compter les succès
curl -s -X POST 'http://localhost:9200/logstash-*/_count' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match":{"status":"success"}}}' | jq

# Compter les échecs
curl -s -X POST 'http://localhost:9200/logstash-*/_count' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match":{"status":"failed"}}}' | jq
```

### Agrégations Elasticsearch

**Top 10 des erreurs** :
```bash
curl -s -X POST 'http://localhost:9200/logstash-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "query": { "match": { "status": "failed" } },
    "aggs": {
      "error_types": {
        "terms": { "field": "error_message.keyword", "size": 10 }
      }
    }
  }' | jq '.aggregations'
```

**Répartition par type de paiement** :
```bash
curl -s -X POST 'http://localhost:9200/logstash-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "payment_types": {
        "terms": { "field": "payment_type.keyword", "size": 10 }
      }
    }
  }' | jq '.aggregations'
```

**Transactions par heure** :
```bash
curl -s -X POST 'http://localhost:9200/logstash-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 0,
    "aggs": {
      "transactions_over_time": {
        "date_histogram": {
          "field": "@timestamp",
          "fixed_interval": "1h"
        }
      }
    }
  }' | jq '.aggregations'
```

---

## ✅ Checklist de Validation

### Préparation
- [x] Fichier `ecommerce_transactions.csv` créé (100 transactions)
- [x] Guide complet `KIBANA_SETUP_GUIDE.md` rédigé
- [x] Script `kibana_setup.sh` créé et testé
- [x] Script `export_kibana_dashboard.sh` créé

### Services
- [ ] Elasticsearch accessible (http://localhost:9200)
- [ ] Kibana accessible (http://localhost:5601)
- [ ] Flask upload accessible (http://localhost:8000/upload)

### Upload et indexation
- [ ] Fichier CSV uploadé via l'interface web
- [ ] 100 documents indexés dans Elasticsearch
- [ ] Données visibles avec `curl localhost:9200/logstash-*/_count`

### Configuration Kibana
- [ ] Index pattern `logstash-*` créé avec champ `@timestamp`
- [ ] Données visibles dans Discover
- [ ] Visualisation 1 créée : "E-Commerce - Transactions par Heure"
- [ ] Visualisation 2 créée : "E-Commerce - Top 10 Erreurs"
- [ ] Visualisation 3 créée : "E-Commerce - Répartition Paiements"

### Dashboard
- [ ] Dashboard "E-Commerce Logs Dashboard" créé
- [ ] 3 visualisations ajoutées au dashboard
- [ ] Layout organisé correctement
- [ ] Dashboard sauvegardé

### Export
- [ ] Dashboard exporté (fichier .ndjson)
- [ ] Fichier renommé et sauvegardé dans le projet
- [ ] Export testé (import sur un autre Kibana ou même instance)

### Documentation
- [ ] Screenshots capturés (optionnel)
- [ ] README.md mis à jour avec section Prompt 8
- [ ] Ce fichier PROMPT8_SUMMARY.md créé

---

## 📈 Résultats Attendus

Après avoir suivi toutes les étapes, vous aurez :

1. **Un dashboard Kibana fonctionnel** affichant :
   - La courbe de volume de transactions sur la journée
   - Les 10 types d'erreurs les plus fréquents
   - La distribution des moyens de paiement utilisés

2. **Des données indexées** :
   - 100 transactions e-commerce
   - Période : 8h00 à 17h45 le 25 novembre 2025
   - Champs structurés et interrogeables

3. **Un fichier d'export réutilisable** :
   - Format `.ndjson`
   - Contient le dashboard et toutes ses dépendances
   - Importable sur d'autres instances Kibana

4. **Documentation complète** :
   - Guide pas à pas (KIBANA_SETUP_GUIDE.md)
   - Scripts automatiques pour vérification et export
   - README mis à jour

---

## 🎓 Compétences Démontrées

- ✅ Création de données de test réalistes (CSV)
- ✅ Upload de fichiers via interface web
- ✅ Configuration d'index patterns Kibana
- ✅ Création de visualisations Kibana (Line, Bar, Pie charts)
- ✅ Utilisation d'agrégations Elasticsearch (Count, Terms, Date Histogram)
- ✅ Filtrage de données (status=failed)
- ✅ Assemblage de dashboards
- ✅ Export/Import d'objets Kibana
- ✅ Scripting Bash pour automatisation
- ✅ Documentation technique complète

---

## 🔗 Liens Rapides

- **Kibana Home** : http://localhost:5601
- **Kibana Discover** : http://localhost:5601/app/discover
- **Kibana Visualize** : http://localhost:5601/app/visualize
- **Kibana Dashboards** : http://localhost:5601/app/dashboards
- **Kibana Stack Management** : http://localhost:5601/app/management
- **Upload Interface** : http://localhost:8000/upload
- **Elasticsearch API** : http://localhost:9200

---

## 📝 Notes

- Les visualisations utilisent des champs `.keyword` pour les agrégations (important pour les champs texte)
- Le champ `@timestamp` est automatiquement créé par Logstash à partir du champ `timestamp` du CSV
- Les filtres Kibana sont interactifs et permettent d'explorer les données dynamiquement
- L'export `.ndjson` peut être versionné dans Git pour partager les dashboards

---

**Prompt 8 complété avec succès** ✅

Créé le 25 novembre 2025
