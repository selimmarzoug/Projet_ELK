from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import csv
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from elasticsearch import Elasticsearch
import requests

# Import du module database (Prompt 12)
from database import (
    init_databases,
    get_mongodb_db,
    get_redis_client,
    health_check as db_health_check,
)

# Import des routes d'authentification
from routes.auth import auth_bp, login_required

# Créer l'instance Flask
app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "elk-secret-key-change-in-production-2026"
)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["UPLOAD_FOLDER"] = "/data/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max
app.config["ALLOWED_EXTENSIONS"] = {"csv", "json"}

# Initialisation des connexions MongoDB et Redis (Prompt 12)
print("🚀 Initialisation des connexions aux bases de données...")
db_status = init_databases()
print(f"📊 Statut MongoDB: {'✅ Connecté' if db_status else '❌ Échec'}")

# Récupération des instances
db = get_mongodb_db()
redis_client = get_redis_client()
files_collection = db["files"] if db is not None else None
print(f"📦 MongoDB Database: {'✅' if db is not None else '❌'}")
print(f"🔴 Redis Client: {'✅' if redis_client is not None else '❌'}")

# Créer le dossier uploads s'il n'existe pas (seulement si pas en mode test)
if not app.config.get("TESTING", False):
    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    except (PermissionError, OSError) as e:
        print(f"⚠️  Impossible de créer {app.config['UPLOAD_FOLDER']}: {e}")
        # En test, on ne crée pas le dossier (géré par pytest fixtures)

# Configuration Elasticsearch
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch:9200")

# Connexion Elasticsearch
try:
    # Si l'host contient déjà le port, on l'utilise tel quel
    if ":" in ELASTICSEARCH_HOST:
        es_url = f"http://{ELASTICSEARCH_HOST}"
    else:
        es_url = f"http://{ELASTICSEARCH_HOST}:9200"

    es_client = Elasticsearch([es_url], request_timeout=5)

    # Test de connexion
    if es_client.ping():
        print(f"✅ Connexion Elasticsearch réussie : {es_url}")
    else:
        print(f"⚠️ Elasticsearch non disponible : {es_url}")
        es_client = None
except Exception as e:
    print(f"❌ Erreur connexion Elasticsearch: {e}")
    es_client = None


def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def parse_csv_preview(filepath, lines=10):
    """Parse un fichier CSV et retourne les N premières lignes avec headers."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            data = []
            for i, row in enumerate(reader):
                if i >= lines:
                    break
                data.append(row)
            return {"headers": headers, "data": data}
    except Exception as e:
        raise ValueError(f"Erreur lors du parsing CSV: {str(e)}")


def parse_json_preview(filepath, lines=10):
    """Parse un fichier JSON et retourne les N premières entrées."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Si c'est une liste
        if isinstance(json_data, list):
            preview_data = json_data[:lines]
            # Extraire les headers depuis la première entrée
            if preview_data and isinstance(preview_data[0], dict):
                headers = list(preview_data[0].keys())
            else:
                headers = None
            return {"headers": headers, "data": preview_data}

        # Si c'est un objet
        elif isinstance(json_data, dict):
            # Convertir en liste de paires clé-valeur
            items = list(json_data.items())[:lines]
            headers = ["Clé", "Valeur"]
            data = [[k, str(v)] for k, v in items]
            return {"headers": headers, "data": data}

        else:
            raise ValueError(
                "Format JSON non supporté (doit être une liste ou un objet)"
            )

    except json.JSONDecodeError as e:
        raise ValueError(f"Fichier JSON invalide: {str(e)}")
    except Exception as e:
        raise ValueError(f"Erreur lors du parsing JSON: {str(e)}")


