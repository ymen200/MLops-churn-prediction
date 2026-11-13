import argparse
import importlib
import subprocess

try:
  prefect = importlib.import_module("prefect")
except ModuleNotFoundError as exc:
  if exc.name != "prefect":
    raise
  raise RuntimeError(
      "Prefect is required to run this pipeline. Install it with 'pip install prefect'."
  ) from exc

flow = prefect.flow
task = prefect.task
from model_pipeline import (
    evaluate_model,
    load_model,
    prepare_data,
    save_model,
    train_model,
)

TARGET_FILES = ["model_pipeline.py", "main.py", "pipeline_prefect.py", "app.py"]
DOCKER_IMAGE_NAME = "aymen_ouerghi_5ia_mlops"  # Nom d'image exigé par l'atelier[cite: 8]
DOCKER_HUB_USER = (  # Remplace par ton pseudo Docker Hub si besoin
    "aymen177"
)


@task(name="Installer les dépendances")
def install_dependencies():
  print("Vérification et installation des dépendances...")
  subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)


@task(name="Formatage du code")
def format_code():
  print("Formatage du code avec black...")
  subprocess.run(["black"] + TARGET_FILES, check=False)


@task(name="Qualité du code")
def code_quality():
  print("Vérification de la qualité du code avec flake8...")
  subprocess.run(["flake8"] + TARGET_FILES, check=False)


@task(name="Sécurité du code")
def code_security():
  print("Analyse de sécurité du code avec bandit...")
  subprocess.run(["bandit", "-r"] + TARGET_FILES, check=False)


@task(name="Tests unitaires")
def unit_tests():
  print("Exécution des tests unitaires avec pytest...")
  subprocess.run(["pytest", "test_model.py"], check=True)


@task(name="Préparation des données")
def prepare_data_task():
  print("Préparation des données...")
  return prepare_data("Churn_Modelling.csv")


@task(name="Entrainement du modèle")
def train_model_task(X_train, y_train):
  print("Entraînement du modèle Random Forest...")
  return train_model(X_train, y_train)


@task(name="Sauvegarder le modèle")
def save_model_task(model):
  print("Sauvegarde du modèle...")
  save_model(model)


@task(name="Charger le modèle")
def load_model_task():
  print("Chargement du modèle...")
  return load_model()


@task(name="Evaluer le modèle")
def evaluate_model_task(model, X_test, y_test):
  print("Évaluation du modèle...")
  return evaluate_model(model, X_test, y_test)


@task(name="Lancer FastAPI")
def run_api_task():
  print("Démarrage du serveur Uvicorn / FastAPI sur le port 8000...")
  subprocess.run(
      ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  )


# --- NOUVELLES TÂCHES POUR DOCKER (Atelier 6) ---


@task(name="Construction de l'image Docker")
def build_docker_image():
  print(f"Construction de l'image Docker : {DOCKER_IMAGE_NAME}...")
  subprocess.run(
      ["docker", "build", "-t", DOCKER_IMAGE_NAME, "."], check=True
  )
  print("Image Docker construite avec succès.")


@task(name="Push de l'image sur Docker Hub")
def push_docker_image():
  local_tag = DOCKER_IMAGE_NAME
  remote_tag = f"{DOCKER_HUB_USER}/{DOCKER_IMAGE_NAME}:latest"

  print(f"Tagage de l'image {local_tag} vers {remote_tag}...")
  subprocess.run(["docker", "tag", local_tag, remote_tag], check=True)

  print(f"Envoi (push) de l'image sur Docker Hub : {remote_tag}...")
  subprocess.run(["docker", "push", remote_tag], check=True)
  print("Image poussée avec succès sur Docker Hub.")


# --- FLOWS PREFECT ---


@flow(name="code")
def code_flow():
  install_dependencies()
  format_code()
  code_quality()
  code_security()
  unit_tests()


@flow(name="train")
def train_flow():
  X_train, X_test, y_train, y_test = prepare_data_task()
  model = train_model_task(X_train, y_train)
  save_model_task(model)


@flow(name="evaluate")
def evaluate_flow():
  _, X_test, _, y_test = prepare_data_task()
  model = load_model_task()
  evaluate_model_task(model, X_test, y_test)


@flow(name="api")
def api_flow():
  run_api_task()


@flow(name="docker-cd")
def docker_flow():
  """Flux de Continuous Delivery (CD) : Build et Push de l'image Docker."""
  build_docker_image()
  push_docker_image()


@flow(name="all")
def all_flow():
  # Étapes de suivi du code
  install_dependencies()
  format_code()
  code_quality()
  code_security()
  unit_tests()

  # Étapes data / modèles
  X_train, X_test, y_train, y_test = prepare_data_task()
  model = train_model_task(X_train, y_train)
  save_model_task(model)
  evaluate_model_task(model, X_test, y_test)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Orchestration Prefect - Pipeline MLOps"
  )
  parser.add_argument(
      "--flow",
      type=str,
      choices=["code", "train", "evaluate", "api", "docker", "all"],
      default="all",
      help="Flow Prefect à exécuter",
  )
  args = parser.parse_args()

  if args.flow == "code":
    code_flow()
  elif args.flow == "train":
    train_flow()
  elif args.flow == "evaluate":
    evaluate_flow()
  elif args.flow == "api":
    api_flow()
  elif args.flow == "docker":
    docker_flow()
  elif args.flow == "all":
    all_flow()