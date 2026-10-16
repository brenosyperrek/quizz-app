# --- diagnostics bootstrap: install crash/exception logging before app code ---
import os as _diag_os
import sys as _diag_sys

_diag_dir = _diag_os.path.dirname(_diag_os.path.abspath(__file__))
if _diag_dir not in _diag_sys.path:
    _diag_sys.path.insert(0, _diag_dir)
import app_diagnostics  # noqa: E402

app_diagnostics.install_diagnostics()
# --- end diagnostics bootstrap ---

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Quizz App", layout="centered")

QUESTIONS = [
    {"q": "Qual é a capital do Brasil?", "options": ["São Paulo", "Brasília", "Rio de Janeiro", "Salvador"], "answer": 1},
    {"q": "Quanto é 7 x 8?", "options": ["54", "56", "58", "64"], "answer": 1},
    {"q": "Qual linguagem é muito usada com Apache Spark?", "options": ["Python", "COBOL", "Fortran", "Pascal"], "answer": 0},
    {"q": "Qual é o maior planeta do Sistema Solar?", "options": ["Terra", "Marte", "Júpiter", "Vênus"], "answer": 2},
    {"q": "Qual formato de tabela é padrão no Databricks?", "options": ["CSV", "Delta", "XML", "TXT"], "answer": 1},
]


def reset():
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.last_correct = False
    st.session_state.results = []


if "idx" not in st.session_state:
    reset()

user = st.context.headers.get("X-Forwarded-Preferred-Username")
st.title("Quizz App")
st.caption(f"Olá, {user}!" if user else "Olá!")

total = len(QUESTIONS)
idx = st.session_state.idx

if idx >= total:
    st.progress(1.0)
    st.success(f"Fim! Você acertou {st.session_state.score} de {total}.")
    results = st.session_state.results
    chart_data = pd.DataFrame(
        {
            "Pergunta": [f"P{i + 1}" for i in range(len(results))],
            "Acertos": [int(r) for r in results],
            "Erros": [int(not r) for r in results],
        }
    ).set_index("Pergunta")
    hits = int(chart_data["Acertos"].sum())
    totals = pd.DataFrame({"Resultado": ["Acertos", "Erros"], "Quantidade": [hits, len(results) - hits]})
    st.subheader("Acertos x Erros")
    st.vega_lite_chart(
        totals,
        {
            "mark": {"type": "arc", "innerRadius": 50, "tooltip": True},
            "encoding": {
                "theta": {"field": "Quantidade", "type": "quantitative"},
                "color": {
                    "field": "Resultado",
                    "type": "nominal",
                    "scale": {"domain": ["Acertos", "Erros"], "range": ["#2e7d32", "#c62828"]},
                },
            },
        },
        use_container_width=True,
    )
    st.subheader("Resultado por pergunta")
    st.bar_chart(chart_data, color=["#2e7d32", "#c62828"])
    st.button("Reiniciar", on_click=reset)
else:
    item = QUESTIONS[idx]
    st.progress(idx / total, text=f"Pergunta {idx + 1} de {total}")
    choice = st.radio(
        item["q"],
        range(len(item["options"])),
        format_func=lambda i: item["options"][i],
        index=None,
        key=f"choice_{idx}",
        disabled=st.session_state.answered,
    )

    if not st.session_state.answered:
        if st.button("Responder", disabled=choice is None):
            st.session_state.answered = True
            st.session_state.last_correct = choice == item["answer"]
            st.session_state.results.append(st.session_state.last_correct)
            if st.session_state.last_correct:
                st.session_state.score += 1
            st.rerun()
    else:
        if st.session_state.last_correct:
            st.success("Correto!")
        else:
            st.error(f"Errado. Resposta certa: {item['options'][item['answer']]}")

        def next_question():
            st.session_state.idx += 1
            st.session_state.answered = False

        st.button("Próxima" if idx + 1 < total else "Ver resultado", on_click=next_question)
