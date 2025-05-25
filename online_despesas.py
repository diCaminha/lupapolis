#!/usr/bin/env python
# coding: utf-8
"""
Dashboard Streamlit – estilo “portal público”:
fundo off-white (#f8f9fa) e verdes institucionais.
"""

import csv
import json
from pathlib import Path

import requests
import streamlit as st

from teste import run_model

# ──────────────────────  PALETA & CSS  ───────────────────── #

PRIMARY_BG   = "#f8f9fa"   # off-white
CARD_BG      = "#ffffff"   # branco puro para cards
ACCENT_GREEN = "#2e7d32"   # verde principal
ACCENT_LIGHT = "#4caf50"   # hover / claro

st.set_page_config(page_title="Monitor de Despesas",
                   page_icon="💰",
                   layout="wide")

st.markdown(
    """
    <style>
    /* -------- reset do tema Streamlit -------- */
    @media (prefers-color-scheme: dark) {
      html, body, [data-testid="stApp"] { color-scheme: light; }
    }

    /* fundo geral */
    .stApp {
        background-color: #f7f8f9; /* off-white um tom mais quente */
        color: #212529;            /* cinza-escuro */
    }

    /* cabeçalho principal */
    h1 {
        color: #2e7d32;
        font-size: 2.2rem;
        margin-bottom: .2rem;
    }
    /* subtítulos dentro de cards */
    h3 {margin: .2rem 0 .4rem 0;}

    /* container central */
    .block-container {
        max-width: 900px;
        padding: 1rem 2rem;
        margin: auto;
    }

    /* componente select */
    label, .stSelectbox, .stMultiSelect {
        width: 100%;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px;
    }

    /* botão primário */
    div.stButton > button {
        background: #2e7d32;
        border: none;
        color: #fff;
        padding: .5rem 1.2rem;
        border-radius: 6px;
    }
    div.stButton > button:hover {
        background: #43a047;
        color: #fff;
    }

    /* cards das despesas */
    .card {
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,.05);
        padding: 1rem 1.4rem;
        margin-bottom: 1.2rem;
    }

    /* aviso dentro de card */
    .alert-label {
        color: #c62828;
        font-weight: 600;
        margin: .5rem 0 0 0;
    }

    /* imagem deput. alinhada à esquerda do texto */
    .dep-header {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    .dep-header img {border-radius: 50%;}
    
    .stAlert > div {
        color: #2e7d32 !important;          /* texto verde-escuro */
        background-color: #e8f5e9 !important;  /* verde bem claro */
        border-left: 6px solid #2e7d32 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ───────────────────────  dados fixos  ────────────────────── #

selected_categories = [
    "COMBUSTÍVEIS E LUBRIFICANTES.",
    "PASSAGEM AÉREA - RPA",
    "TELEFONIA",
    "SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO",
    "PASSAGEM AÉREA - SIGEPA",
    "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR",
    "FORNECIMENTO DE ALIMENTAÇÃO DO PARLAMENTAR",
    "SERVIÇOS POSTAIS",
    "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR.",
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

STATS = json.loads(Path("saved_models/robust_stats_by_supplier.json").read_text())


# ─────────────────────  helpers  ───────────────────── #

class Deputado:
    def __init__(self, id_, nome, foto, email):
        self.id = id_
        self.nome = nome
        self.foto = foto
        self.email = email


def bucket_nome(fornecedor, tipo):
    return fornecedor if fornecedor in txtFornecedores else f"OUTROS_{tipo}"


def valor_tipico(bucket: str) -> float:
    """Retorna a mediana do bucket ou, se ele não existir,
    a mediana do primeiro bucket disponível."""
    stats = STATS.get(bucket)
    if stats is None:            # bucket ausente
        stats = next(iter(STATS.values()))  # pega qualquer outro
    return stats["median"]


def load_deputados():
    with open("deputados.csv", encoding="utf-8") as f:
        return [Deputado(*row[:4]) for row in csv.reader(f)]


def fetch_anomalies(deps):
    anomalies = []
    for dep in deps:
        url = (
            f"https://dadosabertos.camara.leg.br/api/v2/deputados/"
            f"{dep.id}/despesas?ordem=desc&ordenarPor=dataDocumento"
        )
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            for desp in r.json()["dados"]:
                if desp["tipoDespesa"] not in selected_categories:
                    continue
                res = run_model(desp, k_threshold=5.0)  # limite mais rígido
                if res["alert"] == "RED":
                    bucket = bucket_nome(
                        desp["nomeFornecedor"], desp["tipoDespesa"]
                    )
                    anomalies.append(
                        {
                            "dep": dep,
                            "desp": desp,
                            "valor_tipico": valor_tipico(bucket),
                        }
                    )
        except requests.RequestException as err:
            st.error(f"Erro ao buscar dados de {dep.nome}: {err}")
    return anomalies


# ───────────────────────  UI  ─────────────────────── #

def main():
    st.markdown("<h1>Monitor de Despesas Parlamentares</h1>", unsafe_allow_html=True)
    st.write(
        "Selecione os deputados para verificar se existem despesas recentes "
        "que fogem do padrão histórico."
    )

    deputados = load_deputados()
    nomes = [d.nome for d in deputados]
    escolhidos = st.multiselect("Deputados", nomes)

    if st.button("Buscar Despesas"):
        alvos = [d for d in deputados if d.nome in escolhidos]
        if not alvos:
            st.warning("Nenhum deputado selecionado.")
            return

        with st.spinner("Analisando despesas..."):
            anomalias = fetch_anomalies(alvos)

        if not anomalias:
            st.success("Nenhuma despesa com valor anormal encontrada.")
            return

        st.success(f"Foram encontradas {len(anomalias)} despesas fora do padrão.")

        for a in anomalias:
            dep, desp, tipic = a["dep"], a["desp"], a["valor_tipico"]
            # “card” manual
            st.markdown(
                f"""
                <div class="card">
                    <h3>{dep.nome}</h3>
                    <img src="{dep.foto}" width="80">
                    <p><b>Valor da despesa:</b> R$ {desp['valorLiquido']:.2f}</p>
                    <p><b>Valor típico para este tipo:</b> R$ {tipic:.2f}</p>
                    <p><b>Tipo de despesa:</b> {desp['tipoDespesa']}</p>
                    <p><b>Data do documento:</b> {desp['dataDocumento']}</p>
                    <p><b>Documento:</b> <a href="{desp['urlDocumento']}" target="_blank">abrir</a></p>
                    <div style="color:{ACCENT_GREEN};font-weight:600;">
                        ⚠️ Despesa fora do padrão histórico.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
