import os
from fastapi import BackgroundTasks, FastAPI, HTTPException
import joblib
from model_pipeline import evaluate_model, prepare_data, save_model, train_model
import numpy as np
from pydantic import BaseModel, Field

app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "API REST pour la prédiction et le réentraînement du modèle Customer"
        " Churn"
    ),
    version="1.1.0",
)

MODEL_PATH = "classifier.joblib"

# Variable globale pour stocker le modèle en mémoire
model = None


def reload_model():
  global model
  if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print(f"Modèle rechargé depuis {MODEL_PATH}")


# Chargement initial du modèle au démarrage
reload_model()


# Schéma pour la prédiction
class CustomerFeatures(BaseModel):
  CreditScore: int = Field(..., example=650)
  Gender: int = Field(..., example=1, description="0 pour Female, 1 pour Male")
  Age: int = Field(..., example=40)
  Tenure: int = Field(..., example=3)
  Balance: float = Field(..., example=60000.0)
  NumOfProducts: int = Field(..., example=2)
  HasCrCard: int = Field(..., example=1, description="0 ou 1")
  IsActiveMember: int = Field(..., example=1, description="0 ou 1")
  EstimatedSalary: float = Field(..., example=50000.0)


# Schéma pour les hyperparamètres de réentraînement (Perspective Atelier 4)
class RetrainParams(BaseModel):
  n_estimators: int = Field(
      100, ge=10, le=1000, description="Nombre d'arbres dans le Random Forest"
  )
  max_depth: int | None = Field(
      None, description="Profondeur maximale des arbres (optionnel)"
  )
  random_state: int = Field(
      42, description="Graine aléatoire pour la reproductibilité"
  )


@app.get("/")
def home():
  return {"message": "Bienvenue sur l'API de Customer Churn (Predict & Retrain)"}


@app.post("/predict")
def predict(features: CustomerFeatures):
  """Effectue une prédiction en fonction des caractéristiques fournies."""
  if model is None:
    raise HTTPException(
        status_code=500,
        detail="Le modèle n'est pas disponible. Entraînez-le d'abord.",
    )

  try:
    data = np.array([[
        features.CreditScore,
        features.Gender,
        features.Age,
        features.Tenure,
        features.Balance,
        features.NumOfProducts,
        features.HasCrCard,
        features.IsActiveMember,
        features.EstimatedSalary,
    ]])

    prediction = model.predict(data)[0]
    probability = (
        model.predict_proba(data)[0][1]
        if hasattr(model, "predict_proba")
        else None
    )

    return {
        "prediction": int(prediction),
        "churn_status": (
            "Exited (Client parti)"
            if prediction == 1
            else "Not Exited (Client fidèle)"
        ),
        "churn_probability": (
            round(float(probability), 4) if probability is not None else "N/A"
        ),
    }
  except Exception as e:
    raise HTTPException(
        status_code=400, detail=f"Erreur lors de la prédiction: {str(e)}"
    )


def execute_retrain(params: RetrainParams):
  """Fonction d'arrière-plan pour réentraîner le modèle et mettre à jour le fichier."""
  print(f"--- Début du réentraînement avec params: {params.dict()} ---")
  X_train, X_test, y_train, y_test = prepare_data("Churn_Modelling.csv")

  # Entraînement avec les nouveaux hyperparamètres
  new_model = train_model(
      X_train,
      y_train,
      n_estimators=params.n_estimators,
      max_depth=params.max_depth,
      random_state=params.random_state,
  )

  # Évaluation
  acc, _ = evaluate_model(new_model, X_test, y_test)

  # Sauvegarde et rechargement en mémoire
  save_model(new_model, MODEL_PATH)
  reload_model()
  print(
      f"--- Réentraînement terminé avec succès ! Nouvelle Accuracy: {acc*100:.2f}% ---"
  )


@app.post("/retrain")
def retrain(params: RetrainParams, background_tasks: BackgroundTasks):
  """Point de terminaison POST pour déclencher le réentraînement du modèle."""
  # Lance l'entraînement en arrière-plan
  background_tasks.add_task(execute_retrain, params)

  return {
      "message": "Le réentraînement du modèle a été lancé en arrière-plan.",
      "hyperparameters": params.dict(),
      "status": "Processing",
  }