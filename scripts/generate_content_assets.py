"""Gera os arquivos de conteudo usados nos 3 cenarios de teste do Trabalho 3:
- imagem_1mb.jpg   (~1 MB)
- imagem_300kb.jpg (~300 KB)
- texto_400kb.html (~400 KB de texto em HTML)

Uso: py scripts/generate_content_assets.py
Saida: locust/assets/
"""
import os
import random

from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "locust", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def gerar_imagem_com_tamanho_alvo(caminho, tamanho_alvo_bytes, tolerancia=0.05):
    """Gera uma imagem JPEG de ruido colorido e ajusta a qualidade ate
    chegar perto do tamanho alvo em bytes."""
    largura, altura = 1600, 1200
    imagem = Image.new("RGB", (largura, altura))
    pixels = imagem.load()
    for y in range(altura):
        for x in range(largura):
            pixels[x, y] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

    baixo, alto = 1, 95
    melhor_qualidade = 85
    while baixo <= alto:
        meio = (baixo + alto) // 2
        imagem.save(caminho, "JPEG", quality=meio)
        tamanho_atual = os.path.getsize(caminho)
        diferenca = abs(tamanho_atual - tamanho_alvo_bytes) / tamanho_alvo_bytes
        if diferenca <= tolerancia:
            melhor_qualidade = meio
            break
        if tamanho_atual < tamanho_alvo_bytes:
            baixo = meio + 1
        else:
            alto = meio - 1
        melhor_qualidade = meio

    imagem.save(caminho, "JPEG", quality=melhor_qualidade)
    print(f"{caminho}: {os.path.getsize(caminho) / 1024:.1f} KB (qualidade={melhor_qualidade})")


def gerar_texto_com_tamanho_alvo(caminho, tamanho_alvo_bytes):
    """Gera um bloco de texto HTML (paragrafos) com ~tamanho_alvo_bytes."""
    paragrafo = (
        "<p>Este e um paragrafo de conteudo gerado automaticamente para o "
        "cenario de teste de carga com texto longo. O objetivo deste texto e "
        "simular um post de blog com um volume de conteudo textual proximo de "
        "400 KB, de modo a avaliar o desempenho do WordPress ao servir paginas "
        "com muito HTML renderizado a partir do banco de dados MySQL.</p>\n"
    )
    repeticoes = tamanho_alvo_bytes // len(paragrafo.encode("utf-8")) + 1
    conteudo = paragrafo * repeticoes
    conteudo_bytes = conteudo.encode("utf-8")[:tamanho_alvo_bytes]
    with open(caminho, "wb") as arquivo:
        arquivo.write(conteudo_bytes)
    print(f"{caminho}: {os.path.getsize(caminho) / 1024:.1f} KB")


if __name__ == "__main__":
    gerar_imagem_com_tamanho_alvo(os.path.join(ASSETS_DIR, "imagem_1mb.jpg"), 1_000_000)
    gerar_imagem_com_tamanho_alvo(os.path.join(ASSETS_DIR, "imagem_300kb.jpg"), 300_000)
    gerar_texto_com_tamanho_alvo(os.path.join(ASSETS_DIR, "texto_400kb.html"), 400_000)
