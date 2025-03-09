import pandas as pd
import joblib
import numpy as np
import shap
import json


txtFornecedores = ['SILT SELF SERVICE EIRELI ME',
                   'PARLANET WEB E TECNOLOGIA EIRELI',
                   '99 POP', 'Companhia Energética de Pernambuco',
                   'BRASAL COMBUSTIVEIS LTDA', 'ENEL - Eletropaulo',
                   'Telefônica Brasil S.A. VIVO',
                   'CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
                   'Copel Distribuição S.A.',
                   'CONCESSIONARIA BR-040 S.A.',
                   'AMORETTO CAFES EXPRESSO LTDA',
                   'CELULAR FUNCIONAL',
                   '076 - MELHOR 10 - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
                   'CENTRO DE GESTÃO DE MEIOS DE PGTO. LTDA. - SEM PARAR',
                   'DRA4 DERIVADOS DE PETROLEO LTDA', 'GOL',
                   'TELEFÔNICA BRASIL S. A. VIVO',
                   'MADERO INDUSTRIA E COMERCIO S.',
                   '031 - 302 NORTE - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
                   'COMPANHIA DE ELETRICIDADE DO ESTADO DA BAHIA',
                   'VIVO TELEFONIA BRASIL S/A',
                   'CONCEBRA - CONCESSIONARIA DAS RODOVIAS CENTRAIS DO BRASIL S.A.',
                   'MAP',
                   'AUTO POSTO AEROPORTO LTDA',
                   'LIGHT SERVICOS DE ELETRICIDADE S A',
                   'Telefônica Brasil S. A. VIVO',
                   'RESTAURANTE DAS MINAS LTDA', '063 - 311 SUL - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA', 'ARTESANAL SERVICOS DE ALIMENTACAO E BUFFET EIRELI', 'TÁXI LEGAL', 'TELEFONICA BRASIL S.A.', 'PETRUS GASTRONOMIA E SERVICOS LTDA', 'J&F BAR E RESTAURANTE LTDA', 'TAM', 'PD PAES E DELICIAS COMERCIO E INDUSTRIA', 'WMS COMERCIO DE ARTIGOS DE PAPELARIA LTDA-ME', 'CEEE - Companhia Estadual de Distribuição de Energia Elétrica', 'Telefônica do Brasil S/A - VIVO', 'CEMIG DISTRIBUIÇÃO S.A.', 'EGR EMPRESA GAUCHA DE RODOVIAS SA', 'CONC. RODOVIAS INTEGRADAS DO SUL', 'AUTO POSTO CINCO ESTRELAS LTDA', 'CONC. SISTEMA ANHANGUERA-BANDEIRANTES S/A', 'Claro S/A', 'SANTO BUFFET SERVICOS DE ALIMENTACAO LTDA', 'AUTO POSTO 303 NORTE LTDA', 'RAMAL', 'UBER DO BRASIL TECNOLOGIA LTDA.', 'SERVICO NACIONAL DE APRENDIZAGEM COMERCIAL SENAC', 'EMPRESA CONCESSIONARIA DE RODOVIAS DO SUL S/A - ECOSUL', 'Claro NXT Telecomunicações S.A', 'TAIOBA SELF-SERVICE LTDA EPP', 'POSTO DA TORRE EIRELI EPP', 'AZUL']



def mapper_expense(expense):
    return {
             "numMes": [expense["mes"]],
             "numAno": [expense["ano"]],
             "numParcela": [expense["parcela"]],
             "txtDescricao": [expense["tipoDespesa"]],
             "vlrLiquido": [expense["valorLiquido"]],
            "txtFornecedor": [expense["nomeFornecedor"]]
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

    # Determina o fornecedor para definir o grupo
    supplier = expense_from_rest["nomeFornecedor"] if expense_from_rest[
                                                          "nomeFornecedor"] in txtFornecedores else "OUTROS"

    # Cria um DataFrame de uma linha com apenas a coluna 'vlrLiquido'
    df_single = pd.DataFrame({"vlrLiquido": [expense_from_rest["valorLiquido"]]})

    # Carrega o dicionário de pipelines treinados
    pipelines_dict = joblib.load("saved_models/isolation_forest_pipeline_by_supplier.pkl")

    # Obtém o pipeline para o fornecedor ou usa "OUTROS" como fallback
    if supplier in pipelines_dict:
        pipeline_model = pipelines_dict[supplier]
    else:
        pipeline_model = pipelines_dict.get("OUTROS")

    # Previsão (-1 para anomalia, 1 para normal)
    prediction = pipeline_model.predict(df_single)[0]

    # Transforma os dados com o scaler
    transformed_data = pipeline_model["scaler"].transform(df_single)
    anomaly_score = pipeline_model["isolation_forest"].decision_function(transformed_data)[0]

    # Tenta usar TreeExplainer; se falhar, utiliza KernelExplainer
    try:
        explainer = shap.TreeExplainer(pipeline_model["isolation_forest"])
        shap_values = explainer.shap_values(transformed_data)
    except Exception as e:
        background = transformed_data
        explainer = shap.KernelExplainer(pipeline_model["isolation_forest"].decision_function, background)
        shap_values = explainer.shap_values(transformed_data)

    # Como temos apenas uma feature, pegamos seu valor absoluto de SHAP
    shap_df = pd.DataFrame(shap_values, columns=["vlrLiquido"])
    influential_features = [{"feature": "vlrLiquido", "impact": float(abs(shap_df.iloc[0, 0]))}]

    # Define o nível de alerta com base na predição e score
    if prediction == 1:
        alert = "GREEN"
    elif prediction == -1:
        alert = "RED"
    else:
        alert = "RED"

    output = {
        "expense": {
            "type": expense_from_rest["tipoDespesa"],
            "url_doc": expense_from_rest["urlDocumento"],
            "valor": expense_from_rest["valorLiquido"],
            "supplier_name": expense_from_rest["nomeFornecedor"],
            "supplier_identifier": expense_from_rest["cnpjCpfFornecedor"],
            "date": expense_from_rest["dataDocumento"]
        },
        "is_anomaly": bool(prediction == -1),  # Converter para bool do Python
        "score_anomaly": float(anomaly_score),
        "alert": alert,
        "influential_features": influential_features
    }
    return output