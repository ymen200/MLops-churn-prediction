from datetime import datetime
import os
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

try:
  import mlflow  # type: ignore[import-not-found]
  import mlflow.sklearn  # type: ignore[import-not-found]
except ModuleNotFoundError:
  mlflow = None  # type: ignore[assignment]

try:
  from elasticsearch import Elasticsearch  # type: ignore[import-not-found]
except ModuleNotFoundError:
  Elasticsearch = None  # type: ignore[assignment]

# Configuration du serveur de tracking MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", None)
if MLFLOW_TRACKING_URI and mlflow is not None:
  mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
  mlflow.set_experiment("Customer_Churn_Experiment")


def send_to_elasticsearch(
    run_id,
    run_name,
    experiment_id,
    experiment_name,
    status,
    duration_seconds,
    train_accuracy,
    n_estimators,
    max_depth,
    params,
    metrics,
):
  """Envoie les métriques et logs d'entraînement vers Elasticsearch (Atelier 7)[cite: 10, 11]."""
  if Elasticsearch is None:
    print("Module elasticsearch non installé. Ignoré.")
    return
  try:
    es = Elasticsearch("http://localhost:9200")
    document = {
        "@timestamp": datetime.now().isoformat(),
        "run_id": str(run_id),
        "run_name": str(run_name),
        "experiment_id": str(experiment_id),
        "experiment_name": str(experiment_name),
        "status": str(status),
        "duration_seconds": float(duration_seconds),
        "metric_train_accuracy": (
            float(train_accuracy) if train_accuracy is not None else 0.0
        ),
        "metric_prediction": 0.0,
        "param_n_estimators": str(n_estimators),
        "param_max_depth": str(max_depth) if max_depth is not None else "None",
        "params": params,
        "metrics": metrics,
    }
    es.index(index="mlflow-metrics", document=document)
    print("Données de monitoring envoyées à Elasticsearch avec succès.")
  except Exception as e:
    print(f"Erreur lors de l'envoi vers Elasticsearch : {e}")


def prepare_data(filepath="Churn_Modelling.csv"):
  """Charge et prétraite les données du fichier CSV."""
  df = pd.read_csv(filepath)

  # Encodage de la variable Gender
  encoder = LabelEncoder()
  df["Gender"] = encoder.fit_transform(df["Gender"])

  # Suppression des colonnes non pertinentes
  columns_to_drop = ["Surname", "Geography", "RowNumber", "CustomerId"]
  df = df.drop(
      columns=[col for col in columns_to_drop if col in df.columns], axis=1
  )

  # Séparation Features (X) et Target (y)
  X = df.drop(["Exited"], axis=1)
  y = df["Exited"]

  # Division train/test
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.2, random_state=1
  )

  # Standardisation des caractéristiques
  scaler = StandardScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)

  return X_train_scaled, X_test_scaled, y_train, y_test


def train_model(
    X_train, y_train, n_estimators=100, max_depth=None, random_state=42
):
  """Entraîne le modèle Random Forest, trace avec MLflow et indexe dans Elasticsearch[cite: 10, 11]."""
  start_time = time.time()
  run_id = None
  run_name = "RandomForest_Training"
  experiment_id = "1"
  experiment_name = "Customer_Churn_Experiment"
  status = "FINISHED"

  use_mlflow = mlflow is not None and MLFLOW_TRACKING_URI is not None

  if use_mlflow:
    run = mlflow.start_run(run_name=run_name)
    run_id = run.info.run_id
    experiment_id = run.info.experiment_id
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth if max_depth is not None else "None")
    mlflow.log_param("random_state", random_state)

  rf = RandomForestClassifier(
      n_estimators=n_estimators, max_depth=max_depth, random_state=random_state
  )
  rf.fit(X_train, y_train)

  duration = time.time() - start_time

  if use_mlflow:
    mlflow.sklearn.log_model(
        rf,
        artifact_path="model",
        skops_trusted_types=["sklearn.tree._tree.Tree"],
    )
    mlflow.end_run()
    print("Modèle enregistré avec succès dans MLflow.")

  # Préparation des paramètres et métriques pour Elasticsearch
  params = {
      "n_estimators": str(n_estimators),
      "max_depth": str(max_depth) if max_depth is not None else "None",
      "random_state": str(random_state),
  }
  metrics = {"duration_seconds": duration}

  # Envoi vers Elasticsearch (Étape 3 du TP)[cite: 11]
  send_to_elasticsearch(
      run_id=run_id or "local_run",
      run_name=run_name,
      experiment_id=experiment_id,
      experiment_name=experiment_name,
      status=status,
      duration_seconds=duration,
      train_accuracy=0.0,
      n_estimators=n_estimators,
      max_depth=max_depth,
      params=params,
      metrics=metrics,
  )

  return rf


def evaluate_model(model, X_test, y_test):
  """Évalue les performances du modèle, affiche les métriques, les log dans MLflow et Elasticsearch[cite: 10, 11]."""
  y_pred = model.predict(X_test)
  acc = accuracy_score(y_test, y_pred)
  report = classification_report(y_test, y_pred)
  matrix = confusion_matrix(y_test, y_pred)

  print(f"Accuracy score: {acc * 100:.2f}%")
  print("\nClassification Report:\n", report)

  run_id = "evaluation_run"
  if mlflow is not None:
    if mlflow.active_run():
      active_run = mlflow.active_run()
      run_id = active_run.info.run_id
      mlflow.log_metric("accuracy", acc)
    else:
      with mlflow.start_run(run_name="Evaluation_Only") as run:
        run_id = run.info.run_id
        mlflow.log_metric("accuracy", acc)
  else:
    print("MLflow n'est pas installé ou non configuré.")

  # Envoi de la métrique d'évaluation vers Elasticsearch
  send_to_elasticsearch(
      run_id=run_id,
      run_name="Evaluation_Only",
      experiment_id="1",
      experiment_name="Customer_Churn_Experiment",
      status="FINISHED",
      duration_seconds=1.0,
      train_accuracy=acc,
      n_estimators="100",
      max_depth="None",
      params={},
      metrics={"accuracy": acc},
  )

  return acc, matrix


def save_model(model, filepath="classifier.joblib"):
  """Sauvegarde le modèle entraîné à l'aide de joblib."""
  joblib.dump(model, filepath)
  print(f"Modèle sauvegardé avec succès dans : {filepath}")


def load_model(filepath="classifier.joblib"):
  """Charge un modèle sauvegardé."""
  model = joblib.load(filepath)
  print(f"Modèle chargé depuis : {filepath}")
  return model