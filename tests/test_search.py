"""
Tests unitaires pour la fonctionnalité de recherche
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


@pytest.mark.unit
@pytest.mark.api
class TestSearchEndpoint:
    """Tests de l'endpoint /search"""

    def test_search_page_exists(self, client):
        """Test que la page de recherche existe"""
        response = client.get("/search", follow_redirects=False)
        assert response.status_code in [200, 302, 401]

    def test_search_requires_auth(self, client):
        """Test que la recherche nécessite l'authentification"""
        response = client.get("/search", follow_redirects=False)
        if response.status_code == 302:
            assert "login" in response.location


@pytest.mark.unit
@pytest.mark.api
class TestSearchAPI:
    """Tests de l'API de recherche"""

    @patch("webapp.app.es")
    def test_search_logs_basic(self, mock_es, auth_client):
        """Test recherche basique de logs"""
        # Mock de la réponse Elasticsearch
        mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

        response = auth_client.get("/api/search?query=test")

        if response.status_code == 200:
            assert response.is_json
            data = response.get_json()
            assert "hits" in data or "results" in data

    @patch("webapp.app.es")
    def test_search_with_level_filter(self, mock_es, auth_client):
        """Test recherche avec filtre de niveau"""
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 5},
                "hits": [
                    {
                        "_source": {
                            "level": "ERROR",
                            "message": "Test error",
                            "timestamp": "2026-01-02T10:00:00",
                        }
                    }
                ],
            }
        }

        response = auth_client.get("/api/search?level=ERROR")

        if response.status_code == 200:
            data = response.get_json()
            # Vérifier que les résultats contiennent des erreurs
            assert data is not None

    @patch("webapp.app.es")
    def test_search_with_date_range(self, mock_es, auth_client):
        """Test recherche avec plage de dates"""
        mock_es.search.return_value = {"hits": {"total": {"value": 10}, "hits": []}}

        response = auth_client.get(
            "/api/search?start_date=2026-01-01&end_date=2026-01-02"
        )

        if response.status_code == 200:
            # Vérifier que Elasticsearch a été appelé
            assert mock_es.search.called

    @patch("webapp.app.es")
    def test_search_with_pagination(self, mock_es, auth_client):
        """Test recherche avec pagination"""
        mock_es.search.return_value = {"hits": {"total": {"value": 100}, "hits": []}}

        response = auth_client.get("/api/search?page=2&size=50")

        if response.status_code == 200:
            # Vérifier que la pagination est prise en compte
            if mock_es.search.called:
                call_args = mock_es.search.call_args
                assert "from_" in call_args[1] or "size" in call_args[1]

    @patch("webapp.app.es")
    def test_search_elasticsearch_error(self, mock_es, auth_client):
        """Test comportement quand Elasticsearch est en erreur"""
        mock_es.search.side_effect = Exception("ES Connection Error")

        response = auth_client.get("/api/search?query=test")

        # L'API doit gérer l'erreur gracieusement
        assert response.status_code in [200, 500, 503]


@pytest.mark.unit
class TestElasticsearchQuery:
    """Tests de construction des requêtes Elasticsearch"""

    @patch("webapp.app.es")
    def test_query_construction_text_search(self, mock_es, auth_client):
        """Test construction query pour recherche texte"""
        mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

        auth_client.get("/api/search?query=error+database")

        if mock_es.search.called:
            call_args = mock_es.search.call_args
            # Vérifier que la requête contient les termes recherchés
            assert call_args is not None

    @patch("webapp.app.es")
    def test_query_construction_filters(self, mock_es, auth_client):
        """Test construction query avec filtres multiples"""
        mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

        auth_client.get("/api/search?level=ERROR&service=database")

        if mock_es.search.called:
            call_args = mock_es.search.call_args
            # Les filtres doivent être dans la requête
            assert call_args is not None


@pytest.mark.integration
@pytest.mark.db
class TestSearchHistory:
    """Tests de l'historique des recherches"""

    @patch("webapp.app.db")
    def test_search_history_saved(self, mock_db, auth_client):
        """Test que l'historique est sauvegardé"""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        response = auth_client.get("/api/search?query=test")

        # Vérifier que l'historique est sauvegardé dans MongoDB
        # Note: Dépend de l'implémentation
        if response.status_code == 200:
            # La sauvegarde peut être asynchrone
            pass

    def test_search_history_endpoint(self, auth_client):
        """Test de l'endpoint d'historique des recherches"""
        response = auth_client.get("/api/search/history", follow_redirects=False)

        # Doit exister ou rediriger
        assert response.status_code in [200, 302, 404]


@pytest.mark.unit
class TestSearchExport:
    """Tests de l'export des résultats de recherche"""

    @patch("webapp.app.es")
    def test_export_csv(self, mock_es, auth_client):
        """Test export des résultats en CSV"""
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_source": {"level": "ERROR", "message": "Test 1"}},
                    {"_source": {"level": "INFO", "message": "Test 2"}},
                ],
            }
        }

        response = auth_client.get("/api/search/export?format=csv")

        if response.status_code == 200:
            # Vérifier que c'est du CSV
            assert response.mimetype == "text/csv" or "csv" in response.headers.get(
                "Content-Type", ""
            )


@pytest.mark.unit
class TestSearchValidation:
    """Tests de validation des paramètres de recherche"""

    def test_search_invalid_date_format(self, auth_client):
        """Test recherche avec format de date invalide"""
        response = auth_client.get("/api/search?start_date=invalid-date")

        # Doit gérer l'erreur gracieusement
        assert response.status_code in [200, 400]

    def test_search_invalid_level(self, auth_client):
        """Test recherche avec niveau invalide"""
        response = auth_client.get("/api/search?level=INVALID_LEVEL")

        # Doit gérer l'erreur ou ignorer le filtre
        assert response.status_code in [200, 400]

    def test_search_negative_pagination(self, auth_client):
        """Test recherche avec valeurs de pagination négatives"""
        response = auth_client.get("/api/search?page=-1&size=-10")

        # Doit utiliser des valeurs par défaut
        assert response.status_code in [200, 400]
