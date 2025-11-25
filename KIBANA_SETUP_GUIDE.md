# Configuration Kibana - Guide Complet

## 📊 Prompt 8 — Configuration Kibana pour E-Commerce

Ce guide vous accompagne pour configurer Kibana avec un index pattern et créer un dashboard e-commerce complet.

---

## Étape 1 : Upload des Données E-Commerce 📤

### 1.1 Accéder à l'interface d'upload
```
http://localhost:8000/upload
```

### 1.2 Uploader le fichier
1. Ouvrez votre navigateur à `http://localhost:8000/upload`
2. Glissez-déposez le fichier `ecommerce_transactions.csv` ou cliquez sur "Browse Files"
3. Vérifiez la prévisualisation des données
4. Cliquez sur "Upload File"
5. Attendez la confirmation "File uploaded successfully!"

**Fichier créé** : `/home/selim/Bureau/ProjetELK/ecommerce_transactions.csv`
- 100 transactions
- Période : 25 novembre 2025, 8h00-17h45
- Statuts : success (75%) et failed (25%)
- Types de paiement : credit_card, paypal, debit_card, bank_transfer

---

## Étape 2 : Créer l'Index Pattern dans Kibana 🔍

### 2.1 Accéder à Kibana
```
http://localhost:5601
```

### 2.2 Naviguer vers Stack Management
1. Ouvrez Kibana : `http://localhost:5601`
2. Cliquez sur le menu hamburger ☰ (en haut à gauche)
3. Allez dans **Management** → **Stack Management**
4. Dans la section **Kibana**, cliquez sur **Data Views** (ou **Index Patterns**)

### 2.3 Créer le Data View/Index Pattern
1. Cliquez sur **"Create data view"** (ou "Create index pattern")
2. Remplissez les champs :
   - **Name** : `Logs Pattern`
   - **Index pattern** : `logstash-*`
   - **Timestamp field** : `@timestamp`
3. Cliquez sur **"Create data view"** ou **"Create index pattern"**

### 2.4 Vérification
- Allez dans **Discover** (menu principal)
- Sélectionnez votre data view `logstash-*`
- Vous devriez voir vos 100 transactions e-commerce

---

## Étape 3 : Créer les Visualisations 📈

### Visualisation 1 : Courbe des Transactions par Heure 📊

**Type** : Line Chart (Area)

1. **Navigation** : Menu ☰ → **Visualize Library** → **Create visualization**
2. **Sélectionner le type** : Cliquez sur **"Area"** ou **"Line"**
3. **Choisir la source** : Sélectionnez `logstash-*`
4. **Configuration** :

   **Axe Y (Metrics)** :
   - Aggregation : `Count`
   - Custom label : `Nombre de transactions`

   **Axe X (Buckets)** :
   - Aggregation : `Date Histogram`
   - Field : `@timestamp`
   - Minimum interval : `1h` (1 heure)
   - Custom label : `Heure`

5. **Options supplémentaires** :
   - Dans "Metrics & axes" → Cochez "Show values on chart"
   - Dans "Panel settings" → Ajoutez un titre : `Transactions par Heure`

6. **Sauvegarder** :
   - Cliquez sur **"Save"** en haut à droite
   - Nom : `E-Commerce - Transactions par Heure`
   - Cliquez sur **"Save and return"**

---

### Visualisation 2 : Top 10 des Erreurs 🚫

**Type** : Horizontal Bar Chart

1. **Navigation** : Menu ☰ → **Visualize Library** → **Create visualization**
2. **Sélectionner le type** : Cliquez sur **"Bar horizontal"** ou **"Horizontal Bar"**
3. **Choisir la source** : Sélectionnez `logstash-*`
4. **Ajouter un filtre** :
   - Cliquez sur **"Add filter"**
   - Field : `status.keyword`
   - Operator : `is`
   - Value : `failed`
   - Cliquez sur **"Save"**

5. **Configuration** :

   **Axe Y (Metrics)** :
   - Aggregation : `Count`
   - Custom label : `Nombre d'erreurs`

   **Axe X (Buckets)** :
   - Aggregation : `Terms`
   - Field : `error_message.keyword`
   - Order by : `Metric: Count`
   - Order : `Descending`
   - Size : `10`
   - Custom label : `Type d'erreur`

6. **Options supplémentaires** :
   - Dans "Metrics & axes" → Cochez "Show values on chart"
   - Panel settings → Titre : `Top 10 des Erreurs de Paiement`

7. **Sauvegarder** :
   - Nom : `E-Commerce - Top 10 Erreurs`
   - Cliquez sur **"Save and return"**

---

### Visualisation 3 : Répartition par Type de Paiement 💳

**Type** : Pie Chart (Donut)

