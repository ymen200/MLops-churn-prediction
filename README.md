# Prédiction du désabonnement client — projet MLOps

Ce projet met en œuvre un cycle de vie MLOps autour du jeu de données `Churn_Modelling.csv` : préparation des données, entraînement et évaluation d’un classifieur Random Forest, exposition des prédictions avec FastAPI, orchestration avec Prefect, suivi d’expériences avec MLflow et supervision avec Elasticsearch/Kibana.

Il s’agit d’un projet pédagogique (ateliers MLOps), et non d’un service prêt à être exposé en production.

## Fonctionnalités

- Prétraitement des données et séparation entraînement/test.
- Entraînement, évaluation et sérialisation du modèle dans `classifier.joblib`.
- Interface en ligne de commande pour entraîner ou évaluer le modèle.
- API REST FastAPI pour prédire le risque de désabonnement et déclencher un réentraînement.
- Flows Prefect pour les contrôles de code, les tests, l’entraînement, l’évaluation et le lancement de l’API.
- Suivi optionnel des paramètres, métriques et artefacts avec MLflow.
- Envoi optionnel de métriques vers Elasticsearch et visualisation avec Kibana.
- Conteneurisation de l’API avec Docker.

## Architecture

```text
Churn_Modelling.csv
        |
        v
model_pipeline.py <---- main.py / pipeline_prefect.py
        |                         |
        |                         +--> Prefect (orchestration)
        +--> classifier.joblib
        +--> MLflow (expériences et artefacts, optionnel)
        +--> Elasticsearch --> Kibana (monitoring, optionnel)
        |
        v
app.py (FastAPI) --> POST /predict et POST /retrain
        |
        v
Docker (conteneur de l’API)
```

## Prérequis

- Python 3.10 ou supérieur.
- Docker Desktop ou Docker Engine pour les étapes Docker et Elasticsearch/Kibana.
- Le fichier de données `Churn_Modelling.csv`, fourni à la racine du dépôt.

## Installation

Depuis la racine du dépôt, créez un environnement virtuel et installez les dépendances :

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Vérifiez que le fichier `Churn_Modelling.csv` est présent à la racine. Les commandes et chemins relatifs ci-dessous sont prévus pour être lancés depuis ce répertoire.

## Entraîner et évaluer le modèle

Le script `main.py` propose trois actions :

```bash
# Préparer les données, entraîner, évaluer et enregistrer le modèle
python main.py --action all

# Entraîner, évaluer et enregistrer le modèle
python main.py --action train

# Charger classifier.joblib et l’évaluer
python main.py --action evaluate
```

Pour utiliser un autre fichier de données :

```bash
python main.py --data chemin/vers/donnees.csv --action all
```

L’entraînement crée ou remplace `classifier.joblib`. L’évaluation affiche l’accuracy et le rapport de classification.

## API FastAPI

L’API charge `classifier.joblib` au démarrage. Entraînez d’abord un modèle si ce fichier n’existe pas, puis lancez le serveur :

```bash
uvicorn app:app --reload
```

- Accueil : <http://127.0.0.1:8000/>
- Documentation interactive : <http://127.0.0.1:8000/docs>

### Prédiction

Envoyez une requête `POST /predict` avec les neuf caractéristiques attendues :

```json
{
  "CreditScore": 650,
  "Gender": 1,
  "Age": 40,
  "Tenure": 3,
  "Balance": 60000.0,
  "NumOfProducts": 2,
  "HasCrCard": 1,
  "IsActiveMember": 1,
  "EstimatedSalary": 50000.0
}
```

`Gender` est encodé sous forme numérique (`0` pour Female, `1` pour Male). La réponse contient la classe prédite, son libellé et, si le modèle la fournit, une probabilité de désabonnement.

### Réentraînement

`POST /retrain` accepte des hyperparamètres facultatifs. Exemple :

```json
{
  "n_estimators": 100,
  "max_depth": 10,
  "random_state": 42
}
```

Le réentraînement est lancé en tâche de fond par FastAPI. Les valeurs autorisées pour `n_estimators` vont de 10 à 1000 ; `max_depth` peut être omis.

> **Limite à corriger avant utilisation réelle :** `prepare_data()` standardise les caractéristiques avant l’entraînement, mais `/predict` construit actuellement un vecteur à partir des valeurs brutes de la requête. Le prétraitement d’inférence doit être identique à celui de l’entraînement (par exemple en sauvegardant et réutilisant un pipeline complet) pour que les prédictions soient cohérentes. `/retrain` est également sans authentification : ne l’exposez pas à un réseau non fiable.

