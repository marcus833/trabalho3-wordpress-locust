# Análise dos Resultados — Trabalho 3

## Como testei

Rodei 75 combinações de teste no total. Variei três coisas ao mesmo tempo:

- **o tipo de conteúdo da página** (um post com imagem grande de 1MB, um post
  com bastante texto — uns 400KB de HTML —, um post com imagem menor de
  300KB, a página inicial do blog listando vários posts, e uma busca no
  site);
- **quantas instâncias de WordPress** estavam atrás do Nginx (de 1 até 5);
- **quantos usuários simultâneos** o Locust simulava (100, 1.000 e 10.000).

Cada teste rodou entre 30 segundos (nos casos mais leves) e 90 segundos (nos
mais pesados), com um timeout de 10 segundos por requisição — sem isso, o
próprio teste ficava travado quando o servidor parava de responder, o que
aconteceu mais de uma vez enquanto eu rodava tudo isso.

## O que os números mostraram

A primeira coisa que me chamou atenção foi que **o tipo de conteúdo importou
muito mais do que eu esperava**. Os posts com imagem se saíram bem: mesmo com
10.000 usuários batendo ao mesmo tempo, a taxa de erro ficou entre 2% e 20%,
dependendo do número de instâncias. Já as páginas que dependem de consulta ao
banco — o post de texto, a home e a busca — simplesmente desabavam. Com
apenas 1.000 usuários simultâneos, mais da metade das requisições já estava
falhando (entre 52% e 81%, variando conforme o cenário). E subir pra 10.000
usuários praticamente não piorou mais isso, porque o sistema já estava no
chão desde os 1.000.

Faz sentido quando eu paro pra pensar: servir uma imagem é só o Apache lendo
um arquivo do disco e mandando de volta. Já qualquer página dinâmica do
WordPress precisa abrir conexão com o MySQL, rodar a query, montar o template
em PHP e só então gerar o HTML — isso é muito mais caro, e nessa configuração
não tem nenhum cache de página rodando pra aliviar.

### O que eu não esperava: mais instâncias nem sempre ajudou

Fui testar achando que ia ver uma curva bem clara de "quanto mais instância,
melhor", e na prática isso só apareceu de forma consistente nos tempos de
resposta — não na taxa de falha. Teve caso em que ir de 1 para 2 instâncias
piorou a situação: no cenário da home com 1.000 usuários, a taxa de falha foi
de 57,6% com 1 instância pra 73,3% com 2.

Olhando a arquitetura, isso faz todo sentido: eu escalei o número de
WordPress, mas o **MySQL continuou sendo um único container** o tempo todo.
Então colocar mais instâncias de WordPress só significa mais gente batendo
na mesma porta do banco de dados ao mesmo tempo — ajuda a processar mais
requisições HTTP, mas não resolve o gargalo real, que é o banco. Pra essa
arquitetura funcionar de verdade sob carga pesada, precisaria também escalar
(ou pelo menos aliviar) a camada de dados — réplica de leitura, cache de
objeto com Redis, algo assim —, não só a camada de aplicação.

### O próprio Locust também teve limite

Outra coisa interessante: em 10.000 usuários, o número de requisições por
segundo ficou travado numa faixa de ~60 a ~115 req/s em praticamente todos os
cenários, não importando quantas instâncias de WordPress eu colocava atrás do
Nginx. Isso é um sinal de que, nesse ponto, quem tava limitando o teste já não
era mais o WordPress — era o próprio Locust, rodando como um processo só numa
máquina só. É basicamente por isso que não dava pra simular 100 mil ou 1
milhão de usuários nesse ambiente: a partir de um certo nível de carga, eu
deixaria de medir o desempenho do WordPress e passaria a medir só a
capacidade do meu notebook de gerar tráfego. Pra ir além disso de verdade,
precisaria rodar o Locust distribuído em várias máquinas (ele tem um modo
`--master`/`--worker` pra isso), o que ficou fora do escopo aqui.

## Limitações que vale deixar claras

- Cada combinação rodou só uma vez, sem repetição — então os números têm uma
  margem de ruído que eu não consegui medir (tipo: um pico de uso de disco do
  Docker Desktop no meio do teste pode ter puxado algum resultado pra cima ou
  pra baixo sem relação nenhuma com a carga em si).
- Nginx, as 5 instâncias de WordPress, o MySQL e o próprio Locust rodaram
  todos na mesma máquina, competindo pelos mesmos núcleos de CPU. Isso não
  reflete um ambiente de produção real, onde cada peça teria seu próprio
  servidor.
- Não tinha nenhum plugin de cache ativado no WordPress. Isso é
  propositalmente o pior cenário possível — a maioria dos sites WordPress
  reais usaria cache de página e amorteceria boa parte da degradação que
  apareceu aqui nos cenários dinâmicos.

## O que eu tiro disso

O balanceamento de carga com Nginx funciona bem quando o problema é CPU/
memória da aplicação — ficou claro nos cenários de imagem. Mas pra maioria do
tráfego real de um WordPress, que depende do banco, só adicionar mais
instâncias de aplicação não resolve muita coisa, porque o MySQL único
continua sendo o teto. Se fosse continuar esse projeto, o próximo passo não
seria "mais WordPress", e sim atacar o banco: cache de página, réplica de
leitura, ou um Redis compartilhado entre as instâncias.