1. **Navigation** : Menu ☰ → **Visualize Library** → **Create visualization**
2. **Sélectionner le type** : Cliquez sur **"Pie"** ou **"Donut"**
3. **Choisir la source** : Sélectionnez `logstash-*`
4. **Configuration** :

   **Slice size (Metrics)** :
   - Aggregation : `Count`
   - Custom label : `Nombre de transactions`

   **Split slices (Buckets)** :
   - Aggregation : `Terms`
   - Field : `payment_type.keyword`
   - Order by : `Metric: Count`
   - Order : `Descending`
   - Size : `10`
   - Custom label : `Type de paiement`

5. **Options supplémentaires** :
   - Type : Cochez **"Donut"** pour un graphique moderne
   - Labels : Cochez "Show labels"
   - Values : Cochez "Show values"
   - Panel settings → Titre : `Répartition par Type de Paiement`

6. **Sauvegarder** :
   - Nom : `E-Commerce - Répartition Paiements`
   - Cliquez sur **"Save and return"**

---

## Étape 4 : Créer le Dashboard 🎯

### 4.1 Créer un nouveau Dashboard
1. **Navigation** : Menu ☰ → **Dashboard** → **Create dashboard**
2. Cliquez sur **"Add from library"**

### 4.2 Ajouter les visualisations
1. Recherchez et sélectionnez vos 3 visualisations :
   - ✅ `E-Commerce - Transactions par Heure`
   - ✅ `E-Commerce - Top 10 Erreurs`
   - ✅ `E-Commerce - Répartition Paiements`
2. Cliquez sur **"Add"**

### 4.3 Organiser le Dashboard
1. **Redimensionner** : Cliquez et faites glisser les coins des panneaux
2. **Déplacer** : Cliquez sur l'en-tête et faites glisser
3. **Layout suggéré** :
   ```
   ┌─────────────────────────────────────────┐
   │  Transactions par Heure (ligne)         │
   │  (Large, en haut)                        │
   └─────────────────────────────────────────┘
   ┌──────────────────────┬──────────────────┐
   │  Top 10 Erreurs      │  Répartition     │
   │  (Barres)            │  Paiements (Pie) │
   │                      │                  │
   └──────────────────────┴──────────────────┘
   ```

### 4.4 Ajouter des filtres et métriques
1. Cliquez sur **"Add panel"** → **"Add filter"**
2. Ajoutez des filtres utiles :
   - Filtre par pays : `country.keyword`
   - Filtre par statut : `status.keyword`
   - Filtre par catégorie : `product_category.keyword`

3. (Optionnel) Ajoutez des métriques supplémentaires :
   - **Add panel** → **"Metrics"**
   - Ajoutez : Total des transactions, Montant moyen, Taux de réussite

### 4.5 Sauvegarder le Dashboard
1. Cliquez sur **"Save"** en haut à droite
2. **Title** : `E-Commerce Logs Dashboard`
3. **Description** : `Dashboard de monitoring des transactions e-commerce avec analyse des erreurs et types de paiement`
4. Cochez **"Store time with dashboard"**
5. Cliquez sur **"Save"**

---

## Étape 5 : Exporter le Dashboard 📦

### 5.1 Méthode 1 : Export via l'interface Kibana

1. **Navigation** : Menu ☰ → **Stack Management** → **Saved Objects**
2. **Rechercher** : Tapez "E-Commerce" dans la barre de recherche
3. **Sélectionner** : Cochez les objets suivants :
   - ✅ Dashboard : `E-Commerce Logs Dashboard`
   - ✅ Visualization : `E-Commerce - Transactions par Heure`
   - ✅ Visualization : `E-Commerce - Top 10 Erreurs`
   - ✅ Visualization : `E-Commerce - Répartition Paiements`
   - ✅ Index Pattern : `logstash-*`
4. Cliquez sur **"Export"** (bouton en haut à droite)
5. Un fichier `export.ndjson` sera téléchargé

### 5.2 Méthode 2 : Export via API (Automatique)

Vous pouvez aussi exporter via une commande curl :

```bash
# Export du dashboard
curl -X POST "localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dashboard",
    "search": "E-Commerce Logs Dashboard"
  }' > ecommerce_dashboard_export.ndjson

# Export complet (dashboard + visualisations)
curl -X POST "localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "objects": [
      {"type": "dashboard", "id": "<DASHBOARD_ID>"}
    ],
    "includeReferencesDeep": true
  }' > ecommerce_complete_export.ndjson
```

### 5.3 Renommer et sauvegarder
```bash
# Déplacer l'export dans le dossier du projet
mv ~/Downloads/export.ndjson /home/selim/Bureau/ProjetELK/kibana_ecommerce_dashboard.ndjson
```

---

## Étape 6 : Import du Dashboard (pour réutilisation) 🔄

Pour importer le dashboard sur un autre Kibana :

