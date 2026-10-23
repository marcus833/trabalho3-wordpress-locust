#!/usr/bin/env bash
# Executa a matriz completa de testes de carga do Trabalho 3:
#   5 cenarios de conteudo x 5 quantidades de instancias de WordPress x
#   3 quantidades de usuarios simulados = 75 execucoes do Locust.
#
# Pre-requisitos:
#   - docker compose up -d  (Trabalho 2 no ar)
#   - ./scripts/setup_wordpress_content.sh  (cria os 3 posts e corrige os locustfiles)
#
# Uso: ./scripts/run_load_tests.sh

set -euo pipefail
cd "$(dirname "$0")/.."

# Evita que o Git Bash/MSYS no Windows reescreva caminhos estilo /locust ou
# /resultados para caminhos do Windows antes de chegarem ao Docker.
export MSYS_NO_PATHCONV=1

NETWORK="wordpress_net"
INSTANCIAS=(1 2 3 4 5)
USUARIOS=(100 1000 10000)
CENARIOS=(cenario1_imagem_1mb cenario2_texto_400kb cenario3_imagem_300kb cenario4_home cenario5_busca)

RESULTADOS_DIR="$(pwd)/resultados"
mkdir -p "$RESULTADOS_DIR"

# Nome fixo para o container ad-hoc do Locust usado nos testes. Se o script
# for interrompido a meio caminho (ex: TaskStop/Ctrl+C), o processo do
# docker run pode morrer sem o container do daemon ser avisado, deixando-o
# orfao a martelar o WordPress sozinho. Por isso sempre removemos qualquer
# sobra com esse nome antes de comecar, e tambem ao sair do script.
LOCUST_RUN_NAME="locust-teste-carga"
docker rm -f "$LOCUST_RUN_NAME" >/dev/null 2>&1 || true
trap 'docker rm -f "$LOCUST_RUN_NAME" >/dev/null 2>&1 || true' EXIT INT TERM

# Taxa de spawn (usuarios novos por segundo) escalada para que o ramp-up nao
# consuma todo o tempo do teste nas cargas mais pesadas.
spawn_rate_para() {
  local usuarios=$1
  if [ "$usuarios" -le 100 ]; then
    echo "$usuarios"
  elif [ "$usuarios" -le 1000 ]; then
    echo 100
  else
    echo 500
  fi
}

# Duracao do teste escalada: cargas extremas precisam de mais tempo para
# completar o ramp-up e ainda assim ter um periodo estavel de medicao.
run_time_para() {
  local usuarios=$1
  if [ "$usuarios" -le 100 ]; then
    echo "30s"
  elif [ "$usuarios" -le 1000 ]; then
    echo "45s"
  else
    echo "90s"
  fi
}

# Watchdog: tempo maximo de parede (em segundos) que um unico teste pode
# rodar antes de ser morto a forca. Mesmo com timeout nas requisicoes do
# Locust, isso e uma segunda camada de seguranca contra travamentos que
# ja aconteceram sob carga extrema (ex: 1 teste travado por 27+ minutos).
watchdog_para() {
  local tempo_s="${1%s}"
  echo $((tempo_s + 60))
}

for inst in "${INSTANCIAS[@]}"; do
  echo "============================================================"
  echo "Configurando Nginx para $inst instancia(s) de WordPress..."
  echo "============================================================"
  cp "nginx-configs/nginx-${inst}-instancia$([ "$inst" -gt 1 ] && echo "s").conf" nginx.conf
  docker compose restart nginx
  echo "Aguardando estabilizacao (10s)..."
  sleep 10

  for cenario in "${CENARIOS[@]}"; do
    for usuarios in "${USUARIOS[@]}"; do
      r=$(spawn_rate_para "$usuarios")
      tempo=$(run_time_para "$usuarios")
      watchdog=$(watchdog_para "$tempo")
      prefixo="${cenario}_${inst}inst_${usuarios}users"

      if [ -f "$RESULTADOS_DIR/${prefixo}_stats.csv" ]; then
        echo "----> Ja existe, pulando: $prefixo"
        continue
      fi

      echo ""
      echo "----> Rodando: cenario=$cenario instancias=$inst usuarios=$usuarios (spawn-rate=$r)"

      # O Locust retorna exit code 1 quando ha falhas de requisicao durante o
      # teste (esperado sob carga pesada - e exatamente o que este trabalho
      # quer observar). Isso nao deve interromper a matriz de testes.
      set +e
      docker rm -f "$LOCUST_RUN_NAME" >/dev/null 2>&1 || true
      timeout "$watchdog" docker run --rm \
        --name "$LOCUST_RUN_NAME" \
        --network "$NETWORK" \
        -v "$(pwd)/locust/locustfiles:/locust" \
        -v "$RESULTADOS_DIR:/resultados" \
        -e ATTACKED_HOST="http://nginx" \
        -e LOCUST_FILE="${cenario}.py" \
        -e LOCUST_OPTS="--headless -u $usuarios -r $r --run-time $tempo --csv=/resultados/$prefixo" \
        grubykarol/locust
      if [ $? -eq 124 ]; then
        echo "----> AVISO: $prefixo excedeu o watchdog de ${watchdog}s e foi morto a forca."
        docker rm -f "$LOCUST_RUN_NAME" >/dev/null 2>&1 || true
      fi
      set -e

      echo "----> Concluido: $prefixo"
      sleep 3
    done
  done
done

echo ""
echo "============================================================"
echo "Restaurando configuracao padrao do Nginx (3 instancias)..."
echo "============================================================"
cp "nginx-configs/nginx-3-instancias.conf" nginx.conf
docker compose restart nginx

echo ""
echo "Todos os testes foram executados. Resultados em: $RESULTADOS_DIR"
echo "Gere os graficos com: py scripts/plot_results.py"
