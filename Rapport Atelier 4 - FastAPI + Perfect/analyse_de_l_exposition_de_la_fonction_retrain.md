# Analyse Architecture MLOps : Exposer un Endpoint `/retrain` via FastAPI

## 1. Contexte et Objectif

La perspective d'exposer une route `POST /retrain` dans l'API REST FastAPI vise à permettre le réentraînement dynamique du modèle de Machine Learning en lui passant de nouveaux hyperparamètres (par exemple `n_estimators`, `max_depth`) au format JSON.

---

## 2. Avantages (Pourquoi l'implémenter)

* **Continuous Training (CT) :** Illustre le concept de réentraînement continu en MLOps sans intervention manuelle directe sur le serveur.
* **Flexibilité des hyperparamètres :** Permet d'expérimenter et de tester l'impact de différents hyperparamètres à la volée via une simple requête HTTP POST.
* **Découplage de la configuration :** Les paramètres du modèle ne sont plus codés en dur dans les scripts, mais injectables à distance.

---

## 3. Risques et Limites Techniques en Production

1. **Blocage Synchrone et Timeouts HTTP :**
   * L'entraînement d'un modèle ML est une tâche gourmande en CPU/RAM.
   * Si la requête HTTP attend la fin de l'entraînement pour répondre, la connexion risque d'expirer (*Gateway Timeout 504*).

2. **Concurrence et Verrouillage de Fichiers (*Race Conditions*) :**
   * Si la route `/retrain` écrase le fichier `classifier.joblib` pendant qu'une requête `/predict` essaie simultanément de le lire, le service d'inférence risque de crasher ou de retourner une erreur de fichier corrompu.

3. **Sécurité et Épuisement des Ressources :**
   * Sans authentification ni limiteur de débit (*Rate Limiting*), des appels répétés à `/retrain` peuvent saturer le serveur et le rendre indisponible (*Denial of Service*).

---

## 4. Recommandations MLOps & Bonnes Pratiques

### A. L'approche Simple (Pour Exercice / PoC)
Pour un cadre d'atelier ou un prototype, on peut ajouter la route de manière synchrone ou en tâche d'arrière-plan basique (`BackgroundTasks` de FastAPI).

### B. L'approche MLOps Industrielle (Délégation à l'Orchestrateur)
En environnement de production, l'API FastAPI ne doit pas exécuter le réentraînement elle-même :
1. L'utilisateur ou le système envoie une requête à `POST /retrain`.
2. FastAPI enregistre la demande et déclenche un flux Prefect (`train_flow`) de manière asynchrone via l'API client Prefect.
3. Prefect gère l'entraînement dans un processus dédié, met à jour le registre de modèles, puis informe l'API qu'une nouvelle version du modèle est disponible.
4. L'API retourne immédiatement un code `202 Accepted` avec un ID de suivi d'exécution.

---

## 5. Tableau Comparatif des Approches

| Critère | Réentraînement Synchrone dans FastAPI | Tâche Async / Déclenchement via Prefect |
| :--- | :--- | :--- |
| **Complexité** | Faible | Moyenne |
| **Gestion du Timeout** | Risque élevé de timeout | Aucun risque |
| **Observabilité** | Logs simples dans Uvicorn | Suivi complet dans le Dashboard Prefect |
| **Robustesse MLOps** | Faible (environnement dev/PoC) | Elevée (Prêt pour la Production) |