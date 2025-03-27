import csv
import logging
import requests
import streamlit as st

from teste import run_model
from teste_llm import run_llm
from teste_rf import run

logging.getLogger("shap").setLevel(logging.ERROR)

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


class Deputado:
    def __init__(self, id, name, urlPhoto, email):
        self.id = id
        self.name = name
        self.urlPhoto = urlPhoto
        self.email = email

    def __str__(self):
        return f"Deputado {self.id}: {self.name} ({self.urlPhoto})"


def build_data_to_alert(deputado, result):
    return {
        "resultado": {
            **result
        },
        "deputado": {
            "id": deputado.id,
            "nome": deputado.name,
            "email": deputado.email,
            "foto": deputado.urlPhoto
        }
    }


def run_model_random_forest(deputado, despesa):
    return run(deputado, despesa)


def run_model_isolation_forest(deputado, despesa):
    result = run_model(despesa)
    return build_data_to_alert(deputado, result)


def load_deputados():
    deputados = []
    filename = 'files/deputados.csv'
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            deputado = Deputado(id=row[0], name=row[1], urlPhoto=row[2], email=row[3])
            deputados.append(deputado)
    return deputados


def get_anomalies_for_deputados(deputados):
    anomalies = []
    for deputado in deputados:
        url_despesas = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputado.id}/despesas?ordem=desc&ordenarPor=dataDocumento"
        try:
            response = requests.get(url_despesas)
            response.raise_for_status()
            content = response.json()
            despesas = content["dados"]

            for despesa in despesas:
                if despesa["tipoDespesa"] not in selected_categories:
                    continue

                result_if = run_model_isolation_forest(deputado, despesa)
                is_anomaly_by_rf = run_model_random_forest(deputado, despesa)
                result_llm = run_llm(despesa)

                print(f"Resultados:")
                print(f"Result IF: {result_if}")
                print(f"Result RF: {is_anomaly_by_rf}")
                print(f"Result LLM: {result_llm}")

                if result_if['resultado']['alert'] == "RED" or is_anomaly_by_rf or result_llm["is_anomaly"]:
                    anomaly = {
                        "Deputado": result_if["deputado"]["nome"],
                        "Valor Líquido": result_if["resultado"]["expense"]["valor"],
                        "Documento": result_if["resultado"]["expense"]["url_doc"],
                        "Tipo": result_if["resultado"]["expense"]["type"],
                        "IF Anomaly": result_if["resultado"]["is_anomaly"],
                        "RF Anomaly": is_anomaly_by_rf,
                        "LLM Anomaly": result_llm["is_anomaly"],
                        "LLM Description": result_llm["description"],
                        "Despesa": despesa
                    }
                    anomalies.append(anomaly)
        except requests.RequestException as error:
            st.error(f"Erro ao buscar dados do deputado {deputado.name}: {error}")
    return anomalies


def main():
    st.title("Análise de Despesas dos Deputados")
    st.write("Selecione os deputados para buscar as despesas e verificar possíveis anomalias.")

    deputados = load_deputados()
    options = [dep.name for dep in deputados]
    selected_names = st.multiselect("Selecione os Deputados", options)

    if st.button("Buscar Despesas"):
        # Filtra os deputados selecionados
        selected_deputados = [dep for dep in deputados if dep.name in selected_names]
        if not selected_deputados:
            st.warning("Nenhum deputado selecionado!")
        else:
            with st.spinner("Buscando dados..."):
                anomalies = get_anomalies_for_deputados(selected_deputados)
            if anomalies:
                st.success(f"Foram encontradas {len(anomalies)} anomalias.")
                # Exibe cada anomalia em um bloco separado
                for anomaly in anomalies:
                    st.markdown("---")
                    st.subheader(f"Deputado: {anomaly['Deputado']}")
                    st.write(f"**Valor Líquido:** R$ {anomaly['Valor Líquido']:.2f}")
                    st.write(f"**Documento:** [Link]({anomaly['Documento']})")
                    st.write(f"**Tipo de Despesa:** {anomaly['Tipo']}")
                    st.write(f"**Anomalia (Isolation Forest):** {anomaly['IF Anomaly']}")
                    st.write(f"**Anomalia (Random Forest):** {anomaly['RF Anomaly']}")
                    st.write(f"**Anomalia (LLM):** {anomaly['LLM Anomaly']}")
                    st.write("**Descrição (LLM):**")
                    st.info(anomaly["LLM Description"])
                    with st.expander("Ver Detalhes da Despesa"):
                        st.json(anomaly["Despesa"])
            else:
                st.warning("Nenhuma anomalia encontrada.")


if __name__ == '__main__':
    main()
