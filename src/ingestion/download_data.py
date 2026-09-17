import requests
from pathlib import Path

# Anos que vamos analisar
ANOS = ["22", "23", "24"] #2022, 2023, 2024
BASE_URL = "HTTPS://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/csv/DENGBR{ano}.csv.zip"

# Pasta de destino dos dados brutos
RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

def baixar_arquivo(url : str, destino: Path) -> None:
    """Baixa um arquivo de uma URL e salva no destino especificado."""
    print(f"Baixando {url} ...")
    resposta = requests.get(url, stream=True, timeout=60)
    resposta.raise_for_status()  # Levanta um erro se a requisição falhar

    with open(destino, 'wb') as arquivo:
        for bloco in resposta.iter_content(chunk_size=8192):
            arquivo.write(bloco)

    print(f"Download completo: {destino}")

def main() -> None:
    """Função principal para baixar os arquivos de dados brutos."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)  # Cria o diretório se não existir

    for ano in ANOS:
        url = BASE_URL.format(ano=ano)
        nome_arquivo =  f"DENGBR{ano}.csv.zip"
        destino = RAW_DATA_DIR / nome_arquivo
        baixar_arquivo(url, destino)

        if destino.exists():
            print(f"Arquivo {nome_arquivo} baixado com sucesso.")
            continue

        baixar_arquivo(url, destino)

if __name__ == "__main__":
    main()