# Fonction pour récupérer les statistiques depuis Elasticsearch
def get_elasticsearch_stats():
    """Récupère les statistiques depuis Elasticsearch."""
    stats = {"total_logs": 0, "logs_today": 0, "errors": 0, "timeline_data": []}

    if es_client is None:
        return stats

    try:
        # Total de logs
        total_response = es_client.count(index="logstash-*")
        stats["total_logs"] = total_response["count"]

        # Logs aujourd'hui
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_response = es_client.count(
            index="logstash-*",
            body={"query": {"range": {"@timestamp": {"gte": today.isoformat()}}}},
        )
        stats["logs_today"] = today_response["count"]

        # Nombre d'erreurs (logs avec status:failed ou error_message présent)
        errors_response = es_client.count(
            index="logstash-*",
            body={
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"status": "failed"}},
                            {"exists": {"field": "error_message"}},
                        ],
                        "minimum_should_match": 1,
                    }
                }
            },
        )
        stats["errors"] = errors_response["count"]

        # Timeline des 24 dernières heures (agrégation par heure)
        timeline_response = es_client.search(
            index="logstash-*",
            body={
                "size": 0,
                "query": {"range": {"@timestamp": {"gte": "now-24h/h"}}},
                "aggs": {
                    "logs_over_time": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "fixed_interval": "1h",
                            "min_doc_count": 0,
                            "extended_bounds": {"min": "now-24h/h", "max": "now"},
                        }
                    }
                },
            },
        )

        # Extraire les données de la timeline
        buckets = timeline_response["aggregations"]["logs_over_time"]["buckets"]
        stats["timeline_data"] = [
            {
                "timestamp": (
                    bucket["key_as_string"]
                    if "key_as_string" in bucket
                    else bucket["key"]
                ),
                "count": bucket["doc_count"],
            }
            for bucket in buckets
        ]

    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération des stats Elasticsearch: {e}")

    return stats


# Route Health Check (Prompt 12)
@app.route("/health")
def health():
    """
    Endpoint de health check pour vérifier l'état des services
    Returns:
        JSON avec le statut de chaque service (MongoDB, Redis, Elasticsearch)
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # Check MongoDB et Redis via database.py
    db_health = db_health_check()
    health_status["services"]["mongodb"] = db_health["mongodb"]
    health_status["services"]["redis"] = db_health["redis"]

    # Check Elasticsearch
    try:
        es_health = es_client.cluster.health()
        health_status["services"]["elasticsearch"] = {
            "status": "healthy",
            "details": {
                "cluster_name": es_health.get("cluster_name"),
                "status": es_health.get("status"),
                "number_of_nodes": es_health.get("number_of_nodes"),
            },
        }
    except Exception as e:
        health_status["services"]["elasticsearch"] = {
            "status": "error",
            "details": {"error": str(e)},
        }
        health_status["status"] = "degraded"

    # Déterminer le statut global
    if any(svc.get("status") == "error" for svc in health_status["services"].values()):
        health_status["status"] = "unhealthy"
    elif any(
        svc.get("status") == "disconnected"
        for svc in health_status["services"].values()
    ):
        health_status["status"] = "degraded"

    return jsonify(health_status)


# Route Health Dashboard (page visuelle)
@app.route("/health-dashboard")
@login_required
def health_dashboard():
    """Affiche le dashboard visuel de santé des services"""
    return render_template("health_dashboard.html")


# Route principale
@app.route("/")
@login_required
def index():
    """Affiche la page d'accueil avec le dashboard."""

    # Récupérer les statistiques Elasticsearch
    es_stats = get_elasticsearch_stats()

    # Récupérer le nombre de fichiers uploadés depuis MongoDB
    files_count = 0
    if files_collection is not None:
        try:
            files_count = files_collection.count_documents({})
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des fichiers MongoDB: {e}")

    # Préparer les données pour le template
    dashboard_data = {
        "total_logs": es_stats["total_logs"],
        "logs_today": es_stats["logs_today"],
        "errors": es_stats["errors"],
        "files_uploaded": files_count,
        "timeline_data": es_stats["timeline_data"],
    }

    return render_template("index.html", data=dashboard_data)


