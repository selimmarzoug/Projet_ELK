#!/bin/bash

# Script de vérification et accès rapides pour le Prompt 8
# Configuration Kibana Dashboard E-Commerce

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     PROMPT 8 - Configuration Kibana Dashboard              ║"
echo "║     E-Commerce Logs Dashboard Setup                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction pour vérifier un service
check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}✅ $name${NC} - Disponible"
        return 0
    else
        echo -e "${RED}❌ $name${NC} - Non disponible"
        return 1
    fi
}

echo -e "${CYAN}📊 STATUT DES SERVICES${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier les services
check_service "Elasticsearch" "http://localhost:9200"
check_service "Kibana       " "http://localhost:5601/api/status"
check_service "Flask Upload " "http://localhost:8000"
check_service "Mongo Express" "http://localhost:8081"

echo ""
echo -e "${CYAN}📁 FICHIER DE DONNÉES${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "ecommerce_transactions.csv" ]; then
    LINES=$(wc -l < ecommerce_transactions.csv)
    SIZE=$(du -h ecommerce_transactions.csv | cut -f1)
    echo -e "${GREEN}✅ ecommerce_transactions.csv${NC}"
    echo "   📊 Lignes: $((LINES - 1)) transactions (+ 1 ligne d'en-tête)"
    echo "   💾 Taille: $SIZE"
else
    echo -e "${RED}❌ ecommerce_transactions.csv non trouvé${NC}"
fi

echo ""
echo -e "${CYAN}🔍 DONNÉES DANS ELASTICSEARCH${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier les données
DOC_COUNT=$(curl -s "http://localhost:9200/logstash-*/_count" 2>/dev/null | grep -o '"count":[0-9]*' | cut -d':' -f2)

if [ -n "$DOC_COUNT" ] && [ "$DOC_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ $DOC_COUNT documents indexés${NC}"
    
    # Compter les succès et échecs
    SUCCESS_COUNT=$(curl -s -X POST "http://localhost:9200/logstash-*/_count" \
        -H 'Content-Type: application/json' \
        -d '{"query":{"match":{"status":"success"}}}' 2>/dev/null | grep -o '"count":[0-9]*' | cut -d':' -f2)
    
    FAILED_COUNT=$(curl -s -X POST "http://localhost:9200/logstash-*/_count" \
        -H 'Content-Type: application/json' \
        -d '{"query":{"match":{"status":"failed"}}}' 2>/dev/null | grep -o '"count":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$SUCCESS_COUNT" ]; then
        echo "   💚 Transactions réussies: $SUCCESS_COUNT"
    fi
    if [ -n "$FAILED_COUNT" ]; then
        echo "   ❌ Transactions échouées: $FAILED_COUNT"
    fi
else
    echo -e "${YELLOW}⚠️  Aucune donnée trouvée${NC}"
    echo "   📤 Uploadez d'abord le fichier CSV via l'interface web"
fi

echo ""
echo -e "${CYAN}🔗 LIENS D'ACCÈS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}1. Upload Interface:${NC}"
echo "   🌐 http://localhost:8000/upload"
echo ""
echo -e "${BLUE}2. Kibana - Accueil:${NC}"
echo "   🌐 http://localhost:5601"
echo ""
echo -e "${BLUE}3. Kibana - Discover (pour voir les données):${NC}"
echo "   🌐 http://localhost:5601/app/discover"
echo ""
echo -e "${BLUE}4. Kibana - Stack Management (pour créer l'index pattern):${NC}"
echo "   🌐 http://localhost:5601/app/management/kibana/dataViews"
echo ""
echo -e "${BLUE}5. Kibana - Visualize (pour créer les visualisations):${NC}"
echo "   🌐 http://localhost:5601/app/visualize"
echo ""
echo -e "${BLUE}6. Kibana - Dashboards (pour créer le dashboard):${NC}"
echo "   🌐 http://localhost:5601/app/dashboards"
echo ""

echo -e "${CYAN}📋 ÉTAPES À SUIVRE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}ÉTAPE 1: Upload des données${NC}"
echo "  1. Ouvrez: http://localhost:8000/upload"
echo "  2. Uploadez le fichier: ecommerce_transactions.csv"
echo "  3. Attendez la confirmation de succès"
echo ""
echo -e "${YELLOW}ÉTAPE 2: Créer l'index pattern${NC}"
echo "  1. Ouvrez Kibana: http://localhost:5601"
echo "  2. Menu ☰ → Management → Stack Management → Data Views"
echo "  3. Create data view:"
echo "     - Name: Logs Pattern"
echo "     - Index pattern: logstash-*"
echo "     - Timestamp field: @timestamp"
echo ""
echo -e "${YELLOW}ÉTAPE 3: Créer les visualisations${NC}"
echo "  1. Menu ☰ → Visualize Library → Create visualization"
echo "  2. Créez ces 3 visualisations:"
echo "     📊 Transactions par Heure (Line/Area chart)"
echo "     📊 Top 10 Erreurs (Horizontal Bar)"
echo "     📊 Répartition Paiements (Pie/Donut)"
echo ""
echo -e "${YELLOW}ÉTAPE 4: Créer le dashboard${NC}"
echo "  1. Menu ☰ → Dashboard → Create dashboard"
echo "  2. Add from library → Sélectionnez vos 3 visualisations"
echo "  3. Organisez le layout"
echo "  4. Save: 'E-Commerce Logs Dashboard'"
echo ""
echo -e "${YELLOW}ÉTAPE 5: Exporter le dashboard${NC}"
echo "  1. Option A (Interface):"
echo "     Menu ☰ → Stack Management → Saved Objects → Export"
echo "  2. Option B (Script automatique):"
echo "     ./export_kibana_dashboard.sh"
echo ""

echo -e "${CYAN}📚 DOCUMENTATION${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📖 Guide complet: cat KIBANA_SETUP_GUIDE.md"
echo "  📖 Ou ouvrez: KIBANA_SETUP_GUIDE.md dans votre éditeur"
echo ""

echo -e "${CYAN}🛠️  COMMANDES UTILES${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  # Voir le guide complet"
echo "  cat KIBANA_SETUP_GUIDE.md"
echo ""
echo "  # Vérifier les données indexées"
echo "  curl -s 'http://localhost:9200/logstash-*/_count' | jq"
echo ""
echo "  # Exporter le dashboard (après création)"
echo "  ./export_kibana_dashboard.sh"
echo ""
echo "  # Rechercher les transactions échouées"
echo "  curl -s -X POST 'http://localhost:9200/logstash-*/_search' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\":{\"match\":{\"status\":\"failed\"}}}' | jq"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Bon courage pour la configuration Kibana! 🚀             ║"
echo "╚════════════════════════════════════════════════════════════╝"
