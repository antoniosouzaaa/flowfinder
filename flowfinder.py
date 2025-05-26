import streamlit as st
import requests
import pandas as pd
import time

st.title("FlowFinder - Buscador de Leads Completo")

api_key = st.text_input("AIzaSyCmlfy0wx9brikdwrHet43JU_I_yoZ1dj0", type="password")
nicho = st.text_input("Nicho (ex: pizzaria, dentista, salão)")
cidade = st.text_input("Cidade (ex: São Paulo, Rio de Janeiro)")
quantidade = st.slider("Quantidade de empresas", 10, 30, 20)

def buscar_places(api_key, query, cidade, max_results):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} em {cidade}",
        "key": api_key,
        "language": "pt-BR",
    }
    resultados = []
    while len(resultados) < max_results:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            st.error("Erro na API do Google Places.")
            break
        data = response.json()
        resultados.extend(data.get("results", []))
        if "next_page_token" in data and len(resultados) < max_results:
            next_page_token = data["next_page_token"]
            time.sleep(2)  # Aguarda token ativar
            params["pagetoken"] = next_page_token
        else:
            break
    return resultados[:max_results]

def buscar_detalhes_place(api_key, place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website",
        "key": api_key,
        "language": "pt-BR",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        resultado = response.json().get("result", {})
        telefone = resultado.get("formatted_phone_number", "")
        site = resultado.get("website", "")
        return telefone, site
    return "", ""

if st.button("Buscar Leads"):
    if not api_key or not nicho or not cidade:
        st.warning("Preencha todos os campos e insira a API Key.")
    else:
        with st.spinner("Buscando leads... isso pode levar alguns minutos"):
            results = buscar_places(api_key, nicho, cidade, quantidade)
            nomes, enderecos, telefones, sites, ratings = [], [], [], [], []
            for place in results:
                nomes.append(place.get("name", ""))
                enderecos.append(place.get("formatted_address", ""))
                ratings.append(place.get("rating", ""))
                telefone, site = buscar_detalhes_place(api_key, place["place_id"])
                telefones.append(telefone)
                sites.append(site)
                time.sleep(0.2)  # Para evitar limite rápido da API
            df = pd.DataFrame({
                "Nome": nomes,
                "Endereço": enderecos,
                "Telefone": telefones,
                "Site": sites,
                "Avaliação": ratings
            })
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Baixar CSV", data=csv, file_name=f"Leads_{nicho}_{cidade}.csv", mime="text/csv")