# Route GET pour afficher la page de recherche
@app.route("/search", methods=["GET"])
@login_required
def search_page():
    """Affiche la page de recherche."""
    return render_template("search.html")


# Route POST pour effectuer une recherche
@app.route("/api/search", methods=["POST"])
@login_required
def search_logs():
    """
    API pour rechercher dans les logs Elasticsearch.
    Paramètres:
    - query: recherche texte libre
    - level: niveau/statut (success, failed)
    - service: type de paiement
    - date_from: date début
    - date_to: date fin
    - page: numéro de page (défaut: 1)
    - size: taille de page (défaut: 50)
    """
    try:
        data = request.get_json()

        # Paramètres de recherche (avec aliases pour compatibilité Prompt 11)
        query_text = data.get("query", "")
        date_from = data.get("date_from", "")
        date_to = data.get("date_to", "")

        # Aliases: level = status, service = payment_type
        status_filter = data.get("level", data.get("status", ""))
        payment_type_filter = data.get("service", data.get("payment_type", ""))
        country_filter = data.get("country", "")

        page = int(data.get("page", 1))
        size = int(data.get("size", 50))  # 50 logs/page par défaut (Prompt 11)

        # Timestamp de la requête
        search_timestamp = datetime.utcnow()

        if es_client is None:
            return jsonify({"error": "Elasticsearch non disponible"}), 503

        # Construire la requête Elasticsearch
        must_queries = []

        # Recherche textuelle
        if query_text:
            must_queries.append(
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["*"],
                        "type": "best_fields",
                        "operator": "or",
                    }
                }
            )

        # Filtre par status (niveau)
        if status_filter:
            must_queries.append({"term": {"status": status_filter}})

        # Filtre par payment_type (service)
        if payment_type_filter:
            must_queries.append({"term": {"payment_type": payment_type_filter}})

        # Filtre par country
        if country_filter:
            must_queries.append({"term": {"country": country_filter}})

        # Filtre par date
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            must_queries.append({"range": {"@timestamp": date_range}})

        # Query finale
        es_query = {
            "bool": {"must": must_queries if must_queries else [{"match_all": {}}]}
        }

        # Exécuter la recherche
        from_offset = (page - 1) * size
        response = es_client.search(
            index="logstash-*",
            body={
                "query": es_query,
                "from": from_offset,
                "size": size,
                "sort": [{"@timestamp": {"order": "desc"}}],
            },
        )

        # Formater les résultats
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]

        results = []
        for hit in hits:
            source = hit["_source"]

            # Convertir amount en float si c'est une string
            amount = source.get("amount", 0)
            try:
                amount = float(amount) if amount else 0.0
            except (ValueError, TypeError):
                amount = 0.0

            results.append(
                {
                    "id": hit["_id"],
                    "timestamp": source.get("@timestamp", ""),
                    "transaction_id": source.get("transaction_id", ""),
                    "customer_id": source.get("customer_id", ""),
                    "amount": amount,
                    "payment_type": source.get("payment_type", ""),
                    "status": source.get("status", ""),
                    "country": source.get("country", ""),
                    "product_category": source.get("product_category", ""),
                    "error_message": source.get("error_message", ""),
                }
            )

        # Préparer la réponse
        response_data = {
            "success": True,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size,
            "results": results,
            "query_info": {
                "query": query_text,
                "level": status_filter,
                "service": payment_type_filter,
                "country": country_filter,
                "date_from": date_from,
                "date_to": date_to,
            },
        }

        # Sauvegarder l'historique de recherche dans MongoDB (Prompt 11)
        if db is not None:
            try:
                history_collection = db["search_history"]
                history_entry = {
                    "timestamp": search_timestamp,
                    "query": query_text,
                    "filters": {
                        "level": status_filter,
                        "service": payment_type_filter,
                        "country": country_filter,
                        "date_from": date_from,
                        "date_to": date_to,
                    },
                    "elasticsearch_query": es_query,
                    "results_count": total,
                    "page": page,
                    "size": size,
                    "execution_time_ms": int(
                        (datetime.utcnow() - search_timestamp).total_seconds() * 1000
                    ),
                    "ip_address": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", "unknown"),
                }
                history_collection.insert_one(history_entry)
                print(f"✅ Recherche sauvegardée dans l'historique MongoDB")
            except Exception as mongo_error:
                print(f"⚠️ Erreur sauvegarde historique MongoDB: {mongo_error}")

        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Erreur API search: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# Route GET pour afficher l'historique des recherches
