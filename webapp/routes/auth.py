"""
Routes d'authentification (login, register, logout)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models.user import UserManager
from database import db_manager

# Créer le Blueprint
auth_bp = Blueprint("auth", __name__)


def get_user_manager():
    """Retourne une instance du UserManager avec la connexion MongoDB actuelle"""
    # S'assurer que MongoDB est connecté
    if not db_manager.mongodb._connected:
        db_manager.mongodb.connect()

    db = db_manager.mongodb.db
    if db is None:
        return None
    return UserManager(db)


def login_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("⚠️ Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Page d'inscription"""
    # Si déjà connecté, rediriger vers l'accueil
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not username or not email or not password:
            flash("❌ Tous les champs sont obligatoires.", "error")
            return render_template("register.html")

        if len(username) < 3:
            flash(
                "❌ Le nom d'utilisateur doit contenir au moins 3 caractères.", "error"
            )
            return render_template("register.html")

        if len(password) < 6:
            flash("❌ Le mot de passe doit contenir au moins 6 caractères.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("❌ Les mots de passe ne correspondent pas.", "error")
            return render_template("register.html")

        # Obtenir le UserManager
        user_manager = get_user_manager()
        if not user_manager:
            flash("❌ Erreur de connexion à la base de données.", "error")
            return render_template("register.html")

        # Vérifier si l'utilisateur existe déjà
        if user_manager.user_exists(username=username):
            flash("❌ Ce nom d'utilisateur est déjà pris.", "error")
            return render_template("register.html")

        if user_manager.user_exists(email=email):
            flash("❌ Cet email est déjà utilisé.", "error")
            return render_template("register.html")

        # Créer l'utilisateur
        user = user_manager.create_user(username, email, password)
        if user:
            flash(f"✅ Compte créé avec succès ! Bienvenue {username} 🎉", "success")
            # Connexion automatique après inscription
            session["user_id"] = user.get_id()
            session["username"] = user.username
            return redirect(url_for("index"))
        else:
            flash("❌ Erreur lors de la création du compte.", "error")
            return render_template("register.html")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion"""
    # Si déjà connecté, rediriger vers l'accueil
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("❌ Nom d'utilisateur et mot de passe requis.", "error")
            return render_template("login.html")

        # Obtenir le UserManager
        user_manager = get_user_manager()
        if not user_manager:
            flash("❌ Erreur de connexion à la base de données.", "error")
            return render_template("login.html")

        # Authentifier l'utilisateur
        user = user_manager.authenticate(username, password)
        if user:
            session["user_id"] = user.get_id()
            session["username"] = user.username
            flash(f"✅ Bienvenue {user.username} ! 👋", "success")

            # Rediriger vers la page demandée ou l'accueil
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("❌ Nom d'utilisateur ou mot de passe incorrect.", "error")
            return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Déconnexion"""
    username = session.get("username", "Utilisateur")
    session.clear()
    flash(f"✅ À bientôt {username} ! 👋", "info")
    return redirect(url_for("auth.login"))
