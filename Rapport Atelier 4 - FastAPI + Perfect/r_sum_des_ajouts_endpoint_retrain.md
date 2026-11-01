# Résumé des Modificatifs : Intégration du Réentraînement (`/retrain`) dans FastAPI

## 1. Vue d'Ensemble
Dans cette étape complémentaire de l'**Atelier 4**, nous avons fait évoluer le service REST pour qu'il ne se limite plus uniquement à la prédiction (`/predict`), mais qu'il supporte également le **réentraînement continu (*Continuous Training*)** à travers un point de terminaison dédié `POST /retrain`.

---

## 2. Détail des Modifications par Fichier

### A. Adaptation de la logique ML (`model_pipeline.py`)
* **Paramétrage des hyperparamètres** : La fonction `train_model` accepte désormais des paramètres configurables (`n_estimators`, `max_depth`, `random_state`) au lieu de valeurs codées en dur.
* **Flexibilité** : Permet de tester des modèles avec différentes profondeurs d'arbres ou différents nombres d'estimateurs directement depuis les requêtes API.

### B. Évolution de l'API REST (`app.py`)
* **Schéma Pydantic `RetrainParams`** : Validation stricte des données entrantes pour les hyperparamètres (bornes min/max, types).
* **Tâches en arrière-plan (`BackgroundTasks`)** :
  * Exécution du réentraînement de manière asynchrone pour éviter les blocages de connexions (*Timeouts HTTP*).
  * Réponse immédiate de l'API avec un statut `200 OK` ("Processing").
* **Mise à jour à chaud du modèle (`reload_model`)** : Une fois l'entraînement terminé, l'instance du modèle chargée en mémoire globale est automatiquement rafraîchie avec le nouveau fichier `classifier.joblib`.

### C. Maintien de l'Orchestration (`pipeline_prefect.py`)
* **Couverture globale** : Le fichier `app.py` révisé reste entièrement intégrable et supervisé via le flux `api` de Prefect (`python pipeline_prefect.py --flow api`).

---

## 3. Flux de Fonctionnement (`POST /retrain`)

1. **Requête Client** : L'utilisateur envoie une requête JSON avec les nouveaux hyperparamètres sur `http://127.0.0.1:8000/retrain`.
2. **Réponse API** : FastAPI valide la structure via Pydantic et retourne immédiatement un accusé de réception.
3. **Exécution Async** : En arrière-plan, le serveur prépare les données, réentraîne le Random Forest, réévalue l'accuracy et sauvegarde le nouveau modèle.
4. **Mise à jour** : Le modèle en mémoire est rechargé sans interrompre la disponibilité des requêtes `/predict`.