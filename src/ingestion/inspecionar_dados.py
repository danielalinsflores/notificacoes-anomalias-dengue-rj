import zipfile
from pathlib import Path
import pandas as pd

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
ANOS = ["22", "23", "24"]


def extrair_zip(caminho_zip: Path) -> Path:
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        nomes = zip_ref.namelist()
        zip_ref.extractall(RAW_DATA_DIR)
        # Renomeia o csv extraído para bater com o ano esperado,
        # evitando que uma extração sobrescreva a outra
        nome_original = RAW_DATA_DIR / nomes[0]
        return nome_original


def inspecionar_csv(caminho_csv: Path, ano_esperado: str) -> None:
    df = pd.read_csv(caminho_csv, sep=",", encoding="latin1", nrows=1000, low_memory=False)

    ano_real = df["NU_ANO"].unique() if "NU_ANO" in df.columns else "coluna NU_ANO não encontrada"

    print(f"\n--- Ano esperado: 20{ano_esperado} ---")
    print(f"Formato da amostra: {df.shape}")
    print(f"Ano(s) real(is) encontrado(s) na coluna NU_ANO: {ano_real}")
    print(f"Nº de colunas: {len(df.columns)}")


def main() -> None:
    for ano in ANOS:
        zip_path = RAW_DATA_DIR / f"DENGBR{ano}.csv.zip"
        csv_path = extrair_zip(zip_path)
        inspecionar_csv(csv_path, ano)


if __name__ == "__main__":
    main()