@app.route("/api/search/history", methods=["GET"])
@login_required
def search_history():
    """Récupère l'historique des recherches depuis MongoDB."""
    try:
        if db is None:
            return jsonify({"success": False, "error": "MongoDB non disponible"}), 503

        history_collection = db["search_history"]

        # Paramètres de pagination
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))

        # Récupérer l'historique (tri par date décroissante)
        history = list(
            history_collection.find({}, {"_id": 0})  # Exclure l'ObjectId
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        # Compter le total
        total = history_collection.count_documents({})

        return jsonify(
            {
                "success": True,
                "total": total,
                "limit": limit,
                "skip": skip,
                "history": history,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Route GET pour afficher le formulaire d'upload
@app.route("/upload", methods=["GET"])
@login_required
def upload_page():
    """Affiche la page d'upload."""
    return render_template("upload.html")


# Route POST pour traiter l'upload
@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Traite l'upload d'un fichier CSV ou JSON."""
    try:
        # Vérifier si un fichier est présent
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files["file"]

        # Vérifier si un fichier a été sélectionné
        if file.filename == "":
            return jsonify({"error": "Aucun fichier sélectionné"}), 400

        # Vérifier l'extension
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Format de fichier non autorisé. Seuls CSV et JSON sont acceptés."
                    }
                ),
                400,
            )

        # Sécuriser le nom de fichier
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Sauvegarder le fichier
        file.save(filepath)

        # Parser et générer le preview
        extension = filename.rsplit(".", 1)[1].lower()

        try:
            if extension == "csv":
                preview_info = parse_csv_preview(filepath)
            elif extension == "json":
                preview_info = parse_json_preview(filepath)
            else:
                return jsonify({"error": "Extension non supportée"}), 400

            # Récupérer les métadonnées du fichier
            file_size = os.path.getsize(filepath)
            upload_date = datetime.utcnow()

            # Stocker les métadonnées dans MongoDB
            mongodb_success = False
            file_id = None

            if files_collection is not None:
                try:
                    file_metadata = {
                        "filename": filename,
                        "original_filename": file.filename,
                        "size": file_size,
                        "type": extension,
                        "upload_date": upload_date,
                        "filepath": filepath,
                        "status": "uploaded",
                    }
                    result = files_collection.insert_one(file_metadata)
                    file_id = str(result.inserted_id)
                    mongodb_success = True
                    print(f"✅ Métadonnées stockées dans MongoDB : {file_id}")
                except Exception as mongo_error:
                    print(f"⚠️ Erreur MongoDB (métadonnées non stockées): {mongo_error}")
            else:
                print("⚠️ MongoDB non disponible, métadonnées non stockées")

            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Fichier {filename} uploadé avec succès !",
                        "filename": filename,
                        "size": file_size,
                        "type": extension,
                        "upload_date": upload_date.isoformat(),
                        "mongodb_stored": mongodb_success,
                        "file_id": file_id,
                        "preview": preview_info["data"],
                        "headers": preview_info["headers"],
                    }
                ),
                200,
            )

        except ValueError as e:
            # Supprimer le fichier en cas d'erreur de parsing
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur serveur: {str(e)}"}), 500


# Route pour le favicon
@app.route("/favicon.ico")
def favicon():
    """Sert le favicon SVG."""
    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.svg", mimetype="image/svg+xml"
    )


# Enregistrer le Blueprint d'authentification
app.register_blueprint(auth_bp)

# Point d'entrée pour le développement
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
