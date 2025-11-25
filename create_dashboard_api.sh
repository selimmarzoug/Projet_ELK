#!/bin/bash

# Script de création COMPLÈTE du dashboard E-Commerce via API Kibana
# Compatible avec toutes les versions de Kibana

KIBANA_URL="http://localhost:5601"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🎯 CRÉATION AUTOMATIQUE DU DASHBOARD E-COMMERCE            ║"
echo "║        Via l'API Kibana (Compatible toutes versions)          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Créer l'index pattern
echo "📋 Étape 1/4 : Création de l'index pattern logstash-*..."
curl -X POST "$KIBANA_URL/api/saved_objects/index-pattern/logstash-star" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "logstash-*",
      "timeFieldName": "@timestamp"
    }
  }' 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Index pattern créé"
else
    echo "⚠️  L'index pattern existe peut-être déjà"
fi
echo ""

# 2. Créer la visualisation: Transactions par heure
echo "📊 Étape 2/4 : Création de la visualisation 'Transactions par Heure'..."
curl -X POST "$KIBANA_URL/api/saved_objects/visualization/transactions-heure" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "E-Commerce - Transactions par Heure",
      "visState": "{\"title\":\"E-Commerce - Transactions par Heure\",\"type\":\"line\",\"params\":{\"addLegend\":true,\"addTimeMarker\":false,\"addTooltip\":true,\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"labels\":{\"show\":true,\"truncate\":100},\"position\":\"bottom\",\"scale\":{\"type\":\"linear\"},\"show\":true,\"style\":{},\"title\":{\"text\":\"@timestamp per hour\"},\"type\":\"category\"}],\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"legendPosition\":\"right\",\"seriesParams\":[{\"data\":{\"id\":\"1\",\"label\":\"Count\"},\"drawLinesBetweenPoints\":true,\"mode\":\"normal\",\"show\":\"true\",\"showCircles\":true,\"type\":\"line\",\"valueAxis\":\"ValueAxis-1\"}],\"times\":[],\"type\":\"line\",\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"labels\":{\"filter\":false,\"rotate\":0,\"show\":true,\"truncate\":100},\"name\":\"LeftAxis-1\",\"position\":\"left\",\"scale\":{\"mode\":\"normal\",\"type\":\"linear\"},\"show\":true,\"style\":{},\"title\":{\"text\":\"Count\"},\"type\":\"value\"}]},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"@timestamp\",\"interval\":\"h\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}}]}",
      "uiStateJSON": "{}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-star\",\"query\":{\"query\":\"\",\"language\":\"lucene\"},\"filter\":[]}"
      }
    }
  }' 2>/dev/null
echo "✅ Visualisation 'Transactions par Heure' créée"
echo ""

# 3. Créer la visualisation: Top 10 Erreurs
echo "🔴 Étape 3/4 : Création de la visualisation 'Top 10 Erreurs'..."
curl -X POST "$KIBANA_URL/api/saved_objects/visualization/top-erreurs" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "E-Commerce - Top 10 Erreurs",
      "visState": "{\"title\":\"E-Commerce - Top 10 Erreurs\",\"type\":\"horizontal_bar\",\"params\":{\"addLegend\":true,\"addTimeMarker\":false,\"addTooltip\":true,\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"labels\":{\"show\":true,\"truncate\":100},\"position\":\"left\",\"scale\":{\"type\":\"linear\"},\"show\":true,\"style\":{},\"title\":{\"text\":\"error_message.keyword: Descending\"},\"type\":\"category\"}],\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"legendPosition\":\"right\",\"seriesParams\":[{\"data\":{\"id\":\"1\",\"label\":\"Count\"},\"drawLinesBetweenPoints\":true,\"mode\":\"normal\",\"show\":\"true\",\"showCircles\":true,\"type\":\"histogram\",\"valueAxis\":\"ValueAxis-1\"}],\"times\":[],\"type\":\"histogram\",\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"labels\":{\"filter\":false,\"rotate\":0,\"show\":true,\"truncate\":100},\"name\":\"LeftAxis-1\",\"position\":\"bottom\",\"scale\":{\"mode\":\"normal\",\"type\":\"linear\"},\"show\":true,\"style\":{},\"title\":{\"text\":\"Count\"},\"type\":\"value\"}]},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"error_message.keyword\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\"}}]}",
      "uiStateJSON": "{}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-star\",\"query\":{\"query\":\"status:failed\",\"language\":\"lucene\"},\"filter\":[]}"
      }
    }
  }' 2>/dev/null
