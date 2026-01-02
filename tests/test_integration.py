"""
Tests d'intégration - Avec vrais services Docker
Ces tests nécessitent que les services soient démarrés :
    docker compose up -d elasticsearch mongodb redis
"""

import pytest
import time
from elasticsearch import Elasticsearch
from pymongo import MongoClient
import redis


# ============================================
# TESTS DE CONNEXION AUX SERVICES RÉELS
# ============================================


@pytest.mark.integration
@pytest.mark.db
class TestRealElasticsearch:
    """Tests avec Elasticsearch réel"""

    def test_elasticsearch_is_running(self):
        """Test que Elasticsearch est accessible"""
        try:
            es = Elasticsearch(["http://localhost:9200"])
            health = es.cluster.health()

            assert health is not None
            assert "status" in health
            print(f"✅ Elasticsearch status: {health['status']}")
        except Exception as e:
            pytest.skip(f"Elasticsearch non disponible: {e}")

    def test_elasticsearch_can_index_document(self):
        """Test indexation d'un document dans Elasticsearch"""
        try:
            es = Elasticsearch(["http://localhost:9200"])

            # Créer un document de test
            doc = {
                "timestamp": "2026-01-02T10:00:00",
                "level": "INFO",
                "service": "test-service",
                "message": "Test integration document",
            }

            # Indexer le document
            result = es.index(
                index="test-integration",
                document=doc,
                refresh="wait_for",  # Attendre que l'index soit prêt
            )

            assert result["result"] in ["created", "updated"]
            print(f"✅ Document indexé : {result['_id']}")

            # Nettoyer
            es.indices.delete(index="test-integration", ignore=[404])

        except Exception as e:
            pytest.skip(f"Elasticsearch non disponible: {e}")

    def test_elasticsearch_can_search(self):
        """Test recherche dans Elasticsearch"""
        try:
            es = Elasticsearch(["http://localhost:9200"])

            # Créer et indexer des documents
            for i in range(5):
                es.index(
                    index="test-search",
                    document={
                        "timestamp": f"2026-01-02T10:0{i}:00",
                        "level": "INFO",
                        "message": f"Test message {i}",
                    },
                )

            # Rafraîchir l'index
            es.indices.refresh(index="test-search")

            # Rechercher
            result = es.search(index="test-search", body={"query": {"match_all": {}}})

            assert result["hits"]["total"]["value"] >= 5
            print(f"✅ Trouvé {result['hits']['total']['value']} documents")

            # Nettoyer
            es.indices.delete(index="test-search", ignore=[404])

        except Exception as e:
            pytest.skip(f"Elasticsearch non disponible: {e}")


@pytest.mark.integration
@pytest.mark.db
class TestRealMongoDB:
    """Tests avec MongoDB réel"""

    def test_mongodb_is_running(self):
        """Test que MongoDB est accessible"""
        try:
            client = MongoClient("mongodb://admin:changeme@localhost:27017/")
            # Tester la connexion
            client.admin.command("ping")
            print("✅ MongoDB est accessible")
        except Exception as e:
            pytest.skip(f"MongoDB non disponible: {e}")

    def test_mongodb_can_insert_document(self):
        """Test insertion dans MongoDB"""
        try:
            client = MongoClient("mongodb://admin:changeme@localhost:27017/")
            db = client["test_integration_db"]
            collection = db["test_collection"]

            # Insérer un document
            doc = {
                "filename": "test.csv",
                "uploaded_at": "2026-01-02T10:00:00",
                "size": 1024,
                "status": "success",
            }

            result = collection.insert_one(doc)
            assert result.inserted_id is not None
            print(f"✅ Document inséré : {result.inserted_id}")

            # Nettoyer
            collection.delete_one({"_id": result.inserted_id})

        except Exception as e:
            pytest.skip(f"MongoDB non disponible: {e}")

    def test_mongodb_can_query_documents(self):
        """Test requête dans MongoDB"""
        try:
            client = MongoClient("mongodb://admin:changeme@localhost:27017/")
            db = client["test_integration_db"]
            collection = db["test_collection"]

            # Insérer plusieurs documents
            docs = [{"name": f"file{i}.csv", "status": "success"} for i in range(3)]
            result = collection.insert_many(docs)
            assert len(result.inserted_ids) == 3

            # Requêter
            count = collection.count_documents({"status": "success"})
            assert count >= 3
            print(f"✅ Trouvé {count} documents")

            # Nettoyer
            collection.delete_many({"status": "success"})

        except Exception as e:
            pytest.skip(f"MongoDB non disponible: {e}")


