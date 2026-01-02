# 📝 CHANGELOG - ProjetELK

## [2.0.0] - 2 janvier 2026

### 🔐 Ajouté - Système d'Authentification
- **Inscription d'utilisateurs** : Page register avec validation
- **Connexion sécurisée** : Page login avec gestion de sessions
- **Protection des routes** : Décorateur `@login_required` sur toutes les pages
- **Stockage MongoDB** : Collection `users` avec passwords hashés
- **Menu utilisateur** : Affichage du nom et bouton de déconnexion
- **Messages flash** : Feedback visuel pour les actions utilisateur

**Fichiers créés :**
- `webapp/models/user.py` - Modèle User et UserManager
- `webapp/routes/auth.py` - Routes d'authentification
- `webapp/templates/login.html` - Page de connexion
- `webapp/templates/register.html` - Page d'inscription

**Fichiers modifiés :**
- `webapp/app.py` - Intégration du Blueprint auth et protection des routes
- `webapp/templates/base.html` - Ajout du menu utilisateur

### 💚 Ajouté - Health Dashboard
- **Page de monitoring visuelle** : `/health-dashboard`
- **Design moderne** : Gradients, animations, effets hover
- **Statut global** : Indicateur healthy/degraded/unhealthy
- **Cartes des services** : Elasticsearch, MongoDB, Redis avec détails
- **Métriques en temps réel** : Nombre de services, heure système
- **Auto-refresh** : Mise à jour automatique toutes les 30 secondes
- **Responsive design** : Adapté mobile et desktop

**Fichiers créés :**
- `webapp/templates/health_dashboard.html` - Dashboard de santé

**Fichiers modifiés :**
- `webapp/app.py` - Route `/health-dashboard`
- `webapp/templates/base.html` - Lien "Health" dans la navbar

### 📊 Ajouté - Données de Test
- **Fichier test avec dates récentes** : `test_today_2026.csv`
  - 30 transactions du 2 janvier 2026
  - Timestamps à jour pour tests des statistiques "Aujourd'hui"
  - Données e-commerce réalistes

### 📝 Documentation
- **README.md mis à jour** : Documentation complète
  - Section authentification
  - Section Health Dashboard
  - Guide de démarrage rapide
  - Commandes utiles (Docker, Elasticsearch, MongoDB, Redis)
  - Structure du projet détaillée
  
- **CHANGELOG.md créé** : Historique des modifications

### 🔧 Améliorations
- **Navbar modernisée** : Ajout des liens Health et Search
- **Gestion des erreurs** : Meilleure gestion de la connexion MongoDB
- **Sessions persistantes** : Durée de 7 jours
- **Messages d'erreur clairs** : Feedback amélioré pour l'utilisateur

---

## [1.0.0] - Novembre 2025

### 🎉 Version Initiale
- **Stack ELK complète** : Elasticsearch, Logstash, Kibana
- **Services supplémentaires** : MongoDB, Redis, Mongo Express
- **Application Flask** : Interface web de base
- **Upload de fichiers** : CSV et JSON avec prévisualisation
- **Dashboard principal** : Statistiques et graphiques
- **Recherche** : Interface de recherche dans les logs
- **Multi-pipeline Logstash** : Traitement CSV et JSON séparés
- **Configuration Docker Compose** : Orchestration des services
- **Healthchecks** : Monitoring de base des services

**Fonctionnalités :**
- Upload de fichiers via interface web ou API
- Stockage des métadonnées dans MongoDB
- Ingestion automatique dans Elasticsearch via Logstash
- Dashboard avec KPIs et graphiques
- Recherche avancée avec filtres
- API Health Check JSON

**Infrastructure :**
- 7 conteneurs Docker
- Volumes persistants pour les données
- Réseau bridge isolé
- Configuration via variables d'environnement

---

## Légende

- 🔐 **Sécurité** : Authentification, autorisation, encryption
- 💚 **Monitoring** : Surveillance, health checks, métriques
- 📊 **Données** : Bases de données, stockage, indexation
- 🎨 **UI/UX** : Interface utilisateur, design, ergonomie
- 🔧 **Technique** : Refactoring, optimisations, fixes
- 📝 **Documentation** : README, guides, commentaires
- 🎉 **Majeur** : Nouvelles fonctionnalités importantes
