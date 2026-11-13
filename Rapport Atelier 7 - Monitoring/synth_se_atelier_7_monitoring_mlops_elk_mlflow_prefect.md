# Synthèse de l'Atelier 7 : Monitoring et Observabilité en MLOps

## 1. Résumé de ce qui a été réalisé dans l'Atelier 7

Dans cet atelier, nous avons mis en place une architecture complète de **supervision (monitoring) et d'observabilité** pour suivre l'entraînement, les performances et l'exécution de notre modèle de Machine Learning (*Customer Churn*).

Voici les 4 grandes étapes accomplies :

1. **Déploiement de la stack d'observabilité :** Mise en place des conteneurs Elasticsearch et Kibana via Docker Compose, et configuration de l'environnement WSL2 (`vm.max_map_count`).
2. **Adaptation du code (`model_pipeline.py`) :** Implémentation d'un système de **double journalisation (dual-logging)**. À chaque entraînement, le script enregistre les artefacts dans **MLflow** tout en expédiant un document structuré (JSON) vers **Elasticsearch** contenant le statut, la durée (`duration_seconds`), les hyperparamètres (`n_estimators`, `max_depth`) et les métriques.
3. **Exécution orchestrée via Prefect :** Lancement du serveur Prefect (`prefect server start`) et exécution automatisée du flux d'entraînement (`python3 pipeline_prefect.py --flow train`), déclenchant la préparation des données, l'entraînement et l'indexation en temps réel.
4. **Configuration et exploration dans Kibana :**
   * Création de l'index `mlflow-metrics` et définition de son schéma (*mapping*) via la console **Dev Tools**.
   * Configuration de l'**Index Pattern** `mlflow-metrics` basé sur le champ temporel `@timestamp`.
   * Validation visuelle des logs et métriques dans l'interface **Discover**.

---

## 2. Architecture et Rôle des Outils Utilisés

Dans un projet MLOps moderne, chaque brique logicielle joue un rôle précis dans le cycle de vie du modèle :

### 🔍 Elasticsearch (Le moteur de stockage et d'indexation)
* **C'est quoi ?** Elasticsearch est un moteur de recherche et d'analyse distribué, orienté documents (NoSQL), capable de stocker et d'interroger d'énormes volumes de données en quasi temps réel.
* **Son rôle dans l'atelier :** Il agit comme notre **entrepôt centralisé de logs et de métriques**. Lorsque notre script Python termine un entraînement, il envoie un document JSON à Elasticsearch via son API REST (sur le port `9200`), qui l'indexe immédiatement dans `mlflow-metrics`.

### 📊 Kibana (L'interface de visualisation et d'analyse)
* **C'est quoi ?** Kibana est l'interface web graphique associée à Elasticsearch (le « K » de la stack ELK). Il permet d'explorer les données indexées, de créer des graphiques interactifs, des tableaux de bord (*dashboards*) et des alertes.
* **Son rôle dans l'atelier :** Il sert de **tour de contrôle visuelle** (port `5601`). Grâce à lui, nous avons défini la structure de nos données (*Dev Tools*), lié nos logs (*Index Patterns*) et inspecté en temps réel le déroulement et les performances de nos entraînements (*Discover*).

### 🧪 MLflow (Le suivi d'expériences et registre de modèles)
* **C'est quoi ?** MLflow est une plateforme open-source dédiée à la gestion du cycle de vie du Machine Learning.
* **Son rôle dans l'atelier :** Il assure la **traçabilité scientifique**. Contrairement à Elasticsearch qui se concentre sur les logs opérationnels et le monitoring global, MLflow sauvegarde les objets lourds (le modèle entraîné lui-même, les graphiques, les environnements) et permet de comparer les expériences entre elles (port `5000`).

### ⚙️ Prefect (L'orchestrateur de workflows)
* **C'est quoi ?** Prefect est un outil moderne d'orchestration de pipelines de données et de Machine Learning. Il permet de découper un script en tâches (`@task`) regroupées dans un flux (`@flow`), avec gestion des erreurs, des logs et des planifications.
* **Son rôle dans l'atelier :** Il joue le rôle de **chef d'orchestre** (port `4200`). C'est lui qui enchaîne automatiquement la préparation des données, l'entraînement du modèle, l'envoi des métriques vers Elasticsearch/MLflow et la sauvegarde du modèle final.

### 🐳 Docker & Docker Compose (La conteneurisation)
* **C'est quoi ?** Docker permet d'exécuter des applications dans des environnements isolés appelés conteneurs. Docker Compose permet de définir et de lancer plusieurs conteneurs interconnectés à l'aide d'un seul fichier YAML.
* **Son rôle dans l'atelier :** Il garantit un **déploiement rapide et reproductible** de l'infrastructure. Plutôt que d'installer manuellement Elasticsearch et Kibana (et de gérer leurs dépendances Java/système), Docker Compose a démarré les deux services déjà configurés et reliés sur un réseau virtuel commun.

---

## 3. Vue d'ensemble du Flux de Données

```text
[Données CSV] 
      │
      ▼
[Prefect Flow] ──► Préparation & Entraînement (model_pipeline.py)
      │
      ├──► [MLflow (Port 5000)]        : Sauvegarde du modèle (.joblib) & artefacts
      │
      └──► [Elasticsearch (Port 9200)] : Indexation JSON des métriques & durées
                 │
                 ▼
           [Kibana (Port 5601)]        : Exploration (Discover) & Tableaux de bord
```

---

## 4. Piste d'Excellence (Pour aller plus loin)

Pour enrichir davantage cette architecture en environnement de production, la suite Elastic propose des agents complémentaires :
* **Metricbeat :** Collecte les métriques matérielles de la machine hôte et des conteneurs Docker (utilisation CPU, RAM, espace disque).
* **Filebeat :** Surveille et expédie automatiquement les fichiers de logs générés par l'API FastAPI lors des prédictions en production.
* **Logstash :** Pipeline de traitement qui permet de filtrer, nettoyer et transformer les logs avant leur insertion dans Elasticsearch.