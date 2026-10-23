# Análise dos Resultados — Trabalho 3 (Testes de Carga com Locust)

## 1. Metodologia

Foram executadas **75 combinações de teste**, cruzando:

- **5 cenários de conteúdo**: post com imagem de ~1MB, post com texto de ~400KB,
  post com imagem de ~300KB, página inicial (listagem de posts) e busca no site
  (`/?s=termo`);
- **5 níveis de escalabilidade horizontal**: 1, 2, 3, 4 e 5 instâncias do
  WordPress atrás do Nginx;
- **3 níveis de carga simultânea**: 100, 1.000 e 10.000 usuários simulados
  pelo Locust.

Cada combinação rodou entre 30s (100 usuários) e 90s (10.000 usuários) após o
período de ramp-up, com timeout de 10s por requisição para evitar que o teste
travasse indefinidamente sob saturação extrema do backend.

## 2. Resultados principais

### 2.1 Tempo de resposta e throughput por cenário

| Cenário | 100 usuários (1 inst.) | 10.000 usuários (1 inst.) | 10.000 usuários (3 inst.) |
|---|---|---|---|
| Imagem 1MB | 486 ms / 66,5 req/s | 10.654 ms / 81,9 req/s | 8.886 ms / 82,7 req/s |
| Texto 400KB | 1.361 ms / 30,3 req/s | 10.501 ms / 67,6 req/s | 6.520 ms / 86,2 req/s |
| Imagem 300KB | 1.739 ms / 36,0 req/s | 8.512 ms / 103,3 req/s | 6.981 ms / 94,3 req/s |
| Home (listagem) | 1.967 ms / 25,0 req/s | 8.837 ms / 85,4 req/s | 6.558 ms / 88,8 req/s |
| Busca | 1.303 ms / 30,3 req/s | 7.632 ms / 107,4 req/s | 6.485 ms / 100,5 req/s |

### 2.2 Taxa de falhas (requisições com erro/timeout)

| Cenário | 100 usuários | 1.000 usuários | 10.000 usuários |
|---|---|---|---|
| Imagem 1MB | 0% | 0,3% – 9,0% | 4,6% – 19,2% |
| Texto 400KB | 0% | 51,8% – 81,1% | 55,7% – 70,4% |
| Imagem 300KB | 0% | 1,1% – 14,8% | 2,2% – 8,8% |
| Home (listagem) | 0% | 57,6% – 73,3% | 56,9% – 76,5% |
| Busca | 0% | 65,9% – 71,7% | 65,4% – 70,8% |

## 3. Discussão

### 3.1 Conteúdo estático vs. dinâmico: o fator que mais pesou

O achado mais claro do estudo não foi o número de instâncias, e sim **o tipo
de conteúdo**. Os cenários que servem majoritariamente arquivos estáticos
(imagens enviadas como mídia) toleraram carga muito melhor — taxa de falha
abaixo de 20% mesmo em 10.000 usuários — enquanto os cenários cuja resposta
depende inteiramente de consultas dinâmicas ao MySQL (texto renderizado,
home com listagem de posts, busca) já colapsavam com **mais de 50% de falha
a partir de apenas 1.000 usuários simultâneos**, independente de quantas
instâncias de WordPress estavam no ar.

Isso é esperado: uma imagem servida pelo Apache é basicamente I/O de disco,
enquanto toda página dinâmica do WordPress paga o custo de abrir conexão
MySQL, montar a query, hidratar o template PHP e renderizar HTML a cada
requisição — não há cache de página ativado nesta configuração.

### 3.2 O MySQL como gargalo compartilhado

Escalar o número de instâncias do WordPress (1 → 5) reduziu o tempo de
resposta de forma consistente apenas até certo ponto, e em vários casos
**não reduziu a taxa de falha** — chegando a piorar (ex.: cenário "home" com
1.000 usuários: 57,6% de falha com 1 instância, 73,3% com 2 instâncias).

A explicação arquitetural é direta: todas as instâncias de WordPress, não
importa quantas, compartilham o **mesmo único container MySQL**. Adicionar
mais frontends PHP aumenta a capacidade de processar requisições HTTP, mas
também aumenta a quantidade de conexões concorrentes disputando o mesmo
banco de dados — que não foi escalado junto. Nesta arquitetura, o MySQL é o
verdadeiro limite de capacidade do sistema para qualquer página dinâmica;
escalar só a camada web (como pede o Trabalho 2) tem retorno decrescente, e
eventualmente nulo, sem também escalar ou otimizar a camada de dados
(réplicas de leitura, cache de objeto/página, connection pooling, etc.).

### 3.3 Efeito da carga de usuários simultâneos

Em todos os cenários, o salto de 100 → 1.000 usuários já foi suficiente para
sair de 0% de falhas para dezenas de pontos percentuais nos cenários
dinâmicos. O salto de 1.000 → 10.000 teve efeito proporcionalmente menor na
taxa de falha — sinal de que o sistema já estava saturado em 1.000 usuários
para conteúdo dinâmico, e 10.000 apenas mantém (ou pouco agrava) esse
patamar de colapso, em vez de piorar na mesma proporção do aumento de carga.

### 3.4 Saturação do próprio gerador de carga

Em 10.000 usuários, o throughput (requisições por segundo) ficou
consistentemente limitado à faixa de ~60–115 req/s **independentemente do
número de instâncias de WordPress**. Esse teto não varia com a escala do
backend, o que indica que o gargalo nesse patamar deixou de ser o WordPress
e passou a ser o próprio processo do Locust — rodando como um único
container/processo Python, limitado pela forma como o `gevent` agenda
milhares de conexões simultâneas em um único núcleo. Isso reforça por que
não foi viável testar com 100.000 ou 1.000.000 de usuários simulados neste
ambiente: a partir de um certo ponto, a métrica deixaria de refletir o
desempenho do WordPress e passaria a refletir apenas a capacidade do próprio
gerador de carga. Um teste nessa escala exigiria distribuir o Locust em
múltiplos workers/máquinas (modo `--master`/`--worker`), fora do escopo de
uma única máquina local.

### 3.5 Limitações do estudo

- Cada combinação rodou uma única vez (não há repetição/média), então os
  números têm variância não quantificada — flutuações pontuais de alguns
  segundos no ambiente local (ex.: picos de I/O do Docker Desktop) podem
  aparecer como ruído nos dados.
- O ambiente roda inteiramente em uma única máquina física: Nginx, 5
  WordPress, MySQL e o próprio Locust competem pelos mesmos núcleos de CPU e
  pela mesma memória, então os números de tempo de resposta não são
  diretamente comparáveis aos de uma infraestrutura com máquinas dedicadas
  por serviço.
- O WordPress estava sem nenhum cache de página/objeto ativado (plugin de
  cache, Redis, etc.), o que é o pior caso realista para uma aplicação
  WordPress em produção — a maioria dos sites reais mitigaria boa parte da
  degradação observada nos cenários dinâmicos com cache.

## 4. Conclusão

O balanceamento de carga via Nginx cumpre bem o seu papel quando o gargalo
está na camada de aplicação (CPU/memória dos processos PHP), como ficou claro
nos cenários de imagem estática. Porém, para cenários dependentes de banco de
dados — a maioria do tráfego real de um WordPress — escalar apenas o número
de instâncias de aplicação tem efeito limitado, porque o MySQL único continua
sendo o ponto único de contenção. Isso aponta como próximo passo natural de
evolução da arquitetura (fora do escopo deste trabalho): cache de página,
réplicas de leitura do banco, ou um serviço de cache de objetos como Redis
compartilhado entre as instâncias.
