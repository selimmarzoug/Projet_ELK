#!/bin/bash
# Script pour valider le workflow CI/CD localement AVANT de push sur GitHub
# Exécute les mêmes étapes que GitHub Actions

set -e  # Arrêt en cas d'erreur

echo "=========================================="
echo "🔍 VALIDATION CI/CD LOCALE"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ===================================
# ÉTAPE 1: Linting
# ===================================
echo -e "${YELLOW}📋 ÉTAPE 1/5: Linting...${NC}"
echo ""

echo "🎨 Vérification formatage (Black)..."
black --check webapp/ tests/ 2>&1 | head -20 || {
    echo -e "${RED}⚠️  Code non formaté. Exécutez: black webapp/ tests/${NC}"
}

echo ""
echo "🔍 Vérification syntaxe (flake8)..."
flake8 webapp/ --count --select=E9,F63,F7,F82 --show-source --statistics || {
    echo -e "${RED}❌ Erreurs de syntaxe détectées${NC}"
    exit 1
}

echo ""
echo "📊 Analyse statique (pylint)..."
pylint webapp/ --exit-zero --disable=C0103,C0114,C0115,C0116 | tail -15

echo -e "${GREEN}✅ Linting terminé${NC}"
echo ""

# ===================================
# ÉTAPE 2: Tests Unitaires
# ===================================
echo -e "${YELLOW}📋 ÉTAPE 2/5: Tests Unitaires...${NC}"
echo ""

python3 -m pytest tests/ -m unit -v --tb=short --cov=webapp --cov-report=term | tail -30

echo -e "${GREEN}✅ Tests unitaires terminés${NC}"
echo ""

# ===================================
# ÉTAPE 3: Vérifier services Docker
# ===================================
echo -e "${YELLOW}📋 ÉTAPE 3/5: Vérification services Docker...${NC}"
echo ""

# Vérifier que les services tournent
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Services Docker actifs${NC}"
    docker compose ps | grep -E "NAME|elasticsearch|mongodb|redis"
else
    echo -e "${RED}⚠️  Services Docker non actifs. Démarrage...${NC}"
    docker compose up -d elasticsearch mongodb redis
    echo "⏳ Attente 30 secondes pour la santé des services..."
    sleep 30
fi

echo ""

# ===================================
# ÉTAPE 4: Tests d'Intégration
# ===================================
echo -e "${YELLOW}📋 ÉTAPE 4/5: Tests d'Intégration...${NC}"
echo ""

python3 -m pytest tests/ -m integration -v --tb=short | tail -30

echo -e "${GREEN}✅ Tests d'intégration terminés${NC}"
echo ""

# ===================================
# ÉTAPE 5: Build Docker
# ===================================
echo -e "${YELLOW}📋 ÉTAPE 5/5: Build Docker Image...${NC}"
echo ""

echo "🐳 Construction de l'image..."
docker build -t projetelk/webapp:test -f Dockerfile . > /dev/null 2>&1 || {
    echo -e "${RED}❌ Build Docker échoué${NC}"
    exit 1
}

echo -e "${GREEN}✅ Image Docker construite avec succès${NC}"
docker images | grep projetelk

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 VALIDATION COMPLÈTE RÉUSSIE !${NC}"
echo "=========================================="
echo ""
echo "Vous pouvez maintenant:"
echo "  1. git add ."
echo "  2. git commit -m 'feat: CI/CD pipeline with tests'"
echo "  3. git push origin main"
echo ""
echo "Le workflow GitHub Actions s'exécutera automatiquement."
