from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "anomalias_dengue.csv"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "dashboards"


def carregar_dados() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def plotar_serie_temporal(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))

    for ano, grupo in df.groupby("nu_ano"):
        grupo = grupo.sort_values("semana_calendario")
        ax.plot(
            grupo["semana_calendario"],
            grupo["total_casos"],
            label=str(ano),
            marker="o",
            markersize=3,
        )

    # Destaca os pontos marcados como anomalia
    anomalias = df[df["status"] == "ANOMALIA"]
    ax.scatter(
        anomalias["semana_calendario"],
        anomalias["total_casos"],
        color="red",
        s=60,
        zorder=5,
        label="Anomalia (Z-score > 2)",
    )

    ax.set_xlabel("Semana epidemiológica")
    ax.set_ylabel("Casos de dengue notificados")
    ax.set_title("Notificações de dengue por semana epidemiológica — RJ (2022-2024)")
    ax.legend(title="Ano")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    destino = OUTPUT_DIR / "serie_temporal_anomalias.png"
    fig.savefig(destino, dpi=150)
    print(f"Gráfico salvo em {destino}")


def main() -> None:
    df = carregar_dados()
    plotar_serie_temporal(df)


if __name__ == "__main__":
    main()