import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

PROCESSED_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
CSV_PATH = PROCESSED_DATA_DIR / "dengue_rj_consolidado.csv"

# Mapeamento: nome da coluna no CSV -> nome da coluna na tabela do banco
COLUNAS_RENOMEADAS = {
    "DT_NOTIFIC": "dt_notific",
    "SEM_NOT": "sem_not",
    "NU_ANO": "nu_ano",
    "ID_MUNICIP": "id_municipio",
    "MUNICIPIO": "municipio",
    "CS_SEXO": "cs_sexo",
    "NU_IDADE_N": "nu_idade",
    "CLASSI_FIN": "classi_fin",
    "EVOLUCAO": "evolucao",
}


def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def main() -> None:
    print("Lendo CSV consolidado...")
    df = pd.read_csv(CSV_PATH, parse_dates=["DT_NOTIFIC"])

    # SG_UF_NOT não existe na tabela (já usamos só para filtrar RJ, não precisamos mais dela)
    df = df.rename(columns=COLUNAS_RENOMEADAS)
    colunas_tabela = list(COLUNAS_RENOMEADAS.values())
    df = df[colunas_tabela]

    print(f"Carregando {len(df)} linhas no PostgreSQL...")
    engine = get_engine()

    df.to_sql(
        "notificacoes_dengue",
        engine,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )
    print("Carga concluída.")


if __name__ == "__main__":
    main()