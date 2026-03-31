import streamlit as st
import google.generativeai as genai
from datetime import datetime
import PIL.Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# CONFIGURACIÓN CON SALTO DE MODELO (Solución 1)
if 'nucleo_conectado' not in st.session_state:
    st.session_state.nucleo_conectado = False

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # ORDEN DE ATAQUE: El 8b es el que tiene más cuota libre siempre
    nombres_motor = [
        'gemini-1.5-flash-8b', 
        'gemini-2.0-flash-lite', 
        'gemini-1.5-flash'
    ]
    
    # Intentamos conectar con el modelo que tenga cuota disponible
    for nombre in nombres_motor:
        try:
            model = genai.GenerativeModel(nombre)
            # Guardamos el primero que no nos dé error de conexión
            st.session_state.motor_activo = nombre
            st.session_state.nucleo_conectado = True
            break
        except:
            continue
else:
    st.error("⚠️ No se encontró GOOGLE_API_KEY en los Secrets.")

# Memoria del Sistema (Tus datos de entrenamiento y dieta)
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# Funciones de Tiempo
def obtener_bloque_comida():
    h = datetime.now().hour
    if 5 <= h < 12: return "Desayuno"
    elif 12 <= h < 18: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo Visual Jarvis Dark
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA ---
if not st.session_state.biometria_completada:
    st.title("👤 Configuración de Guerrero Jarvis")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_obj = st.selectbox("Objetivo:", ["Subir de peso", "Bajar de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 ACTIVAR NÚCLEO"):
        m_p = 12000 if u_obj == "Bajar de peso" else 8000
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "objetivo": u_obj, "meta_pasos": m_p}
