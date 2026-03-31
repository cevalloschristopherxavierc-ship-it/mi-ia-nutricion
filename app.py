import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Panel Xavier - Jarvis Core", page_icon="🦾", layout="wide")

# Base de datos en sesión
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual de tu captura (MODO OSCURO PREMIUM)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-label { font-size: 16px; color: #8b949e; margin-bottom: 5px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PREGUNTAS DEL INICIO (TUS DETALLES) ---
st.sidebar.title("🔋 PROTOCOLO DE INICIO")
with st.sidebar.expander("👤 Identificación y Biometría", expanded=True):
    u_nombre = st.text_input("Nombre:", value="Xavier")
    u_edad = st.number_input("Edad:", value=20)
    u_peso = st.number_input("Peso (kg):", value=75.0)
    u_altura = st.number_input("Altura (cm):", value=175)
    
with st.sidebar.expander("📝 Estado Actual", expanded=True):
    energia = st.select_slider("Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    humor = st.selectbox("Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"])

# --- 3. PANEL DE CONTROL (CAPTURA ORIGINAL 31/03/2026) ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")

dia_hoy = obtener_dia_actual()
registros_hoy = st.session_state.historial[dia_hoy]
kcal_hoy = sum(r.get('kcal', 0) for r in registros_hoy)
prot_hoy = sum(r.get('prot', 0) for r in registros_hoy)

# Las 3 cajas grandes de tu captura
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{kcal_hoy} / 2800</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">{prot_hoy}g / 160g</p></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 4. ACCESO DISCRETO ---
es_maestro = False
with st.expander("🔐 Sincronización"):
    m_key = st.text_input("Código Maestro:", type="password")
    if m_key == "xavier2210":
        es_maestro = True
        st.success(f"Bienvenido, Creador {u_nombre}.")

# --- 5. PESTAÑAS ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "📅 HORARIO SEMANAL", "👥 DISCÍPULOS", "💻 REVISIÓN"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 MI HORARIO"])

# --- 6. MOTOR DE ESCANEO Y GUARDADO ---
def procesar_nutricion(img, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    prompt = """Analiza esta comida para Xavier. Devuelve:
    Calorías: (solo número)
    Carbohidratos: (solo número)
    Azúcares (fructosa natural): (solo número)
    Fibra: (solo número)
    Proteína: (solo número)"""
    
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    res = requests.post(url, json=payload).json()
    
    if 'candidates' in res:
        texto = res['candidates'][0]['content']['parts'][0]['text']
        # Registro automático en el historial
        nuevo = {"hora": datetime.now().strftime("%H:%M"), "detalle": texto, "kcal": 0, "prot": 0}
        st.session_state.historial[dia_hoy].append(nuevo)
        return texto
    return "Error de escaneo."

# --- 7. CONTENIDO ---
with tabs[0]:
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Subir plato...", type=["jpg", "png", "jpeg"])
    if archivo and "GOOGLE_API_KEY" in st.secrets:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        if st.button("ANALIZAR Y GUARDAR"):
            st.success(procesar_nutricion(img, st.secrets["GOOGLE_API_KEY"]))

with tabs[1]:
    st.subheader(f"📅 Registro Semanal ({u_nombre})")
    for dia, regs in st.session_state.historial.items():
        with st.expander(f"📍 {dia}", expanded=(dia == dia_hoy)):
            if not regs: st.write("Sin registros.")
            for r in regs: st.info(f"**[{r['hora']}]**\n{r['detalle']}")

if es_maestro:
    with tabs[2]:
        st.subheader("👥 Panel de Discípulos")
        st.write("Aquí aparecerán los registros de los usuarios que usen tu app.")
        st.warning("Actualmente visualizando registros globales del sistema.")
        st.json(st.session_state.historial) # Aquí verás lo de todos

# --- 8. HIDRATACIÓN ---
st.sidebar.markdown("---")
st.sidebar.subheader(f"💧 Agua: {st.session_state.agua}/12")
progreso = min(st.session_state.agua / 12, 1.0)
st.sidebar.progress(progreso)
if st.sidebar.button("➕ Beber Vaso"):
    st.session_state.agua += 1
    st.rerun()