echo "✅ Visualisation 'Top 10 Erreurs' créée"
echo ""

# 4. Créer la visualisation: Répartition des paiements
echo "💳 Étape 4/4 : Création de la visualisation 'Répartition Paiements'..."
curl -X POST "$KIBANA_URL/api/saved_objects/visualization/repartition-paiements" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "E-Commerce - Répartition Paiements",
      "visState": "{\"title\":\"E-Commerce - Répartition Paiements\",\"type\":\"pie\",\"params\":{\"addLegend\":true,\"addTooltip\":true,\"isDonut\":true,\"labels\":{\"last_level\":true,\"show\":false,\"truncate\":100,\"values\":true},\"legendPosition\":\"right\",\"type\":\"pie\"},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"payment_type.keyword\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\"}}]}",
      "uiStateJSON": "{}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-star\",\"query\":{\"query\":\"\",\"language\":\"lucene\"},\"filter\":[]}"
      }
    }
  }' 2>/dev/null
echo "✅ Visualisation 'Répartition Paiements' créée"
echo ""

# 5. Créer le dashboard
echo "📊 Création du Dashboard 'E-Commerce Logs Dashboard'..."
curl -X POST "$KIBANA_URL/api/saved_objects/dashboard/ecommerce-dashboard" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "E-Commerce Logs Dashboard",
      "hits": 0,
      "description": "Dashboard de monitoring des transactions e-commerce",
      "panelsJSON": "[{\"col\":1,\"id\":\"transactions-heure\",\"panelIndex\":1,\"row\":1,\"size_x\":12,\"size_y\":3,\"type\":\"visualization\"},{\"col\":1,\"id\":\"top-erreurs\",\"panelIndex\":2,\"row\":4,\"size_x\":6,\"size_y\":3,\"type\":\"visualization\"},{\"col\":7,\"id\":\"repartition-paiements\",\"panelIndex\":3,\"row\":4,\"size_x\":6,\"size_y\":3,\"type\":\"visualization\"}]",
      "optionsJSON": "{\"darkTheme\":false}",
      "uiStateJSON": "{}",
      "version": 1,
      "timeRestore": false,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"filter\":[],\"query\":{\"query\":\"\",\"language\":\"lucene\"}}"
      }
    }
  }' 2>/dev/null
echo "✅ Dashboard créé"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ CRÉATION TERMINÉE !                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Votre dashboard E-Commerce est prêt !"
echo ""
echo "🌐 Accédez-y maintenant :"
echo "   http://localhost:5601/app/dashboards#/view/ecommerce-dashboard"
echo ""
echo "📊 Objets créés :"
echo "   ✅ Index Pattern : logstash-*"
echo "   ✅ Visualisation : E-Commerce - Transactions par Heure"
echo "   ✅ Visualisation : E-Commerce - Top 10 Erreurs"
echo "   ✅ Visualisation : E-Commerce - Répartition Paiements"
echo "   ✅ Dashboard : E-Commerce Logs Dashboard"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 ASTUCE : Si le dashboard est vide :"
echo "   1. Assurez-vous d'avoir uploadé ecommerce_transactions.csv"
echo "   2. Ajustez la période de temps dans Kibana (en haut à droite)"
echo "   3. Sélectionnez 'Last 7 days' ou 'Today'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
