"""
Module de gestion des connexions aux bases de données MongoDB et Redis.
Gère les connexions, la configuration et les tests de santé.
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration centralisée des connexions aux bases de données."""
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://admin:changeme@mongodb:27017')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'logsdb')
    MONGO_TIMEOUT = int(os.getenv('MONGO_TIMEOUT', '5000'))  # ms
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DECODE_RESPONSES = os.getenv('REDIS_DECODE_RESPONSES', 'true').lower() == 'true'
    REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT', '5'))
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv('DB_MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('DB_RETRY_DELAY', '2'))  # seconds


class MongoDBConnection:
    """Gestionnaire de connexion MongoDB avec gestion d'erreurs."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Établit la connexion à MongoDB.
        
        Returns:
            bool: True si connexion réussie, False sinon
        """
        try:
            logger.info(f"🔌 Connexion à MongoDB: {DatabaseConfig.MONGO_URI.split('@')[-1]}")
            
            self.client = MongoClient(
                DatabaseConfig.MONGO_URI,
                serverSelectionTimeoutMS=DatabaseConfig.MONGO_TIMEOUT,
                connectTimeoutMS=DatabaseConfig.MONGO_TIMEOUT,
                socketTimeoutMS=DatabaseConfig.MONGO_TIMEOUT,
            )
            
            # Test de connexion
            self.client.admin.command('ping')
            
            # Sélection de la base de données
            self.db = self.client[DatabaseConfig.MONGO_DB_NAME]
            
            self._connected = True
            logger.info(f"✅ MongoDB connecté - Base: {DatabaseConfig.MONGO_DB_NAME}")
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Erreur connexion MongoDB: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue MongoDB: {e}")
            self._connected = False
            return False
    
    def get_collection(self, collection_name: str):
        """
        Récupère une collection MongoDB.
        
        Args:
            collection_name: Nom de la collection
            
        Returns:
            Collection MongoDB ou None
        """
        if not self._connected or self.db is None:
            logger.warning(f"⚠️  MongoDB non connecté - tentative de reconnexion")
            if not self.connect():
                return None
        
        return self.db[collection_name]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé de la connexion MongoDB.
        
        Returns:
            Dictionnaire avec le statut et les informations
        """
        try:
            if not self._connected or self.client is None:
                return {
                    'status': 'disconnected',
                    'healthy': False,
                    'message': 'MongoDB non connecté'
                }
            
            # Test ping
            result = self.client.admin.command('ping')
            
            # Récupération des stats
            stats = self.db.command('dbStats')
            
            return {
                'status': 'connected',
                'healthy': True,
                'database': DatabaseConfig.MONGO_DB_NAME,
                'collections': self.db.list_collection_names(),
                'size_mb': round(stats['dataSize'] / (1024 * 1024), 2),
                'documents': stats.get('objects', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check MongoDB échoué: {e}")
            return {
                'status': 'error',
                'healthy': False,
                'message': str(e)
            }
    
    def close(self):
        """Ferme la connexion MongoDB."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔌 Connexion MongoDB fermée")


class RedisConnection:
    """Gestionnaire de connexion Redis avec gestion d'erreurs."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Établit la connexion à Redis.
        
        Returns:
            bool: True si connexion réussie, False sinon
        """
        try:
            logger.info(f"🔌 Connexion à Redis: {DatabaseConfig.REDIS_HOST}:{DatabaseConfig.REDIS_PORT}")
            
            self.client = redis.Redis(
                host=DatabaseConfig.REDIS_HOST,
                port=DatabaseConfig.REDIS_PORT,
                db=DatabaseConfig.REDIS_DB,
                password=DatabaseConfig.REDIS_PASSWORD,
                decode_responses=DatabaseConfig.REDIS_DECODE_RESPONSES,
                socket_timeout=DatabaseConfig.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=DatabaseConfig.REDIS_SOCKET_TIMEOUT,
            )
            
            # Test de connexion
            self.client.ping()
            
            self._connected = True
            logger.info(f"✅ Redis connecté - DB: {DatabaseConfig.REDIS_DB}")
            
            return True
            
        except RedisConnectionError as e:
            logger.error(f"❌ Erreur connexion Redis: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue Redis: {e}")
            self._connected = False
            return False
    
    def get_client(self) -> Optional[redis.Redis]:
        """
        Récupère le client Redis.
        
        Returns:
            Client Redis ou None
        """
        if not self._connected or self.client is None:
            logger.warning(f"⚠️  Redis non connecté - tentative de reconnexion")
            if not self.connect():
                return None
        
        return self.client
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé de la connexion Redis.
        
        Returns:
            Dictionnaire avec le statut et les informations
        """
        try:
            if not self._connected or self.client is None:
                return {
                    'status': 'disconnected',
                    'healthy': False,
                    'message': 'Redis non connecté'
                }
            
            # Test ping
            self.client.ping()
            
            # Récupération des infos
            info = self.client.info()
            
            return {
                'status': 'connected',
                'healthy': True,
                'version': info.get('redis_version', 'unknown'),
                'uptime_days': info.get('uptime_in_days', 0),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_mb': round(info.get('used_memory', 0) / (1024 * 1024), 2),
                'total_keys': self.client.dbsize(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check Redis échoué: {e}")
            return {
                'status': 'error',
                'healthy': False,
                'message': str(e)
            }
    
    def close(self):
        """Ferme la connexion Redis."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔌 Connexion Redis fermée")


