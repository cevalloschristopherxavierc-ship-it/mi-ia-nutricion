import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾", layout="wide")

# Estilo visual estilo Jarvis
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00d4ff; color: black; font-weight: bold; height: 3em; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE APIS Y MODELO (SOLUCIÓN ERROR 404) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    try:
        # Forzamos la ruta completa del modelo para evitar el error 404 de v1beta
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
else:
    st.error("⚠️ Error: Falta 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

# --- 3. EL CEREBRO DE JARVIS (PROMPT DE NUTRICIÓN) ---
SISTEMA_EXPERTO = """
Actúa como un Nutriólogo experto en Hipertrofia y Entrenamiento de Fuerza.
Tu misión es analizar la imagen de comida que el usuario (Xavier) te proporciona.
Debes entregar:
1. Identificación de alimentos.
2. APROXIMADO de: Calorías totales, Proteínas (g), Carbohidratos (g) y Grasas (g).
3. EVALUACIÓN: ¿Este plato es óptimo para ganar masa muscular en piernas y glúteos?
4. RECOMENDACIÓN: ¿Qué falta para llegar al requerimiento proteico ideal?
Responde de forma técnica, eficiente y motivadora, como una IA avanzada.
"""

# --- 4. INTERFAZ DE USUARIO ---
st.title("🦾 JARVIS CORE: SYSTEM V1.0")
st.markdown("---")

col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("🍎 Escaneo de Nutrientes")
    archivo = st.file_uploader("Sube tu foto, Xavier...", type=["jpg", "png", "jpeg"])

    if archivo:
        img = Image.open(archivo)
        # Usamos la nueva función container para evitar avisos de versión
        st.image(img, caption="Sensor visual activo", use_container_width=True)
        
        if st.button("EJECUTAR ANÁLISIS DE MACROS"):
            with st.spinner("🤖 Jarvis procesando datos nutricionales..."):
                try:
                    # Llamada directa al modelo corregido
                    resultado = model.generate_content([SISTEMA_EXPERTO, img])
                    st.success("Análisis completado:")
                    st.markdown(resultado.text)
                except Exception as e:
                    st.error(f"Error en el análisis: {e}")
                    st.info("Nota: Si ves un 404, asegúrate de que tu GOOGLE_API_KEY esté activa en AI Studio.")

with col_der:
    st.subheader("📺 Control de Entorno")
    # Usamos la llave que verificamos antes
    if st.button("ENCENDER CHRIS-TV"):
        if "IFTTT_KEY" in st.secrets:
            key_tv = st.secrets["IFTTT_KEY"]
            url_tv = f"https://maker.ifttt.com/trigger/prender_tele/with/key/{key_tv}"
            try:
                r = requests.post(url_tv)
                if r.status_code == 200:
                    st.success("🤖 Comando enviado con éxito.")
                else:
                    st.error(f"Error en IFTTT: {r.status_code}")
            except:
                st.error("No se pudo conectar con el servidor de la tele.")
        else:
            st.warning("⚠️ Falta IFTTT_KEY en Secrets.")

    st.markdown("---")
    st.subheader("🏋️ Log de Entrenamiento")
    ejer = st.selectbox("Ejercicio:", ["Smith Machine Lunges", "Hip Thrust", "RDL", "Sentadilla Búlgara"])
    peso = st.number_input("Peso (lb/kg):", min_value=0)
    if st.button("GUARDAR EN EL NÚCLEO"):
        st.info(f"Registro: {ejer} cargado con {peso}. ¡A seguir creciendo!")

# --- 5. BARRA LATERAL (ESTADO) ---
st.sidebar.header("📈 Estado del Sistema")
st.sidebar.write("**Usuario:** Xavier Cevallos")
st.sidebar.write("**Ubicación:** Portoviejo, Manabí")
if "GOOGLE_API_KEY" in st.secrets:
    st.sidebar.success("✅ Servidor Gemini: Online")
else:
    st.sidebar.error("❌ Servidor Gemini: Offline")
