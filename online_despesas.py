#!/usr/bin/env python
# coding: utf-8
"""
Dashboard Streamlit – detector robusto (mediana + MAD) sem partes de LLM
e sem jargões técnicos para o usuário final.
"""

import csv
import json
import logging
from pathlib import Path

import requests
import streamlit as st

from teste import run_model           # detector robusto já implementado

# ─────────────────────────  configuração ────────────────────────── #

logging.basicConfig(level=logging.WARNING)

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

# set para lookup O(1)
txtFornecedores = {
    'SERVIÇO NACIONAL DE APRENDIZAGEM COMERCIAL - SENAC',
    'CLARO S.A',
    'UBER DO BRASIL TECNOLOGIA LTDA',
    # … (restante da lista)
    'TELEFÔNICA BRASIL S.A'
}

# carrega estatísticas salvas pelo treinamento
STATS_FILE = Path("saved_models/robust_stats_by_supplier.json")
with STATS_FILE.open(encoding="utf-8") as f:
    STATS = json.load(f)


# ─────────────────────────  classes utilitárias ──────────────────── #

class Deputado:
    def __init__(self, id_, name, foto, email):
        self.id = id_
        self.name = name
        self.foto = foto
        self.email = email


def bucket_name(fornecedor: str, tipo: str) -> str:
    """Define o bucket utilizado no treinamento."""
    return fornecedor if fornecedor in txtFornecedores else f"OUTROS_{tipo}"


def valor_tipico(bucket: str) -> float:
    stats = STATS.get(bucket) or STATS.get("GLOBAL")
    return stats["median"]


# ─────────────────────────  fluxo principal ──────────────────────── #

def load_deputados():
    with open("deputados.csv", encoding="utf-8") as f:
        return [Deputado(*row[:4]) for row in csv.reader(f)]


def get_anomalies(deputados):
    anomalies = []
    for dep in deputados:
        url = (f"https://dadosabertos.camara.leg.br/api/v2/deputados/"
               f"{dep.id}/despesas?ordem=desc&ordenarPor=dataDocumento")
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            for desp in r.json()["dados"]:
                if desp["tipoDespesa"] not in selected_categories:
                    continue

                res = run_model(desp)
                if res["alert"] != "RED":
                    continue  # não é anomalia

                bucket = bucket_name(desp["nomeFornecedor"], desp["tipoDespesa"])
                anomalies.append({
                    "deputado": dep,
                    "despesa": desp,
                    "valor_tipico": valor_tipico(bucket)
                })
        except requests.RequestException as err:
            st.error(f"Erro ao buscar dados de {dep.name}: {err}")
    return anomalies


# ─────────────────────────────  UI  ──────────────────────────────── #

def main():
    st.title("Despesas de Deputados – Monitor de Anomalias")
    st.write("Selecione deputados para verificar despesas recentes fora do padrão.")

    deputados = load_deputados()
    nomes = [d.name for d in deputados]
    selecionados = st.multiselect("Deputados", nomes)

    if st.button("Buscar Despesas"):
        alvo = [d for d in deputados if d.name in selecionados]
        if not alvo:
            st.warning("Nenhum deputado selecionado.")
            return

        with st.spinner("Buscando e analisando despesas..."):
            lista_anomalias = get_anomalies(alvo)

        if not lista_anomalias:
            st.success("Nenhuma despesa suspeita encontrada.")
            return

        st.success(f"{len(lista_anomalias)} despesas suspeitas encontradas.")
        for a in lista_anomalias:
            dep   = a["deputado"]
            desp  = a["despesa"]
            tipic = a["valor_tipico"]

            st.markdown("---")
            st.subheader(dep.name)
            st.image(dep.foto, width=80)
            st.write(f"**Valor da despesa:** R$ {desp['valorLiquido']:.2f}")
            st.write(f"**Valor típico para este tipo:** R$ {tipic:.2f}")
            st.write(f"**Tipo de despesa:** {desp['tipoDespesa']}")
            st.write(f"**Data do documento:** {desp['dataDocumento']}")
            st.write(f"**Link do documento:** [abrir]({desp['urlDocumento']})")
            st.warning("⚠️ Esta despesa parece fora do padrão histórico para "
                       "este fornecedor/tipo.")

            with st.expander("Ver detalhes brutos"):
                st.json(desp)


if __name__ == "__main__":
    main()
