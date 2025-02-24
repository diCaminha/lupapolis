import pandas as pd
import joblib
import numpy as np
import shap
import json


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


# Create JSON output
def __check_if_anomaly(prediction):
    if prediction == 1:
        return False
    elif prediction == -1:
        return True
    else:
        raise Exception("strange prediction value!")

def run_model(expense_from_rest):

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
        alert = "RED"
    elif prediction == 1 and anomaly_score > 0.1:
        alert = "GREEN"
    elif prediction == 1 and anomaly_score <= 0.1:
        alert = "YELLOW"

    output = {
        "expense": {
            "type": expense_from_rest["tipoDespesa"],
            "url_doc": expense_from_rest["urlDocumento"],
            "valor": expense_from_rest["valorLiquido"],
            "supplier_name": expense_from_rest["nomeFornecedor"],
            "supplier_identifier": expense_from_rest["cnpjCpfFornecedor"],
            "date": expense_from_rest["dataDocumento"]
        },
        "is_anomaly": __check_if_anomaly(int(prediction)),
        "score_anomaly": float(anomaly_score),
        "alert": alert,
        "influential_features": influential_features
    }
    return output
    # Print JSON result
    #print(json.dumps(output, indent=4))
