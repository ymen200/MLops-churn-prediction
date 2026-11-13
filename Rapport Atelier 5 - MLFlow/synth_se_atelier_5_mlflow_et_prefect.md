# Synthèse de l'Atelier 5 : Introduction à MLflow & Comparaison avec Prefect

## 1. Résumé de l'Atelier 5 : Introduction à MLflow

L'**Atelier 5** est consacré à l'intégration de **MLflow** dans le projet MLOps afin d'assurer un suivi rigoureux et standardisé des expérimentations de Machine Learning.

* **Objectifs principaux** : Comprendre le rôle de MLflow dans le suivi des exécutions (*runs*) et la gestion des modèles, puis configurer l'outil au sein du projet.
* **Contenu et Mise en œuvre** :
  * Enregistrement des hyperparamètres d'entraînement via `mlflow.log_param()`.
  * Suivi des métriques de performance (comme l'Accuracy) via `mlflow.log_metric()`.
  * Sauvegarde et journalisation du modèle entraîné sous forme d'artefact avec `mlflow.sklearn.log_model()` (en autorisant le type sécurisé `sklearn.tree._tree.Tree` via `skops_trusted_types`).
  * Visualisation de l'ensemble des exécutions dans l'interface graphique locale de MLflow (`http://127.0.0.1:5000`).
* **Livrables** : Un projet entièrement intégré avec MLflow permettant de tracer, comparer et inspecter les différents modèles générés, ainsi qu'une commande automatisée pour démarrer l'interface MLflow.

---

## 2. Le But de MLflow

**MLflow** est une plateforme open-source conçue pour gérer l'intégralité du **cycle de vie des modèles de Machine Learning**. Ses buts fondamentaux sont :

* **La Traçabilité et la Reproductibilité** : Conserver une trace exacte de chaque entraînement (quels paramètres ont été utilisés, quelles données ont servi, quel code a été exécuté).
* **Le Suivi des Expériences (MLflow Tracking)** : Centraliser et comparer les métriques (précision, perte, etc.) de plusieurs dizaines de modèles pour identifier le plus performant.
* **La Gestion des Artefacts** : Stocker proprement les fichiers binaires des modèles et leurs dépendances pour faciliter leur passage en production.

---

## 3. Différence entre MLflow et Prefect

Bien que ces deux outils collaborent étroitement dans une architecture MLOps moderne, ils ont des rôles et des responsabilités totalement complémentaires :

| Caractéristique | Prefect | MLflow |
| :--- | :--- | :--- |
| **Rôle principal** | **Orchestrateur de workflows** (Exécution et automatisation de pipelines). | **Plateforme de suivi et de gestion du cycle de vie ML** (MLOps Tracking & Registry). |
| **Que fait-il ?** | Il planifie, déclenche, automatise et surveille l'enchaînement des tâches techniques (nettoyage $\rightarrow$ entraînement $\rightarrow$ déploiement API). | Il enregistre la "science" du modèle : hyperparamètres, métriques de performance, courbes et fichiers de modèles (artefacts). |
| **Interface Web** | Affiche l'état des flux (*Flow Runs* et *Task Runs*), les erreurs d'exécution et les logs d'infrastructure. | Affiche les tableaux comparatifs d'expériences, les graphiques de performances et les détails des modèles entraînés. |
| **Analogie** | C'est le **chef d'orchestre** qui s'assure que chaque étape s'exécute dans le bon ordre et gère les pannes. | C'est le **cahier de laboratoire** du Data Scientist où l'on consigne précisément les résultats, les dosages (hyperparamètres) et les modèles produits. |

### Synergie dans le projet :
Dans notre architecture, **Prefect** automatise et orchestre le déclenchement du code d'entraînement (`train_flow`), tandis que **MLflow** capture, mesure et stocke intelligemment les performances et artefacts du modèle généré lors de cette exécution.