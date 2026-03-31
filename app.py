import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (ESTABILIZACIÓN TOTAL) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Configuramos el modelo para que use la versión de producción, no la beta
    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 2048,
    }
    
    try:
        # Usamos el nombre del modelo sin prefijos raros
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )
    except Exception as e:
        st.error(f"Error de inicialización: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets.")

# --- 3. LÓGICA DE NUTRICIÓN ---
SISTEMA_EXPERTO = """
Analiza la imagen como un experto en nutrición deportiva. 
Dime: 1. Alimentos. 2. Calorías y Macros (Prot/Carb/Fat). 
3. ¿Sirve para hipertrofia de pierna/glúteo? 
4. Recomendación técnica.
"""

# --- 4. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")

archivo = st.file_uploader("Sube tu comida...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR MACROS"):
        with st.spinner("🤖 Jarvis analizando..."):
            try:
                # Intentamos la generación de contenido
                # Nota: Pasamos la imagen directamente en una lista
                response = model.generate_content([SISTEMA_EXPERTO, img])
                st.success("Análisis completado:")
                st.markdown(response.text)
            except Exception as e:
                # Si sale el 404, mostramos un mensaje de diagnóstico
                st.error(f"Error crítico: {e}")
                st.info("💡 REVISIÓN FINAL: Ve a tu panel de Streamlit Cloud, dale a 'Reboot App'. A veces el servidor se queda trabado con versiones viejas y necesita un reinicio total.")

# --- 5. CONTROL ---
if st.button("ENCENDER CHRIS-TV"):
    key = st.secrets.get("IFTTT_KEY", "bQpyH6xT10n6e2YJsTXE_oK22s7GQTLuqEiMFNNrvDd")
    url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{key}"
    requests.post(url)
    st.success("Señal enviada.")
