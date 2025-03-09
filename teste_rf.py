import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import mean_absolute_error

from main import txtFornecedores


def load_transformers():
    with open('saved_models/numeric_transformer_old.pkl', 'rb') as f:
        numeric_transformer = pickle.load(f)
    with open('saved_models/categorical_transformer_old.pkl', 'rb') as f:
        categorical_transformer = pickle.load(f)
    return numeric_transformer, categorical_transformer

def preprocess_data(df, numeric_transformer, categorical_transformer):
    features = ['numMes', 'numAno', 'numParcela', 'txtDescricao', 'fornecedorId']
    df = df.copy()

    numeric_features = ['numMes', 'numAno', 'numParcela']
    X_numeric = numeric_transformer.transform(df[numeric_features])

    categorical_features = ['txtDescricao', 'fornecedorId']
    X_categorical = categorical_transformer.transform(df[categorical_features])

    X_processed = np.concatenate((X_numeric, X_categorical), axis=1)
    return X_processed

def mapper_expense(expense):
    features = ['sgPartido', 'sgUF', 'numMes', 'numAno', 'numParcela', 'txtDescricao']
    return {
        "numMes": [expense["mes"]],
        "numAno": [expense["ano"]],
        "numParcela": [expense["parcela"]],
        "txtDescricao": [expense["tipoDespesa"]]
    }

def run(deputado, despesa):
    with open('saved_models/best_model_old.pkl', 'rb') as f:
        best_model = pickle.load(f)

    numeric_transformer, categorical_transformer = load_transformers()

    despesa_mapped = {
        "numMes": despesa["mes"],
        "numAno": despesa["ano"],
        "numParcela": despesa["parcela"],
        "txtDescricao": despesa["tipoDespesa"],
        "txtFornecedor": despesa["nomeFornecedor"],
        "vlrLiquido": despesa["valorLiquido"]
    }

    df_despesa = pd.DataFrame([despesa_mapped])

    df_despesa['fornecedorId'] = 'OUTROS'
    df_despesa.loc[df_despesa['txtFornecedor'].isin(txtFornecedores), 'fornecedorId'] = df_despesa['txtFornecedor']

    features = ['numMes', 'numAno', 'numParcela', 'txtDescricao', 'fornecedorId']

    X_new = preprocess_data(df_despesa[features], numeric_transformer, categorical_transformer)

    prediction   = best_model.predict(X_new)

    # Diferença absoluta
    diff = abs(despesa_mapped["vlrLiquido"] - prediction)

    # Definir um limiar de anomalia
    LIMIAR_FIXO = 2000

    is_anomaly = diff > LIMIAR_FIXO

    return is_anomaly