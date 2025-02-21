import pandas as pd
import joblib
import numpy as np
import shap
import json

# Example single expense record
# single_expense = {
#     "txtDescricao": ["PASSAGEM AÉREA - SIGEPA"],  # Categorical
#     "numMes": [2],
#     "numAno": [2024],
#     "vlrDocumento": [2000.70],
#     "numParcela": [0],
#     "vlrGlosa": [0.0],
#     "vlrLiquido": [2000.70]
# }

def mapper_expense(expense):
    return {
        "txtDescricao": [expense["tipoDespesa"]],
             "numMes": [expense["mes"]],
             "numAno": [expense["ano"]],
             "vlrDocumento": [expense["valorDocumento"]],
             "numParcela": [expense["parcela"]],
             "vlrGlosa": [expense["valorGlosa"]],
             "vlrLiquido": [expense["valorLiquido"]]
    }

expense_from_rest = {
      "ano": 2024,
      "mes": 11,
      "tipoDespesa": "PASSAGEM AÉREA - RPA",
      "codDocumento": 7836314,
      "tipoDocumento": "Nota Fiscal Eletrônica",
      "codTipoDocumento": 4,
      "dataDocumento": "2024-11-27T17:11:56",
      "numDocumento": "1034802",
      "valorDocumento": 2000.92,
      "urlDocumento": "http://www.camara.leg.br/cota-parlamentar/nota-fiscal-eletronica?ideDocumentoFiscal=7836314",
      "nomeFornecedor": "076 - MELHOR 10 - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA",
      "cnpjCpfFornecedor": "00306597007614",
      "valorLiquido": 2000.92,
      "valorGlosa": 0,
      "numRessarcimento": "",
      "codLote": 2092142,
      "parcela": 0
    }



single_expense = mapper_expense(expense_from_rest)
# Create a single-row DataFrame
df_single = pd.DataFrame(single_expense)

# Load the trained pipeline
pipeline = joblib.load("saved_models/isolation_forest_pipeline.pkl")

# Get the prediction (-1 for anomaly, 1 for normal)
prediction = pipeline.predict(df_single)[0]

# Transform the data using the preprocessor
transformed_data = pipeline["preprocessor"].transform(df_single)
if hasattr(transformed_data, "toarray"):
    transformed_data = transformed_data.toarray()

# Convert transformed data to NumPy array (ensure float type for SHAP)
transformed_data = np.array(transformed_data, dtype=np.float32)

# Get anomaly score
anomaly_score = pipeline["isolation_forest"].decision_function(transformed_data)[0]

# --- SHAP Analysis to Identify Most Influential Features ---
# Initialize SHAP Explainer
explainer = shap.TreeExplainer(pipeline["isolation_forest"])

# Compute SHAP values
shap_values = explainer.shap_values(transformed_data)

# Convert SHAP values to DataFrame
shap_df = pd.DataFrame(shap_values, columns=pipeline["preprocessor"].get_feature_names_out())

# Get the top 2 most influential features (by absolute SHAP value)
top_features = shap_df.T.iloc[:, 0].abs().sort_values(ascending=False).head(2)
influential_features = [{"feature": feature, "impact": float(value)} for feature, value in top_features.items()]

# Define alert levels based on score
if prediction == -1:
    alert = "🔴 RED ALERT (High Anomaly Risk)"
elif prediction == 1 and anomaly_score > 0.1:
    alert = "✅ GREEN (Normal)"
elif prediction == 1 and anomaly_score <= 0.1:
    alert = "🟡 YELLOW ALERT (Borderline Anomaly Risk)"

# Create JSON output
output = {
    "expense": {

    }
    "prediction": int(prediction),
    "score": float(anomaly_score),
    "alert": alert,
    "influential_features": influential_features
}

# Print JSON result
print(json.dumps(output, indent=4))
