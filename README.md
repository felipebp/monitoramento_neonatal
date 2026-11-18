# 🩺 NeonatoScan — Monitoramento e Estratificação de Risco de Mortalidade Neonatal (Ceará)

[![Streamlit App](https://img.shields.io/badge/Live%20Demo-neonatoscan.site-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://neonatoscan.site)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Analytics-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Logistic%20Regression-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

Pipeline ponta a ponta de **Engenharia e Ciência de Dados** desenvolvido para integrar registros públicos de nascimentos e óbitos do DATASUS (Ceará), identificar fatores críticos associados ao óbito neonatal precoce e tardio (0 a 27 dias de vida) e disponibilizar uma ferramenta interativa de apoio à triagem clínica.

🔗 **Aplicação online:** [https://neonatoscan.site](https://neonatoscan.site)

---

## 🎯 Problema de Negócio e Contexto

No Brasil, a mortalidade neonatal representa a principal parcela da mortalidade infantil, estando fortemente associada a condições perinatais preveníveis, prematuridade, baixo peso ao nascer e qualidade da assistência ao parto.

O desafio técnico deste projeto consiste em **unificar duas bases governamentais originalmente isoladas** — **SINASC** (Sistema de Informações sobre Nascidos Vivos) e **SIM** (Sistema de Informações sobre Mortalidade) — para construir uma coorte epidemiológica consolidada e transformar dados históricos em **estratificação de risco interpretável** para profissionais de saúde e gestores públicos.

---

## 🏗️ Arquitetura do Pipeline

```text
[ Google BigQuery (Base dos Dados / DATASUS) ]
                     │
                     ▼  (src/01_importar_dados_brutos.py)
         [ data/raw/*.parquet ]
                     │
                     ▼  (src/02_*.py & src/03_*.py)
       [ PostgreSQL — Camada Staging ]
                     │
                     ▼  (sql/linkage_ceara.sql)
   [ PostgreSQL — analytics.base_neonatal_pura ]  (> 594 mil registros)
          │                        │
          ▼                        ▼
[ notebooks/exploracao... ]   [ data/processed/coorte_ceara.parquet ]
          │                        │
          ▼                        ▼
[ models/modelo_neonatal.pkl ] ──► [ app.py (Streamlit Dashboard) ]
```

## ⚙️ Principais Decisões de Engenharia e Modelagem

* **Linkage Determinístico em SQL (`sql/linkage_ceara.sql`):** Cruzamento relacional entre SINASC e SIM utilizando a chave oficial da Declaração de Nascido Vivo (`numero_dn`), com higienização de registros inconsistentes e tipagem estrita para garantir integridade referencial em mais de **594 mil nascimentos**.
* **Interpretabilidade Clínica com Regressão Logística:** Optou-se por um modelo linear generalizado calibrado para permitir a leitura direta dos coeficientes em **Odds Ratio (Razão de Chances)**, evidenciando o peso isolado de variáveis como *Apgar no 5º minuto*, *peso ao nascer*, *semanas de gestação*, *idade materna*, *presença de anomalia congênita* e *sexo*.
* **Estratificação por Percentis de Risco (P80 / P95):** Em vez de um corte binário genérico de 50%, os limiares de alerta foram calibrados sobre a distribuição real de probabilidades da coorte para separar perfis de **Risco Habitual**, **Atenção Prioritária (≥ P80)** e **Alto Risco / UTI Neonatal (≥ P95)**.
* **Arquitetura Híbrida (PostgreSQL + Fallback Parquet):** O `app.py` conecta-se diretamente ao banco PostgreSQL quando as credenciais estão configuradas no `.env`, mas alterna automaticamente para a coorte otimizada em `data/processed/coorte_ceara.parquet` caso executado em ambiente offline ou sem banco ativo.
---

## 🩺 Diretrizes Clínicas e Critérios de Estratificação

A construção das regras de negócio, a seleção das variáveis preditoras e a definição das faixas de alerta do simulador apoiam-se em três pilares metodológicos:

1. **Definições Epidemiológicas Oficiais (DATASUS / Ministério da Saúde e OMS):**
   * **Desfecho de Óbito Neonatal:** Segue a padronização da Organização Mundial da Saúde (OMS) e do Sistema de Informações sobre Mortalidade (**SIM**), contemplando todo óbito ocorrido entre **0 e 27 dias completos de vida** (soma do período neonatal precoce, de 0 a 6 dias, e tardio, de 7 a 27 dias).
   * **Parâmetros Perinatais:** Os indicadores clínicos selecionados (`peso`, `semana_gestacao`, `idade_mae`, `id_anomalia` e `sexo`) e os marcos clássicos de atenção perinatal — como baixo peso ao nascer (**< 2.500 g**) e prematuridade (**< 37 semanas**) — seguem os dicionários técnicos do **SINASC/DATASUS**.

2. **Avaliação de Vitalidade pelo Escore de Apgar no 5º Minuto (StatPearls / NCBI):**
   * A adoção do **Apgar no 5º minuto** como principal indicador de vitalidade pós-natal e resposta à reanimação — categorizado clinicamente em **normal/tranquilizador (7 a 10)**, **moderadamente anormal (4 a 6)** e **crítico (0 a 3)** — fundamenta-se na revisão clínica *Apgar Score* publicada pelo *National Center for Biotechnology Information* (NCBI / StatPearls, `NBK430782`).

3. **Faixas de Alerta do Simulador (Calibração Empírica P80 / P95):**
   * Como o óbito neonatal é um evento estatisticamente raro (desbalanceamento severo de classes), aplicar um corte genérico de **50% (0,50)** subestimaria casos graves. Por isso, os três níveis de alerta do painel — **Risco Habitual**, **Atenção Prioritária (≥ P80)** e **Alto Risco / Vigilância Intensiva (≥ P95)** — foram calibrados empiricamente sobre a distribuição real de probabilidades estimadas pelo modelo na coorte histórica do Ceará.
> [!IMPORTANT]
  > **Escopo de Apoio à Decisão:** Os estratos de risco gerados pelo **NeonatoScan** refletem associações estatísticas populacionais e têm finalidade estritamente **epidemiológica e educativa**. O modelo **não deve orientar isoladamente a conduta médica**, sendo indispensável a avaliação clínica presencial, a análise individualizada do contexto perinatal e o julgamento profissional de uma equipe de saúde habilitada.
---

## 📊 Funcionalidades do Painel (`app.py`)

* **Panorama Epidemiológico:** Indicadores gerais da coorte estadual, taxa de mortalidade neonatal e distribuição demográfica e clínica dos nascimentos.
* **Fatores de Risco (Odds Ratio):** Visualização divergente bicolor que destaca fatores agravantes e protetores com base nos pesos do modelo treinado.
* **Simulador de Triagem Neonatal:** Formulário interativo para inserção de parâmetros clínicos do recém-nascido em tempo real, retornando a probabilidade estimada de risco e a faixa de encaminhamento sugerida.

---

## 📂 Estrutura do Repositório
```text
🟦 monitoramento_neonatal/
├── 🟩 data/
│   ├── 🟨 processed/
│   │   └── 📄 coorte_ceara.parquet          # Coorte consolidada para execução offline do painel
│   └── 🟨 raw/
│       └── 📄 .gitkeep                      # Diretório de aterrissagem dos microdados brutos
├── 🟩 models/
│   └── 📄 modelo_neonatal.pkl               # Artefato serializado do modelo e limiares de corte
├── 🟩 notebooks/
│   └── 📄 exploracao_e_modelagem.ipynb      # EDA, seleção de variáveis, treino e avaliação
├── 🟩 sql/
│   └── 📄 linkage_ceara.sql                 # Script SQL de integração SINASC + SIM e regras de filtro
    └── 📄 validacao_importacao.sql          # Script SQL para validação do linkage
├── 🟩 src/
│   ├── 📄 01_importar_dados_brutos.py       # Extração dos microdados via Base dos Dados (BigQuery)
│   ├── 📄 02_sinasc_parquet_to_postgres.py  # Carga da tabela SINASC no PostgreSQL
│   ├── 📄 03_sim_parquet_to_postgres.py     # Carga da tabela SIM no PostgreSQL
│   └── 📄 04_validacao.py                   # Auditoria de volumetria, nulos e integridade pós-carga
├── 📄 .env.example                          # Template de variáveis de conexão com o PostgreSQL
├── 📄 .gitignore
├── 📄 app.py                                # Aplicação web interativa (Streamlit + Plotly)
├── 📄 launcher_linux_mac.sh                 # Script de inicialização automática (Linux / macOS)
├── 📄 launcher_windows.bat                  # Script de inicialização automática (Windows)
├── 📄 README.md
├── 📄 requirements-dev.txt                  # Dependências para extração BigQuery e notebooks
└── 📄 requirements.txt                      # Dependências enxutas para execução do dashboard
```
## 🚀 Como Executar Localmente

O projeto conta com inicializadores automatizados que criam o ambiente virtual isolado (`.venv`), instalam as dependências pré-compiladas e abrem o dashboard no navegador utilizando a base local em Parquet (sem necessidade de configurar banco de dados).

### Opção 1: Execução Automatizada (Recomendada)

* **Windows:** Dê um duplo clique no arquivo `launcher_windows.bat` na raiz do projeto.
* **Linux / macOS:** No terminal, execute:
  ```bash
  chmod +x launcher_linux_mac.sh
  ./launcher_linux_mac.sh
  ```

### Opção 2: Execução Manual via Terminal

```bash
git clone [https://github.com/felipebp/monitoramento_neonatal.git](https://github.com/felipebp/monitoramento_neonatal.git)
cd monitoramento_neonatal

python -m venv .venv
# Linux/macOS: source .venv/bin/activate | Windows: .venv\Scripts\activate

pip install --prefer-binary -r requirements.txt
streamlit run app.py
```

### Opção 3: Reproduzindo o Pipeline Completo com PostgreSQL

Caso deseje executar a ingestão e o *linkage* em uma instância própria do PostgreSQL:

1. Instale também as dependências de extração: `pip install -r requirements-dev.txt`
2. Copie o arquivo `.env.example` para `.env` e preencha as credenciais do seu servidor PostgreSQL.
3. Execute os scripts da pasta `src/` na ordem numérica (`01` a `04`) e rode `sql/linkage_ceara.sql` no banco antes de iniciar o `app.py`.

## 📚 Referências Técnicas e Epidemiológicas

* **DATASUS / Ministério da Saúde (Brasil):** Sistema de Informações sobre Nascidos Vivos (SINASC) e Sistema de Informações sobre Mortalidade (SIM) — microdados consolidados via projeto *Base dos Dados*.
* **Simon, L. V.; Hashmi, M. F.; Bragg, B. N.** *Apgar Score*. StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; NCBI Bookshelf ID: `NBK430782`. Disponível em: [https://www.ncbi.nlm.nih.gov/books/NBK430782/](https://www.ncbi.nlm.nih.gov/books/NBK430782/).

## 🛠️ Stack Tecnológica

- Linguagem & Manipulação de Dados: Python, Pandas, NumPy, PyArrow

- Banco de Dados & Engenharia: PostgreSQL, SQLAlchemy, Psycopg2, Google BigQuery (basedosdados)

- Machine Learning: Scikit-Learn, Joblib

- Visualização & Deploy: Streamlit, Plotly

## 👤 Autor

**Felipe Barros Pereira**  
Graduando em Ciência de Dados — Universidade Federal de Mato Grosso do Sul (UFMS)  
*Projeto desenvolvido para fins acadêmicos e de portfólio em Ciência e Engenharia de Dados.*
