import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# --- 2. CONFIGURACIÓN DE APIS (EL FIX DEL 404) ---
if "GOOGLE_API_KEY" in st.secrets:
    # Configuramos la API Key
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    try:
        # CAMBIO CLAVE: Quitamos 'models/' y dejamos que la librería elija la versión estable
        # Si esto falla, probaremos con la versión completa abajo.
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al inicializar el modelo: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

# --- 3. PROMPT DE NUTRICIÓN ---
SISTEMA_EXPERTO = """
Actúa como un Nutriólogo experto en Hipertrofia.
Analiza la imagen de comida y entrega:
1. Identificación de alimentos.
2. Aproximado de: Calorías, Proteínas (g), Carbohidratos (g) y Grasas (g).
3. Evaluación: ¿Es óptimo para ganar masa muscular en piernas y glúteos?
4. Recomendación: ¿Qué falta para optimizarlo?
Responde de forma técnica y eficiente, como Jarvis.
"""

# --- 4. INTERFAZ DE USUARIO ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")
st.markdown("---")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("🍎 Análisis de Nutrientes")
    archivo = st.file_uploader("Sube tu foto, Xavier...", type=["jpg", "png", "jpeg"])

    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Sensor visual activo", use_container_width=True)
        
        if st.button("EJECUTAR ANÁLISIS"):
            with st.spinner("🤖 Jarvis procesando..."):
                try:
                    # FORZAMOS LA LLAMADA
                    response = model.generate_content([SISTEMA_EXPERTO, img])
                    st.success("Análisis completado:")
                    st.markdown(response.text)
                except Exception as e:
                    # Si sale el 404 aquí, intentamos la ruta alternativa automáticamente
                    try:
                        model_alt = genai.GenerativeModel('models/gemini-1.5-flash')
                        response = model_alt.generate_content([SISTEMA_EXPERTO, img])
                        st.markdown(response.text)
                    except:
                        st.error(f"Error persistente en la API: {e}")
                        st.info("Verifica que tu API Key en AI Studio no tenga restricciones de facturación.")

with col_der:
    st.subheader("📺 Control de Entorno")
    if st.button("ENCENDER CHRIS-TV"):
        if "IFTTT_KEY" in st.secrets:
            key_tv = st.secrets["IFTTT_KEY"]
            url_tv = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{key_tv}"
            requests.post(url_tv)
            st.success("Comando enviado.")
        else:
            st.warning("⚠️ Falta IFTTT_KEY.")

    st.markdown("---")
    st.subheader("🏋️ Log de Entrenamiento")
    ejer = st.selectbox("Ejercicio:", ["Smith Machine Lunges", "Hip Thrust", "RDL", "Sentadilla Búlgara"])
    peso = st.number_input("Peso (lb/kg):", min_value=0)
    if st.button("GUARDAR EN EL NÚCLEO"):
        st.info(f"Registro: {ejer} con {peso}. ¡Buen trabajo!")

# --- 5. ESTADO ---
st.sidebar.header("📈 Estado")
st.sidebar.write("**Usuario:** Xavier Cevallos")
if "GOOGLE_API_KEY" in st.secrets:
    st.sidebar.success("✅ Servidor Online")
else:
    st.sidebar.error("❌ Servidor Offline")
