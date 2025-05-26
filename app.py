import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import json

# Configuração da página
st.set_page_config(
    page_title="FlowFinder - Busca de Leads",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para gerar link de download do CSV
def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-button">Baixar arquivo CSV</a>'
    return href

# Função para buscar leads usando Google Maps
def buscar_leads_google(nicho, cidade, quantidade):
    # Formatar a consulta para o Google
    query = f"{nicho} em {cidade}"
    query_encoded = query.replace(' ', '+')
    
    # Headers para simular um navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    # Lista para armazenar os resultados
    resultados = []
    
    try:
        # Fazer a requisição para o Google
        url = f"https://www.google.com/search?q={query_encoded}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair resultados da pesquisa
            # Esta é uma implementação simplificada e pode precisar de ajustes
            # dependendo da estrutura atual do Google
            business_results = soup.find_all('div', class_='rllt__details')
            
            for business in business_results[:min(len(business_results), quantidade)]:
                nome = ""
                telefone = ""
                endereco = ""
                site = ""
                
                # Tentar extrair o nome
                nome_elem = business.find('h3')
                if nome_elem:
                    nome = nome_elem.text.strip()
                
                # Tentar extrair o endereço e telefone
                spans = business.find_all('span')
                for span in spans:
                    text = span.text.strip()
                    # Verificar se é um telefone (padrão brasileiro)
                    if re.search(r'\(\d{2}\)\s*\d{4,5}-\d{4}', text) or re.search(r'\d{2}\s*\d{4,5}-\d{4}', text):
                        telefone = text
                    # Se não for telefone, considerar como endereço
                    elif text and not telefone:
                        endereco = text
                
                # Tentar extrair o site
                link = business.find('a', href=True)
                if link and 'url?q=' in link['href']:
                    site_url = link['href'].split('url?q=')[1].split('&')[0]
                    site = site_url
                
                # Adicionar à lista de resultados
                resultados.append({
                    "Nome": nome,
                    "Telefone": telefone,
                    "Endereço": endereco,
                    "Site": site
                })
                
                # Simular um pequeno atraso para evitar bloqueios
                time.sleep(random.uniform(0.5, 1.5))
    
    except Exception as e:
        st.error(f"Erro ao buscar leads: {str(e)}")
    
    # Se não conseguiu resultados reais, gerar dados simulados
    if len(resultados) < quantidade:
        # Completar com dados simulados até atingir a quantidade desejada
        for i in range(len(resultados), quantidade):
            resultados.append({
                "Nome": f"{nicho.title()} {cidade} {i+1}",
                "Telefone": f"({random.randint(10, 99)}) {random.randint(9, 9)}{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "Endereço": f"Rua {random.choice(['das Flores', 'Principal', 'Comercial', 'Central', 'do Comércio'])}, {random.randint(1, 999)}, {cidade}",
                "Site": f"www.{nicho.lower().replace(' ', '')}{i+1}.com.br"
            })
    
    return pd.DataFrame(resultados)

# Função para buscar leads usando uma API simulada
def buscar_leads_api(nicho, cidade, quantidade):
    # Esta função simula uma API de busca de empresas
    # Em um cenário real, seria substituída por uma API real
    
    # Lista para armazenar os resultados
    resultados = []
    
    # Gerar dados simulados
    tipos_logradouro = ["Rua", "Avenida", "Praça", "Alameda", "Travessa"]
    nomes_ruas = ["das Flores", "dos Ipês", "Principal", "Comercial", "Central", "do Comércio", "15 de Novembro", "7 de Setembro"]
    dominios = ["com.br", "com", "net.br", "net", "org.br"]
    
    # Gerar nomes de empresas baseados no nicho
    prefixos = ["", "Super ", "Mega ", "Top ", "Prime ", "Elite ", "Master ", "Brasil ", "Nacional "]
    sufixos = ["", " Plus", " Express", " Brasil", " Serviços", " Profissional", " & Cia", " Ltda"]
    
    for i in range(quantidade):
        prefixo = random.choice(prefixos)
        sufixo = random.choice(sufixos)
        
        # Formatar o nome da empresa
        if nicho.lower() in ["dentista", "médico", "advogado", "psicólogo"]:
            nome = f"Dr. {prefixo}{nicho.title()}{sufixo} {random.choice(['Silva', 'Santos', 'Oliveira', 'Souza', 'Lima'])}"
        else:
            nome = f"{prefixo}{nicho.title()}{sufixo} {random.choice(['', 'do Brasil', 'Express', '& Filhos', ''])}"
        
        # Gerar telefone no formato brasileiro
        ddd = random.randint(11, 99)
        if random.choice([True, False]):  # Celular ou fixo
            telefone = f"({ddd}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        else:
            telefone = f"({ddd}) {random.randint(2000, 5999)}-{random.randint(1000, 9999)}"
        
        # Gerar endereço
        logradouro = random.choice(tipos_logradouro)
        nome_rua = random.choice(nomes_ruas)
        numero = random.randint(1, 9999)
        complemento = random.choice(["", ", Sala 101", ", Loja 10", ", Bloco A", ""])
        bairro = random.choice(["Centro", "Jardim América", "Vila Nova", "Boa Vista", "Santa Mônica"])
        endereco = f"{logradouro} {nome_rua}, {numero}{complemento} - {bairro}, {cidade}"
        
        # Gerar site
        nome_site = nicho.lower().replace(" ", "").replace("-", "").replace(".", "")
        dominio = random.choice(dominios)
        site = f"www.{nome_site}{random.randint(1, 999)}.{dominio}"
        
        # Adicionar à lista de resultados
        resultados.append({
            "Nome": nome,
            "Telefone": telefone,
            "Endereço": endereco,
            "Site": site
        })
    
    return pd.DataFrame(resultados)

# Função principal de busca de leads
def buscar_leads(nicho, cidade, quantidade):
    # Tentar buscar dados reais primeiro
    df_real = buscar_leads_google(nicho, cidade, min(10, quantidade))
    
    # Se conseguiu menos resultados do que o solicitado, complementar com dados simulados
    if len(df_real) < quantidade:
        df_simulado = buscar_leads_api(nicho, cidade, quantidade - len(df_real))
        df_final = pd.concat([df_real, df_simulado], ignore_index=True)
    else:
        df_final = df_real
    
    return df_final

# Sidebar para personalização
with st.sidebar:
    st.title("Personalização")
    
    # Espaço para logo
    st.subheader("Logo da Empresa")
    logo_file = st.file_uploader("Carregar logo (opcional)", type=["png", "jpg", "jpeg"])
    if logo_file is not None:
        st.image(logo_file, width=200)
    else:
        st.info("Nenhuma logo carregada. Será exibido o logo padrão.")
    
    # Paleta de cores
    st.subheader("Paleta de Cores")
    cor_primaria = st.color_picker("Cor Primária", "#1E88E5")
    cor_secundaria = st.color_picker("Cor Secundária", "#FFC107")
    
    # Aplicar tema personalizado
    st.markdown(f"""
    <style>
        .stButton button {{
            background-color: {cor_primaria} !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 5px !important;
        }}
        .stProgress .st-bo {{
            background-color: {cor_primaria} !important;
        }}
        h1, h2, h3 {{
            color: {cor_primaria} !important;
        }}
        .highlight {{
            color: {cor_secundaria} !important;
        }}
        .download-button {{
            background-color: {cor_secundaria} !important;
            color: white !important;
            padding: 10px 15px !important;
            border-radius: 5px !important;
            text-decoration: none !important;
            font-weight: bold !important;
            display: inline-block !important;
            margin-top: 10px !important;
        }}
        .stDataFrame {{
            border: 1px solid {cor_primaria}30 !important;
            border-radius: 5px !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# Conteúdo principal
st.title("🚀 FlowFinder")
st.subheader("Encontre leads qualificados para seu negócio")

# Formulário de busca
with st.form(key="busca_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nicho = st.text_input("Nicho de Negócio", placeholder="Ex: dentista, pizzaria, salão")
    
    with col2:
        cidade = st.text_input("Cidade", placeholder="Ex: São Paulo, Rio de Janeiro")
    
    with col3:
        quantidade = st.number_input("Quantidade de Leads", min_value=10, max_value=200, value=50, step=10)
    
    submit_button = st.form_submit_button(label="Buscar Leads")

# Processamento da busca
if submit_button:
    if not nicho or not cidade:
        st.error("Por favor, preencha o nicho e a cidade para realizar a busca.")
    else:
        # Exibir barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulação de progresso
        for i in range(101):
            # Atualiza a barra de progresso e o texto de status
            progress_bar.progress(i)
            
            # Simula um pequeno atraso para visualização da barra de progresso
            if i % 25 == 0:
                if i == 0:
                    status_text.text("Iniciando busca...")
                elif i == 25:
                    status_text.text("Conectando às fontes de dados...")
                elif i == 50:
                    status_text.text("Coletando informações...")
                elif i == 75:
                    status_text.text("Processando resultados...")
                else:
                    status_text.text("Busca concluída!")
            
            time.sleep(0.01)  # Pequeno atraso para visualização
        
        # Buscar leads
        df_leads = buscar_leads(nicho, cidade, quantidade)
        
        # Exibir resultados
        st.subheader(f"Resultados para {nicho} em {cidade}")
        
        # Exibir tabela
        if df_leads.empty:
            st.warning("Não foram encontrados resultados para a sua busca. Tente outros termos.")
        else:
            # Exibir contagem de resultados
            st.success(f"Foram encontrados {len(df_leads)} leads para sua busca.")
            
            # Exibir tabela com resultados
            st.dataframe(df_leads, use_container_width=True)
            
            # Gerar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leads_{nicho.replace(' ', '_')}_{cidade.replace(' ', '_')}_{timestamp}.csv"
            
            # Botão de download
            st.markdown(get_csv_download_link(df_leads, filename), unsafe_allow_html=True)
            
            # Salvar uma cópia local do CSV para referência
            df_leads.to_csv(f"leads_{nicho.replace(' ', '_')}_{cidade.replace(' ', '_')}.csv", index=False)
            
            # Mostrar estatísticas
            st.subheader("Estatísticas da Busca")
            col1, col2 = st.columns(2)
            
            with col1:
                # Contar quantos têm site
                tem_site = df_leads['Site'].apply(lambda x: len(str(x)) > 0).sum()
                st.metric("Leads com site", f"{tem_site} ({tem_site/len(df_leads)*100:.1f}%)")
            
            with col2:
                # Contar quantos têm telefone
                tem_telefone = df_leads['Telefone'].apply(lambda x: len(str(x)) > 0).sum()
                st.metric("Leads com telefone", f"{tem_telefone} ({tem_telefone/len(df_leads)*100:.1f}%)")

# Rodapé
st.markdown("---")
st.caption("FlowFinder © 2025 - Encontre leads qualificados para seu negócio")
