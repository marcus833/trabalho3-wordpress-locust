"""Le os CSVs gerados pelo Locust (resultados/*_stats.csv) e monta os
graficos de barras agrupadas pedidos no Trabalho 3:
  1) Tempo de resposta (eixo Y) x Numero de usuarios (eixo X), agrupado por
     numero de instancias de WordPress.
  2) Requisicoes por segundo (eixo Y) x Numero de instancias (eixo X),
     agrupado por numero de usuarios.

Um par de graficos e gerado para cada cenario de conteudo.

Uso: py scripts/plot_results.py
Saida: resultados/graficos/*.png
"""
import glob
import os
import re

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados")
GRAFICOS_DIR = os.path.join(RESULTADOS_DIR, "graficos")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

PADRAO_NOME = re.compile(r"^(cenario\d_\w+?)_(\d+)inst_(\d+)users_stats\.csv$")

CORES = ["#8ecae6", "#ffd166", "#ef476f", "#06d6a0", "#073b4c", "#9d4edd", "#f3722c"]


def carregar_resultados():
    linhas = []
    for caminho in glob.glob(os.path.join(RESULTADOS_DIR, "*_stats.csv")):
        nome_arquivo = os.path.basename(caminho)
        match = PADRAO_NOME.match(nome_arquivo)
        if not match:
            continue
        cenario, instancias, usuarios = match.groups()

        df = pd.read_csv(caminho)
        agregada = df[df["Name"] == "Aggregated"]
        if agregada.empty:
            continue
        agregada = agregada.iloc[0]

        linhas.append({
            "cenario": cenario,
            "instancias": int(instancias),
            "usuarios": int(usuarios),
            "tempo_resposta_ms": agregada["Average Response Time"],
            "requisicoes_por_segundo": agregada["Requests/s"],
        })

    if not linhas:
        raise SystemExit(
            "Nenhum resultado encontrado em 'resultados/'. "
            "Rode primeiro scripts/run_load_tests.sh."
        )

    return pd.DataFrame(linhas)


def grafico_tempo_resposta_por_usuarios(df, cenario):
    dados = df[df["cenario"] == cenario]
    usuarios_unicos = sorted(dados["usuarios"].unique())
    instancias_unicas = sorted(dados["instancias"].unique())

    largura_barra = 0.8 / len(instancias_unicas)
    fig, ax = plt.subplots(figsize=(8, 5))

    for i, inst in enumerate(instancias_unicas):
        valores = [
            dados[(dados["usuarios"] == u) & (dados["instancias"] == inst)]
            ["tempo_resposta_ms"].mean()
            for u in usuarios_unicos
        ]
        posicoes = [x + i * largura_barra for x in range(len(usuarios_unicos))]
        ax.bar(posicoes, valores, width=largura_barra,
               label=f"{inst} instancia(s)", color=CORES[i % len(CORES)])

    ax.set_xticks([x + largura_barra * (len(instancias_unicas) - 1) / 2
                   for x in range(len(usuarios_unicos))])
    ax.set_xticklabels([str(u) for u in usuarios_unicos])
    ax.set_xlabel("Numero de usuarios")
    ax.set_ylabel("Tempo de resposta (ms)")
    ax.set_title(f"Tempo de resposta - {cenario}")
    ax.legend()
    fig.tight_layout()
    saida = os.path.join(GRAFICOS_DIR, f"{cenario}_tempo_resposta.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Gerado: {saida}")


def grafico_rps_por_instancias(df, cenario):
    dados = df[df["cenario"] == cenario]
    instancias_unicas = sorted(dados["instancias"].unique())
    usuarios_unicos = sorted(dados["usuarios"].unique())

    largura_barra = 0.8 / len(usuarios_unicos)
    fig, ax = plt.subplots(figsize=(8, 5))

    for i, usuarios in enumerate(usuarios_unicos):
        valores = [
            dados[(dados["instancias"] == inst) & (dados["usuarios"] == usuarios)]
            ["requisicoes_por_segundo"].mean()
            for inst in instancias_unicas
        ]
        posicoes = [x + i * largura_barra for x in range(len(instancias_unicas))]
        ax.bar(posicoes, valores, width=largura_barra,
               label=f"{usuarios} usuarios", color=CORES[i % len(CORES)])

    ax.set_xticks([x + largura_barra * (len(usuarios_unicos) - 1) / 2
                   for x in range(len(instancias_unicas))])
    ax.set_xticklabels([str(i) for i in instancias_unicas])
    ax.set_xlabel("Numero de instancias")
    ax.set_ylabel("Requisicoes por segundo")
    ax.set_title(f"Requisicoes por segundo - {cenario}")
    ax.legend()
    fig.tight_layout()
    saida = os.path.join(GRAFICOS_DIR, f"{cenario}_requisicoes_por_segundo.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Gerado: {saida}")


if __name__ == "__main__":
    df = carregar_resultados()
    df.to_csv(os.path.join(RESULTADOS_DIR, "resumo_consolidado.csv"), index=False)
    print(f"Resumo consolidado salvo em resultados/resumo_consolidado.csv")

    for cenario in sorted(df["cenario"].unique()):
        grafico_tempo_resposta_por_usuarios(df, cenario)
        grafico_rps_por_instancias(df, cenario)
