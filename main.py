import argparse
from model_pipeline import (
    prepare_data,
    train_model,
    evaluate_model,
    save_model,
    load_model,
)


def main():
    parser = argparse.ArgumentParser(description="Pipeline MLOps - Churn Modelling")
    parser.add_argument(
        "--data",
        type=str,
        default="Churn_Modelling.csv",
        help="Chemin vers le fichier de données CSV",
    )
    parser.add_argument(
        "--action",
        type=str,
        choices=["train", "evaluate", "all"],
        default="all",
        help="Action à exécuter : train, evaluate, all",
    )
    args = parser.parse_args()

    X_train, X_test, y_train, y_test = prepare_data(args.data)

    if args.action in ["train", "all"]:
        model = train_model(X_train, y_train)
        evaluate_model(model, X_test, y_test)
        save_model(model)
    elif args.action == "evaluate":
        model = load_model()
        evaluate_model(model, X_test, y_test)


if __name__ == "__main__":
    main()
