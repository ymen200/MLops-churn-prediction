# Rapport d'Atelier 3 : Orchestration du Pipeline MLOps avec Prefect

## 1. Introduction et Objectifs
L'objectif principal de cet atelier était de transformer un code Machine Learning modulaire en un **pipeline MLOps complètement orchestré, automatisé et observable** à l'aide de la plateforme **Prefect**.

En passant de simples scripts à un workflow d'orchestration, le projet gère désormais de manière automatique le contrôle de qualité du code, les tests unitaires, le prétraitement des données, l'entraînement du modèle, sa sauvegarde et son évaluation.

---

## 2. Architecture du Pipeline et Composants Clefs

Le pipeline a été découpé en plusieurs fichiers structurés, garantissant la séparabilité des responsabilités (SOC - *Separation of Concerns*) :

### A. Pipeline de Machine Learning (`model_pipeline.py`)
Contient toute la logique métier pour la prédiction du désabonnement client (*Customer Churn*) :
* **`prepare_data`** : Chargement du fichier `Churn_Modelling.csv`, encodage des variables qualitatives (`Gender`), nettoyage des identifiants non pertinents, division du jeu de données (Train/Test) et standardisation des caractéristiques (`StandardScaler`).
* **`train_model`** : Entraînement d'un modèle de classification par forêt aléatoire (`RandomForestClassifier`).
* **`evaluate_model`** : Calcul des métriques globales (Accuracy) et détaillées (Precision, Recall, F1-Score).
* **`save_model` & `load_model`** : Sérialisation et chargement du modèle binaire via `joblib`.

### B. Validation et Tests Unitaires (`test_model.py`)
Mise en place de tests automatisés via **`pytest`** pour vérifier le bon comportement des fonctions :
* Validation du chargement et du découpage des données.
* Vérification de l'instanciation du modèle d'entraînement.
* Validation du processus de prédiction sur le jeu de test.

### C. Définition des Tâches et des Flux Prefect (`pipeline_prefect.py`)
Ce fichier constitue le cœur de l'orchestration. Les fonctions sont décorées avec `@task` et `@flow` de Prefect.

1. **Tâches de suivi du code (Code Quality & Security) :**
   * **Installation des dépendances** : Vérification des paquetages via `requirements.txt`.
   * **Formatage du code** : Alignement du style de code avec `black`.
   * **Qualité du code** : Audit statique du code via `flake8`.
   * **Sécurité du code** : Recherche de vulnérabilités avec `bandit`.
   * **Tests unitaires** : Exécution automatique de la suite `pytest`.

2. **Flux de travail (`Flows`) :**
   * **`code`** : Exécute uniquement la chaîne de contrôle de qualité et de sécurité.
   * **`train`** : Prépare les données, entraîne et sauvegarde le modèle.
   * **`evaluate`** : Charge un modèle existant et calcule ses métriques.
   * **`all`** : Enchaîne la totalité des étapes (Quality Check $\rightarrow$ Pipeline ML complet).

### D. Automatisation et Planification (`deploiement_prefect.py`)
Ce fichier gère l'enregistrement et la planification des flux auprès du serveur central :
* Configuration d'une planification automatique (**Cron Schedule**) réglée quotidiennement à 02:00 AM UTC.
* Tagging des déploiements (`full-pipeline`, `mlops`, `training`, `evaluation`) pour faciliter la gestion et le suivi sur l'interface graphique.

---

## 3. Architecture d'Exécution Distribuée

Pour exécuter et suivre le pipeline en conditions réelles, une architecture à trois terminaux a été déployée et validée sous **WSL** (Windows Subsystem for Linux) :

1. **Terminal 1 : Le Serveur (`prefect server start`)**
   * Sert de "cerveau" central pour la gestion des états, la base de données SQLite et l'interface utilisateur web (**Dashboard** sur `http://localhost:4200`).
2. **Terminal 2 : Le Worker / Service d'Exécution**
   * Écoute le serveur, récupère les tâches en attente dans la file (`default-agent-pool`) et exécute les flux directement dans le répertoire du projet.
3. **Terminal 3 : Le Déclencheur (`prefect deployment run`)**
   * Permet d'envoyer manuellement des ordonnancements d'exécution au serveur (ex: `prefect deployment run 'all/ml-pipeline-all'`).

---

## 4. Résultats et Bilan

* **Exécution réussie :** Le flux complet (`all`) s'est exécuté avec succès, validant les **9 tâches** prévues (Quality, Security, Tests, Prep Data, Train, Save, Evaluate).
* **Indicateurs clés :**
  * Taux de succès des tâches : **100% (Completed)**.
  * Statut visuel validé au vert dans le tableau de bord Prefect.
* **Bénéfices MLOps :**
  * **Traçabilité** : Chaque exécution possède un identifiant unique et des journaux d'exécution (*logs*) consultables à tout moment.
  * **Reproductibilité** : L'environnement et l'enchaînement des étapes sont strictement encadrés et répétables.
  * **Qualité garantie** : Pas de mise en entraînement du modèle sans passage préalable des tests unitaires et des audits de sécurité.