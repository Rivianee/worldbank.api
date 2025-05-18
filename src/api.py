"""
API FastAPI para acessar dados do Banco Mundial.
"""
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Depends, Path as FastAPIPath
from typing import List, Dict, Optional, Any
from pathlib import Path
import uvicorn
import os
import nest_asyncio

# Aplicar nest_asyncio para Jupyter
nest_asyncio.apply()

# Configurações
DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_PATH = PROCESSED_DIR / "worldbank.db"

# Criar diretórios se não existirem
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Inicializar FastAPI
app = FastAPI(
    title="API do Banco Mundial",
    description="API para acessar dados de países e indicadores do Banco Mundial",
    version="1.0.0",
)

# Dependência para conexão com o banco de dados
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Retornar resultados como dicionários
    try:
        yield conn
    finally:
        conn.close()

# Rotas da API
@app.get("/")
def read_root():
    """Retorna informações básicas sobre a API."""
    return {
        "name": "API do Banco Mundial",
        "description": "API para acessar dados de países e indicadores do Banco Mundial",
        "endpoints": {
            "countries": "/countries",
            "country": "/countries/{country_code}",
            "indicators": "/countries/{country_code}/indicators",
            "profile": "/countries/{country_code}/profile",
            "categories": "/indicators/categories"
        }
    }

@app.get("/countries")
def list_countries(
    skip: int = Query(0, description="Número de registros para pular"),
    limit: int = Query(100, description="Número máximo de registros para retornar"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Lista todos os países disponíveis."""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM countries")
    total = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT country_code, name, region FROM countries ORDER BY name LIMIT ? OFFSET ?", 
        (limit, skip)
    )
    countries = [dict(row) for row in cursor.fetchall()]
    
    return {"total": total, "data": countries}

@app.get("/countries/{country_code}")
def get_country(
    country_code: str = FastAPIPath(..., description="Código do país"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Retorna informações detalhadas sobre um país específico."""
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM countries WHERE country_code = ?", 
        (country_code,)
    )
    
    country = cursor.fetchone()
    
    if not country:
        raise HTTPException(status_code=404, detail=f"País com código '{country_code}' não encontrado")
    
    return dict(country)

@app.get("/countries/{country_code}/indicators")
def get_country_indicators(
    country_code: str = FastAPIPath(..., description="Código do país"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Retorna indicadores para um país específico."""
    cursor = db.cursor()
    
    # Verificar se o país existe
    cursor.execute("SELECT * FROM countries WHERE country_code = ?", (country_code,))
    country = cursor.fetchone()
    
    if not country:
        raise HTTPException(status_code=404, detail=f"País com código '{country_code}' não encontrado")
    
    # Construir consulta para indicadores
    query = """
    SELECT 
        i.indicator_code, 
        i.name, 
        i.category,
        iv.year, 
        iv.value
    FROM 
        indicator_values iv
    JOIN 
        indicators i ON iv.indicator_code = i.indicator_code
    WHERE 
        iv.country_code = ?
    """
    
    params = [country_code]
    
    if category:
        query += " AND i.category = ?"
        params.append(category)
    
    query += " ORDER BY i.name, iv.year DESC"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    # Agrupar por indicador
    indicators = {}
    for row in results:
        indicator_code = row["indicator_code"]
        
        if indicator_code not in indicators:
            indicators[indicator_code] = {
                "indicator_code": indicator_code,
                "name": row["name"],
                "category": row["category"],
                "values": []
            }
        
        indicators[indicator_code]["values"].append({
            "year": row["year"],
            "value": row["value"]
        })
    
    return {
        "country": dict(country),
        "indicators": list(indicators.values())
    }

@app.get("/countries/{country_code}/profile")
def get_country_profile(
    country_code: str = FastAPIPath(..., description="Código do país"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Retorna um perfil completo do país com os indicadores mais recentes."""
    cursor = db.cursor()
    
    # Verificar se o país existe
    cursor.execute("SELECT * FROM countries WHERE country_code = ?", (country_code,))
    country = cursor.fetchone()
    
    if not country:
        raise HTTPException(status_code=404, detail=f"País com código '{country_code}' não encontrado")
    
    # Buscar indicadores mais recentes por categoria
    query = """
    WITH RankedIndicators AS (
        SELECT 
            i.indicator_code, 
            i.name,
            i.category,
            iv.year, 
            iv.value,
            ROW_NUMBER() OVER (PARTITION BY i.indicator_code ORDER BY iv.year DESC) as rank
        FROM 
            indicator_values iv
        JOIN 
            indicators i ON iv.indicator_code = i.indicator_code
        WHERE 
            iv.country_code = ?
    )
    SELECT 
        indicator_code, 
        name,
        category,
        year, 
        value
    FROM 
        RankedIndicators
    WHERE 
        rank = 1
    ORDER BY 
        category, name
    """
    
    cursor.execute(query, (country_code,))
    indicators = cursor.fetchall()
    
    # Organizar por categoria
    categories = {}
    for indicator in indicators:
        category = indicator["category"] or "other"
        
        if category not in categories:
            categories[category] = []
        
        categories[category].append({
            "indicator_code": indicator["indicator_code"],
            "name": indicator["name"],
            "value": indicator["value"],
            "year": indicator["year"]
        })
    
    return {
        "country": dict(country),
        "profile": categories
    }

@app.get("/indicators/categories")
def get_indicator_categories(
    db: sqlite3.Connection = Depends(get_db)
):
    """Retorna as categorias de indicadores disponíveis."""
    cursor = db.cursor()
    cursor.execute(
        "SELECT category, COUNT(*) as count FROM indicators GROUP BY category ORDER BY count DESC"
    )
    
    categories = [dict(row) for row in cursor.fetchall()]
    
    return {"categories": categories}

def start_server(port=8000):
    """
    Inicia o servidor FastAPI em uma porta específica.
    """
    print(f"Iniciando servidor na porta {port}...")
    print(f"Acesse a API em: http://127.0.0.1:{port}")
    print(f"Documentação em: http://127.0.0.1:{port}/docs")
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    start_server()