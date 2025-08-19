import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Explorador TUI", page_icon="🧭", layout="wide")

# ---------- util: leer en raíz o en data/ ----------
def read_any(filename, **kwargs):
    for p in [Path(filename), Path("data")/filename]:
        if p.exists():
            return pd.read_csv(p, **kwargs)
    return None

def pick_col(df: pd.DataFrame, candidates):
    lc = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lc:
            return lc[cand]
    return None

@st.cache_data
def load_data():
    experiences = read_any("Experience_Catalog_Complete.csv")
    upsells     = read_any("upsell_linkage_data.csv")
    return experiences, upsells

exp_df, ups_df = load_data()

st.title("Explorador de Experiencias")

# ===================== 1) DATOS (primero) =====================
colL, colR = st.columns([1,1])

with colL:
    st.subheader("📂 Experience_Catalog_Complete.csv")
    if exp_df is None:
        st.error("No encuentro **Experience_Catalog_Complete.csv** (en raíz ni en `data/`).")
    else:
        st.caption(f"{exp_df.shape[0]:,} filas × {exp_df.shape[1]} columnas")
        st.dataframe(exp_df.head(50), use_container_width=True)

with colR:
    st.subheader("📂 upsell_linkage_data.csv")
    if ups_df is None:
        st.error("No encuentro **upsell_linkage_data.csv** (en raíz ni en `data/`).")
    else:
        st.caption(f"{ups_df.shape[0]:,} filas × {ups_df.shape[1]} columnas")
        st.dataframe(ups_df.head(50), use_container_width=True)

if exp_df is None and ups_df is None:
    st.stop()

st.divider()

# ===================== 2) ESTADÍSTICAS CON VALOR =====================
st.header("Indicadores clave")

# --- detectar columnas útiles en experiencias ---
exp_name = exp_city = exp_cat = exp_price = exp_rating = None
if exp_df is not None:
    exp_name   = pick_col(exp_df, ["experience_name","name","title"])
    exp_city   = pick_col(exp_df, ["city","destino","location","municipio"])
    exp_cat    = pick_col(exp_df, ["category","type","segment","experience_type"])
    exp_price  = pick_col(exp_df, ["price","precio","cost","amount","avg_price"])
    exp_rating = pick_col(exp_df, ["rating","score","valoracion"])

# --- detectar columnas útiles en upsells ---
ups_id    = ups_amount = ups_conv = None
if ups_df is not None:
    ups_id    = pick_col(ups_df, ["upsell_id","upsell","id"])
    ups_amount= pick_col(ups_df, ["amount","price","precio","revenue","importe"])
    ups_conv  = pick_col(ups_df, ["purchased","converted","is_sold","sold","bought"])

# KPIs
m1, m2, m3, m4 = st.columns(4)

# KPI 1: nº experiencias
if exp_df is not None:
    m1.metric("Experiencias en catálogo", f"{len(exp_df):,}")
else:
    m1.metric("Experiencias en catálogo", "—")

# KPI 2: nº ciudades
if exp_df is not None and exp_city:
    m2.metric("Ciudades disponibles", f"{exp_df[exp_city].nunique():,}")
else:
    m2.metric("Ciudades disponibles", "—")

# KPI 3: precio medio (si existe)
if exp_df is not None and exp_price and pd.api.types.is_numeric_dtype(exp_df[exp_price]):
    m3.metric("Precio medio (catálogo)", f"{exp_df[exp_price].mean():.2f}")
else:
    m3.metric("Precio medio (catálogo)", "—")

# KPI 4: conversión upsell o total upsells
if ups_df is not None and ups_conv and ups_df[ups_conv].dropna().isin([1,True,"true","True","YES","Yes"]).any():
    conv = (ups_df[ups_conv].astype(str).str.lower().isin(["1","true","yes","y","si","sí"])).mean()*100
    m4.metric("Conversión de upsells", f"{conv:.1f}%")
elif ups_df is not None and ups_id:
    m4.metric("Total de eventos de upsell", f"{len(ups_df):,}")
else:
    m4.metric("Upsells", "—")

st.divider()

# ===================== 3) GRÁFICOS RESUMEN =====================
gL, gR = st.columns(2)

with gL:
    st.subheader("Top categorías / tipos")
    if exp_df is not None and exp_cat:
        top_cat = exp_df[exp_cat].fillna("Sin categoría").value_counts().head(12)
        st.bar_chart(top_cat)
    elif exp_df is not None and exp_name:
        top_exp = exp_df[exp_name].fillna("—").value_counts().head(12)
        st.bar_chart(top_exp)
    else:
        st.info("No se detectó columna de categoría ni de nombre para agrupar.")

with gR:
    st.subheader("Top upsells por frecuencia")
    if ups_df is not None and ups_id:
        st.bar_chart(ups_df[ups_id].fillna("—").value_counts().head(12))
    else:
        st.info("No se detectó columna identificadora de upsell.")

st.divider()

# ===================== 4) Exploración puntual =====================
st.header("Detalle por experiencia")
if exp_df is not None:
    # Si no encontramos columna de nombre, deja elegir cualquier columna de texto
    if not exp_name:
        text_cols = [c for c in exp_df.columns if exp_df[c].dtype == "object"]
        if text_cols:
            exp_name = st.selectbox(
                "No pude detectar el nombre. Selecciona la columna a usar como 'nombre' 👇",
                text_cols
            )
        else:
            st.warning("No hay columnas de texto para usar como nombre.")
    if exp_name:
        choice = st.selectbox(
            "Elige una experiencia",
            sorted(exp_df[exp_name].dropna().astype(str).unique())
        )
        st.dataframe(exp_df[exp_name].astype(str).eq(choice))
        st.dataframe(exp_df[exp_df[exp_name].astype(str) == choice].head(100), use_container_width=True)
    else:
        st.info("No se pudo configurar un campo de nombre para explorar el detalle.")