class DatabaseManager:
    """Gestionnaire centralisé des connexions aux bases de données."""
    
    def __init__(self):
        self.mongodb = MongoDBConnection()
        self.redis = RedisConnection()
    
    def connect_all(self) -> Dict[str, bool]:
        """
        Connecte toutes les bases de données.
        
        Returns:
            Dictionnaire avec le statut de chaque connexion
        """
        logger.info("=" * 60)
        logger.info("🚀 Initialisation des connexions aux bases de données")
        logger.info("=" * 60)
        
        results = {
            'mongodb': self.mongodb.connect(),
            'redis': self.redis.connect()
        }
        
        logger.info("=" * 60)
        if all(results.values()):
            logger.info("✅ Toutes les connexions établies avec succès")
        else:
            failed = [db for db, status in results.items() if not status]
            logger.warning(f"⚠️  Échec connexion: {', '.join(failed)}")
        logger.info("=" * 60)
        
        return results
    
    def health_check_all(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé de toutes les connexions.
        
        Returns:
            Dictionnaire avec le statut de chaque base
        """
        return {
            'mongodb': self.mongodb.health_check(),
            'redis': self.redis.health_check(),
            'overall_healthy': all([
                self.mongodb.health_check()['healthy'],
                self.redis.health_check()['healthy']
            ])
        }
    
    def close_all(self):
        """Ferme toutes les connexions."""
        logger.info("🔌 Fermeture des connexions...")
        self.mongodb.close()
        self.redis.close()
        logger.info("✅ Toutes les connexions fermées")


# Instance globale du gestionnaire de bases de données
db_manager = DatabaseManager()


def init_databases() -> bool:
    """
    Initialise toutes les connexions aux bases de données.
    Fonction utilitaire pour l'initialisation au démarrage de l'application.
    
    Returns:
        bool: True si toutes les connexions réussies, False sinon
    """
    results = db_manager.connect_all()
    return all(results.values())


def get_mongodb_db():
    """
    Récupère l'objet database MongoDB.
    Fonction utilitaire pour accès à la base de données.
    
    Returns:
        Database MongoDB ou None
    """
    return db_manager.mongodb.db if db_manager.mongodb._connected else None


def get_mongodb_collection(collection_name: str):
    """
    Récupère une collection MongoDB.
    Fonction utilitaire pour accès rapide.
    
    Args:
        collection_name: Nom de la collection
        
    Returns:
        Collection MongoDB ou None
    """
    return db_manager.mongodb.get_collection(collection_name)


def get_redis_client() -> Optional[redis.Redis]:
    """
    Récupère le client Redis.
    Fonction utilitaire pour accès rapide.
    
    Returns:
        Client Redis ou None
    """
    return db_manager.redis.get_client()


def health_check() -> Dict[str, Any]:
    """
    Effectue un health check de toutes les connexions.
    Fonction utilitaire pour monitoring.
    
    Returns:
        Dict avec le statut de santé de chaque service
    """
    return db_manager.health_check_all()


# Test de connexion si exécuté directement
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🧪 TEST DES CONNEXIONS AUX BASES DE DONNÉES")
    print("=" * 60 + "\n")
    
    # Test connexion
    success = init_databases()
    
    if success:
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK")
        print("=" * 60 + "\n")
        
        # Health check
        health = db_manager.health_check_all()
        
        print("📦 MongoDB:")
        mongo_health = health['mongodb']
        for key, value in mongo_health.items():
            print(f"  - {key}: {value}")
        
        print("\n💾 Redis:")
        redis_health = health['redis']
        for key, value in redis_health.items():
            print(f"  - {key}: {value}")
        
        print("\n" + "=" * 60)
        print(f"🏥 État global: {'✅ HEALTHY' if health['overall_healthy'] else '❌ UNHEALTHY'}")
        print("=" * 60 + "\n")
        
        # Test opérations
        print("\n" + "=" * 60)
        print("🧪 TEST DES OPÉRATIONS")
        print("=" * 60 + "\n")
        
        # Test MongoDB
        try:
            test_collection = get_mongodb_collection('test_collection')
            if test_collection is not None:
                test_doc = {'test': True, 'timestamp': datetime.utcnow()}
                result = test_collection.insert_one(test_doc)
                print(f"✅ MongoDB insert test: {result.inserted_id}")
                test_collection.delete_one({'_id': result.inserted_id})
                print(f"✅ MongoDB delete test: OK")
        except Exception as e:
            print(f"❌ MongoDB test failed: {e}")
        
        # Test Redis
        try:
            redis_client = get_redis_client()
            if redis_client is not None:
                redis_client.set('test_key', 'test_value', ex=10)
                value = redis_client.get('test_key')
                print(f"✅ Redis set/get test: {value}")
                redis_client.delete('test_key')
                print(f"✅ Redis delete test: OK")
        except Exception as e:
            print(f"❌ Redis test failed: {e}")
        
        # Fermeture
        db_manager.close_all()
        
        print("\n" + "=" * 60)
        print("✅ TESTS TERMINÉS AVEC SUCCÈS")
        print("=" * 60 + "\n")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ ÉCHEC DES CONNEXIONS")
        print("=" * 60 + "\n")
        sys.exit(1)
