# API do Banco Mundial

Uma API RESTful que fornece acesso a dados econômicos e sociais de países coletados do site do Banco Mundial.

## Descrição

Este projeto realiza web scraping do site oficial do Banco Mundial (https://data.worldbank.org/country) para coletar dados sobre países e seus indicadores econômicos, sociais, ambientais e institucionais. Os dados são processados, armazenados em um banco de dados SQLite e disponibilizados através de uma API RESTful construída com FastAPI.

## Funcionalidades

- Web scraping do site do Banco Mundial
- Processamento e limpeza de dados
- Banco de dados SQLite para armazenamento
- API RESTful com documentação automática
- Indicadores organizados por categorias
- Filtros por país, categoria e ano

## Tecnologias Utilizadas

- **Python 3.9+**
- **FastAPI**: Framework web para construção da API
- **BeautifulSoup4**: Para web scraping
- **SQLite**: Banco de dados leve
- **Pandas**: Processamento de dados
- **Uvicorn**: Servidor ASGI para execução da API
- **Jupyter Notebook**: Para análise e demonstração

## Instalação

1. Clone este repositório:
git clone https://github.com/seu-usuario/worldbank-api.git
cd worldbank-api

2. Instale as dependências:
pip install -r requirements.txt

3. Configure o banco de dados inicial:
python scripts/setup_db.py

Por padrão, serão coletados dados para 10 países. Para personalizar:
python scripts/setup_db.py 20  # Coleta dados para 20 países

## Uso

### Iniciar o Servidor API
python -m src.api

O servidor será iniciado em `http://127.0.0.1:8000`

### Acessar a Documentação

Acesse `http://127.0.0.1:8000/docs` para visualizar a documentação interativa da API (Swagger UI).

### Endpoints Disponíveis

- `GET /countries`: Lista de todos os países
- `GET /countries/{country_code}`: Detalhes de um país específico
- `GET /countries/{country_code}/indicators`: Indicadores para um país
- `GET /countries/{country_code}/profile`: Perfil completo com indicadores por categoria
- `GET /indicators/categories`: Lista de categorias de indicadores disponíveis

## Estrutura do Projeto
worldbank-api/
│
├── src/                  # Código-fonte principal
│   ├── init.py
│   ├── scraper.py        # Código de web scraping
│   ├── database.py       # Funções do banco de dados
│   └── api.py            # Código da API
│
├── scripts/              # Scripts utilitários
│   └── setup_db.py       # Configura o banco de dados inicial
│
├── notebooks/            # Jupyter Notebooks
│   └── demo.ipynb        # Notebook de demonstração
│
├── data/                 # Dados (não incluídos no repositório)
│   ├── raw/              # Dados brutos coletados
│   └── processed/        # Dados processados e banco de dados
│
├── tests/                # Testes unitários
│   └── ...
│
├── requirements.txt      # Dependências do projeto
└── README.md             # Esta documentação

## Metodologia

### Web Scraping

O projeto utiliza BeautifulSoup para extrair dados do site do Banco Mundial. O processo ocorre em duas etapas:
1. Coleta da lista de países disponíveis
2. Coleta de dados detalhados de cada país, incluindo indicadores econômicos e sociais

### Processamento de Dados (ETL)

- **Extract**: Extração dos dados brutos via web scraping
- **Transform**: Limpeza, normalização e estruturação dos dados
- **Load**: Carregamento em um banco de dados SQLite

### Banco de Dados

O banco de dados possui três tabelas principais:
- `countries`: Informações sobre os países
- `indicators`: Metadados dos indicadores
- `indicator_values`: Valores dos indicadores por país e ano

### API

A API é construída com FastAPI, que oferece:
- Documentação automática com Swagger UI
- Validação de parâmetros
- Respostas JSON estruturadas
- Alto desempenho

## Licença

Este projeto está licenciado sob a Licença MI