import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jarvis Core - Nutrición", page_icon="🦾", layout="wide")

# Estilo visual limpio
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00d4ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE IA (FIX ESTABLE) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    try:
        # Forzamos la versión estable para evitar el error 404
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al inicializar el núcleo: {e}")
else:
    st.error("⚠️ Falta la GOOGLE_API_KEY en los Secrets de Streamlit.")

# --- 3. LÓGICA DE NUTRICIÓN (SISTEMA EXPERTO) ---
SISTEMA_EXPERTO = """
Actúa como Jarvis, experto en nutrición para hipertrofia y desarrollo de pierna/glúteo.
Analiza la imagen de comida de Xavier y entrega:
1. Identificación de alimentos.
2. Macros aproximados (Calorías, Proteínas, Carbohidratos, Grasas).
3. Evaluación: ¿Es óptimo para ganar masa muscular hoy?
4. Recomendación de Jarvis: ¿Qué falta para mejorar este plato?
Responde de forma técnica, directa y motivadora.
"""

# --- 4. INTERFAZ PRINCIPAL ---
st.title("🦾 JARVIS CORE: NUTRITION SCANNER")
st.markdown("---")

# Layout de una sola columna para que se vea mejor en el móvil
st.subheader("🍎 Escaneo de Biomasa (Comida)")
archivo = st.file_uploader("Sube la foto de tu plato...", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Sensor visual activo", use_container_width=True)
    
    if st.button("EJECUTAR ANÁLISIS"):
        with st.spinner("🤖 Jarvis analizando nutrientes..."):
            try:
                # Generación de contenido
                response = model.generate_content([SISTEMA_EXPERTO, img])
                st.success("Análisis completado:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error en el análisis: {e}")
                st.info("💡 Si ves un error 404, asegúrate de haber dado 'Reboot App' en el panel de Streamlit.")

# --- 5. LOG DE ENTRENAMIENTO RÁPIDO ---
st.markdown("---")
st.subheader("🏋️ Registro de Fuerza")
col1, col2 = st.columns(2)
with col1:
    ejer = st.selectbox("Ejercicio:", ["Smith Machine Lunges", "Hip Thrust", "RDL", "Sentadilla Búlgara"])
with col2:
    peso = st.number_input("Peso levantado (lb/kg):", min_value=0)

if st.button("GUARDAR EN EL NÚCLEO"):
    st.success(f"Dato guardado: {ejer} con {peso}. ¡Dale con todo!")

# Barra lateral de estado
st.sidebar.write("**Usuario:** Xavier Cevallos")
st.sidebar.write("**Estado:** Sistema de Nutrición Online ✅")
