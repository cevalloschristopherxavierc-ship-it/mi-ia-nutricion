import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾")

# Verificación de conexión
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Usamos el modelo más estable
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Error Crítico: No se encontró la API KEY en los Secrets.")

st.title("🦾 JARVIS CORE: SYSTEM V1.1")

# Interfaz de escaneo
archivo = st.file_uploader("Sube tu plato de hoy...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR NUTRIENTES"):
        with st.spinner("🤖 Jarvis analizando..."):
            try:
                # Prompt directo para evitar fallos de v1beta
                response = model.generate_content([
                    "Analiza esta comida para Xavier. Dame calorías y macros aproximados (Proteína, Carb, Grasa) para sus metas de hipertrofia.", 
                    img
                ])
                st.success("Análisis de Jarvis:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error de conexión: {e}")
                st.info("Si el error dice 'API_KEY_INVALID', revisa que en Secrets no haya espacios antes o después de la llave.")

# Estado en la barra lateral
st.sidebar.info(f"Estado: {'Conectado ✅' if 'GOOGLE_API_KEY' in st.secrets else 'Desconectado ❌'}")
