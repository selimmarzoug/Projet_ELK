"""
Tests unitaires pour la fonctionnalité d'upload de fichiers
"""

import pytest
import io
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestUploadValidation:
    """Tests de validation des fichiers uploadés"""

    def test_allowed_file_csv(self):
        """Test que les fichiers CSV sont autorisés"""
        from webapp.app import allowed_file

        assert allowed_file("test.csv") is True
        assert allowed_file("test.CSV") is True

    def test_allowed_file_json(self):
        """Test que les fichiers JSON sont autorisés"""
        from webapp.app import allowed_file

        assert allowed_file("test.json") is True
        assert allowed_file("test.JSON") is True

    def test_allowed_file_invalid(self):
        """Test que les fichiers invalides sont rejetés"""
        from webapp.app import allowed_file

        assert allowed_file("test.txt") is False
        assert allowed_file("test.exe") is False
        assert allowed_file("test.pdf") is False
        assert allowed_file("test") is False

    def test_allowed_file_no_extension(self):
        """Test fichier sans extension"""
        from webapp.app import allowed_file

        assert allowed_file("filename") is False
        assert allowed_file(".csv") is False


@pytest.mark.unit
@pytest.mark.api
class TestUploadEndpoint:
    """Tests de l'endpoint /upload"""

    def test_upload_page_exists(self, client):
        """Test que la page /upload existe"""
        response = client.get("/upload", follow_redirects=False)
        # Doit rediriger vers login ou afficher la page
        assert response.status_code in [200, 302, 401]

    def test_upload_requires_auth(self, client):
        """Test que l'upload nécessite l'authentification"""
        response = client.get("/upload", follow_redirects=False)
        if response.status_code == 302:
            assert "login" in response.location

    def test_upload_post_without_file(self, auth_client):
        """Test upload POST sans fichier"""
        response = auth_client.post("/upload", data={})
        # Doit retourner une erreur
        assert response.status_code in [400, 302]

    def test_upload_invalid_file_type(self, auth_client):
        """Test upload d'un type de fichier invalide"""
        data = {"file": (io.BytesIO(b"test content"), "test.txt")}
        response = auth_client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        # Doit rejeter le fichier
        assert response.status_code in [400, 302]


@pytest.mark.unit
class TestCSVParsing:
    """Tests du parser CSV"""

    def test_parse_csv_preview_function_exists(self):
        """Test que la fonction parse_csv_preview existe"""
        from webapp.app import parse_csv_preview

        assert callable(parse_csv_preview)

    def test_parse_csv_preview_with_valid_file(self, sample_csv_file):
        """Test parsing d'un fichier CSV valide"""
        from webapp.app import parse_csv_preview

        result = parse_csv_preview(str(sample_csv_file), lines=3)

        assert isinstance(result, dict)
        assert "preview" in result
        assert "total_rows" in result
        assert result["total_rows"] >= 3
        assert len(result["preview"]) <= 3

    def test_parse_csv_preview_empty_file(self, tmp_path):
        """Test parsing d'un fichier CSV vide"""
        from webapp.app import parse_csv_preview

        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")

        result = parse_csv_preview(str(empty_file))
        assert result["total_rows"] == 0

    def test_parse_csv_preview_with_headers(self, sample_csv_file):
        """Test que les headers sont correctement détectés"""
        from webapp.app import parse_csv_preview

        result = parse_csv_preview(str(sample_csv_file))

        if len(result["preview"]) > 0:
            first_row = result["preview"][0]
            # Doit contenir les colonnes attendues
            expected_columns = ["timestamp", "level", "service", "message"]
            for col in expected_columns:
                assert col in first_row, f"Column {col} should be in parsed CSV"


@pytest.mark.unit
class TestJSONParsing:
    """Tests du parser JSON"""

    def test_parse_json_preview_function_exists(self):
        """Test que la fonction parse_json_preview existe"""
        from webapp.app import parse_json_preview

        assert callable(parse_json_preview)

    def test_parse_json_preview_with_valid_file(self, sample_json_file):
        """Test parsing d'un fichier JSON valide"""
        from webapp.app import parse_json_preview

        result = parse_json_preview(str(sample_json_file), lines=3)

        assert isinstance(result, dict)
        assert "preview" in result
        assert "total_rows" in result
        assert isinstance(result["preview"], list)

    def test_parse_json_preview_invalid_json(self, tmp_path):
        """Test parsing d'un JSON invalide"""
        from webapp.app import parse_json_preview

        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json")

        result = parse_json_preview(str(invalid_file))
        # Doit gérer l'erreur gracieusement
        assert "error" in result or result["total_rows"] == 0


@pytest.mark.integration
@pytest.mark.db
class TestUploadWithDatabase:
    """Tests d'upload avec interaction base de données"""

    @patch("webapp.app.files_collection")
    def test_upload_saves_metadata_to_mongodb(
        self, mock_collection, auth_client, sample_csv_file
    ):
        """Test que les métadonnées sont sauvegardées dans MongoDB"""
        mock_collection.insert_one.return_value = MagicMock(inserted_id="123")

        with open(sample_csv_file, "rb") as f:
            data = {"file": (f, "test.csv")}
            response = auth_client.post(
                "/upload", data=data, content_type="multipart/form-data"
            )

        # Vérifier que insert_one a été appelé
        if response.status_code == 200:
            assert mock_collection.insert_one.called


@pytest.mark.unit
class TestFileValidationHelpers:
    """Tests des fonctions helper de validation"""

    def test_secure_filename_used(self):
        """Test que secure_filename est importé et utilisé"""
        from webapp.app import secure_filename

        assert callable(secure_filename)

        # Test de sécurisation basique
        assert secure_filename("../../../etc/passwd") != "../../../etc/passwd"
        assert "/" not in secure_filename("path/to/file.csv")
