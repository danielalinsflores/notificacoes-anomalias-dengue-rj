import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

QUERY_ANOMALIAS = """
WITH casos_por_semana AS (
    SELECT
        nu_ano,
        sem_not % 100 AS semana_calendario,
        COUNT(*) AS total_casos
    FROM notificacoes_dengue
    GROUP BY nu_ano, sem_not
)
SELECT
    a.nu_ano,
    a.semana_calendario,
    a.total_casos,
    b.media_outros,
    b.desvio_outros,
    (a.total_casos - b.media_outros) / NULLIF(b.desvio_outros, 0) AS z_score
FROM casos_por_semana a
JOIN LATERAL (
    SELECT
        AVG(total_casos) AS media_outros,
        STDDEV(total_casos) AS desvio_outros
    FROM casos_por_semana c
    WHERE c.semana_calendario = a.semana_calendario
      AND c.nu_ano != a.nu_ano
) b ON true
ORDER BY a.nu_ano, a.semana_calendario;
"""


def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def carregar_anomalias() -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(QUERY_ANOMALIAS), conn)
    return df


def main() -> None:
    df = carregar_anomalias()
    df["status"] = df["z_score"].apply(lambda z: "ANOMALIA" if pd.notna(z) and z > 2 else "normal")

    print(f"Total de semanas analisadas: {len(df)}")
    print(f"Total de anomalias detectadas: {(df['status'] == 'ANOMALIA').sum()}")

    saida = Path(__file__).resolve().parents[2] / "data" / "processed" / "anomalias_dengue.csv"
    df.to_csv(saida, index=False)
    print(f"Salvo em {saida}")


if __name__ == "__main__":
    main()