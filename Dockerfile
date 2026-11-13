# Utiliser une image officielle Python slim (légère)
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système de base si nécessaire
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les exigences Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source, le modèle (classifier.joblib) et les données (Churn_Modelling.csv)
COPY . .

# Exposer le port qu'utilise FastAPI
EXPOSE 8000

# Commande pour démarrer l'API Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]