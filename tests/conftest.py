"""
Configuration pytest et fixtures communes pour tous les tests
"""

import os
import sys
import pytest
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../webapp"))
)


@pytest.fixture(scope="session")
def app():
    """
    Fixture Flask app pour tous les tests
    Configure l'app en mode testing
    """
    # Configuration de test
    os.environ["TESTING"] = "True"
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"

    # Import de l'app (après avoir configuré les variables d'env)
    from webapp.app import app as flask_app

    # Configuration pour les tests
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["SERVER_NAME"] = "localhost:5000"

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """
    Fixture Flask test client
    Crée un nouveau client pour chaque test
    """
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """
    Fixture Flask CLI runner
    """
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def auth_client(client):
    """
    Fixture client authentifié
    Crée un utilisateur de test et se connecte
    """
    # TODO: Implémenter l'authentification de test
    # Pour l'instant, retourne le client normal
    return client


@pytest.fixture(scope="function")
def sample_csv_file(tmp_path):
    """
    Fixture pour créer un fichier CSV de test
    """
    csv_content = """timestamp,level,service,message,ip_address,user
2026-01-02 10:00:00,INFO,api,Request received,192.168.1.1,user1
2026-01-02 10:01:00,ERROR,database,Connection timeout,192.168.1.2,user2
2026-01-02 10:02:00,WARNING,auth,Invalid password attempt,192.168.1.3,user3
"""
    file_path = tmp_path / "test_logs.csv"
    file_path.write_text(csv_content)
    return file_path


@pytest.fixture(scope="function")
def sample_json_file(tmp_path):
    """
    Fixture pour créer un fichier JSON de test
    """
    json_content = """[
    {"timestamp": "2026-01-02T10:00:00", "level": "INFO", "service": "api", "message": "Request received"},
    {"timestamp": "2026-01-02T10:01:00", "level": "ERROR", "service": "database", "message": "Connection timeout"},
    {"timestamp": "2026-01-02T10:02:00", "level": "WARNING", "service": "auth", "message": "Invalid password"}
]"""
    file_path = tmp_path / "test_logs.json"
    file_path.write_text(json_content)
    return file_path


@pytest.fixture(scope="function")
def mock_elasticsearch(mocker):
    """
    Fixture pour mocker Elasticsearch
    """
    mock_es = mocker.MagicMock()
    mock_es.ping.return_value = True
    mock_es.cluster.health.return_value = {"status": "green"}
    mock_es.count.return_value = {"count": 100}
    return mock_es


@pytest.fixture(scope="function")
def mock_redis(mocker):
    """
    Fixture pour mocker Redis
    """
    mock_redis_client = mocker.MagicMock()
    mock_redis_client.ping.return_value = True
    mock_redis_client.info.return_value = {"redis_version": "7.2.0"}
    return mock_redis_client


@pytest.fixture(scope="function")
def mock_mongodb(mocker):
    """
    Fixture pour mocker MongoDB
    """
    mock_mongo_client = mocker.MagicMock()
    mock_mongo_db = mocker.MagicMock()
    mock_mongo_client.__getitem__.return_value = mock_mongo_db
    return mock_mongo_client, mock_mongo_db


# Hook pour afficher des informations au début des tests
def pytest_configure(config):
    """Configuration exécutée avant les tests"""
    print("\n" + "=" * 70)
    print("🧪 Démarrage des tests ProjetELK")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """Hook exécuté à la fin de tous les tests"""
    print("\n" + "=" * 70)
    print("✅ Tests terminés")
    print(f"📊 Status: {'SUCCÈS' if exitstatus == 0 else 'ÉCHEC'}")
    print("=" * 70 + "\n")
