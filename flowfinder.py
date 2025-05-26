import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def buscar_leads(nicho, cidade, quantidade):
    servico = Service(ChromeDriverManager().install())
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--headless")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")

    navegador = webdriver.Chrome(service=servico, options=opcoes)

    url = f"https://www.google.com/maps/search/{nicho}+em+{cidade}"
    navegador.get(url)
    time.sleep(5)

    nomes = []
    enderecos = []
    telefones = []
    sites = []

    scrolls = quantidade // 10 + 1
    for _ in range(scrolls):
        navegador.execute_script("window.scrollBy(0,1000)")
        time.sleep(2)

    elementos = navegador.find_elements(By.CLASS_NAME, "hfpxzc")

    for e in elementos[:quantidade]:
        try:
            e.click()
            time.sleep(2)
            nome = navegador.find_element(By.CLASS_NAME, "DUwDvf").text
        except:
            nome = ''
        try:
            endereco = navegador.find_element(By.CLASS_NAME, "Io6YTe").text
        except:
            endereco = ''
        try:
            telefone = navegador.find_element(By.XPATH, "//button[contains(@aria-label, 'Telefone')]").text
        except:
            telefone = ''
        try:
            site = navegador.find_element(By.XPATH, "//a[contains(@aria-label, 'Site')]").get_attribute('href')
        except:
            site = ''
        nomes.append(nome)
        enderecos.append(endereco)
        telefones.append(telefone)
        sites.append(site)

    navegador.quit()

    df = pd.DataFrame({
        'Nome': nomes,
        'Endereço': enderecos,
        'Telefone': telefones,
        'Site': sites
    })
    return df

st.title("FlowFinder - Buscador de Leads")

nicho = st.text_input("Nicho (ex: pizzaria, dentista, salão)")
cidade = st.text_input("Cidade (ex: São Paulo, Rio de Janeiro)")
quantidade = st.slider("Quantidade de empresas", 10, 100, 50)

if st.button("Buscar Leads"):
    with st.spinner("Buscando leads... isso pode levar alguns minutos"):
        df = buscar_leads(nicho, cidade, quantidade)
        st.success(f"Encontrados {len(df)} leads!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name=f"Leads_{nicho}_{cidade}.csv",
            mime='text/csv'
        )
