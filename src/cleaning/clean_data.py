import zipfile
from pathlib import Path
import pandas as pd

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

ANOS = ["22", "23", "24"]

# Colunas que realmente importam para o nosso objetivo:
# detectar anomalias de volume de casos por semana/município
COLUNAS_UTEIS = [
    "DT_NOTIFIC",
    "SEM_NOT",
    "NU_ANO",
    "SG_UF_NOT",
    "ID_MUNICIP",
    "MUNICIPIO",
    "CS_SEXO",
    "NU_IDADE_N",
    "CLASSI_FIN",
    "EVOLUCAO",
]

UF_ALVO = 33  # código do IBGE para o Rio de Janeiro


def carregar_ano(ano: str) -> pd.DataFrame:
    """Lê o CSV de um ano em blocos (chunks), filtrando o RJ a cada bloco
    para não precisar manter o Brasil inteiro na memória de uma vez."""
    caminho_csv = RAW_DATA_DIR / f"DENGBR{ano}.csv"

    blocos_rj = []
    leitor = pd.read_csv(
        caminho_csv,
        sep=",",
        encoding="latin1",
        usecols=COLUNAS_UTEIS,
        chunksize=50_000,  # lê 50 mil linhas por vez
        on_bad_lines="warn",  # avisa (sem quebrar) se achar linha malformada
    )

    for bloco in leitor:
        bloco_rj = bloco[bloco["SG_UF_NOT"] == UF_ALVO]
        blocos_rj.append(bloco_rj)

    return pd.concat(blocos_rj, ignore_index=True)

def filtrar_rj(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas os casos notificados no estado do RJ."""
    return df[df["SG_UF_NOT"] == UF_ALVO].copy()

def decodificar_idade(valor):
    """O SINAN codifica idade com um dígito de unidade + a quantidade:
    1xxx = horas, 2xxx = dias, 3xxx = meses, 4xxx = anos.
    Ex: 4043 = 43 anos. Convertemos tudo para 'idade em anos', arredondado."""
    if pd.isna(valor):
        return None
    valor = int(valor)
    unidade = valor // 1000
    quantidade = valor % 1000

    if unidade == 4:
        return round(quantidade, 1)
    elif unidade == 3:
        return round(quantidade / 12, 1)
    elif unidade == 2:
        return round(quantidade / 365, 1)
    elif unidade == 1:
        return round(quantidade / 8760, 1)
    else:
        return None  # código de unidade desconhecido/inválido


def tratar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas para os tipos corretos e trata valores ausentes."""
    df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors="coerce")

    # Linhas sem data de notificação não servem para análise temporal — descartamos
    antes = len(df)
    df = df.dropna(subset=["DT_NOTIFIC"])
    depois = len(df)
    if antes != depois:
        print(f"  Descartadas {antes - depois} linhas sem data de notificação válida.")

    df["NU_IDADE_N"] = df["NU_IDADE_N"].apply(decodificar_idade)

    return df


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    partes = []

    for ano in ANOS:
        print(f"Processando ano 20{ano}...")
        df = carregar_ano(ano)
        print(f"  Total bruto (já filtrado para RJ): {len(df)} linhas")

        df = tratar_tipos(df)
        print(f"  Após tratamento de tipos: {len(df)} linhas")

        partes.append(df)

    df_final = pd.concat(partes, ignore_index=True)
    print(f"\nTotal consolidado (2022-2024, RJ): {len(df_final)} linhas")

    destino = PROCESSED_DATA_DIR / "dengue_rj_consolidado.csv"
    df_final.to_csv(destino, index=False)
    print(f"Salvo em {destino}")


if __name__ == "__main__":
    main()