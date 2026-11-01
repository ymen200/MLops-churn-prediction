import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


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


def train_model(X_train, y_train, n_estimators=100, max_depth=None, random_state=42):
  """Entraîne le modèle Random Forest avec des hyperparamètres configurables."""
  rf = RandomForestClassifier(
      n_estimators=n_estimators, max_depth=max_depth, random_state=random_state
  )
  rf.fit(X_train, y_train)
  return rf


def evaluate_model(model, X_test, y_test):
  """Évalue les performances du modèle et affiche les métriques."""
  y_pred = model.predict(X_test)
  acc = accuracy_score(y_test, y_pred)
  report = classification_report(y_test, y_pred)
  matrix = confusion_matrix(y_test, y_pred)

  print(f"Accuracy score: {acc * 100:.2f}%")
  print("\nClassification Report:\n", report)
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