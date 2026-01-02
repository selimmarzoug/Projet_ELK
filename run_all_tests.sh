#!/bin/bash

# Script pour exécuter tous les tests et générer les rapports
# Usage: ./run_all_tests.sh

set -e  # Exit on error

echo "======================================================================"
echo "🧪 ProjetELK - Suite de Tests Complète"
echo "======================================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Linting
echo -e "${YELLOW}📝 Étape 1/4 : Linting du code...${NC}"
echo "----------------------------------------------------------------------"

if command -v flake8 &> /dev/null; then
    echo "▶️ Flake8..."
    flake8 webapp/ --count --select=E9,F63,F7,F82 --show-source --statistics || echo "⚠️ Warnings detected"
else
    echo "⚠️ flake8 not installed, skipping"
fi

echo ""

# 2. Tests unitaires
echo -e "${YELLOW}🧪 Étape 2/4 : Tests unitaires...${NC}"
echo "----------------------------------------------------------------------"
python3 -m pytest tests/ -m unit -v --tb=short || true
echo ""

# 3. Tests d'intégration (si services disponibles)
echo -e "${YELLOW}🔗 Étape 3/4 : Tests d'intégration...${NC}"
echo "----------------------------------------------------------------------"
if docker ps | grep -q elasticsearch; then
    echo "✅ Services Docker détectés"
    python3 -m pytest tests/ -m integration -v --tb=short || true
else
    echo "⚠️ Services Docker non démarrés, tests d'intégration ignorés"
    echo "💡 Démarrez les services avec: docker-compose up -d"
fi
echo ""

# 4. Coverage complet
echo -e "${YELLOW}📊 Étape 4/4 : Coverage Analysis...${NC}"
echo "----------------------------------------------------------------------"
python3 -m pytest tests/ -v --cov=webapp --cov-report=term-missing --cov-report=html
echo ""

# Résumé
echo "======================================================================"
echo -e "${GREEN}✅ Suite de tests terminée${NC}"
echo "======================================================================"
echo ""
echo "📊 Rapports générés :"
echo "  - Coverage HTML : htmlcov/index.html"
echo "  - Coverage XML  : coverage.xml"
echo ""
echo "🌐 Voir le rapport HTML :"
echo "  xdg-open htmlcov/index.html  # Linux"
echo "  open htmlcov/index.html      # macOS"
echo ""
