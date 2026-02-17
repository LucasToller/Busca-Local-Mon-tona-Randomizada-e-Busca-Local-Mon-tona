import os
import glob
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px


# =========================
# Config do App
# =========================
st.set_page_config(
    page_title="Dashboard - Busca Local (BLM/BLNM)",
    layout="wide"
)

# Ajuste se sua estrutura for diferente
BLNM_DIR = os.path.join("BLNM", "Resultados")
BLM_DIR  = os.path.join("BLM", "Resultados")


# =========================
# Utilitários
# =========================
def encontrar_mais_recente(pasta: str, padrao: str) -> str | None:
    """Encontra o arquivo mais recente (por mtime) em uma pasta."""
    if not os.path.isdir(pasta):
        return None

    arquivos = glob.glob(os.path.join(pasta, padrao))
    if not arquivos:
        return None

    arquivos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return arquivos[0]


@st.cache_data(show_spinner=False)
def ler_resultados_xlsx(path: str) -> pd.DataFrame:
    """Lê a aba 'resultados' de um XLSX e padroniza tipos."""
    df = pd.read_excel(path, sheet_name="resultados")

    # Padroniza nomes (por garantia)
    df.columns = [c.strip().lower() for c in df.columns]

    # Tipos
    if "n" in df: df["n"] = pd.to_numeric(df["n"], errors="coerce").astype("Int64")
    if "m" in df: df["m"] = pd.to_numeric(df["m"], errors="coerce").astype("Int64")
    if "replicacao" in df: df["replicacao"] = pd.to_numeric(df["replicacao"], errors="coerce").astype("Int64")
    if "tempo" in df: df["tempo"] = pd.to_numeric(df["tempo"], errors="coerce")
    if "iteracoes" in df: df["iteracoes"] = pd.to_numeric(df["iteracoes"], errors="coerce").astype("Int64")
    if "valor" in df: df["valor"] = pd.to_numeric(df["valor"], errors="coerce").astype("Int64")

    # parametro pode ser alpha (float) ou "NA"
    if "parametro" in df:
        df["parametro_num"] = pd.to_numeric(df["parametro"], errors="coerce")
    else:
        df["parametro"] = None
        df["parametro_num"] = None

    return df


@st.cache_data(show_spinner=False)
def ler_resumo_xlsx(path: str) -> dict:
    """
    Lê a aba 'resumo' (se existir) e tenta extrair:
    - tempo_total_str  (ex: '2m 49s' OU '0m 65s')
    - tempo_total_s    (float em segundos, se existir)
    """
    try:
        df = pd.read_excel(path, sheet_name="resumo", header=None)
    except Exception:
        return {}

    # transforma em pares "Item" -> "Valor", tentando achar linhas com esses dois campos
    resumo = {}
    for i in range(len(df)):
        a = df.iloc[i, 0] if df.shape[1] > 0 else None
        b = df.iloc[i, 1] if df.shape[1] > 1 else None
        if isinstance(a, str):
            chave = a.strip()
            if chave:
                resumo[chave] = b

    # tenta extrair chaves que você gerou
    tempo_total_str = resumo.get("Tempo total do script")
    tempo_total_s = resumo.get("Tempo total do script (s)")

    # normaliza tempo_total_s
    try:
        if tempo_total_s is not None:
            tempo_total_s = float(str(tempo_total_s).replace(",", "."))
    except Exception:
        tempo_total_s = None

    return {
        "tempo_total_str": tempo_total_str,
        "tempo_total_s": tempo_total_s,
    }


def fmt_min_seg(segundos: float) -> str:
    """Formata segundos para 'Xm Ys'."""
    total = int(round(float(segundos)))
    m = total // 60
    s = total % 60
    return f"{m}m {s}s"


def info_arquivo(path: str) -> str:
    ts = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d/%m/%Y %H:%M:%S")
    return f"{os.path.basename(path)} (última modificação: {ts})"


# =========================
# Cabeçalho + Botão Atualizar
# =========================
st.title("Dashboard - BLM / BLNM (Busca Local)")
st.caption("Lê automaticamente os XLSX mais recentes gerados pelos scripts e monta gráficos/tabelas.")

