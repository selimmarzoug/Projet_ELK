#!/bin/bash

# Script d'import automatique du dashboard E-Commerce dans Kibana
# Ce script crée l'index pattern et importe toutes les visualisations + le dashboard

set -e

KIBANA_URL="http://localhost:5601"
DASHBOARD_FILE="kibana_ecommerce_dashboard_ready.ndjson"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   🚀 IMPORT AUTOMATIQUE DU DASHBOARD E-COMMERCE DANS KIBANA   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier que Kibana est accessible
echo "🔍 Vérification de Kibana..."
if ! curl -s -o /dev/null -w "%{http_code}" "$KIBANA_URL/api/status" | grep -q "200"; then
    echo "❌ Kibana n'est pas accessible à $KIBANA_URL"
    echo "   Vérifiez que le conteneur Kibana est démarré"
    exit 1
fi
echo "✅ Kibana est accessible"
echo ""

# Vérifier les données dans Elasticsearch
echo "📊 Vérification des données dans Elasticsearch..."
DOC_COUNT=$(curl -s "http://localhost:9200/logstash-*/_count" | grep -o '"count":[0-9]*' | cut -d':' -f2)

if [ -z "$DOC_COUNT" ] || [ "$DOC_COUNT" -eq 0 ]; then
    echo "⚠️  ATTENTION : Aucune donnée trouvée dans Elasticsearch !"
    echo "   Uploadez d'abord le fichier ecommerce_transactions.csv"
    echo "   via http://localhost:8000/upload"
    echo ""
    read -p "Voulez-vous continuer quand même ? (o/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        exit 1
    fi
else
    echo "✅ $DOC_COUNT documents trouvés dans Elasticsearch"
fi
echo ""

# Importer le dashboard
echo "📦 Import du dashboard et des visualisations..."
if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "❌ Fichier $DASHBOARD_FILE introuvable"
    exit 1
fi

RESPONSE=$(curl -s -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
    -H "kbn-xsrf: true" \
    --form file=@"$DASHBOARD_FILE" 2>&1)

# Vérifier le résultat
if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✅ Import réussi !"
    echo ""
    
    # Extraire les objets importés
    SUCCESS_COUNT=$(echo "$RESPONSE" | grep -o '"successCount":[0-9]*' | cut -d':' -f2)
    echo "📊 $SUCCESS_COUNT objets importés :"
    echo "   • 1 Index Pattern (logstash-*)"
    echo "   • 3 Visualisations"
    echo "     - E-Commerce - Transactions par Heure"
    echo "     - E-Commerce - Top 10 Erreurs"
    echo "     - E-Commerce - Répartition Paiements"
    echo "   • 1 Dashboard (E-Commerce Logs Dashboard)"
    echo ""
    
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ IMPORT TERMINÉ !                         ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Accédez à votre dashboard ici :"
    echo "   http://localhost:5601/app/dashboards#/view/ecommerce-dashboard"
    echo ""
    echo "📋 Ou depuis Kibana :"
    echo "   Menu ☰ → Dashboard → E-Commerce Logs Dashboard"
    echo ""
    
else
    echo "⚠️  Import avec avertissements ou erreurs :"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "💡 Si l'import a échoué, vérifiez que :"
    echo "   1. Kibana est complètement démarré"
    echo "   2. Elasticsearch contient des données"
    echo "   3. L'index logstash-* existe"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 LIENS UTILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "• Dashboard     : http://localhost:5601/app/dashboards#/view/ecommerce-dashboard"
echo "• Discover      : http://localhost:5601/app/discover"
echo "• Visualisations: http://localhost:5601/app/visualize"
echo "• Data Views    : http://localhost:5601/app/management/kibana/dataViews"
echo ""