1. **Navigation** : Menu ☰ → **Stack Management** → **Saved Objects**
2. Cliquez sur **"Import"**
3. Sélectionnez le fichier `kibana_ecommerce_dashboard.ndjson`
4. **Options d'import** :
   - Cochez "Check for existing objects"
   - Sélectionnez "Create new objects with random IDs" si conflit
5. Cliquez sur **"Import"**
6. Vérifiez que le dashboard apparaît dans **Dashboard**

---

## 📊 Résumé des Objets Créés

### Data View / Index Pattern
- **Nom** : `Logs Pattern`
- **Pattern** : `logstash-*`
- **Champ temporel** : `@timestamp`

### Visualisations
1. **E-Commerce - Transactions par Heure**
   - Type : Area/Line Chart
   - Métrique : Count
   - Intervalle : 1 heure
   - Objectif : Visualiser le volume de transactions dans le temps

2. **E-Commerce - Top 10 Erreurs**
   - Type : Horizontal Bar Chart
   - Métrique : Count sur status=failed
   - Top 10 : error_message.keyword
   - Objectif : Identifier les erreurs les plus fréquentes

3. **E-Commerce - Répartition Paiements**
   - Type : Pie Chart (Donut)
   - Métrique : Count
   - Segmentation : payment_type.keyword
   - Objectif : Voir la distribution des moyens de paiement

### Dashboard
- **Nom** : `E-Commerce Logs Dashboard`
- **Contenu** : 3 visualisations + filtres interactifs
- **Export** : `kibana_ecommerce_dashboard.ndjson`

---

## 🎨 Captures d'Écran Suggérées

Pour documenter votre travail, prenez des captures d'écran de :

1. ✅ Index Pattern créé (liste des champs)
2. ✅ Découverte des données (Discover)
3. ✅ Visualisation 1 : Transactions par heure
4. ✅ Visualisation 2 : Top 10 erreurs
5. ✅ Visualisation 3 : Répartition paiements
6. ✅ Dashboard complet assemblé
7. ✅ Écran d'export des objets

---

## 🚀 Commandes Utiles

### Vérifier les données indexées
```bash
# Compter les documents
curl -s "http://localhost:9200/logstash-*/_count" | jq

# Rechercher les transactions échouées
curl -s -X POST "http://localhost:9200/logstash-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": { "match": { "status": "failed" } },
    "size": 0,
    "aggs": {
      "error_types": {
        "terms": { "field": "error_message.keyword", "size": 10 }
      }
    }
  }' | jq '.aggregations'

# Agrégation par type de paiement
curl -s -X POST "http://localhost:9200/logstash-*/_search" \
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

### Accès rapides
- **Kibana** : http://localhost:5601
- **Discover** : http://localhost:5601/app/discover
- **Visualize** : http://localhost:5601/app/visualize
- **Dashboards** : http://localhost:5601/app/dashboards
- **Upload Interface** : http://localhost:8000/upload

---

## ✅ Checklist de Validation

- [ ] Fichier CSV créé avec 100 transactions
- [ ] Fichier uploadé via l'interface web
- [ ] Données visibles dans Elasticsearch (curl)
- [ ] Index pattern `logstash-*` créé dans Kibana
- [ ] Données visibles dans Kibana Discover
- [ ] Visualisation 1 créée : Transactions par heure
- [ ] Visualisation 2 créée : Top 10 erreurs
- [ ] Visualisation 3 créée : Répartition paiements
- [ ] Dashboard assemblé avec les 3 visualisations
- [ ] Dashboard sauvegardé : "E-Commerce Logs Dashboard"
- [ ] Dashboard exporté en fichier .ndjson
- [ ] Screenshots capturés

---

## 🎓 Notes Pédagogiques

### Types d'agrégations utilisées
- **Count** : Compte le nombre de documents
- **Date Histogram** : Regroupe par intervalles de temps
- **Terms** : Regroupe par valeurs uniques d'un champ

### Champs importants
- `@timestamp` : Horodatage pour la timeline
- `status.keyword` : Statut de transaction (success/failed)
- `payment_type.keyword` : Type de paiement
- `error_message.keyword` : Message d'erreur détaillé
- `amount` : Montant de la transaction

### Bonnes pratiques
- ✅ Utiliser `.keyword` pour les agrégations sur des champs texte
- ✅ Filtrer les données pour des visualisations ciblées
- ✅ Organiser le dashboard de manière logique (timeline en haut)
- ✅ Ajouter des titres clairs et des labels personnalisés
- ✅ Exporter régulièrement pour sauvegarder votre travail

---

**Guide créé le** : 25 novembre 2025  
**Projet** : ELK Stack Monitoring - ProjetELK  
**Auteur** : Configuration Kibana Prompt 8
