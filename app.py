import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Experiencias por ciudad", page_icon="🧭", layout="wide")

# ---------- util: leer en raíz o en data/ ----------
def read_any(filename, **kwargs):
    for p in [Path(filename), Path("data")/filename]:
        if p.exists():
            return pd.read_csv(p, **kwargs)
    st.error(f"❌ No encontré {filename}. Sube el archivo a la raíz o a /data.")
    st.stop()

def pick_col(df: pd.DataFrame, candidates):
    """Devuelve el nombre real de la primera columna que coincida (insensible a mayúsculas)."""
    lookup = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    return None

# ---------- Carga de datos ----------
exp_df = read_any("Experience_Catalog_Complete.csv")

# Detectar columnas clave (ajusta/añade alternativas si tus nombres son otros)
COL_CITY    = pick_col(exp_df, ["city","ciudad","destino","location","municipio"])
COL_NAME    = pick_col(exp_df, ["experience_name","name","title","experience"])
COL_CAT     = pick_col(exp_df, ["category","type","segment","experience_type"])
COL_PRICE   = pick_col(exp_df, ["price","precio","avg_price","amount","cost"])
COL_RATING  = pick_col(exp_df, ["rating","score","valoracion","review_score"])

if not (COL_CITY and COL_NAME):
    st.error("Necesito al menos las columnas de **ciudad** y **nombre de experiencia** en el catálogo.")
    st.write("Columnas del archivo:", list(exp_df.columns))
    st.stop()

st.title("Encuentra experiencias por ciudad")

# ========== BARRA LATERAL: Filtros ==========
st.sidebar.header("Filtros")
city_text = st.sidebar.text_input("Ciudad destino", placeholder="Ej.: Valencia, Sevilla, Bilbao…")

# Propuestas rápidas (por si no sabe la ortografía exacta)
suggestions = sorted(x for x in exp_df[COL_CITY].dropna().astype(str).unique())[:2000]  # recorte por si es enorme
if not city_text:
    city_quick = st.sidebar.selectbox("O elige una ciudad", ["(sin selección)"] + suggestions)
    if city_quick != "(sin selección)":
        city_text = city_quick

# Filtros opcionales si existen
cat_options = sorted(exp_df[COL_CAT].dropna().astype(str).unique()) if COL_CAT else []
cats_sel = st.sidebar.multiselect("Categorías", cat_options) if cat_options else []

if COL_PRICE and pd.api.types.is_numeric_dtype(pd.to_numeric(exp_df[COL_PRICE], errors="coerce")):
    price_min = float(pd.to_numeric(exp_df[COL_PRICE], errors="coerce").min())
    price_max = float(pd.to_numeric(exp_df[COL_PRICE], errors="coerce").max())
    price_range = st.sidebar.slider("Rango de precio", min_value=0.0,
                                    max_value=max(10.0, round(price_max, 2)),
                                    value=(0.0, max(10.0, round(price_max, 2))))
else:
    price_range = None

if COL_RATING and pd.api.types.is_numeric_dtype(pd.to_numeric(exp_df[COL_RATING], errors="coerce")):
    min_rating = st.sidebar.slider("Puntuación mínima", 0.0, 5.0, 0.0, 0.1)
else:
    min_rating = None

st.sidebar.caption("Consejo: escribe parte del nombre de la ciudad (ej. “valen”)")

# ========== FILTRADO ==========
df = exp_df.copy()
# filtro por ciudad (contiene, insensible a mayúsculas/acentos básicos)
if city_text:
    df = df[df[COL_CITY].astype(str).str.contains(city_text, case=False, na=False)]

# filtros extra
if cats_sel and COL_CAT:
    df = df[df[COL_CAT].astype(str).isin(cats_sel)]

if price_range and COL_PRICE:
    p = pd.to_numeric(df[COL_PRICE], errors="coerce")
    df = df[(p >= price_range[0]) & (p <= price_range[1])]

if min_rating is not None and COL_RATING:
    r = pd.to_numeric(df[COL_RATING], errors="coerce")
    df = df[r >= min_rating]

# ========== KPI y tabla amigable ==========
left, right = st.columns([1,1])

with left:
    st.subheader("Resumen")
    st.metric("Experiencias encontradas", f"{len(df):,}")
    if COL_CAT:
        top_cat = df[COL_CAT].value_counts().head(3)
        if not top_cat.empty:
            st.write("Top categorías:")
            for idx, val in top_cat.items():
                st.write(f"- {idx}: {val}")

with right:
    if COL_PRICE and not df.empty:
        p = pd.to_numeric(df[COL_PRICE], errors="coerce")
        st.metric("Precio medio (filtrado)", f"{p.mean():.2f}" if p.notna().any() else "—")
    if COL_RATING and not df.empty:
        r = pd.to_numeric(df[COL_RATING], errors="coerce")
        st.metric("Puntuación media", f"{r.mean():.2f}" if r.notna().any() else "—")

st.divider()

# Selección de columnas limpias para mostrar
nice_cols = [c for c in [COL_NAME, COL_CITY, COL_CAT, COL_PRICE, COL_RATING] if c]
extra_cols = [c for c in df.columns if c not in nice_cols][:3]  # añade 3 columnas más como apoyo (sin códigos raros)

table = df[nice_cols + extra_cols].rename(columns={
    COL_NAME: "Experiencia",
    COL_CITY: "Ciudad",
    COL_CAT: "Categoría",
    COL_PRICE: "Precio",
    COL_RATING: "Puntuación"
})

st.subheader("Resultados")
if city_text and table.empty:
    st.warning("No se encontraron experiencias para esa ciudad con los filtros actuales.")
else:
    st.dataframe(table.head(200), use_container_width=True)

# Botón de descarga
if not table.empty:
    st.download_button(
        "Descargar resultados (CSV)",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="experiencias_filtradas.csv",
        mime="text/csv"
    )




