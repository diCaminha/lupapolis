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
    if df[columns_to_use].isnull().values.any():
        print("Existem valores NaN ou null nas colunas especificadas.")
        df = df.dropna(subset=columns_to_use)
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
        if supplier == "OUTROS":
            # Para fornecedor OUTROS, agrupa por txtDescricao e treina um pipeline para cada descrição
            for description, group_df_desc in group_df.groupby('txtDescricao'):
                X = group_df_desc[['vlrLiquido']]
                if len(X) < 10:
                    logger.info(
                        f"Grupo {description} possui poucos dados ({len(X)} amostras). Ignorando treinamento para esse grupo.")
                    continue

                model_pipeline = build_pipeline_for_vlrLiquido(contamination=contamination_value)
                model_pipeline.fit(X)
                # Armazena o pipeline usando uma chave que combina 'OUTROS' e a descrição
                pipelines_dict[f"OUTROS_{description}"] = model_pipeline
                logger.info(f"Treinamento concluído para a descrição {description} com {len(X)} amostras.")
        else:
            X = group_df[['vlrLiquido']]
            # Se o grupo tiver poucos dados, opta por não treinar um modelo específico
            if len(X) < 10:
                logger.info(
                    f"Grupo {supplier} possui poucos dados ({len(X)} amostras). Ignorando treinamento para esse grupo.")
                continue

            model_pipeline = build_pipeline_for_vlrLiquido(contamination=contamination_value)
            model_pipeline.fit(X)
            pipelines_dict[supplier] = model_pipeline
            logger.info(f"Treinamento concluído para o fornecedor {supplier} com {len(X)} amostras.")

    # Se nenhum modelo foi treinado, cria um modelo global
    if not pipelines_dict:
        global_pipeline = build_pipeline_for_vlrLiquido(contamination=contamination_value)
        X_global = df[['vlrLiquido']]
        global_pipeline.fit(X_global)
        pipelines_dict["GLOBAL"] = global_pipeline
        logger.info("Treinamento do modelo global concluído.")

    # 6) Salvar o dicionário de pipelines
    os.makedirs("saved_models", exist_ok=True)
    joblib.dump(pipelines_dict, "saved_models/isolation_forest_pipeline_by_supplier.pkl")
    logger.info("Modelos salvos em 'saved_models/isolation_forest_pipeline_by_supplier.pkl'.")


if __name__ == "__main__":
    main()