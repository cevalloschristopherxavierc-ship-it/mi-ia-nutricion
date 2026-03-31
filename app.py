import streamlit as st
import google.generativeai as genai

st.title("🕵️‍♂️ Diagnóstico de Núcleo Jarvis")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    st.subheader("Modelos Disponibles en tu Cuenta:")
    try:
        # Este comando le pide a Google la lista real de modelos que tú puedes usar
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.code(f"Nombre: {m.name} | Versión: {m.display_name}")
                st.write(f"Soporta Imagen: {'vision' in m.name or 'flash' in m.name}")
                st.markdown("---")
    except Exception as e:
        st.error(f"Error al listar modelos: {e}")
else:
    st.error("No se encontró la API KEY en Secrets.")

st.info("Copia el nombre que salga arriba (ejemplo: models/gemini-1.5-flash) y dímelo para ajustar el código final.")
