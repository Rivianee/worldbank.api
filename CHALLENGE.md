Desafio API do Banco Mundial
Visão Geral da Solução
Desenvolvi uma solução completa que:

Realiza web scraping do site do Banco Mundial (https://data.worldbank.org/country)
Processa e estrutura os dados coletados
Armazena os dados em um banco de dados SQLite
Disponibiliza os dados através de uma API RESTful construída com FastAPI

Método de Web Scraping
Abordagem Técnica
Utilizei BeautifulSoup4 para extrair dados do site do Banco Mundial, com uma estratégia em duas etapas:

Extração da lista de países:

Fiz scraping da página principal de países
Extraí URLs, nomes e códigos de cada país
Removi duplicatas para garantir dados limpos


Extração de dados detalhados por país:

Para cada país, acessei sua página específica
Extraí informações básicas (região, nível de renda)
Identifiquei e categorizei indicadores em quatro grupos: social, econômico, ambiental e institucional
Extraí valores e anos para cada indicador encontrado


Tratamento de desafios:

Implementei delays entre requisições para evitar sobrecarga no servidor
Utilizei expressões regulares para extrair anos e limpar valores numéricos
Desenvolvi lógica robusta para lidar com inconsistências na estrutura HTML do site



Limitações e Soluções

Estrutura HTML variável: O site tem diferentes layouts para diferentes países. Desenvolvi uma solução flexível que procura indicadores em várias estruturas possíveis.
Mudanças no site: Para garantir robustez, o código verifica diferentes padrões de elementos HTML que podem conter indicadores.

Armazenamento de Dados e Processo ETL
Estratégia de Armazenamento
Escolhi SQLite como banco de dados pelo seu equilíbrio entre simplicidade, desempenho e portabilidade:

Não requer configuração de servidor
O banco de dados é armazenado como um único arquivo
Suporta consultas SQL complexas para análise de dados

Processo ETL (Extract, Transform, Load)

Extract:

Dados brutos extraídos como JSON são armazenados em data/raw/
Cada país tem seu próprio arquivo para facilitar inspeção e depuração


Transform:

Normalização de dados em estrutura relacional
Conversão de valores textuais para numéricos
Limpeza para remover caracteres não numéricos dos valores
Criação de códigos ISO2 e ISO3 para melhor compatibilidade
Categorização de indicadores em grupos lógicos


Load:

Criação de esquema relacional com três tabelas principais
Índices para otimização de consultas
Constraints de integridade referencial para garantir consistência



Modelo de Dados
O banco de dados segue um modelo relacional com três tabelas principais:

countries: Armazena metadados dos países
indicators: Armazena informações sobre os indicadores disponíveis
indicator_values: Mantém os valores dos indicadores por país e ano em um modelo de séries temporais

Dados Escolhidos para a API
Selecionei indicadores em quatro categorias principais:

Sociais:

População total e crescimento populacional
Expectativa de vida
Índice de pobreza
Índice de Capital Humano
Migração líquida


Econômicos:

PIB (total e per capita)
Crescimento do PIB
Taxa de desemprego
Inflação
Remessas pessoais


Ambientais:

Emissões de CO2
Áreas florestais
Acesso à eletricidade
Consumo de água
Produção de energia renovável


Institucionais:

Taxa de homicídios
Dívida governamental
Acesso à internet
Representação feminina no parlamento
Investimento estrangeiro direto



Esta seleção abrangente permite uma visão holística de cada país, cobrindo aspectos sociais, econômicos, ambientais e de governança.
Qualidade e Desempenho do Código
Organização e Legibilidade
Estruturei o código em módulos com responsabilidades bem definidas:

scraper.py: Responsável pelo web scraping
database.py: Gerencia operações do banco de dados e processamento de dados
api.py: Implementa a API FastAPI
setup_db.py: Script de configuração inicial

Otimizações de Desempenho

Indexação de banco de dados:

Índices nas colunas mais consultadas
Índices compostos para consultas frequentes


Consultas SQL otimizadas:

Uso de Common Table Expressions (CTE) para consultas de ranking
Joins eficientes entre tabelas


Lazy loading na API:

Implementação de paginação para evitar carregamento de grandes conjuntos de dados
Dependência de conexão com banco de dados encapsulada para garantir fechamento adequado


Cache de resultados:

Valores previamente calculados são armazenados para melhorar a latência da API



Desafios Enfrentados

Estrutura HTML inconsistente:
O site do Banco Mundial tem layouts diferentes para diferentes países, exigindo uma abordagem de scraping flexível e robusta.
Extração de valores e unidades:
Os valores dos indicadores muitas vezes incluem unidades e são formatados de maneiras diferentes (ex: "45.3%", "45.3 (2019)"), exigindo estratégias avançadas de extração e limpeza.
Padronização de códigos de país:
Conciliar diferentes padrões de códigos (ISO2, ISO3, nomes completos) para garantir consistência na API.
Integração entre módulos:
Garantir que os dados fluam corretamente do scraper para o banco de dados e depois para a API, mantendo a integridade dos dados em cada passo.

Melhorias Futuras

Expansão da cobertura de dados:

Coletar mais indicadores e séries temporais mais longas
Adicionar comparações regionais e médias globais


Funcionalidades adicionais da API:

Endpoints para análise comparativa entre países
Suporte para visualizações de dados integradas (gráficos, mapas)
Exportação de dados em diversos formatos (CSV, Excel)


Automação e agendamento:

Implementar atualização periódica dos dados
Sistema de cache para melhorar desempenho


Melhorias de segurança e desempenho:

Implementar autenticação e autorização
Otimizações adicionais de consultas e armazenamento



Conclusão
Este projeto demonstra uma implementação completa de scraping, processamento e disponibilização de dados através de uma API moderna e bem documentada. A abordagem utilizada garante dados de qualidade, desempenho adequado e facilidade de uso para consumidores da API.
A solução pode ser facilmente expandida para incluir mais fontes de dados, mais indicadores ou funcionalidades adicionais, graças à arquitetura modular e bem estruturada do código.