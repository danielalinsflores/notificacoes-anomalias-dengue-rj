# Detecção de Anomalias em Notificações de Dengue — RJ

Pipeline de dados que consolida notificações de dengue do estado do Rio de 
Janeiro (SINAN/DataSUS, 2022-2024) para identificar picos anômalos de casos, 
usando SQL, Python e PostgreSQL.

## Status
Em desenvolvimento

## Stack
- Python (pandas, SQLAlchemy)
- PostgreSQL
- Power BI (em breve)

## Como rodar
1. Clone o repositório
2. Crie um ambiente virtual e instale `requirements.txt`
3. Configure o `.env` com suas credenciais de banco (veja `.env.example`)
4. Rode os scripts em `src/ingestion`, depois `src/cleaning`