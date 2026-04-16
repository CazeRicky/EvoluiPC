RigRevive (Foco em Hardware/Sustentabilidade)
O Problema: Fazer upgrade de computadores esbarra em uma barreira técnica grande. É difícil cruzar variáveis como gargalos entre CPU e GPU, limitações de placas-mãe de gerações anteriores e consumo de energia, o que gera compras erradas ou lixo eletrônico desnecessário.

A Solução: Uma plataforma de planejamento de hardware. O usuário insere o setup atual, e o sistema mapeia a rota de upgrade com o melhor custo-benefício, mostrando exatamente qual a melhor peça compatível e o ganho real de performance em porcentagem.

Tecnologia Não Convencional: Grafos de Conhecimento (Knowledge Graphs) integrados a Scraping de dados. A plataforma usaria um banco de dados em grafos para mapear a relação de compatibilidade entre milhares de componentes e cruzaria isso com bots que varrem o mercado de usados e novos para sugerir a peça exata com o melhor preço naquele momento.
🖥️ Nome do Projeto: EvoluiPC
1. Descrição detalhada do projeto
O EvoluiPC é uma plataforma inteligente de planejamento de rotas de upgrade para computadores. O problema central que ele resolve é a barreira técnica na hora de melhorar um PC: usuários leigos ou até entusiastas têm dificuldade em calcular gargalos entre processador e placa de vídeo, ou desconhecem limitações de compatibilidade. O usuário insere as peças que já possui, e o sistema gera uma "árvore de evolução", indicando qual componente trocar primeiro para obter o maior ganho de performance gastando o mínimo possível, evitando compras erradas e a geração de lixo eletrônico.

2. Repositório(s) de cada parte do projeto
Para manter uma arquitetura organizada e pronta para o MVP, o ideal é dividir em dois repositórios principais:

Interface (Front-end): github.com/sua-equipe/evoluipc-web (Sugestão: React ou Next.js para criar uma interface visual fluida onde o usuário monta o setup).

Motor de Dados (Back-end): github.com/sua-equipe/evoluipc-engine (Sugestão: Python, ideal para lidar com a raspagem de dados de preços e a lógica matemática da plataforma).

3. Quadro Kanban das atividades
Crie um quadro no Trello, GitHub Projects ou Notion com as seguintes colunas e cards iniciais:

Backlog: Integrar API de lojas de hardware, Criar sistema de autenticação de usuários, Mapear requisitos de energia (Fontes).

To Do (Sprint 1): Configurar repositórios no GitHub, Criar banco de dados em grafos, Fazer o design da tela principal de input do setup.

In Progress: Preencher o Lean Canvas, Definir o esquema de compatibilidade inicial (ex: mapear a linha de soquetes AM4).

Review: Testar algoritmo de cálculo de gargalo entre CPU e GPU.

Done: Definição do escopo e nome do MVP.

4. Quais os modais serão atrelados

Web App (Desktop/Mobile): O modal principal. Uma aplicação responsiva onde o usuário cadastra sua máquina atual e visualiza os gráficos de performance e a rota do upgrade.

Extensão de Navegador (Visão de Futuro para o MVP): Um modal secundário que, ao navegar em um e-commerce de informática, avisa na tela se aquela peça específica é 100% compatível com o setup salvo no perfil do usuário.

5. Descrição detalhada da tecnologia não convencional
O projeto usará Grafos de Conhecimento (Knowledge Graphs) aliados a Web Scraping dinâmico.
Bancos de dados relacionais tradicionais são lentos e complexos para cruzar tantas variáveis de hardware. O EvoluiPC usa um banco orientado a grafos (como o Neo4j), onde cada peça é um "nó" e a compatibilidade é a "aresta".
O sistema consegue conectar visualmente e logicamente que um upgrade para um Ryzen 7 5700X3D é compatível com uma placa-mãe PRIME A320M-K/BR, mas a aresta do grafo alertaria imediatamente sobre a necessidade de uma atualização crítica de BIOS antes da instalação, ou sugeriria a troca para uma placa B550M para liberar recursos mais modernos. O algoritmo navega por esses grafos instantaneamente para traçar o caminho mais seguro, enquanto robôs (scrapers) buscam os preços dessas peças em tempo real na internet.

Bloco,O que preencher
1. Problema,"Dificuldade técnica para realizar upgrades em PCs (gargalos, compatibilidade de placas-mãe e processadores). Compras erradas geram desperdício de dinheiro e lixo eletrônico."
2. Segmento de Clientes,"Gamers de PC, entusiastas de tecnologia com orçamento limitado e profissionais que precisam prolongar a vida útil de suas máquinas."
3. Proposta de Valor,"O EvoluiPC planeja a rota de upgrade perfeita para o seu computador atual, garantindo 100% de compatibilidade e o melhor custo-benefício em tempo real."
4. Solução,"Sistema web que utiliza Grafos de Conhecimento para mapear gargalos e cruzar com preços do mercado, sugerindo a peça exata para o próximo passo."
5. Canais,"Fóruns de hardware, criadores de conteúdo tech no YouTube/TikTok, grupos de promoções no Discord e Telegram."
6. Fontes de Receita,Links de afiliados (comissões por vendas em lojas parceiras) e assinaturas premium com ferramentas extras para montadores profissionais.
7. Estrutura de Custos,"Hospedagem do banco de dados em grafos, servidores para rodar os bots de busca de preços, custos de desenvolvimento e manutenção."
8. Métricas-Chave,"Quantidade de rotas de upgrade geradas por usuário, Taxa de cliques (CTR) nos links de afiliados sugeridos."
9. Vantagem Injusta,O uso de Grafos de Conhecimento permite calcular compatibilidades complexas (como versões de BIOS e barramentos) de forma muito superior aos calculadores de gargalo estáticos atuais.

FAÇA o lean canva e o quadro Kambam