from pipeline_prefect import all_flow, train_flow, evaluate_flow, code_flow

if __name__ == "__main__":
    print("Démarrage du service Prefect pour le pipeline MLOps...")

    # La méthode serve() maintient le service actif, écoute le serveur
    # et exécute les flux directement dans le répertoire courant du projet.
    all_flow.serve(
        name="ml-pipeline-all",
        tags=["full-pipeline", "mlops"],
        cron="0 2 * * *"
    )