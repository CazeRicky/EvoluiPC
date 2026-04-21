# 🖥️ EvoluiPC: O Waze do Upgrade de Hardware

**EvoluiPC é uma plataforma inteligente de planejamento de rotas de upgrade. Através de Grafos de Conhecimento (Knowledge Graphs), mapeamos gargalos e compatibilidades técnicas para gerar uma "árvore de evolução" personalizada. Maximize performance com o melhor custo-benefício e reduza o lixo eletrônico com dados precisos.**

---

## 📊 Lean Canvas (Planejamento Estratégico)

Organização sistêmica do projeto seguindo a ordem lógica de desenvolvimento (1-9).

| **1. Problema (Detonadores)** | **2. Segmento de Clientes** | **3. Proposta de Valor Única** |
| :--- | :--- | :--- |
| • Assimetria de Informação (Gargalo).<br>• Geração de E-waste desnecessário.<br>• Barreira Técnica (BIOS/PCIe/VRMs). | • Gamers de Entrada.<br>• Home Office / Workstations.<br>• Lojas de Informática (B2B).<br>• *Early Adopters:* Entusiastas de hardware. | **"O Waze do Upgrade de Hardware"**<br><br>Eliminamos o erro na compra e maximizamos a vida útil do PC com rotas inteligentes. |

| **4. Solução (Diferenciais)** | **5. Canais** | **6. Fontes de Receita** |
| :--- | :--- | :--- |
| • Motor de Recomendação via Grafos.<br>• Scraping de preços em tempo real.<br>• Simulador de Ganho de Performance. | • Marketing de Conteúdo Técnico.<br>• Comunidades (Discord/Reddit).<br>• Micro-Influenciadores Tech. | • Comissões de Afiliados (CPA).<br>• Modelo SaaS B2B (Licenciamento).<br>• Anúncios Segmentados. |

| **7. Estrutura de Custos** | **8. Métricas-Chave (KPIs)** | **9. Vantagem Injusta** |
| :--- | :--- | :--- |
| • Infraestrutura Cloud (Neo4j).<br>• Manutenção de Scrapers e APIs.<br>• Custo de Aquisição (CAC). | • Usuários Ativos (MAU).<br>• Valor Médio de Compra (AOV).<br>• Taxa de Retenção de Usuários. | • Algoritmo proprietário Neo4j.<br>• Base de hardware "curada" com regras de engenharia reais. |

---

## 🏗️ Pilares de Engenharia e ESG

* **Sistemas Especialistas:** Uso de IA de grafos para prever gargalos lógicos (ex: VRM/Firmware).
* **Sustentabilidade (ESG):** Extensão da vida útil do hardware em 2-3 anos, combatendo o lixo eletrônico.
* **Escalabilidade:** Arquitetura que permite expansão para novos hardwares sem refatoração.

---

## 📋 Gestão do Projeto (Sprint Inicial)

| 📥 Backlog | 📝 To Do (Sprint 1) | 🏗️ In Progress | 🧐 Review | ✅ Done |
| :--- | :--- | :--- | :--- | :--- |
| [ ] Mapeamento PSU/TDP | [ ] Modelagem Neo4j | [ ] Scraper Base (Python) | [ ] Validar Lógica de Gargalo | [x] Nome: EvoluiPC |
| [ ] Alerta de BIOS | [ ] Setup Front (React) | [ ] Regra Intel vs AMD | [ ] Teste Integração API | [x] Escopo do MVP |
| [ ] Filtro de Usados | [ ] Setup Back (FastAPI) | [ ] UI de Input (Design) | | [x] Arquitetura de Grafos |

---

## 🛠️ Stack Tecnológica
* **Frontend:** React / Next.js
* **Backend:** Python / FastAPI
* **Banco de Dados:** Neo4j (Knowledge Graph)
* **Automação:** Web Scraping (Selenium/BeautifulSoup)

## ▶️ Motor Neo4j
* O arquivo `.env` deve ficar em [`evoluipc-engine/.env`](evoluipc-engine/.env.example), usando o banco `EvoluiPC` no Neo4j Desktop.
* O motor lê `NEO4J_DATABASE=EvoluiPC` por padrão; ajuste apenas a URI, o usuário e a senha do seu Neo4j local.

---

## 👨‍💻 Autor
* **Carlos Henrique** *Estudante de Engenharia da Computação - UFRPE*
* **David Alenor** *Estudante de Engenharia da Computação - UFRPE*
* **Victor Felipe** *Estudante de Engenharia da Computação - UFRPE*
  
