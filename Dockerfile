FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source de l'application
COPY . .

# Exposer le port 8000
EXPOSE 8000

# Commande pour lancer l'application avec gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