# Estado para mostrar "Atualizado em..."
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = None

col_btn, col_spacer = st.columns([1, 5])
with col_btn:
    if st.button("🔄 Atualizar dados"):
        st.session_state["last_refresh"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.cache_data.clear()
        st.rerun()

# Feedback da atualização
if st.session_state["last_refresh"]:
    st.success(f"✅ Dados atualizados em {st.session_state['last_refresh']}")


# =========================
# Carrega arquivos mais recentes
# =========================
blnm_path = encontrar_mais_recente(BLNM_DIR, "resultados_blnm_*.xlsx")
blm_path  = encontrar_mais_recente(BLM_DIR,  "resultados_blm_*.xlsx")


colA, colB = st.columns(2)
with colA:
    st.subheader("BLNM (Monótona Randomizada)")
    if blnm_path:
        st.write("Arquivo:", info_arquivo(blnm_path))
    else:
        st.warning(f"Não encontrei XLSX em: {BLNM_DIR}")

with colB:
    st.subheader("BLM (Melhor Melhora)")
    if blm_path:
        st.write("Arquivo:", info_arquivo(blm_path))
    else:
        st.warning(f"Não encontrei XLSX em: {BLM_DIR}")


# =========================
# BLNM
# =========================
if blnm_path:
    df_blnm = ler_resultados_xlsx(blnm_path).copy()
    resumo_blnm = ler_resumo_xlsx(blnm_path)

    # Filtros
    st.divider()
    st.header("BLNM - Análises")

    f1, f2, f3 = st.columns(3)
    with f1:
        m_opts = sorted(df_blnm["m"].dropna().unique().tolist())
        m_sel = st.multiselect("Filtrar m", m_opts, default=m_opts)
    with f2:
        n_opts = sorted(df_blnm["n"].dropna().unique().tolist())
        n_sel = st.multiselect("Filtrar n", n_opts, default=n_opts)
    with f3:
        a_opts = sorted(df_blnm["parametro_num"].dropna().unique().tolist())
        a_sel = st.multiselect("Filtrar α", a_opts, default=a_opts)

    df_blnm_f = df_blnm[
        df_blnm["m"].isin(m_sel) &
        df_blnm["n"].isin(n_sel) &
        df_blnm["parametro_num"].isin(a_sel)
    ].copy()

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Execuções (filtradas)", f"{len(df_blnm_f)}")

    if len(df_blnm_f) > 0:
        k2.metric("Melhor valor (min)", int(df_blnm_f["valor"].min()))

        tempo_medio = float(df_blnm_f["tempo"].mean())
        k3.metric("Tempo médio", f"{fmt_min_seg(tempo_medio)} ({tempo_medio:.3f}s)")

        best_alpha = (
            df_blnm_f.groupby("parametro_num")["valor"]
            .mean()
            .sort_values()
            .index[0]
        )
        # renomeado para ficar incontestável
        k4.metric("Melhor α (menor makespan médio)", f"{best_alpha:.1f}")

        # Tempo total do experimento (aba resumo)
        tempo_total_str = resumo_blnm.get("tempo_total_str")
        tempo_total_s = resumo_blnm.get("tempo_total_s")
        if tempo_total_str:
            if tempo_total_s is not None:
                k5.metric("Tempo total (experimento)", f"{tempo_total_str} ({tempo_total_s:.2f}s)")
            else:
                k5.metric("Tempo total (experimento)", f"{tempo_total_str}")
        elif tempo_total_s is not None:
            k5.metric("Tempo total (experimento)", f"{fmt_min_seg(tempo_total_s)} ({tempo_total_s:.2f}s)")
        else:
            k5.metric("Tempo total (experimento)", "—")

    # Agregações
    agg_alpha = (
        df_blnm_f.groupby("parametro_num", as_index=False)
        .agg(
            valor_medio=("valor", "mean"),
            tempo_medio=("tempo", "mean"),
            iter_medias=("iteracoes", "mean"),
            execucoes=("valor", "count"),
        )
        .sort_values("parametro_num")
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("α × Valor médio (makespan)")
        fig = px.line(
            agg_alpha,
            x="parametro_num",
            y="valor_medio",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("α × Tempo médio (s)")
        fig = px.line(
            agg_alpha,
            x="parametro_num",
            y="tempo_medio",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Distribuição de valores (filtrado)")
        fig = px.histogram(df_blnm_f, x="valor")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Distribuição de tempos (filtrado)")
        fig = px.histogram(df_blnm_f, x="tempo")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tabela agregada por α")
    st.dataframe(agg_alpha, use_container_width=True)

    with st.expander("Ver dados brutos (resultados)"):
        st.dataframe(df_blnm_f, use_container_width=True)


# =========================
# BLM
# =========================
if blm_path:
    df_blm = ler_resultados_xlsx(blm_path).copy()
    resumo_blm = ler_resumo_xlsx(blm_path)

    st.divider()
    st.header("BLM - Análises")

    f1, f2 = st.columns(2)
    with f1:
        m_opts = sorted(df_blm["m"].dropna().unique().tolist())
        m_sel = st.multiselect("Filtrar m (BLM)", m_opts, default=m_opts)
    with f2:
        n_opts = sorted(df_blm["n"].dropna().unique().tolist())
        n_sel = st.multiselect("Filtrar n (BLM)", n_opts, default=n_opts)

    df_blm_f = df_blm[
        df_blm["m"].isin(m_sel) &
        df_blm["n"].isin(n_sel)
    ].copy()

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Execuções (filtradas)", f"{len(df_blm_f)}")

    if len(df_blm_f) > 0:
        k2.metric("Melhor valor (min)", int(df_blm_f["valor"].min()))

        tempo_medio = float(df_blm_f["tempo"].mean())
        k3.metric("Tempo médio", f"{fmt_min_seg(tempo_medio)} ({tempo_medio:.3f}s)")

        k4.metric("Iterações médias", f"{df_blm_f['iteracoes'].mean():.1f}")

        # Tempo total do experimento (aba resumo)
        tempo_total_str = resumo_blm.get("tempo_total_str")
        tempo_total_s = resumo_blm.get("tempo_total_s")
        if tempo_total_str:
            if tempo_total_s is not None:
                k5.metric("Tempo total (experimento)", f"{tempo_total_str} ({tempo_total_s:.2f}s)")
            else:
                k5.metric("Tempo total (experimento)", f"{tempo_total_str}")
        elif tempo_total_s is not None:
            k5.metric("Tempo total (experimento)", f"{fmt_min_seg(tempo_total_s)} ({tempo_total_s:.2f}s)")
        else:
            k5.metric("Tempo total (experimento)", "—")

    # Agregação por instância (m,n)
    agg_inst = (
        df_blm_f.groupby(["m", "n"], as_index=False)
        .agg(
            valor_medio=("valor", "mean"),
            tempo_medio=("tempo", "mean"),
            iter_medias=("iteracoes", "mean"),
            execucoes=("valor", "count"),
        )
        .sort_values(["m", "n"])
    )
    agg_inst["instancia"] = agg_inst.apply(lambda r: f"m={int(r['m'])}, n={int(r['n'])}", axis=1)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Instância × Valor médio (makespan)")
        fig = px.bar(agg_inst, x="instancia", y="valor_medio")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Instância × Tempo médio (s)")
        fig = px.bar(agg_inst, x="instancia", y="tempo_medio")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tabela agregada por instância (m,n)")
    st.dataframe(agg_inst.drop(columns=["instancia"]), use_container_width=True)

    with st.expander("Ver dados brutos (resultados)"):
        st.dataframe(df_blm_f, use_container_width=True)


# =========================
# Rodapé / Dicas
# =========================
st.divider()
st.caption(
    "Dica: rode primeiro os scripts BLNM/BLM para gerar novos XLSX em 'Resultados'. "
    "Depois, clique em 'Atualizar dados' para carregar o arquivo mais recente."
)