import os
import logging
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# Configura o logging
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


def load_data(file_paths, columns_to_use):
    dfs = []
    for path in file_paths:
        df = pd.read_csv(path, sep=";")
        dfs.append(df)
    df_full = pd.concat(dfs, ignore_index=True)
    # Filtra apenas as colunas necessárias e remove linhas sem txtDescricao
    df_filtered = df_full[columns_to_use].copy()
    df_filtered.dropna(subset=["txtDescricao"], inplace=True)
    df_filtered = df_filtered[df_filtered['txtDescricao'].isin(selected_categories)]
    logger.info(f"Loaded data with {df_filtered.shape[0]} rows after filtering.")
    return df_filtered


def build_pipeline_for_vlrLiquido(contamination=0.01):
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("isolation_forest", IsolationForest(contamination=contamination, random_state=42))
    ])
    return pipeline


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

    columns_to_use = [
        "txtDescricao",
        "numMes",
        "numAno",
        "vlrLiquido",
        "txtFornecedor"
    ]

    # Carrega os dados aglomerando os arquivos de historicos de despesas
    df = load_data(file_paths, columns_to_use)

    # Removendo linhas do dataset que não possuem valores para um dos campos importantes para o modelo
    columns_to_check = ['numMes', 'numAno', 'vlrLiquido', 'txtDescricao', 'txtFornecedor']
    if df[columns_to_check].isnull().values.any():
        print("Existem valores NaN ou null nas colunas especificadas.")
        df = df.dropna(subset=columns_to_check)
        print("Linhas com valores NaN ou null foram removidas.")
    else:
        print("Não há valores NaN ou null nas colunas especificadas.")

    # Criando nova coluna: fornecedorId
    df['fornecedorId'] = 'OUTROS'
    df.loc[df['txtFornecedor'].isin(txtFornecedores), 'fornecedorId'] = df['txtFornecedor']

    contamination_value = 0.01
    pipelines_dict = {}

    # Agrupa os dados por fornecedorId e treina um pipeline para cada grupo
    for supplier, group_df in df.groupby('fornecedorId'):
        X = group_df[['vlrLiquido']]
        # Se o grupo tiver poucos dados, opte por não treinar um modelo específico
        if len(X) < 10:
            logger.info(
                f"Grupo {supplier} possui poucos dados ({len(X)} amostras). Ignorando treinamento para esse grupo.")
            continue
        model_pipeline = build_pipeline_for_vlrLiquido(contamination=contamination_value)
        model_pipeline.fit(X)
        pipelines_dict[supplier] = model_pipeline
        logger.info(f"Treinamento concluído para o fornecedor {supplier} com {len(X)} amostras.")

    # Se o grupo "OUTROS" não foi treinado, treina um modelo global
    if "OUTROS" not in pipelines_dict:
        global_pipeline = build_pipeline_for_vlrLiquido(contamination=contamination_value)
        X_global = df[['vlrLiquido']]
        global_pipeline.fit(X_global)
        pipelines_dict["OUTROS"] = global_pipeline
        logger.info("Treinamento do modelo global (OUTROS) concluído.")

    # 6) Salvar o dicionário de pipelines
    os.makedirs("saved_models", exist_ok=True)
    joblib.dump(pipelines_dict, "saved_models/isolation_forest_pipeline_by_supplier.pkl")
    logger.info("Modelos salvos em 'saved_models/isolation_forest_pipeline_by_supplier.pkl'.")


if __name__ == "__main__":
    main()
