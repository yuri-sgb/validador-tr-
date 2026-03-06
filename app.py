import streamlit as st
import re
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

st.title("Reorganizador Inteligente de Descritivo Técnico (CATMAT)")

st.write("Este aplicativo reorganiza automaticamente o descritivo técnico conforme a ordem da tabela do Termo de Referência.")

html_file = st.file_uploader("Enviar HTML completo do TR (tabela + descritivo)", type=["html","txt"])

# --------------------------------------------------
# FUNÇÃO: EXTRAIR ORDEM DA TABELA
# --------------------------------------------------

def extrair_ordem_tabela(html):

    soup = BeautifulSoup(html, "html.parser")

    ordem = []

    tabela = soup.find("table")

    if tabela:

        linhas = tabela.find_all("tr")

        for linha in linhas:

            colunas = linha.find_all("td")

            if len(colunas) >= 3:

                numero = colunas[0].get_text(strip=True)
                catmat = colunas[2].get_text(strip=True)

                if numero.isdigit() and catmat.isdigit():

                    ordem.append(catmat)

    return ordem


# --------------------------------------------------
# FUNÇÃO: EXTRAIR BLOCOS DO DESCRITIVO
# --------------------------------------------------

def extrair_blocos_descritivo(texto):

    blocos = re.split(r'(ITEM\s+\d+)', texto, flags=re.IGNORECASE)

    resultado = {}

    for i in range(1, len(blocos), 2):

        titulo = blocos[i]
        conteudo = blocos[i+1]

        bloco = titulo + conteudo

        match = re.search(r'CATMAT[^0-9]*(\d{6})', bloco, re.IGNORECASE)

        if match:

            catmat = match.group(1)

            resultado[catmat] = bloco

    return resultado


# --------------------------------------------------
# PROCESSAMENTO
# --------------------------------------------------

if html_file:

    html = html_file.read().decode("utf-8", errors="ignore")

    st.success("Arquivo carregado com sucesso.")

    ordem_catmat = extrair_ordem_tabela(html)

    st.subheader("CATMAT detectados na tabela")

    st.write(ordem_catmat)

    blocos = extrair_blocos_descritivo(html)

    st.subheader("Blocos encontrados no descritivo")

    st.write(len(blocos))

    st.write(list(blocos.keys())[:20])

    if st.button("Aplicar Correção do Descritivo"):

        blocos_ordenados = {}

        for catmat in ordem_catmat:

            if catmat in blocos:

                blocos_ordenados[catmat] = blocos[catmat]

        html_corrigido = ""

        contador = 1

        for catmat in ordem_catmat:

            if catmat in blocos_ordenados:

                bloco = blocos_ordenados[catmat]

                bloco_corrigido = re.sub(
                    r'ITEM\s+\d+',
                    f'ITEM {contador}',
                    bloco,
                    count=1,
                    flags=re.IGNORECASE
                )

                html_corrigido += bloco_corrigido + "\n\n"

                contador += 1

        st.subheader("Pré-visualização do resultado")

        st.text_area("Resultado", html_corrigido, height=400)

        st.download_button(
            "Baixar HTML Corrigido",
            html_corrigido,
            file_name="descritivo_corrigido.html",
            mime="text/html"
        )
