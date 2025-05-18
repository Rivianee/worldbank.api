"""
Módulo para processamento de dados e operações de banco de dados.
"""
import sqlite3
import pandas as pd
import json
import re
from pathlib import Path
import os

# Configurações
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_PATH = PROCESSED_DIR / "worldbank.db"

# Criar diretórios se não existirem
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def process_data_for_db(countries_data):
    """
    Processa os dados dos países para criar o banco de dados.
    """
    # Preparar dados para as tabelas
    countries = []
    indicators = []
    indicator_values = []
    
    # Processar cada país
    for country in countries_data:
        # Dados do país
        country_code = country['code']
        countries.append({
            'country_code': country_code,
            'name': country['name'],
            'region': country.get('region'),
            'income_level': country.get('income_level'),
            'capital': country.get('capital'),
            'iso2_code': country_code[:2].lower() if len(country_code) >= 2 else None,
            'iso3_code': country_code[:3].upper() if len(country_code) >= 3 else None
        })
        
        # Processar indicadores por categoria
        for category, category_indicators in country.get('indicators', {}).items():
            for indicator in category_indicators:
                indicator_code = indicator['code']
                indicator_name = indicator['name']
                
                # Adicionar à lista de indicadores únicos
                indicator_exists = False
                for existing in indicators:
                    if existing['indicator_code'] == indicator_code:
                        indicator_exists = True
                        break
                
                if not indicator_exists:
                    indicators.append({
                        'indicator_code': indicator_code,
                        'name': indicator_name,
                        'category': category,
                        'description': '',
                        'source': 'Banco Mundial'
                    })
                
                # Adicionar valor do indicador
                if indicator.get('value') is not None and indicator.get('year'):
                    try:
                        # Limpar e converter o valor
                        value_str = indicator['value']
                        if isinstance(value_str, str):
                            # Remover caracteres não numéricos, exceto ponto decimal
                            value_str = re.sub(r'[^\d.-]', '', value_str)
                        
                        value = float(value_str) if value_str else None
                        
                        if value is not None:
                            indicator_values.append({
                                'country_code': country_code,
                                'indicator_code': indicator_code,
                                'year': indicator['year'],
                                'value': value
                            })
                    except (ValueError, TypeError) as e:
                        print(f"Erro ao processar valor do indicador {indicator_name} para {country['name']}: {e}")
    
    return countries, indicators, indicator_values

def create_database_from_data(countries, indicators, indicator_values):
    """
    Cria o banco de dados SQLite a partir dos dados processados.
    """
    try:
        # Converter para DataFrames
        countries_df = pd.DataFrame(countries)
        indicators_df = pd.DataFrame(indicators)
        values_df = pd.DataFrame(indicator_values)
        
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Criar tabelas
        with conn:
            # Tabela de países
            conn.execute('''
            CREATE TABLE IF NOT EXISTS countries (
                country_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                region TEXT,
                income_level TEXT,
                capital TEXT,
                longitude REAL,
                latitude REAL,
                iso2_code TEXT,
                iso3_code TEXT
            )
            ''')
            
            # Tabela de indicadores (metadados)
            conn.execute('''
            CREATE TABLE IF NOT EXISTS indicators (
                indicator_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                source TEXT
            )
            ''')
            
            # Tabela de valores de indicadores (dados)
            conn.execute('''
            CREATE TABLE IF NOT EXISTS indicator_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT NOT NULL,
                indicator_code TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL,
                FOREIGN KEY (country_code) REFERENCES countries (country_code),
                FOREIGN KEY (indicator_code) REFERENCES indicators (indicator_code),
                UNIQUE(country_code, indicator_code, year)
            )
            ''')
        
        # Inserir dados
        print("Inserindo dados no banco de dados...")
        
        # Países
        countries_df.to_sql("countries", conn, if_exists="replace", index=False)
        print(f"Inseridos {len(countries_df)} países")
        
        # Indicadores (metadados)
        if not indicators_df.empty:
            indicators_df.to_sql("indicators", conn, if_exists="replace", index=False)
            print(f"Inseridos {len(indicators_df)} indicadores")
        
        # Valores de indicadores (dados)
        if not values_df.empty:
            values_df.to_sql("indicator_values", conn, if_exists="replace", index=False)
            print(f"Inseridos {len(values_df)} valores de indicadores")
        
        # Criar índices para melhorar performance
        with conn:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_country_code ON indicator_values (country_code)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_indicator_code ON indicator_values (indicator_code)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON indicator_values (year)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_country_indicator ON indicator_values (country_code, indicator_code)")
        
        conn.close()
        print("Banco de dados criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        return False

def show_countries():
    """
    Exibe os países atualmente no banco de dados como um DataFrame.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql("SELECT country_code, name, region, income_level FROM countries", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao mostrar países: {e}")
        return None

def show_indicators():
    """
    Exibe os indicadores atualmente no banco de dados como um DataFrame.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql("SELECT indicator_code, name, category FROM indicators", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao mostrar indicadores: {e}")
        return None