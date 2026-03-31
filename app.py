import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (SOLUCIÓN DEFINITIVA) ---
if "GOOGLE_API_KEY" in st.secrets:
    # Configuramos la nueva llave
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Usamos un bloque de control para asegurar la conexión
    try:
        # Definimos el modelo de forma simple (la versión 0.8.3 lo llevará a la estable)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de inicialización: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

# --- 3. LÓGICA DE NUTRICIÓN ---
SISTEMA_EXPERTO = """
Eres Jarvis, experto en nutrición para hipertrofia de pierna y glúteo.
Analiza la imagen y entrega:
1. Alimentos.
2. Macros aproximados (Calorías, Prot, Carb, Fat).
3. ¿Ayuda a ganar músculo hoy?
4. ¿Qué le falta al plato?
Responde directo y técnico.
"""

# --- 4. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")

archivo = st.file_uploader("Sube tu plato, Xavier...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("EJECUTAR ANÁLISIS DE MACROS"):
        with st.spinner("🤖 Jarvis analizando biomasa..."):
            try:
                # Esta es la llamada que ya no debería dar 404
                response = model.generate_content([SISTEMA_EXPERTO, img])
                st.success("Análisis completado:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error persistente: {e}")
                st.warning("Si el error persiste tras cambiar la llave y el requirements.txt, revisa que tu cuenta de Google Cloud no tenga restricciones.")

# --- 5. CONTROL DE ENTORNO (TU LLAVE VERIFICADA) ---
st.markdown("---")
if st.button("ENCENDER CHRIS-TV"):
    if "IFTTT_KEY" in st.secrets:
        url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{st.secrets['IFTTT_KEY']}"
        requests.post(url)
        st.success("Señal enviada al servidor IFTTT.")