## Orchestration avec Prefect

Les flows peuvent être exécutés directement depuis le dépôt :

```bash
python pipeline_prefect.py --flow code
python pipeline_prefect.py --flow train
python pipeline_prefect.py --flow evaluate
python pipeline_prefect.py --flow api
python pipeline_prefect.py --flow docker
python pipeline_prefect.py --flow all
```

`code` enchaîne l’installation des dépendances, le formatage, les vérifications Flake8/Bandit et les tests. `all` exécute ces contrôles puis prépare les données, entraîne, sauvegarde et évalue le modèle. Le flow `docker` construit et pousse une image : il nécessite Docker et une authentification Docker Hub.

Pour ouvrir le tableau de bord Prefect, lancez dans un terminal :

```bash
prefect server start
```

Le tableau de bord est disponible à <http://127.0.0.1:4200>. Pour créer le service de déploiement planifié défini dans `deploiement_prefect.py`, exécutez ce fichier dans un autre terminal :

```bash
python deploiement_prefect.py
```

Ce service maintient le déploiement actif et planifie le flow complet chaque jour à 02:00 UTC.

## Suivi MLflow (optionnel)

Le code active le suivi MLflow lorsque la variable `MLFLOW_TRACKING_URI` est définie. Dans un premier terminal, démarrez le serveur :

```bash
mlflow server --host 127.0.0.1 --port 5000
```

Dans le terminal où vous lancerez l’entraînement, configurez l’URI :

**Windows (PowerShell)**

```powershell
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
python main.py --action train
```

**Linux / macOS**

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
python main.py --action train
```

L’interface MLflow est disponible à <http://127.0.0.1:5000>. Sans cette variable, l’entraînement fonctionne sans suivi MLflow.

## Monitoring Elasticsearch et Kibana (optionnel)

Le fichier `docker-compose.yml` démarre Elasticsearch et Kibana, mais pas l’API ni Prefect :

```bash
docker compose up -d
```

- Elasticsearch : <http://localhost:9200>
- Kibana : <http://localhost:5601>

Le pipeline envoie les métriques vers Elasticsearch à `http://localhost:9200`, dans l’index `mlflow-metrics`. Pour activer cet envoi, installez également le client Python Elasticsearch :

```bash
pip install elasticsearch
```

Sans ce client, l’entraînement continue et l’envoi des métriques est ignoré. Dans Kibana, créez une vue de données sur `mlflow-metrics` et utilisez `@timestamp` comme champ temporel pour explorer les événements.

Arrêtez les services lorsque vous avez terminé :

```bash
docker compose down
```

## Docker — API

Depuis la racine du dépôt, construisez l’image et démarrez le conteneur :

```bash
docker build -t churn-api .
docker run --rm -p 8000:8000 churn-api
```

L’API sera disponible sur <http://127.0.0.1:8000/docs>. Le `Dockerfile` copie le code, les données et le modèle présents dans le dépôt au moment de la construction. Il faut donc avoir généré `classifier.joblib` avant de construire l’image. Pour arrêter le conteneur, utilisez `Ctrl+C`.

## Tests

```bash
pytest -q
```

Les tests utilisent le CSV à la racine et vérifient le chargement des données, l’entraînement et la génération de prédictions.

## Structure du dépôt

| Fichier / dossier | Rôle |
| --- | --- |
| `Churn_Modelling.csv` | Données d’entraînement et de test. |
| `model_pipeline.py` | Préparation des données, entraînement, évaluation, sauvegarde et intégrations de suivi. |
| `main.py` | Point d’entrée en ligne de commande pour le pipeline ML. |
| `app.py` | API FastAPI de prédiction et de réentraînement. |
| `pipeline_prefect.py` | Définition des tâches et flows Prefect. |
| `deploiement_prefect.py` | Déploiement Prefect planifié du flow complet. |
| `test_model.py` | Tests automatisés avec pytest. |
| `Dockerfile` | Construction de l’image de l’API. |
| `docker-compose.yml` | Services Elasticsearch et Kibana. |
| `Rapport Atelier */` | Rapports et synthèses des ateliers du projet. |
| `customer_churn.ipynb` | Notebook d’expérimentation. |
| `classifier.joblib` | Modèle sérialisé utilisé par l’API ; généré ou remplacé à l’entraînement. |

## Rapports des ateliers

Les dossiers `Rapport Atelier 2` à `Rapport Atelier 7` contiennent les comptes rendus détaillés : modularisation, orchestration Prefect, API FastAPI, suivi MLflow, conteneurisation et monitoring ELK.
