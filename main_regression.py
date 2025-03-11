import os
import logging
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from tqdm.auto import tqdm
from tqdm_joblib import tqdm_joblib
import pickle
from scipy.stats import zscore

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

selected_categories = [
    "COMBUSTÍVEIS E LUBRIFICANTES.",
    "PASSAGEM AÉREA - RPA",
    "TELEFONIA",
    "SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO",
    "PASSAGEM AÉREA - SIGEPA",
    "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR",
    "FORNECIMENTO DE ALIMENTAÇÃO DO PARLAMENTAR",
    "SERVIÇOS POSTAIS",
    "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR."
]

txtFornecedores = [
    "CASCOL COMBUSTIVEIS PARA VEICULOS LTDA",
    "AUTO POSTO CINCO ESTRELAS LTDA",
    "FRATELLI POSTO DE COMBUSTIVEIS LTDA",
    "AUTO POSTO AEROPORTO LTDA",
    "POSTO DA TORRE EIRELI EPP",
    "Cia Aérea - TAM",
    "Cia Aérea - GOL",
    "Cia Aérea - AVIANCA",
    "Cia Aérea - AZUL",
    "Cia Aérea - PASSAREDO",
    "RAMAL",
    "CELULAR FUNCIONAL",
    "TELEFONICA BRASIL S.A.",
    "TELEMAR NORTE LESTE S/A",
    "Telefônica Brasil S.A. VIVO",
    "UBER DO BRASIL TECNOLOGIA LTDA.",
    "SINPETAXI",
    "UBER DO BRASIL TECNOLOGIA LTDA",
    "TÁXI LEGAL",
    "CONCESSIONARIA BR-040 S.A.",
    "TAM",
    "GOL",
    "AZUL",
    "MAP",
    "WMS COMERCIO DE ARTIGOS DE PAPELARIA LTDA-ME",
    "AMORETTO CAFES EXPRESSO LTDA",
    "CEMIG DISTRIBUIÇÃO S.A.",
    "COMPANHIA DE ELETRICIDADE DO ESTADO DA BAHIA",
    "CEEE - Companhia Estadual de Distribuição de Energia Elétrica"
]

def remover_outliers_iqr(df, coluna):
    Q1 = df[coluna].quantile(0.25)
    Q3 = df[coluna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df_filtrado = df[(df[coluna] >= limite_inferior) & (df[coluna] <= limite_superior)]
    return df_filtrado

def remover_outliers_zscore(df, coluna, threshold=3):
    df['zscore'] = zscore(df[coluna])
    df_filtrado = df[abs(df['zscore']) < threshold].copy()
    df_filtrado.drop(columns=['zscore'], inplace=True)
    return df_filtrado

def load_data(file_paths):
    dfs = []
    for path in file_paths:
        df = pd.read_csv(path, sep=";")
        dfs.append(df)
    df_full = pd.concat(dfs, ignore_index=True)
    # Filtrar apenas as colunas necessárias e remover linhas com txtDescricao ausente
    df_filtered = df_full.copy()
    df_filtered.dropna(subset=["txtDescricao"], inplace=True)
    logger.info(f"Dados carregados com {df_filtered.shape[0]} linhas após o filtro.")
    return df_filtered

def remover_despesas_coletivas(df):
    df_filtered = df[~(df['txNomeParlamentar'].str.contains("LIDERANCA") | (df['txNomeParlamentar'] == "LID.GOV-CD"))]
    return df_filtered

def main():
    file_paths = [
        "files/despesas2015.csv",
        "files/despesas2016.csv",
        "files/despesas2017.csv",
        "files/despesas2018.csv",
        "files/despesas2019.csv",
        "files/despesas2020.csv",
        "files/despesas2021.csv",
        "files/despesas2022.csv",
        "files/despesas2023.csv",
        "files/despesas2024.csv"
    ]

    # Carregando os dados dos arquivos de despesas e montando um df
    df = load_data(file_paths)

    # Criando a coluna fornecedorId
    df['fornecedorId'] = 'OUTROS'
    df.loc[df['txtFornecedor'].isin(txtFornecedores), 'fornecedorId'] = df['txtFornecedor']

    # Remoção de outliers
    df = remover_outliers_iqr(df, 'vlrLiquido')

    df = remover_despesas_coletivas(df)

    df = df[df['txtDescricao'].isin(selected_categories)]

    # Seleciona as variáveis de interesse
    features = ['numMes', 'numAno', 'numParcela', 'txtDescricao', 'fornecedorId']
    target = 'vlrLiquido'
    df = df[features + [target]].dropna()

    # Separar os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)

    # Pré-processamento numérico
    numeric_features = ['numMes', 'numAno', 'numParcela']
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    # Pré-processamento categórico
    categorical_features = ['txtDescricao', 'fornecedorId']
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Ajuste e transformação dos dados
    X_train_categorical = categorical_transformer.fit_transform(X_train[categorical_features])
    X_test_categorical = categorical_transformer.transform(X_test[categorical_features])

    numeric_transformer.fit(X_train[numeric_features])
    X_train_numeric = numeric_transformer.transform(X_train[numeric_features])
    X_test_numeric = numeric_transformer.transform(X_test[numeric_features])

    # Concatena os dados pré-processados
    X_train_processed = np.concatenate((X_train_numeric, X_train_categorical), axis=1)
    X_test_processed = np.concatenate((X_test_numeric, X_test_categorical), axis=1)

    # Modelo Random Forest com ajuste de hiperparâmetros
    model = RandomForestRegressor(random_state=42)

    param_grid = {
        'n_estimators': [100, 200, 300, 500],
        'max_depth': [10, 20, None],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['auto', 'sqrt']
    }

    cv_folds = 3
    total_iterations = len(param_grid['n_estimators']) * len(param_grid['max_depth']) * cv_folds

    grid_search = GridSearchCV(
        model,
        param_grid,
        cv=cv_folds,
        scoring='neg_mean_squared_error'
    )

    # Monitorar o progresso do GridSearchCV com tqdm_joblib
    with tqdm_joblib(tqdm(desc="Grid Search", total=total_iterations)) as progress_bar:
        grid_search.fit(X_train_processed, y_train)

    # Capturando pelo grid search com os melhores parametros
    best_model = grid_search.best_estimator_
    logger.info(f"Melhores hiperparâmetros: {grid_search.best_params_}")

    # Avaliação do modelo
    y_pred = best_model.predict(X_test_processed)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f'MSE: {mse}')
    print(f'R²: {r2}')

    # Salvar o melhor modelo e os transformers para uso
    with open('best_model.pkl', 'wb') as file:
        pickle.dump(best_model, file)

    with open('numeric_transformer.pkl', 'wb') as file:
        pickle.dump(numeric_transformer, file)

    with open('categorical_transformer.pkl', 'wb') as file:
        pickle.dump(categorical_transformer, file)

    print("Modelo e transformers salvos com sucesso.")

if __name__ == "__main__":
    main()
