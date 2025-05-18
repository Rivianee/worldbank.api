"""
Script para configuração inicial do banco de dados.
Realiza web scraping, processa os dados e cria o banco de dados.
"""

import sys
from pathlib import Path
import os

# Adicionar diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from src.scraper import get_country_list, get_country_data
from src.database import process_data_for_db, create_database_from_data

def setup_data(limit=10):
    """
    Coleta dados do Banco Mundial, processa e cria o banco de dados.
    
    Args:
        limit: Número de países para coletar (limite para teste)
        
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    print(f"Coletando dados do Banco Mundial para {limit} países...")
    
    # 1. Obter lista de países
    countries = get_country_list()
    
    if not countries:
        print("Falha ao obter lista de países. Abortando.")
        return False
    
    # 2. Obter dados para um subconjunto de países
    countries_data = []
    for country in countries[:limit]:  # Limitar para teste
        country_data = get_country_data(country['url'], country['code'], country['name'])
        if country_data:
            countries_data.append(country_data)
    
    if not countries_data:
        print("Falha ao obter dados dos países. Abortando.")
        return False
    
    # 3. Processar dados para o banco de dados
    countries, indicators, indicator_values = process_data_for_db(countries_data)
    
    # 4. Criar banco de dados
    return create_database_from_data(countries, indicators, indicator_values)

if __name__ == "__main__":
    # Obter número de países como argumento da linha de comando
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Argumento inválido. Usando valor padrão: {limit}")
    
    success = setup_data(limit)
    
    if success:
        print("Configuração do banco de dados concluída com sucesso!")
    else:
        print("Falha na configuração do banco de dados.")
        sys.exit(1)