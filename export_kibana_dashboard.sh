#!/bin/bash

# Script d'export du Dashboard Kibana E-Commerce
# Usage: ./export_kibana_dashboard.sh

set -e

KIBANA_URL="http://localhost:5601"
OUTPUT_FILE="kibana_ecommerce_dashboard.ndjson"

echo "🔍 Export du Dashboard E-Commerce depuis Kibana..."
echo "---------------------------------------------------"

# Fonction pour attendre que Kibana soit prêt
wait_for_kibana() {
    echo "⏳ Vérification de la disponibilité de Kibana..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$KIBANA_URL/api/status" | grep -q "200"; then
            echo "✅ Kibana est prêt"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "   Tentative $attempt/$max_attempts..."
        sleep 2
    done
    
    echo "❌ Kibana n'est pas accessible après $max_attempts tentatives"
    return 1
}

# Vérifier que Kibana est accessible
if ! wait_for_kibana; then
    exit 1
fi

echo ""
echo "📦 Export des objets Kibana..."

# Méthode 1 : Export par recherche (dashboard E-Commerce)
echo ""
echo "1️⃣  Export du dashboard E-Commerce..."
curl -X POST "$KIBANA_URL/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dashboard",
    "search": "E-Commerce"
  }' > "$OUTPUT_FILE" 2>/dev/null

if [ -s "$OUTPUT_FILE" ]; then
    SIZE=$(wc -l < "$OUTPUT_FILE")
    echo "✅ Dashboard exporté : $OUTPUT_FILE ($SIZE objets)"
else
    echo "⚠️  Aucun dashboard E-Commerce trouvé"
    echo "   Vous devez d'abord créer le dashboard dans Kibana"
    rm -f "$OUTPUT_FILE"
fi

echo ""
echo "2️⃣  Tentative d'export complet avec dépendances..."

# Méthode 2 : Export avec toutes les dépendances
COMPLETE_FILE="kibana_ecommerce_complete.ndjson"

curl -X POST "$KIBANA_URL/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "objects": [
      {"type": "dashboard", "id": "*"}
    ],
    "includeReferencesDeep": true
  }' > "$COMPLETE_FILE" 2>/dev/null

if [ -s "$COMPLETE_FILE" ]; then
    SIZE=$(wc -l < "$COMPLETE_FILE")
    echo "✅ Export complet créé : $COMPLETE_FILE ($SIZE objets)"
    
    # Filtrer uniquement les objets E-Commerce
    grep -i "e-commerce\|ecommerce" "$COMPLETE_FILE" > temp_ecommerce.ndjson || true
    if [ -s temp_ecommerce.ndjson ]; then
        mv temp_ecommerce.ndjson "kibana_ecommerce_filtered.ndjson"
        echo "✅ Export filtré : kibana_ecommerce_filtered.ndjson"
    fi
    rm -f temp_ecommerce.ndjson
else
    echo "⚠️  Export complet échoué"
    rm -f "$COMPLETE_FILE"
fi

echo ""
echo "3️⃣  Liste des objets sauvegardés disponibles..."

# Lister tous les dashboards
DASHBOARDS=$(curl -s "$KIBANA_URL/api/saved_objects/_find?type=dashboard&per_page=100" \
  -H "kbn-xsrf: true" 2>/dev/null)

if echo "$DASHBOARDS" | grep -q "E-Commerce"; then
    echo "✅ Dashboard(s) E-Commerce trouvé(s) :"
    echo "$DASHBOARDS" | jq -r '.saved_objects[] | select(.attributes.title | contains("E-Commerce")) | "   - \(.attributes.title) (ID: \(.id))"' 2>/dev/null || echo "   (Impossible de parser, utilisez jq)"
else
    echo "⚠️  Aucun dashboard E-Commerce trouvé dans Kibana"
    echo ""
    echo "📝 Pour créer le dashboard :"
    echo "   1. Ouvrez Kibana : $KIBANA_URL"
    echo "   2. Suivez le guide : KIBANA_SETUP_GUIDE.md"
    echo "   3. Relancez ce script après avoir créé le dashboard"
fi

echo ""
echo "---------------------------------------------------"
echo "✅ Script terminé"

if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "📄 Fichiers exportés :"
    ls -lh kibana_ecommerce*.ndjson 2>/dev/null || echo "   Aucun fichier exporté"
    echo ""
    echo "💡 Pour importer sur un autre Kibana :"
    echo "   1. Allez dans Stack Management → Saved Objects"
    echo "   2. Cliquez sur Import"
    echo "   3. Sélectionnez : $OUTPUT_FILE"
fi
