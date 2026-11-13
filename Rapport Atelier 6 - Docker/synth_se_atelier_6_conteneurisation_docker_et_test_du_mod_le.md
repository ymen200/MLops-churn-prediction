# Synthèse de l'Atelier 6 : Conteneurisation avec Docker et Test du Modèle ML

## 1. Résumé de l'Atelier 6

L'**Atelier 6** marque l'étape finale de mise à disposition de notre solution MLOps : la **conteneurisation**. Après avoir entraîné, suivi et exposé notre modèle via une API REST (FastAPI), nous avons empaqueté l'ensemble de l'application dans une image Docker portable et automatisé sa livraison.

* **Configuration de l'environnement Docker** : Création d'un fichier `.dockerignore` (pour exclure les fichiers inutiles et optimiser la taille de l'image) et d'un `Dockerfile` basé sur `python:3.10-slim`.
* **Construction et Convention de Nommage** : Génération de l'image locale nommée `aymen_ouerghi_5ia_mlops`.
* **Publication (Registry)** : Connexion à Docker Hub, taggage de l'image (`aymen177/aymen_ouerghi_5ia_mlops:latest`) et envoi en ligne (`docker push`).
* **Automatisation CD (Continuous Delivery)** : Intégration des tâches `build_docker_image` et `push_docker_image` dans un nouveau flux Prefect (`--flow docker`) pour automatiser le déploiement continu.

---

## 2. Utilité de la Conteneurisation en MLOps

L'utilisation de Docker dans un projet de Machine Learning répond à plusieurs enjeux critiques de production :

1. **Portabilité et Reproductibilité ("Ça marche sur ma machine")** : Le conteneur embarque le code, le modèle sérialisé (`classifier.joblib`), l'interpréteur Python et les versions exactes des bibliothèques (`requirements.txt`). L'application s'exécutera exactement de la même manière sur un ordinateur portable, un serveur sur site ou dans le Cloud.
2. **Isolation des Dépendances** : Évite les conflits entre les versions des librairies (ex. `scikit-learn`, `fastapi`, `mlflow`) avec d'autres applications hébergées sur le même serveur.
3. **Scalabilité et Déploiement Cloud** : Une image publiée sur Docker Hub peut être téléchargée et déployée en quelques secondes sur des orchestrateurs de conteneurs (Kubernetes, AWS ECS, Azure Container Instances) pour absorber une forte charge de requêtes de prédiction.
4. **Intégration Continue / Livraison Continue (CI/CD)** : Facilite l'automatisation des mises à jour. Dès qu'un modèle est réentraîné et validé, une nouvelle image peut être construite et poussée automatiquement via Prefect.

---

## 3. Guide Pratique : Comment lancer un conteneur pour tester le modèle ML

Voici la procédure complète pour récupérer, exécuter et tester le modèle conteneurisé :

### Étape 1 : Récupérer ou construire l'image
Si l'image n'est pas en local, vous pouvez la télécharger directement depuis Docker Hub :
```bash
docker pull aymen177/aymen_ouerghi_5ia_mlops:latest
```
*(Ou la construire localement depuis la racine du projet : `docker build -t aymen_ouerghi_5ia_mlops .`)*

### Étape 2 : Démarrer le conteneur en arrière-plan
Exécutez le conteneur en reliant le port interne de FastAPI (`8000`) à un port de votre machine hôte (`8000`) :
```bash
docker run -d -p 8000:8000 --name test-churn-api aymen177/aymen_ouerghi_5ia_mlops:latest
```
* `-d` : Exécute le conteneur en mode détaché (arrière-plan).
* `-p 8000:8000` : Redirige le trafic du port 8000 de votre machine vers le port 8000 du conteneur.
* `--name` : Attribue un nom lisible au conteneur en cours d'exécution.

### Étape 3 : Vérifier l'état et les logs du conteneur
Assurez-vous que le serveur Uvicorn a bien démarré sans erreur à l'intérieur du conteneur :
```bash
docker ps
docker logs test-churn-api
```

### Étape 4 : Tester le modèle ML (Inférence)

#### Option A : Via l'interface interactive Swagger (Navigateur)
1. Ouvrez votre navigateur à l'adresse : **`http://127.0.0.1:8000/docs`**
2. Déroulez la route **`POST /predict`** et cliquez sur **Try it out**.
3. Saisissez les données d'un client au format JSON et cliquez sur **Execute** pour obtenir la prédiction de Churn.

#### Option B : Via une requête `curl` (Terminal)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'Content-Type: application/json' \
  -d '{
  "CreditScore": 650,
  "Gender": 1,
  "Age": 40,
  "Tenure": 3,
  "Balance": 60000.0,
  "NumOfProducts": 2,
  "HasCrCard": 1,
  "IsActiveMember": 1,
  "EstimatedSalary": 50000.0
}'
```

### Étape 5 : Arrêter et nettoyer le conteneur après le test
Une fois les tests validés, arrêtez et supprimez le conteneur pour libérer le port `8000` :
```bash
docker stop test-churn-api
docker rm test-churn-api
```