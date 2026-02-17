```md
# Trabalho M2–M3 — Busca Local (BLM / BLNM) + Dashboard

Este projeto executa experimentos de **Busca Local** para o problema de escalonamento de *n* tarefas em *m* máquinas paralelas, minimizando o **makespan** (maior carga entre as máquinas), e gera um **dashboard automático** para analisar os resultados.

## Estrutura do projeto

```

TRABALHO M2-M3/
├─ BLM/
│  ├─ Resultados/
│  └─ melhor_melhora.py
├─ BLNM/
│  ├─ Resultados/
│  └─ monotona_randomizada.py
├─ dashboard.py
├─ enunciadoHeurísticas.pdf
└─ Requerimentos.txt

````

## Requisitos

- Python 3.10+ (recomendado)
- Dependências listadas em `Requerimentos.txt`:
  - openpyxl, pandas, plotly, streamlit

## Instalação

### 1) Criar e ativar ambiente virtual (recomendado)

**Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
````

**Linux/Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências

Na raiz do projeto (`TRABALHO M2-M3/`):

```bash
pip install -r Requerimentos.txt
```

## Como rodar

### Passo 1 — Gerar resultados do BLNM (Monótona Randomizada)

```bash
python BLNM/monotona_randomizada.py
```

Saídas geradas em `BLNM/Resultados/`:

* `resultados_blnm_<timestamp>.txt`
* `resultados_blnm_<timestamp>.xlsx`

> O script já salva com timestamp no nome (ex: `11-02-2026_23-32-06`) para **não sobrescrever execuções anteriores**.

O `.xlsx` possui:

* aba `resultados` (dados brutos)
* aba `resumo` (tempo total do script, estatísticas e agregações)

### Passo 2 — Gerar resultados do BLM (Melhor Melhora)

```bash
python BLM/melhor_melhora.py
```

Saídas geradas em `BLM/Resultados/`:

* `resultados_blm_<timestamp>.txt`
* `resultados_blm_<timestamp>.xlsx`

Também com:

* aba `resultados`
* aba `resumo`

### Passo 3 — Rodar o Dashboard (Streamlit)

Na raiz do projeto:

```bash
streamlit run dashboard.py
```

O dashboard:

* detecta automaticamente o **XLSX mais recente** em:

  * `BLNM/Resultados/` (padrão `resultados_blnm_*.xlsx`)
  * `BLM/Resultados/` (padrão `resultados_blm_*.xlsx`)
* monta filtros, KPIs, gráficos e tabelas para cada método
* possui botão **🔄 Atualizar dados** para recarregar o arquivo mais recente sem precisar reiniciar o Streamlit

## O que o dashboard mostra

### BLNM (Monótona Randomizada)

* Filtros: `m`, `n`, `α`
* KPIs: número de execuções, melhor makespan, **tempo médio formatado (Xm Ys)**, melhor α (menor makespan médio)
* Gráficos: α × makespan médio, α × tempo médio, histogramas
* Tabelas: agregada por α + dados brutos

### BLM (Melhor Melhora)

* Filtros: `m`, `n`
* KPIs: execuções, melhor makespan, **tempo médio formatado (Xm Ys)**, iterações médias
* Gráficos: barras por instância (m,n)
* Tabelas: agregada por instância + dados brutos

> Observação: o dashboard também tenta ler a aba `resumo` do XLSX, quando existir, para exibir/usar métricas como **tempo total do experimento**.

## Dicas / Troubleshooting

* **“Não encontrei XLSX…”**
  Rode primeiro `BLNM/monotona_randomizada.py` e/ou `BLM/melhor_melhora.py`. Verifique se os arquivos estão dentro de:

  * `BLNM/Resultados/`
  * `BLM/Resultados/`

* **Rodar sempre da raiz**
  Execute `streamlit run dashboard.py` a partir da **raiz do projeto**, pois o dashboard procura as pastas usando caminhos relativos.

* **Atualizar sem reiniciar**
  Clique em **🔄 Atualizar dados** para limpar cache e recarregar os XLSX mais recentes.

## Notas sobre o experimento

* Repetições por instância: 10
* Critério de parada: 1000 iterações sem melhora
* Parâmetro do BLNM: α ∈ {0.1, 0.2, ..., 0.9}

---

Autores: Lucas Toller Gutmann, Ricardo de Carvalho, Vitor Murilo da Hora Coelho.

```