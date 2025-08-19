import streamlit as st
import os
from pathlib import Path

# ---- DEBUG TEMPORAL ----
ROOT = Path(__file__).parent.resolve()
data_dir = ROOT / "data"
st.sidebar.write("📁 Working dir:", os.getcwd())
st.sidebar.write("📂 App dir:", str(ROOT))
st.sidebar.write("📦 Contenido de 'data/':", list(data_dir.glob("*")) if data_dir.exists() else "NO EXISTE")
# ---- FIN DEBUG ----


import streamlit as st
import pandas as pd

# --- Cabecera de la app ---
st.title("Formulario de Cliente")
st.write("Por favor, completa la siguiente información para personalizar tu experiencia.")

# --- Preguntas al usuario ---
name = st.text_input("Nombre completo")
age = st.number_input("Edad", min_value=0, max_value=120, step=1)
country = st.text_input("País de residencia")
interests = st.selectbox(
    "¿Qué tipo de experiencia prefieres?",
    ["Aventura", "Cultural", "Gastronomía", "Relax", "Otra"]
)

# Mostrar resultados solo si el usuario completó todo
if name and age and country:
    st.subheader("Resumen de tus respuestas")
    st.write(f"**Nombre:** {name}")
    st.write(f"**Edad:** {age}")
    st.write(f"**País:** {country}")
    st.write(f"**Preferencia:** {interests}")

# --- Cargar datasets ---
experiences = pd.read_csv("data/Experience_Catalog_Complete.csv")
upsells = pd.read_csv("data/upsell_linkage_data.csv")

st.title("Explorador de Experiencias")

# Exploración de experiencias
exp_choice = st.selectbox("Elige una experiencia", experiences["Experience_Name"].unique())
st.write("Detalles de la experiencia seleccionada:")
st.dataframe(experiences[experiences["Experience_Name"] == exp_choice])

# Ejemplo de gráfico con upsells
st.subheader("Upsells más frecuentes")
st.bar_chart(upsells["upsell_id"].value_counts())



