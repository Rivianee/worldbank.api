"""
Módulo de web scraping para coletar dados do Banco Mundial.
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from pathlib import Path
import os

# Configurações
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Criar diretórios se não existirem
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# URLs do Banco Mundial
BASE_URL = "https://data.worldbank.org"
COUNTRIES_URL = f"{BASE_URL}/country"

# Cabeçalhos HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Categorias de indicadores
INDICATOR_CATEGORIES = ["social", "economic", "environment", "institutions"]

# Funções de Web Scraping
def get_country_list():
    """
    Realiza scraping da lista de países do site do Banco Mundial.
    """
    print("Obtendo lista de países...")
    
    try:
        # Fazer requisição para a página de países
        response = requests.get(COUNTRIES_URL, headers=HEADERS)
        response.raise_for_status()
        
        # Parsear o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar os links dos países
        country_links = []
        
        # Buscar todos os links de país
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href.startswith('/country/'):
                # Limpar o código do país
                country_code = href.split('/')[-1].split('?')[0]
                country_code = re.sub(r'[^a-zA-Z0-9\-]', '', country_code)
                
                country_links.append({
                    'url': BASE_URL + href,
                    'code': country_code,
                    'name': link.text.strip()
                })
        
        # Remover duplicatas
        unique_links = []
        seen_codes = set()
        for country in country_links:
            if country['code'] not in seen_codes and country['name']:
                unique_links.append(country)
                seen_codes.add(country['code'])
        
        print(f"Encontrados {len(unique_links)} países únicos.")
        
        # Salvar a lista bruta em JSON
        country_list_path = RAW_DIR / "country_list.json"
        with open(country_list_path, 'w', encoding='utf-8') as f:
            json.dump(unique_links, f, indent=2, ensure_ascii=False)
        
        print(f"Lista de países salva em {country_list_path}")
        return unique_links
    
    except Exception as e:
        print(f"Erro ao obter lista de países: {e}")
        return []

def get_country_data(country_url, country_code, country_name):
    """
    Realiza scraping de dados detalhados de um país específico.
    """
    try:
        print(f"Obtendo dados para: {country_name} ({country_code})")
        
        # Fazer requisição para a página do país
        response = requests.get(country_url, headers=HEADERS)
        response.raise_for_status()
        
        # Parsear o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Dados básicos do país
        country_data = {
            'name': country_name,
            'code': country_code,
            'url': country_url,
            'indicators': {},
            'region': None,
            'income_level': None,
            'capital': None
        }
        
        # Buscar região e classificação de renda
        region_element = soup.find('div', string=re.compile(r'Region', re.IGNORECASE))
        if region_element and region_element.find_next():
            country_data['region'] = region_element.find_next().text.strip()
        
        income_element = soup.find('div', string=re.compile(r'Income', re.IGNORECASE))
        if income_element and income_element.find_next():
            country_data['income_level'] = income_element.find_next().text.strip()
        
        # Extrair indicadores da página
        for category in INDICATOR_CATEGORIES:
            country_data['indicators'][category] = []
            
            # Pesquisar por seções que podem conter indicadores desta categoria
            for section in soup.find_all(['section', 'div'], class_=re.compile(r'indicator|data')):
                if category.lower() in section.get_text().lower():
                    # Encontrar tabelas ou indicadores nesta seção
                    for element in section.find_all(['tr', 'div'], class_=re.compile(r'indicator|row')):
                        # Extrair nome e valor
                        name_element = element.find(['th', 'td', 'div'], class_=re.compile(r'name|title'))
                        value_element = element.find(['td', 'div', 'span'], class_=re.compile(r'value|data'))
                        
                        if name_element and value_element:
                            indicator_name = name_element.text.strip()
                            value_text = value_element.text.strip()
                            
                            # Extrair ano
                            year_match = re.search(r'\((\d{4})\)', value_text)
                            year = int(year_match.group(1)) if year_match else 2023
                            
                            # Criar código do indicador
                            indicator_code = re.sub(r'[^a-zA-Z0-9]', '_', indicator_name).lower()
                            
                            # Adicionar indicador
                            country_data['indicators'][category].append({
                                'name': indicator_name,
                                'code': indicator_code,
                                'value': value_text.replace(f"({year})", "").strip(),
                                'year': year
                            })
        
        # Salvar os dados brutos do país
        country_data_path = RAW_DIR / f"{country_code}.json"
        with open(country_data_path, 'w', encoding='utf-8') as f:
            json.dump(country_data, f, indent=2, ensure_ascii=False)
        
        print(f"Dados de {country_name} salvos em {country_data_path}")
        
        # Pausa para evitar sobrecarga no servidor
        time.sleep(random.uniform(1, 2))
        
        return country_data
    
    except Exception as e:
        print(f"Erro ao obter dados do país {country_name}: {e}")
        return None