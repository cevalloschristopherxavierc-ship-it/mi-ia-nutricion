import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Panel Xavier - Jarvis Core", page_icon="🦾", layout="wide")

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #30363d;
    }
    .metric-label { font-size: 14px; color: #8b949e; margin-bottom: 2px; }
    .metric-value { font-size: 22px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROTOCOLO DE INICIO SEPARADO ---
st.sidebar.title("🔋 PROTOCOLO DE INICIO")

# Bloque 1: Estado Mental (Con botón de reinicio)
with st.sidebar.expander("📝 Reporte de Despertar", expanded=True):
    energia = st.select_slider("Nivel de Energía:", options=["Baja", "Normal", "Alta", "Máxima"], key="slider_ene")
    humor = st.selectbox("Estado de Ánimo:", ["Motivado", "Cansado", "Enfocado", "Recuperando"], key="sel_humor")
    if st.button("🔄 Resetear Estado"):
        st.rerun()

# Bloque 2: Biometría Separada (Con opción de ajuste)
with st.sidebar.expander("📏 Datos Biométricos", expanded=True):
    estatura_cm = st.number_input("Estatura (cm):", min_value=100, max_value=250, value=175, key="num_est")
    peso_kg = st.number_input("Peso Actual (kg):", min_value=30.0, max_value=200.0, value=75.0, key="num_peso")
    if st.button("🔄 Corregir Biometría"):
        st.rerun()

# --- 3. PANEL DE CONTROL: DETALLES COMPLETOS ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")

# Métricas Superiores e Hidratación
col_k, col_q, col_h = st.columns(3)
with col_k: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal Totales</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
with col_q: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">0 kcal</p></div>', unsafe_allow_html=True)

with col_h:
    if 'agua' not in st.session_state: st.session_state.agua = 0
    progreso_agua = min(st.session_state.agua / 12, 1.0)
    st.markdown('<div class="metric-box"><p class="metric-label">💧 Hidratación</p></div>', unsafe_allow_html=True)
    st.progress(progreso_agua, text=f"{st.session_state.agua} / 12 vasos")

st.markdown(" ") 

# Macros Detallados
m1, m2, m3 = st.columns(3)
with m1: st.markdown('<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">0 / 160g</p></div>', unsafe_allow_html=True)
with m2: st.markdown('<div class="metric-box"><p class="metric-label">🍝 Carbohidratos</p><p class="metric-value">0 / 350g</p></div>', unsafe_allow_html=True)
with m3: st.markdown('<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">0 / 70g</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO MAESTRO DISCRETO ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización xavier2210"):
    master_key = st.text_input("Código Maestro:", type="password")
    if master_key == "xavier2210":
        es_maestro = True
        st.success("✅ Núcleo Maestro Sincronizado.")

# --- 5. PESTAÑAS DINÁMICAS ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "💻 DOBLE REVISIÓN", "👤 PERFIL", "📅 HORARIOS"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 HORARIOS GENERALES"])

# --- 6. FUNCIÓN DE CONEXIÓN GEMINI 3.1 ---
def analizar_con_jarvis(image_file, api_key):
    img_byte_arr = io.BytesIO()
    image_file.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    
    prompt = f"Analiza esta comida. Usuario: {estatura_cm}cm, {peso_kg}kg. Detalla Kcal, Proteína, Carbos y Grasas."
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    try:
        res = requests.post(url, json=payload)
        return res.json()
    except:
        return {"error": "Error de conexión"}

# --- 7. CONTENIDO ---
with tabs[0]: 
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Subir foto...", type=["jpg", "png", "jpeg"])
    if archivo and "GOOGLE_API_KEY" in st.secrets:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        if st.button("ANALIZAR PLATO"):
            with st.spinner("🤖 Jarvis analizando..."):
                res = analizar_con_jarvis(img, st.secrets["GOOGLE_API_KEY"])
                if 'candidates' in res:
                    st.success("Resultados:")
                    st.markdown(res['candidates'][0]['content']['parts'][0]['text'])

if es_maestro:
    with tabs[1]:
        st.subheader("💻 Doble Revisión de Código")
        codigo_raw = st.text_area("Pega el código aquí:", height=200)
        if st.button("🔍 AUDITAR"):
            st.info("Función lista.")

# --- 8. CONTROL DE HIDRATACIÓN ---
st.sidebar.markdown("---")
st.sidebar.subheader("💧 Registro de Agua")
col_a1, col_a2 = st.sidebar.columns(2)
if col_a1.button("➕ Añadir"):
    st.session_state.agua += 1
    st.rerun()
if col_a2.button("➖ Quitar"):
    st.session_state.agua = max(0, st.session_state.agua - 1)
    st.rerun()
