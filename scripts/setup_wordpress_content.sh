#!/usr/bin/env bash
# Cria no WordPress os 3 posts usados nos cenarios de teste do Trabalho 3,
# usando o wp-cli oficial (imagem wordpress:cli) contra o mesmo volume e
# banco de dados dos containers do Trabalho 2.
#
# Pre-requisito: containers do Trabalho 2 (mysql, wordpress1/2/3, nginx) de pe
# (docker compose up -d), com o WordPress ja instalado (wp-config.php existente).
#
# Uso: ./scripts/setup_wordpress_content.sh

set -euo pipefail
cd "$(dirname "$0")/.."

# Evita que o Git Bash/MSYS no Windows reescreva caminhos estilo /var/www/html
# para caminhos do Windows antes de chegarem ao Docker.
export MSYS_NO_PATHCONV=1

NETWORK="wordpress_net"
DB_HOST="mysql:3306"
DB_USER="wpuser"
DB_PASSWORD="wp123"
DB_NAME="wordpress"

wp() {
  docker run --rm \
    --network "$NETWORK" \
    -v "$(pwd)/wordpress-data:/var/www/html" \
    -e WORDPRESS_DB_HOST="$DB_HOST" \
    -e WORDPRESS_DB_USER="$DB_USER" \
    -e WORDPRESS_DB_PASSWORD="$DB_PASSWORD" \
    -e WORDPRESS_DB_NAME="$DB_NAME" \
    wordpress:cli wp --allow-root "$@"
}

echo "==> Criando post do cenario 1 (imagem ~1MB)..."
POST1_ID=$(wp post create \
  --post_title="Cenario 1 - Post com imagem de 1MB" \
  --post_status=publish \
  --post_content="<p>Post de teste de carga - cenario 1.</p>" \
  --porcelain)
echo "Post 1 criado: ID=$POST1_ID"

echo "==> Importando imagem de 1MB e anexando ao post 1..."
cp "locust/assets/imagem_1mb.jpg" "wordpress-data/imagem_1mb.jpg"
ATTACH1_ID=$(wp media import "/var/www/html/imagem_1mb.jpg" --post_id="$POST1_ID" --porcelain)
IMG1_URL=$(wp post get "$ATTACH1_ID" --field=guid)
wp post update "$POST1_ID" --post_content="<p>Post de teste de carga - cenario 1.</p><img src=\"$IMG1_URL\" />"

echo "==> Criando post do cenario 2 (texto ~400KB)..."
# O conteudo e grande demais para passar como argumento de linha de comando,
# entao copiamos o arquivo para dentro do volume e usamos "wp eval" para que
# o proprio PHP leia o arquivo e grave o post_content diretamente no banco.
cp "locust/assets/texto_400kb.html" "wordpress-data/texto_400kb.html"
POST2_ID=$(wp post create \
  --post_title="Cenario 2 - Post com texto de 400KB" \
  --post_status=publish \
  --post_content="(conteudo sera preenchido a seguir)" \
  --porcelain)
wp eval "wp_update_post(['ID' => $POST2_ID, 'post_content' => file_get_contents(ABSPATH . 'texto_400kb.html')]);"
echo "Post 2 criado: ID=$POST2_ID"

echo "==> Criando post do cenario 3 (imagem ~300KB)..."
POST3_ID=$(wp post create \
  --post_title="Cenario 3 - Post com imagem de 300KB" \
  --post_status=publish \
  --post_content="<p>Post de teste de carga - cenario 3.</p>" \
  --porcelain)
cp "locust/assets/imagem_300kb.jpg" "wordpress-data/imagem_300kb.jpg"
ATTACH3_ID=$(wp media import "/var/www/html/imagem_300kb.jpg" --post_id="$POST3_ID" --porcelain)
IMG3_URL=$(wp post get "$ATTACH3_ID" --field=guid)
wp post update "$POST3_ID" --post_content="<p>Post de teste de carga - cenario 3.</p><img src=\"$IMG3_URL\" />"
echo "Post 3 criado: ID=$POST3_ID"

echo "==> Atualizando os locustfiles com os caminhos reais dos posts..."
sed -i "s#__POST_PATH_CENARIO1__#/?p=$POST1_ID#" locust/locustfiles/cenario1_imagem_1mb.py
sed -i "s#__POST_PATH_CENARIO2__#/?p=$POST2_ID#" locust/locustfiles/cenario2_texto_400kb.py
sed -i "s#__POST_PATH_CENARIO3__#/?p=$POST3_ID#" locust/locustfiles/cenario3_imagem_300kb.py

rm -f wordpress-data/imagem_1mb.jpg wordpress-data/imagem_300kb.jpg wordpress-data/texto_400kb.html

echo ""
echo "Conteudo criado com sucesso:"
echo "  Cenario 1 (imagem 1MB):   /?p=$POST1_ID"
echo "  Cenario 2 (texto 400KB):  /?p=$POST2_ID"
echo "  Cenario 3 (imagem 300KB): /?p=$POST3_ID"
