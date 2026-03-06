import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
import pdfplumber
from docx import Document
from io import BytesIO

st.set_page_config(page_title="Reorganizador de Descritivo Técnico", layout="wide")

st.title("Reorganizador Inteligente de Descritivo Técnico")

st.write("Envie o HTML do TR e opcionalmente o PDF original para validar a sequência.")

html_file = st.file_uploader("Enviar HTML completo do TR", type=["html","htm","txt"])
pdf_file = st.file_uploader("Enviar PDF do TR completo (opcional)", type=["pdf"])

def extrair_catmat_tabela(html):
    soup = BeautifulSoup(html, "lxml")
    tabela = soup.find("table")

    ordem = []

    for linha in tabela.find_all("tr"):
        texto = linha.get_text(" ", strip=True)
        match = re.search(r'\b(\d{6})\b', texto)
        if match:
            ordem.append(match.group(1))

    return ordem


def extrair_blocos_descritivo(texto):

    blocos = re.split(r'(ITEM\s+\d+)', texto)

    resultado = {}

    for i in range(1, len(blocos), 2):

        titulo = blocos[i]
        conteudo = blocos[i+1]

        bloco = titulo + conteudo

        match = re.search(r'CATMAT[: ]+(\d+)', bloco)

        if match:
            catmat = match.group(1)
            resultado[catmat] = bloco

    return resultado


def gerar_html(blocos_ordenados):

    html_final = ""

    for i,(catmat,bloco) in enumerate(blocos_ordenados.items(),1):

        html_final += f"<p><b>ITEM {i}</b><br>{bloco}</p><br>"

    return html_final


if html_file:

    html_texto = html_file.read().decode("utf-8")

    st.success("HTML carregado")

    ordem_catmat = extrair_catmat_tabela(html_texto)

    st.subheader("Ordem detectada na tabela")

    df = pd.DataFrame({"CATMAT":ordem_catmat})

    st.dataframe(df)

    texto = BeautifulSoup(html_texto,"lxml").get_text()

    blocos = extrair_blocos_descritivo(texto)

    blocos_ordenados = {}

    for catmat in ordem_catmat:

        if catmat in blocos:
            blocos_ordenados[catmat] = blocos[catmat]

    if st.button("GERAR DESCRITIVO CORRIGIDO"):

        html_final = gerar_html(blocos_ordenados)

        st.subheader("Resultado")

        st.code(html_final)

        st.download_button(
            "Baixar HTML corrigido",
            html_final,
            file_name="descritivo_corrigido.html"
        )

        doc = Document()

        for i,(catmat,bloco) in enumerate(blocos_ordenados.items(),1):

            doc.add_heading(f"ITEM {i}", level=2)
            doc.add_paragraph(bloco)

        buffer = BytesIO()
        doc.save(buffer)

        st.download_button(
            "Baixar Word",
            buffer.getvalue(),
            file_name="descritivo_corrigido.docx"
        )

        df2 = pd.DataFrame(blocos_ordenados.items(), columns=["CATMAT","DESCRITIVO"])

        excel = BytesIO()
        df2.to_excel(excel,index=False)

        st.download_button(
            "Baixar Excel",
            excel.getvalue(),
            file_name="descritivo_corrigido.xlsx"
        )