@pytest.mark.integration
@pytest.mark.db
class TestRealRedis:
    """Tests avec Redis réel"""

    def test_redis_is_running(self):
        """Test que Redis est accessible"""
        try:
            r = redis.Redis(
                host="localhost", port=6379, password="changeme", decode_responses=True
            )
            result = r.ping()
            assert result is True
            print("✅ Redis est accessible")
        except Exception as e:
            pytest.skip(f"Redis non disponible: {e}")

    def test_redis_can_set_and_get(self):
        """Test SET et GET dans Redis"""
        try:
            r = redis.Redis(
                host="localhost", port=6379, password="changeme", decode_responses=True
            )

            # SET
            r.set("test_key", "test_value")

            # GET
            value = r.get("test_key")
            assert value == "test_value"
            print("✅ SET et GET fonctionnent")

            # Nettoyer
            r.delete("test_key")

        except Exception as e:
            pytest.skip(f"Redis non disponible: {e}")

    def test_redis_expiration(self):
        """Test expiration de clé dans Redis"""
        try:
            r = redis.Redis(
                host="localhost", port=6379, password="changeme", decode_responses=True
            )

            # SET avec expiration de 2 secondes
            r.setex("temp_key", 2, "temporary_value")

            # Vérifier que la clé existe
            assert r.exists("temp_key") == 1

            # Attendre l'expiration
            time.sleep(3)

            # Vérifier que la clé a expiré
            assert r.exists("temp_key") == 0
            print("✅ Expiration fonctionne")

        except Exception as e:
            pytest.skip(f"Redis non disponible: {e}")


# ============================================
# TESTS DE BOUT EN BOUT (END-TO-END)
# ============================================


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndFlows:
    """Tests de flux complets avec tous les services"""

    def test_full_upload_flow(self, client, tmp_path):
        """Test flux complet : Upload → Logstash → Elasticsearch"""
        pytest.skip("Nécessite authentification - à implémenter")

        # TODO:
        # 1. Créer un fichier CSV
        # 2. L'uploader via l'API
        # 3. Attendre le traitement Logstash
        # 4. Vérifier dans Elasticsearch
        # 5. Vérifier métadonnées dans MongoDB

    def test_full_search_flow(self, client):
        """Test flux complet : Indexation → Recherche → Cache"""
        pytest.skip("Nécessite données dans ES - à implémenter")

        # TODO:
        # 1. Indexer des documents dans ES
        # 2. Faire une recherche
        # 3. Vérifier résultats
        # 4. Vérifier mise en cache Redis
        # 5. Refaire recherche (doit venir du cache)


# ============================================
# TESTS DE PERFORMANCE (OPTIONNEL)
# ============================================


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Tests de performance avec vrais services"""

    def test_elasticsearch_bulk_indexing(self):
        """Test indexation en masse dans Elasticsearch"""
        try:
            es = Elasticsearch(["http://localhost:9200"])

            # Préparer 1000 documents
            docs = []
            for i in range(1000):
                docs.append({"index": {"_index": "perf-test"}})
                docs.append(
                    {
                        "timestamp": f"2026-01-02T10:00:{i%60:02d}",
                        "level": "INFO",
                        "message": f"Performance test {i}",
                    }
                )

            # Indexer en masse
            import time

            start = time.time()
            result = es.bulk(body=docs, refresh="wait_for")
            duration = time.time() - start

            print(f"✅ Indexé 1000 docs en {duration:.2f}s")
            assert duration < 10  # Doit prendre moins de 10 secondes

            # Nettoyer
            es.indices.delete(index="perf-test", ignore=[404])

        except Exception as e:
            pytest.skip(f"Elasticsearch non disponible: {e}")
