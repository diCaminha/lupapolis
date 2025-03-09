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
