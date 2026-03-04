import streamlit as st
import pdfplumber
import re
from bs4 import BeautifulSoup
from io import BytesIO
from docx import Document
from openpyxl import Workbook

st.set_page_config(page_title="Validador TR", layout="wide")

st.title("Validador Automático de Descritivo - TR")

# ==========================
# Extrair ordem da tabela
# ==========================

def extrair_ordem_tabela(pdf_file):
    ordem = []

    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            tabelas = pagina.extract_tables()
            for tabela in tabelas:
                for linha in tabela:
                    if linha and len(linha) >= 3:
                        numero = str(linha[0]).strip()
                        catmat = str(linha[2]).strip()

                        if numero.isdigit() and catmat.isdigit():
                            ordem.append({
                                "numero": int(numero),
                                "catmat": catmat
                            })

    vistos = set()
    ordem_filtrada = []
    for item in ordem:
        if item["catmat"] not in vistos:
            ordem_filtrada.append(item)
            vistos.add(item["catmat"])

    return ordem_filtrada


# ==========================
# Extrair blocos do HTML
# ==========================

def extrair_blocos(html):
    soup = BeautifulSoup(html, "html.parser")
    blocos = {}

    itens = soup.find_all("p", class_="Item_Nivel2")

    for item in itens:
        texto = item.get_text()
        catmat_match = re.search(r'CATMAT:\s*(\d+)', texto)

        if catmat_match:
            catmat = catmat_match.group(1)
            bloco_html = str(item)

            next_node = item.find_next_sibling()

            while next_node and not (
                next_node.name == "p" and
                "Item_Nivel2" in (next_node.get("class") or [])
            ):
                bloco_html += str(next_node)
                next_node = next_node.find_next_sibling()

            blocos[catmat] = bloco_html

    return blocos


# ==========================
# Reorganizar
# ==========================

def reorganizar(pdf_file, html):

    ordem = extrair_ordem_tabela(pdf_file)
    blocos = extrair_blocos(html)

    resultado = ""

    for item in ordem:
        numero = item["numero"]
        catmat = item["catmat"]

        if catmat in blocos:
            bloco_original = blocos[catmat]

            bloco_corrigido = re.sub(
                r'Item\s*\d+:',
                f'Item {numero:02d}:',
                bloco_original
            )

            resultado += bloco_corrigido + "<br><br>"

    return resultado


# ==========================
# Interface
# ==========================

pdf_file = st.file_uploader("Envie o PDF com a tabela", type=["pdf"])
html_file = st.file_uploader("Envie o HTML do descritivo", type=["html", "txt"])

if pdf_file and html_file:

    html_content = html_file.read().decode("utf-8")

    if st.button("Processar"):

        resultado = reorganizar(pdf_file, html_content)

        html_final = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        </head>
        <body>
        {resultado}
        </body>
        </html>
        """

        st.success("Processado com sucesso!")

        st.download_button(
            "Baixar HTML Final",
            html_final,
            "descritivo_corrigido.html",
            "text/html"
        )
