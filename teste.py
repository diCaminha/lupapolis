import pandas as pd
import joblib
import numpy as np
import shap
import json


txtFornecedores = ['SERVIÇO NACIONAL DE APRENDIZAGEM COMERCIAL - SENAC',
 'CLARO S.A',
 'UBER DO BRASIL TECNOLOGIA LTDA',
 'ECT - EMP. BRAS. DE CORREIOS E TELEGRAFOS',
 'CEEE - Companhia Estadual de Distribuição de Energia Elétrica',
 'POSTO DA TORRE EIRELI EPP',
 'LIGHT SERVICOS DE ELETRICIDADE S A',
 'CORREIOS - TELEGRAMA',
 'BRASIL 21 EVENTOS E HOTELARIA LTDA',
 'CONCESSIONÁRIA DE RODOVIAS S/A',
 'SINPETAXI',
 'EGR EMPRESA GAUCHA DE RODOVIAS SA',
 'TÁXI LEGAL',
 'POSTO ITAMARATY LTDA',
 'TELEFONICA BRASIL S.A.',
 'TELEFONICA BRASIL S.A. VIVO',
 'IMÓVEL FUNCIONAL',
 'SILT SELF SERVICE EIRELI ME',
 'CORREIOS - SEDEX 12',
 'SINDICATO DOS PERMISSIONARIOS DE TAXIS E MOTORISTAS AUXILIARES DO DISTRITO FEDERAL',
 'EMPRESA CONCESSIONÁRIA DE RODOVIAS DO SUL S.A',
 'OI S.A.',
 'AUTO POSTO PETER PAN 01 LTDA',
 'Claro S/A',
 'AUTO POSTO JK LTDA',
 'CENTRAL PARK RESTAURANTE E EVENTOS LTDA ME',
 'SENAC - COMP. ADM. CAM. DEP. ANEXO IV 10º ANDAR',
 'AZUL',
 'DRA 4 DERIVADOS DE PETROLEO LTDA',
 'GOL',
 'CASCOL COMBUSTÍVEIS PARA VEÍCULOS LTDA.',
 'CORREIOS - SEDEX CONVENCIONAL COM AR',
 'CORREIOS - CARTA COMERCIAL',
 'CORREIOS - ENCOMENDA PAC COM AR',
 'CONCESSIONARIA DA RODOVIA OSORIO PORTO ALEGRE SA - CONCEPA',
 'CASCOL COMBUSTÍVEIS PARA VEÍCULOS LTDA',
 'TELEFONICA BRASIL S.A - VIVO.',
 'UBER DO BRASIL TECNOLOGIA LTDA.',
 'VIA BAHIA',
 'CLARO S.A.',
 'Telefônica do Brasil S/A - VIVO',
 'RAMAL',
 'COMPANHIA DE ELETRICIDADE DO ESTADO DA BAHIA',
 'AUTO POSTO DE COMBUSTIVEIS RENASCENCA LTDA',
 'CORREIOS - CARTA REGISTRADA COM AR',
 'AMORETTO CAFES EXPRESSO LTDA',
 'CEMIG DISTRIBUIÇÃO S.A.',
 'TIM S.A',
 'CONCESS. DA RODOVIA PRESIDENTE DUTRA S.A.',
 'CONC. SISTEMA ANHANGUERA-BANDEIRANTES S/A',
 'Copel Distribuição S.A.',
 'CCR-RODONORTE',
 'BRASAL COMBUSTIVEIS LTDA',
 'POSTO DISBRAVE IMPERIAL LTDA',
 'TELEFONICA BRASIL S.A',
 'SÃO JOÃO POSTOS DE ABASTECIMENTOS E SERVIÇOS',
 'EGR EMPRESA GAUCHA DE RODOVIAS S/A',
 'POSTO KALILANDIA LTDA',
 'Cia Aérea - GOL',
 'VIA 040 CONCESSIONARIA BR040 S/A',
 'COPASA',
 'Telefônica Brasil S.A. VIVO',
 'POSTO DE GASOLINA JB CAXIAS LTDA',
 'CONC. RODOVIAS INTEGRADAS DO SUL',
 'CORREIOS - SEDEX CONVENCIONAL',
 'CORREIOS - ENVELOPE BÁSICO/CONVENCIONAL - PLÁSTICO/BOLHA',
 'TELEMAR NORTE LESTE S/A',
 'AUTO POSTO 303 NORTE LTDA',
 'AUTO PISTA FERNÃO DIAS',
 'CENTROVIAS SISTEMAS RODOVIARIOS S/A',
 'Claro S.A',
 'RESTAURANTE DAS MINAS LTDA',
 'VIVO TELEFONIA BRASIL S/A',
 'WMS COMERCIO DE ARTIGOS DE PAPELARIA LTDA-ME',
 'Concessionaria das Rodovias Ayrton Senna e Carvalho Pinto SA',
 'COELBA GRUPO NEOENERGIA',
 'SERVICO NACIONAL DE APRENDIZAGEM COMERCIAL SENAC',
 'CORREIOS - ENCOMENDA PAC',
 'Telefonica Brasil S.A - VIVO',
 'SINPETAXI DF',
 'CLARO S/A',
 'SERV. NAC. DE APRENDIZAGEM COMERCIAL - SENAC',
 'EMPRESA CONCESSIONARIA DE RODOVIAS DO SUL S/A - ECOSUL',
 'ECT',
 'POSTO DA TORRE EIRELI - EPP',
 'CONCEBRA - CONCESSIONARIA DAS RODOVIAS CENTRAIS DO BRASIL S.A.',
 'Telefônica Brasil S. A. VIVO',
 '99 POP',
 'TIM CELULAR S/A',
 'Autopista Fernão Dias',
 'TELEFÔNICA BRASIL S/A - VIVO',
 'CONC. DE RODOVIAS MINAS GERAIS GOIAS S/A',
 'TELEFÔNICA BRASIL S.A.',
 'FACEBOOK SERVIÇOS ONLINE DO BRASIL LTDA',
 'POSTOS MATARIPE ABASTECIMENTOS E SERVIÇOS LTDA',
 'POSTO ICCAR LTDA',
 'Cascol Combustíveis para Veículos Ltda.',
 'Claro NXT Telecomunicações S.A',
 'Companhia Energética de Pernambuco',
 'TELEFÔNICA BRASIL S. A. VIVO',
 'CORREIOS - CAIXA DE ENCOMENDAS BÁSICA/CONVENCIONAL',
 'ALLPARK EMPREENDIMENTOS PARTICIPAÇÕES E SERVIÇOS S.A.',
 '063 - 311 SUL - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
 'CAMINHOS DO PARANA S/A',
 'ELETROPAULO METROPOLITANA ELETRICIDADE DE SÃO PAULO S.A.',
 'CORREIOS - SEDEX 10 COM AR',
 'SERVIÇO NACIONAL DE APRENDIZ. COMERCIAL SENAC',
 'CONC. RODOVIA DO OESTE DE SÃO PAULO S/A',
 'AUTO POSTO CINCO ESTRELAS LTDA',
 'CORREIOS - MALA DIRETA ENDEREÇADA (POSTAL BÁSICA)',
 '031 - 302 NORTE - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
 'CORREIOS - CARTA REGISTRADA',
 'CONCESSIONARIA DA RODOVIA PRESIDENTE DUTRA S/A',
 'CONC. DE RODOVIAS INTEGRADAS S/A',
 'AUTO POSTO AEROPORTO LTDA',
 'TIM CELULAR S.A.',
 'FRATELLI POSTO DE COMBUSTIVEIS LTDA',
 'CENTRO DE GESTÃO DE MEIOS DE PGTO. LTDA. - SEM PARAR',
 'JK COMBUSTIVEIS',
 'VIA 40 CONCESSIONARIA BR040 S/A',
 'CONCESSIONARIA BR-040 S.A.',
 'RODOVIAS INTEGRADAS DO PARANA S/A',
 'CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
 'CARREFOUR COMERCIO E INDUSTRIA LTDA',
 'Cia Aérea - AVIANCA',
 'OI S.A',
 'Cia Aérea - PASSAREDO',
 'Sintaxi-DF',
 'Cia Aérea - TAM',
 'TELEFÔNICA BRASIL S.A. VIVO',
 'VIA SUL LTDA',
 'Conc. Sistema Anhanguera-Bandeirantes S/A',
 'Cia Aérea - AZUL',
 'AUTO SHOPPING DERIVADOS DE PETROLEO LTDA',
 'TAM',
 'PETROIL COMBUSTIVEIS LTDA',
 'CEMIG DISTRIBUIÇÃO S.A',
 'AUTO POSTO CONCORDE LTDA',
 '076 - MELHOR 10 - CASCOL COMBUSTIVEIS PARA VEICULOS LTDA',
 'CELULAR FUNCIONAL',
 'DRA4 DERIVADOS DE PETROLEO LTDA',
 'CORREIOS - SEDEX 10',
 'TELEFÔNICA BRASIL S.A']


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
                                                          "nomeFornecedor"] in txtFornecedores else f"OUTROS_{expense_from_rest["tipoDespesa"]}"

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