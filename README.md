# Trabalho 2 — WordPress com Nginx e Docker Compose

## Objetivo

Configurar um ambiente com três instâncias do WordPress, um servidor MySQL e um balanceador de carga Nginx, utilizando Docker Compose.

## Tecnologias utilizadas

- Docker e Docker Compose
- MySQL 5.7
- WordPress 5.4.2 com PHP 7.2 e Apache
- Nginx 1.19.0

## Arquitetura

O Nginx recebe as requisições na porta 8081 da máquina hospedeira e as distribui entre três instâncias WordPress.

As instâncias utilizam um banco de dados MySQL compartilhado e compartilham os arquivos da aplicação.

Os contêineres WordPress e MySQL não possuem portas publicadas diretamente na máquina hospedeira.

## Como executar

Na pasta do projeto, execute:

```bash
docker compose up -d
```

Acesse o WordPress em:

http://localhost:8081

Para verificar os contêineres:

```bash
docker compose ps
```

## Evidências de funcionamento

### 1. Cinco contêineres em execução

![Cinco contêineres em execução](evidencias/01-containers.png)

### 2. WordPress funcionando pelo Nginx

![WordPress acessível pelo Nginx](evidencias/02-wordpress.png)

### 3. Balanceamento de carga

Foram realizadas dez requisições HTTP ao Nginx. Todas retornaram status `200 OK`, com respostas dos três servidores WordPress:

- `172.19.0.3:80`
- `172.19.0.4:80`
- `172.19.0.5:80`

![Teste de balanceamento de carga](evidencias/03-balanceamento.png)

## Conclusão

A atividade demonstrou o funcionamento de três instâncias WordPress utilizando um banco MySQL compartilhado e um Nginx como balanceador de carga.

O teste do cabeçalho `X-Upstream` confirmou que as requisições foram distribuídas entre os três servidores.