import os
import logging
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import IsolationForest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(file_paths, columns_to_use):
    dfs = []
    for path in file_paths:
        df = pd.read_csv(path, sep=";")
        dfs.append(df)
    df_full = pd.concat(dfs, ignore_index=True)
    # Filter only the required columns and drop rows with missing txtDescricao
    df_filtered = df_full[columns_to_use].copy()
    df_filtered.dropna(subset=["txtDescricao"], inplace=True)
    logger.info(f"Loaded data with {df_filtered.shape[0]} rows after filtering.")
    return df_filtered


def build_pipeline(categorical_features, numeric_features, contamination=0.02):
    # Transformer for categorical features
    cat_transformer = OneHotEncoder(handle_unknown="ignore")

    # Transformer for numeric features (StandardScaler to normalize magnitudes)
    num_transformer = StandardScaler()  # Change to "passthrough" if preserving original values is desired

    # ColumnTransformer: apply transformations on specific feature groups
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", cat_transformer, categorical_features),
            ("num", num_transformer, numeric_features)
        ]
    )

    # Build the full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("isolation_forest", IsolationForest(
            contamination=contamination,
            random_state=42
        ))
    ])

    return pipeline


def main():
    # -----------------------
    # 1) Define File Paths
    # -----------------------
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

    # -----------------------
    # 2) Define Columns to Use
    # -----------------------
    columns_to_use = [
        "txtDescricao",
        "numMes",
        "numAno",
        "vlrDocumento",
        "numParcela",
        "vlrGlosa",
        "vlrLiquido"
    ]

    # -----------------------
    # 3) Define Feature Groups
    # -----------------------
    categorical_features = ["txtDescricao"]
    numeric_features = ["numMes", "numAno", "vlrDocumento", "numParcela", "vlrGlosa", "vlrLiquido"]

    # -----------------------
    # 4) Load Data
    # -----------------------
    df = load_data(file_paths, columns_to_use)

    # -----------------------
    # 5) Filter Data for Selected txtDescricao Categories
    # -----------------------
    selected_categories = [
        "COMBUSTÍVEIS E LUBRIFICANTES.",
        "PASSAGEM AÉREA - SIGEPA",
        "SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO",
        "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR",
        "TELEFONIA"
    ]
    df = df[df["txtDescricao"].isin(selected_categories)]
    logger.info(f"Filtered data to selected txtDescricao categories. Rows remaining: {df.shape[0]}.")

    # -----------------------
    # 6) Build Pipeline
    # -----------------------
    contamination_value = 0.02  # Adjust based on domain expertise
    pipeline = build_pipeline(categorical_features, numeric_features, contamination=contamination_value)

    # -----------------------
    # 7) Train Pipeline
    # -----------------------
    pipeline.fit(df)
    logger.info("Pipeline training complete.")

    # -----------------------
    # 8) Prediction & Evaluation
    # -----------------------
    predictions = pipeline.predict(df)
    transformed_data = pipeline["preprocessor"].transform(df)
    if hasattr(transformed_data, "toarray"):
        transformed_data = transformed_data.toarray()
    anomaly_scores = pipeline["isolation_forest"].decision_function(transformed_data)

    df["anomaly"] = predictions
    df["anomaly_score"] = anomaly_scores
    anomaly_rate = (df["anomaly"] == -1).mean()
    logger.info(f"Anomaly rate: {anomaly_rate:.2%}")

    # -----------------------
    # 9) Save Pipeline
    # -----------------------
    os.makedirs("saved_models", exist_ok=True)
    joblib.dump(pipeline, "saved_models/isolation_forest_pipeline.pkl")
    logger.info("Saved pipeline to 'saved_models/isolation_forest_pipeline.pkl'.")


if __name__ == "__main__":
    main()
