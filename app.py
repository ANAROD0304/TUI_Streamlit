import streamlit as st

st.title("🚀 Mi primera app en Streamlit")
st.write("¡Hola! Esto está corriendo en Streamlit Cloud.")

name = st.text_input("¿Cómo te llamas?")
if name:
    st.success(f"Encantado de conocerte, {name} 😃")

