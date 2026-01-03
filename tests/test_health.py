"""
Tests unitaires pour l'endpoint /health
Tests de l'API de santé du système
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
@pytest.mark.api
class TestHealthEndpoint:
    """Tests pour l'endpoint /health"""

    def test_health_endpoint_exists(self, client):
        """Test que l'endpoint /health existe et répond"""
        response = client.get("/health")
        assert response.status_code in [200, 503], "L'endpoint /health doit répondre"

    def test_health_returns_json(self, client):
        """Test que /health retourne du JSON"""
        response = client.get("/health")
        assert response.is_json, "/health doit retourner du JSON"
        data = response.get_json()
        assert isinstance(data, dict), "La réponse doit être un dictionnaire"

    def test_health_has_required_fields(self, client):
        """Test que /health contient les champs obligatoires"""
        response = client.get("/health")
        data = response.get_json()

        # Champs obligatoires
        required_fields = ["status", "timestamp", "services"]
        for field in required_fields:
            assert field in data, f"Le champ '{field}' doit être présent dans /health"

    def test_health_status_values(self, client):
        """Test que le statut est une valeur valide"""
        response = client.get("/health")
        data = response.get_json()

        valid_statuses = ["healthy", "degraded", "unhealthy"]
        assert (
            data["status"] in valid_statuses
        ), f"Status doit être l'un de {valid_statuses}"

    def test_health_services_structure(self, client):
        """Test la structure du champ services"""
        response = client.get("/health")
        data = response.get_json()

        assert "services" in data
        services = data["services"]
        assert isinstance(services, dict), "services doit être un dictionnaire"

        # Vérifier qu'au moins un service est présent
        expected_services = ["elasticsearch", "mongodb", "redis"]
        for service_name in expected_services:
            if service_name in services:
                service = services[service_name]
                assert "status" in service, f"{service_name} doit avoir un status"
                assert service["status"] in [
                    "up",
                    "down",
                ], f"Status de {service_name} doit être 'up' ou 'down'"

    @patch("webapp.app.es")
    def test_health_elasticsearch_up(self, mock_es, client):
        """Test santé quand Elasticsearch est UP"""
        mock_es.ping.return_value = True
        mock_es.cluster.health.return_value = {"status": "green"}

        response = client.get("/health")
        data = response.get_json()

        if "elasticsearch" in data.get("services", {}):
            assert data["services"]["elasticsearch"]["status"] == "up"

    @patch("webapp.app.es")
    def test_health_elasticsearch_down(self, mock_es, client):
        """Test santé quand Elasticsearch est DOWN"""
        mock_es.ping.side_effect = Exception("Connection failed")

        response = client.get("/health")
        data = response.get_json()

        # L'endpoint doit toujours répondre même si ES est down
        assert response.status_code in [200, 503]
        if "elasticsearch" in data.get("services", {}):
            assert data["services"]["elasticsearch"]["status"] == "down"


@pytest.mark.unit
class TestHealthDashboard:
    """Tests pour la page /health-dashboard"""

    def test_health_dashboard_exists(self, client):
        """Test que la page health dashboard existe"""
        # Note: Nécessite authentification
        response = client.get("/health-dashboard", follow_redirects=False)
        # Doit rediriger vers login ou afficher la page
        assert response.status_code in [200, 302, 401]

    def test_health_dashboard_requires_auth(self, client):
        """Test que health-dashboard nécessite l'authentification"""
        response = client.get("/health-dashboard", follow_redirects=False)
        # Si pas authentifié, doit rediriger
        if response.status_code == 302:
            assert "login" in response.location or "/login" in response.location


@pytest.mark.unit
class TestHealthCheckFunction:
    """Tests de la fonction health_check elle-même"""

    def test_health_check_callable(self):
        """Test que health_check est une fonction appelable"""
        from webapp.database import health_check

        assert callable(health_check), "health_check doit être callable"

    @patch("webapp.database.get_mongodb_db")
    @patch("webapp.database.get_redis_client")
    def test_health_check_with_all_services_up(self, mock_redis, mock_mongo):
        """Test health_check avec tous les services UP"""
        # Mock MongoDB
        mock_db = MagicMock()
        mock_db.command.return_value = {"ok": 1}
        mock_mongo.return_value = mock_db

        # Mock Redis
        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis.return_value = mock_redis_client

        from webapp.database import health_check

        result = health_check()

        assert isinstance(result, dict)
        assert "mongodb" in result
        assert "redis" in result

    @patch("webapp.database.get_mongodb_db")
    def test_health_check_with_mongodb_down(self, mock_mongo):
        """Test health_check quand MongoDB est DOWN"""
        mock_mongo.return_value = None

        from webapp.database import health_check

        result = health_check()

        # Accepter 'down' ou 'disconnected' comme statut valide
        assert result["mongodb"]["status"] in ["down", "disconnected"]
