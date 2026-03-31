import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# --- CONFIGURACIÓN QUE YA TENÍAS (NO SE TOCA) ---
st.set_page_config(page_title="Jarvis Core", page_icon="🦾")

# --- EL CORAZÓN DE TU IA (Mantenemos tu lógica de conexión) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets")

model = genai.GenerativeModel('gemini-1.5-flash')

# --- LO QUE FALTABA: EL PROMPT DE NUTRICIÓN REAL ---
# Este es el "cerebro" que te da los aproximados exactos que buscabas
SISTEMA_EXPERTO = """
Eres un Nutriólogo experto en Hipertrofia. Tu tarea es analizar la imagen de comida y:
1. Identificar cada alimento con precisión.
2. Dar un APROXIMADO detallado de:
   - Calorías totales.
   - Proteínas (g) -> Vital para tus músculos.
   - Carbohidratos (g).
   - Grasas (g).
3. Dar un veredicto: ¿Esta comida ayuda a la hipertrofia de pierna/glúteo hoy?
4. Sugerir un ajuste rápido si falta proteína.
Sé breve, técnico y eficiente.
"""

# --- INTERFAZ ---
st.title("🦾 Control Central Jarvis")

tab1, tab2 = st.tabs(["🍎 Nutrición Pro", "📺 Control Hogar"])

with tab1:
    st.subheader("Escaneo de Biomasa (
