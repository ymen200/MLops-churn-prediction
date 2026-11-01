import subprocess
import argparse
from prefect import task, flow
from model_pipeline import (
    prepare_data,
    train_model,
    evaluate_model,
    save_model,
    load_model,
)

TARGET_FILES = ["model_pipeline.py", "main.py", "pipeline_prefect.py"]


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
        choices=["code", "train", "evaluate", "all"],
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
    elif args.flow == "all":
        all_flow()
