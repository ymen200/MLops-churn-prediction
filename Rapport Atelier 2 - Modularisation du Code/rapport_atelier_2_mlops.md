# Atelier 2 : Modularisation du Code et Pipeline MLOps (Customer Churn)

Ce document résume l'ensemble des étapes et concepts clés mis en œuvre lors de l'**Atelier 2**, consacré à la modularisation et à la création d'un pipeline Machine Learning opérationnel pour la prédiction du désabonnement client (*Customer Churn*).

---

## 1. Modularisation du Code (`model_pipeline.py`)

Afin de passer d'un environnement d'expérimentation (Jupyter Notebook) à un code maintenable et prêt pour la production, la logique métier a été découpée en fonctions réutilisables :

* **Préparation des données (`prepare_data`) :**
  * Chargement du fichier `Churn_Modelling.csv`.
  * Encodage des variables catégorielles (ex. `Gender` via `LabelEncoder`).
  * Nettoyage et suppression des colonnes non pertinentes (`Surname`, `Geography`, `RowNumber`, `CustomerId`).
  * Séparation des variables explicatives ($X$) et de la cible ($y$).
  * Division en jeu d'entraînement et jeu de test (`train_test_split`).
  * Standardisation des caractéristiques (`StandardScaler`).

* **Entraînement (`train_model`) :**
  * Initialisation et ajustement d'un modèle de classification Random Forest (`RandomForestClassifier`).

* **Évaluation (`evaluate_model`) :**
  * Calcul de l'**Accuracy** (~85,60 % de bonnes prédictions).
  * Génération du **Rapport de classification** (*Precision*, *Recall*, *F1-score*) pour évaluer précisément la prédiction des départs clients (Classe 1) par rapport aux clients fidèles (Classe 0).
  * Matrice de confusion pour visualiser la répartition des erreurs.

* **Gestion du modèle (`save_model` / `load_model`) :**
  * Sérialisation du modèle entraîné à l'aide de la bibliothèque `joblib` (`classifier.joblib`), évitant ainsi le ré-entraînement systématique à chaque exécution.

---

## 2. Interface en Ligne de Commande (`main.py`)

La mise en place d'un point d'entrée unique piloté par `argparse` permet d'exécuter et d'automatiser les tâches de pipeline directement depuis le terminal :

```bash
# Lancer la chaîne complète (préparation, entraînement, évaluation, sauvegarde)
python3 main.py --action all

# Charger un modèle existant et l'évaluer sans ré-entraîner
python3 main.py --action evaluate
```

---

## 3. Environnement d'Exécution (WSL et PyCharm)

L'exécution du projet est validée sous **WSL** (Windows Subsystem for Linux) couplé à **PyCharm** :
* Exécution du code dans un environnement Linux natif et isolé.
* Garantie de reproductibilité et de cohérence avec les environnements de déploiement en production.
* Intégration fluide du workflow de développement sous Windows.

📂 1. Structure du Projet
* Le projet est organisé autour d'un dossier nommé projet_MLOPS contenant les éléments suivants :

* model_pipeline.py : Fichier central contenant toutes les fonctions modulaires de traitement, d'entraînement, d'évaluation et de sérialisation.

* main.py : Point d'entrée en ligne de commande (CLI) pour orchestrer l'exécution du pipeline.

* churn_Modelling.csv : Le jeu de données source utilisé pour la prédiction du désabonnement.

* classifier.joblib : Fichier binaire généré contenant le modèle entraîné.