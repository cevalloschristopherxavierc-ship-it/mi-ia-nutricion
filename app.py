import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (FORCE STABLE) ---
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos la configuración estándar
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # IMPORTANTE: No usamos 'models/' ni rutas largas para evitar el error 404
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al conectar con el cerebro de la IA: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets.")

# --- 3. LÓGICA DE NUTRICIÓN ---
SISTEMA_EXPERTO = """
Eres Jarvis, experto en nutrición para hipertrofia. 
Analiza la imagen y entrega: 
1. Alimentos. 2. Macros aprox (Cal, Prot, Carb, Fat). 
3. ¿Es bueno para pierna/glúteo? 4. ¿Qué falta?
Sé directo y técnico.
"""

# --- 4. INTERFAZ ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")

archivo = st.file_uploader("Sube tu plato, Xavier...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("ANALIZAR MACROS"):
        with st.spinner("🤖 Analizando biomasa..."):
            try:
                # LLAMADA LIMPIA
                response = model.generate_content([SISTEMA_EXPERTO, img])
                st.success("Análisis completado:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error persistente: {e}")
                st.info("💡 RECUERDA: Si el error sigue, borra tu API KEY actual en AI Studio y crea una TOTALMENTE NUEVA.")

# --- 5. CONTROL Y LOG ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("ENCENDER CHRIS-TV"):
        key = st.secrets.get("IFTTT_KEY", "bQpyH6xT10n6e2YJsTXE_oK22s7GQTLuqEiMFNNrvDd")
        url = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{key}"
        requests.post(url)
        st.success("Señal enviada.")

with col2:
    st.subheader("🏋️ Registro Rápido")
    peso_log = st.number_input("Peso (lb):", 0)
    if st.button("Guardar"):
        st.write(f"Guardado en el núcleo: {peso_log}lb")
