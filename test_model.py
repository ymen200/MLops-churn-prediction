import pytest
from model_pipeline import prepare_data, train_model

def test_data_preparation():
    X_train, X_test, y_train, y_test = prepare_data("Churn_Modelling.csv")
    assert X_train is not None
    assert X_test is not None
    assert len(y_train) > 0
    assert len(y_test) > 0

def test_model_training():
    X_train, X_test, y_train, y_test = prepare_data("Churn_Modelling.csv")
    model = train_model(X_train, y_train)
    assert model is not None

def test_model_prediction():
    X_train, X_test, y_train, y_test = prepare_data("Churn_Modelling.csv")
    model = train_model(X_train, y_train)
    preds = model.predict(X_test)
    assert len(preds) == len(y_test)