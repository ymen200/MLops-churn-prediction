# Synthèse de l'Atelier 4 : Exposition de la fonction `predict()` via FastAPI & Intégration Prefect

---

## 1. Pourquoi transformer un modèle ML en API REST avec FastAPI ?

Jusqu'à l'Atelier 3, le modèle de prédiction du désabonnement (*Customer Churn*) était **statique** et confiné à un environnement de développement local :
* Il fallait exécuter un script Python (`main.py` ou `pipeline_prefect.py`) pour obtenir des prédictions.
* Seul un développeur ayant accès au projet et au fichier `classifier.joblib` pouvait interagir avec le modèle.

### Les apports de FastAPI :
1. **Interopérabilité et Découplage :** En exposant la fonction `predict()` sous forme de route HTTP `POST /predict`, le modèle devient un **service indépendant**. Une application Web (React, Angular), une application mobile (Flutter, iOS), ou un système CRM d'entreprise peut interroger le modèle via une simple requête JSON sans savoir comment Python ou Scikit-learn fonctionnent.
2. **Validation des données (Pydantic) :** Les schémas Pydantic garantissent que les données entrantes (ex: `CreditScore`, `Age`, `Balance`) sont du bon type avant d'être soumises au modèle, évitant ainsi les erreurs à l'exécution.
3. **Documentation interactive (Swagger UI) :** FastAPI génère automatiquement l'interface `/docs` permettant d'expérimenter et de tester des requêtes JSON directement dans le navigateur sans outils externes.

---

## 2. Pourquoi lier Prefect et FastAPI ?

Il peut sembler surprenant de lancer un serveur Web (FastAPI / Uvicorn) via un orchestrateur de pipelines ML (Prefect). Pourtant, cette association offre des avantages fondamentaux dans une architecture MLOps complète :

### A. Centralisation du contrôle et de l'orchestration
En intégrant la tâche `run_api_task` et le flow `api` dans Prefect (`python pipeline_prefect.py --flow api`), vous unifiez la gestion de l'ensemble du cycle de vie sous un **seul point d'entrée et une CLI unique** :
* `python pipeline_prefect.py --flow train` $\rightarrow$ Entraîne et sauvegarde le modèle.
* `python pipeline_prefect.py --flow evaluate` $\rightarrow$ Calcule les métriques.
* `python pipeline_prefect.py --flow api` $\rightarrow$ Déploie le service Web d'inférence.

### B. Traçabilité, Observabilité et Logging
Lorsque Uvicorn tourne dans un flow Prefect :
* Le serveur de suivi Prefect enregistre l'état du service (Start, Failure, Restart).
* Les logs de démarrage et les éventuelles erreurs d'exécution de FastAPI sont centralisés dans le Dashboard Prefect.
* En cas de panne ou d'erreur sur le serveur d'API, Prefect peut lever des alertes ou gérer des mécanismes d'auto-retentative (*retries*).

### C. Préparation à l'automatisation Continuous Deployment (CD)
Dans un pipeline d'intégration/déploiement continu automatisé :
1. Un nouveau jeu de données arrive.
2. Prefect exécute les tests de qualité et réentraîne le modèle (`train_flow`).
3. Prefect valide les métriques du nouveau modèle (`evaluate_flow`).
4. Si le nouveau modèle est plus performant, Prefect redémarre ou met à jour le service API (`api_flow`) pour qu'il prenne en compte la nouvelle version du fichier `.joblib`.

---

## 3. Bilan de l'Atelier 4

| Composant | Rôle MLOps |
| :--- | :--- |
| **Modèle (`classifier.joblib`)** | Intelligence décisionnelle entraînée. |
| **FastAPI (`app.py`)** | Couche d'exposition HTTP permettant aux clients externes d'envoyer des données et de recevoir des prédictions. |
| **Uvicorn** | Serveur web ASGI haute performance pour faire tourner l'application FastAPI. |
| **Prefect (`pipeline_prefect.py`)** | Chef d'orchestre assurant le déclenchement, le suivi et la gestion unifiée du pipeline et du service d'inférence. |