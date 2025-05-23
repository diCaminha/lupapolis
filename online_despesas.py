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

st.set_page_config(
    page_title="Monitor de Despesas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"   # esconde a barra preta
)

st.markdown(
    f"""
    <style>
    /* remove barra do Streamlit */
    header, footer {{visibility:hidden;}}

    .stApp {{
        background-color:{PRIMARY_BG};
        color:#212529;
        font-family:'IBM Plex Sans',system-ui,sans-serif;
    }}

    h1 {{color:{ACCENT_GREEN};margin:.3rem 0 1rem 0;font-size:2.4rem}}

    .block-container {{
        max-width:1080px;  /* mais largo */
        margin:auto;
        padding-top:1.2rem;
    }}

    /* painel explicativo recolhível */
    details {{
        background:{CARD_BG};
        border:1px solid #dee2e6;
        border-radius:8px;
        padding:0.8rem 1rem;
        margin-bottom:1.2rem;
    }}
    summary {{font-weight:600;cursor:pointer}}

    /* select */
    div[data-baseweb="select"]>div {{
        background:#fff!important;
        border:1px solid #b5bec6!important;
        border-radius:6px;
    }}
    div[data-baseweb="select"]:focus-within {{
        box-shadow:0 0 0 3px #c8e6c9;
    }}

    /* botão */
    div.stButton>button {{
        background:{ACCENT_GREEN};
        color:#fff;
        border:none;
        padding:.45rem 1.4rem;
        border-radius:6px;
        float:right;           /* alinha à direita */
    }}
    div.stButton>button:hover {{background:{ACCENT_LIGHT}}}

    /* cards */
    .card {{
        background:{CARD_BG};
        border-radius:8px;
        box-shadow:0 1px 3px rgba(0,0,0,.04);
        padding:1rem 1.3rem;
        margin-bottom:1rem;
    }}
    .card-header {{
        display:flex;justify-content:space-between;align-items:center;
        margin-bottom:.4rem;
    }}
    .card-header img{{border-radius:50%;width:50px;height:50px;object-fit:cover}}
    .alert-label{{color:#c62828;font-weight:600;margin-top:.4rem}}
    a{{color:{ACCENT_GREEN};font-weight:600;text-decoration:none}}
    a:hover{{text-decoration:underline}}
    .stAlert > div {{
        color: #2e7d32 !important;          /* texto verde-escuro */
        background-color: #e8f5e9 !important;  /* verde bem claro */
        border-left: 6px solid #2e7d32 !important;
    }}
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

STATS = json.loads(Path("robust_stats_by_supplier.json").read_text())


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
                res = run_model(desp, k_threshold=7.5)  # limite mais rígido
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

    # ▼ painel recolhível
    st.markdown(
        """
        <details>
        <summary>Como identificamos uma despesa fora do padrão?</summary>
        <ul style="margin-top:.6rem">
          <li>Analisamos o histórico de cada <b>fornecedor × tipo de despesa</b>.</li>
          <li>Calculamos a <b>mediana</b> (valor típico) e o <b>MAD</b> (dispersão robusta).</li>
          <li>Uma nova nota que fique <b>7,5 × MAD</b> acima da mediana é sinalizada aqui.</li>
          <li>Isso filtra apenas casos com grande chance de anomalia.</li>
        </ul>
        </details>
        """,
        unsafe_allow_html=True,
    )

    st.write("Selecione os deputados que deseja checar." )

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
