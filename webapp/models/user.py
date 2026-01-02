"""
Modèle User pour l'authentification MongoDB
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId


class User:
    """Classe pour gérer les utilisateurs dans MongoDB"""

    def __init__(self, username, email, password=None, _id=None, created_at=None):
        """
        Initialise un utilisateur
        Args:
            username: Nom d'utilisateur (unique)
            email: Email (unique)
            password: Mot de passe en clair (sera hashé)
            _id: ID MongoDB (optionnel, généré auto)
            created_at: Date de création (optionnel)
        """
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self._id = _id
        self.created_at = created_at or datetime.utcnow()

    def check_password(self, password):
        """Vérifie si le mot de passe est correct"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour MongoDB"""
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data):
        """Crée un utilisateur depuis un dictionnaire MongoDB"""
        user = User(
            username=data.get("username"),
            email=data.get("email"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
        )
        user.password_hash = data.get("password_hash")
        return user

    def get_id(self):
        """Retourne l'ID de l'utilisateur (pour Flask session)"""
        return str(self._id)


class UserManager:
    """Gestionnaire pour les opérations sur les utilisateurs"""

    def __init__(self, db):
        """
        Initialise le gestionnaire
        Args:
            db: Instance de la base MongoDB
        """
        self.collection = db["users"]
        # Créer des index uniques sur username et email
        self.collection.create_index("username", unique=True)
        self.collection.create_index("email", unique=True)

    def create_user(self, username, email, password):
        """
        Crée un nouveau utilisateur
        Returns:
            User object si succès, None si erreur
        """
        try:
            user = User(username, email, password)
            result = self.collection.insert_one(user.to_dict())
            user._id = result.inserted_id
            return user
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            return None

    def get_user_by_username(self, username):
        """Récupère un utilisateur par son username"""
        data = self.collection.find_one({"username": username})
        return User.from_dict(data) if data else None

    def get_user_by_email(self, email):
        """Récupère un utilisateur par son email"""
        data = self.collection.find_one({"email": email})
        return User.from_dict(data) if data else None

    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        try:
            data = self.collection.find_one({"_id": ObjectId(user_id)})
            return User.from_dict(data) if data else None
        except Exception:
            return None

    def authenticate(self, username, password):
        """
        Authentifie un utilisateur
        Returns:
            User object si succès, None si échec
        """
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None

    def user_exists(self, username=None, email=None):
        """Vérifie si un utilisateur existe"""
        query = {}
        if username:
            query["username"] = username
        if email:
            query["email"] = email
        return self.collection.find_one(query) is not None
