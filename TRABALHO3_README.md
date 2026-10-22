# Trabalho 3 — Testes de carga com Locust

Pré-requisito obrigatório: Docker Desktop funcionando (ver bloqueio do WSL2 abaixo).

## Passo a passo

```bash
# 1. Subir o ambiente do Trabalho 2 (mysql, wordpress1/2/3, nginx, locust)
docker compose up -d

# 2. Criar os 3 posts de teste no WordPress (imagem 1MB, texto 400KB, imagem 300KB)
./scripts/setup_wordpress_content.sh

# 3. Rodar a matriz completa de testes (3 cenários x 3 qtd. de instâncias x 3 qtd. de usuários)
#    Demora ~15-20 minutos (27 execuções de 30s cada + trocas de config do nginx).
./scripts/run_load_tests.sh

# 4. Gerar os gráficos exigidos no enunciado
py scripts/plot_results.py
```

Os gráficos finais ficam em `resultados/graficos/*.png` e o resumo numérico em
`resultados/resumo_consolidado.csv`.

## Bloqueio atual: WSL2 não instalado

O Docker Desktop está instalado, mas falha ao conectar porque o Windows
Subsystem for Linux (WSL2), que é o motor padrão usado pelo Docker Desktop no
Windows, não está habilitado nesta máquina. Para corrigir (precisa de
PowerShell **como administrador**):

```powershell
wsl --install
```

Isso instala o WSL2 e a distro padrão. Depois é necessário **reiniciar o
Windows**. Após reiniciar, abra o Docker Desktop manualmente e aguarde o
ícone da baleia ficar parado (engine pronto), então repita o passo 1 acima.

## Regenerar os arquivos de conteúdo (opcional)

Os arquivos em `locust/assets/` (imagem 1MB, imagem 300KB, texto 400KB) já
foram gerados. Para recriá-los:

```bash
py scripts/generate_content_assets.py
```
