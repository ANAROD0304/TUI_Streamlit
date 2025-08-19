import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Formulario y Explorador", page_icon="🧭")

# --------- util: leer en raíz o en data/ ---------
def read_any(filename, **kwargs):
    candidates = [Path(filename), Path("data") / filename]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p, **kwargs)
    st.warning(f"Archivo no encontrado: {filename} (busqué en {candidates[0]} y {candidates[1]})")
    return None

# --------- formulario (para cliente) ----------
st.title("Formulario de Cliente")
st.write("Completa la información para personalizar la experiencia.")

name = st.text_input("Nombre completo")
age = st.number_input("Edad", min_value=0, max_value=120, step=1)
country = st.text_input("País de residencia")
interests = st.selectbox(
    "¿Qué tipo de experiencia prefieres?",
    ["Cultural", "Aventura", "Gastronomía", "Relax", "Otra"]
)

if name and age and country:
    st.subheader("Resumen")
    st.write(f"**Nombre:** {name}")
    st.write(f"**Edad:** {age}")
    st.write(f"**País:** {country}")
    st.write(f"**Preferencia:** {interests}")

st.divider()

# --------- datos (se cargan desde RAÍZ o data/) ----------
experiences = read_any("Experience_Catalog_Complete.csv")
upsells     = read_any("upsell_linkage_data.csv")

st.header("Explorador de Experiencias")

if experiences is not None:
    # Evitar columna inexistente por nombre distinto
    exp_name_col = None
    for c in experiences.columns:
        if c.lower() in ("experience_name", "experience", "name"):
            exp_name_col = c
            break
    if exp_name_col is None:
        st.error("No encontré la columna de nombre de experiencia (ej.: 'Experience_Name').")
    else:
        exp_choice = st.selectbox(
            "Elige una experiencia",
            sorted(experiences[exp_name_col].dropna().unique())
        )
        st.write("Detalles seleccionados:")
        st.dataframe(experiences[experiences[exp_name_col] == exp_choice].head(50))
else:
    st.info("Sube o deja en el repo el archivo Experience_Catalog_Complete.csv")

st.subheader("Upsells más frecuentes")
if upsells is not None:
    # Usar una columna razonable si existe
    count_col = None
    for c in upsells.columns:
        if c.lower() in ("upsell_id","upsell","id"):
            count_col = c
            break
    if count_col:
        st.bar_chart(upsells[count_col].value_counts())
    else:
        st.info("No encontré una columna tipo 'upsell_id' para graficar.")
else:
    st.info("Sube o deja en el repo el archivo upsell_linkage_data.csv")


