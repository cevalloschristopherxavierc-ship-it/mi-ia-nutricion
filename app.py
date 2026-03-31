import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Inicialización de Memoria (Bucle Semanal)
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# Lógica de Horarios Xavier
def obtener_bloque_comida():
    hora = datetime.now().hour
    if 6 <= hora < 12: return "Desayuno"
    elif 12 <= hora < 17: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual de la captura
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 13px; color: #8b949e; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. IDENTIFICACIÓN Y BIOMETRÍA (INICIO - SOLO UNA VEZ) ---
if not st.session_state.biometria_completada:
    st.title("👤 Identificación y Biometría")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_eda = st.number_input("Edad:", value=20)
    with c2:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 INICIAR SISTEMA"):
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "edad": u_eda}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL: 31/03/2026 ---
st.sidebar.title("🔋 ESTADO")
with st.sidebar.expander("📝 Reporte Inicial", expanded=True):
    st.select_slider("Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    if st.button("🔄 Repetir Biometría"):
        st.session_state.biometria_completada = False
        st.rerun()

st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
dia_hoy = obtener_dia_actual()

# Cálculos de nutrientes (Todos los detalles)
regs = st.session_state.historial[dia_hoy]
tkcal = sum(r.get('kcal', 0) for r in regs)
tprot = sum(r.get('prot', 0) for r in regs)

# Filas de Métricas (6 Detalladas)
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/2800</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">{tprot}g/160g</p></div>', unsafe_allow_html=True)
with m3: st.markdown('<div class="metric-box"><p class="metric-label">🍝 Carbohidratos</p><p class="metric-value">0g</p></div>', unsafe_allow_html=True)

m4, m5, m6 = st.columns(3)
with m4: st.markdown('<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">0g</p></div>', unsafe_allow_html=True)
with m5: st.markdown('<div class="metric-box"><p class="metric-label">🍏 Fibra</p><p class="metric-value">0g</p></div>', unsafe_allow_html=True)
with m6: st.markdown('<div class="metric-box"><p class="metric-label">🍭 Azúcares (Fructosa)</p><p class="metric-value">0g</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO MAESTRO ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización"):
    if st.text_input("Código:", type="password") == "xavier2210": es_maestro = True

# --- 5. PESTAÑAS ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL", "👥 CREADOR", "💻 REVISIÓN"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 REGISTRO SEMANAL"])

# --- 6. ESCANEO INTELIGENTE ---
def analizar_plato(img, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    prompt = "Dame el peso aprox y nutrientes: Kcal, Proteína, Carbohidratos, Azúcares (fructosa), Fibra y Grasas. Sé muy directo."
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        texto = res['candidates'][0]['content']['parts'][0]['text']
        bloque = obtener_bloque_comida()
        nuevo = {"hora": datetime.now().strftime("%H:%M"), "bloque": bloque, "detalle": texto, "kcal": 0, "prot": 0}
        st.session_state.historial[dia_hoy].append(nuevo)
        return texto, bloque
    except:
        return "Fallo en Jarvis.", "Error"

# --- 7. CONTENIDO ---
with tabs[0]:
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Capturar...", type=["jpg", "png", "jpeg"])
    if archivo and st.button("ANALIZAR Y GUARDAR"):
        res, blq = analizar_plato(Image.open(archivo), st.secrets["GOOGLE_API_KEY"])
        st.success(f"Guardado en {blq}: {res}")

with tabs[1]:
    st.subheader("📅 Registro Semanal")
    for dia, regs in st.session_state.historial.items():
        with st.expander(f"📍 {dia}", expanded=(dia == dia_hoy)):
            for b in ["Desayuno", "Merienda", "Cena"]:
                st.markdown(f"**--- {b} ---**")
                comidas = [r for r in regs if r.get('bloque') == b]
                if comidas:
                    for c in comidas: st.info(f"{c['hora']}: {c['detalle']}")
                else: st.write("Vacío.")

if es_maestro:
    with tabs[2]: # CREADOR - DISCÍPULOS
        st.subheader("👥 Panel de Creador")
        st.write(f"Perfil: {st.session_state.u_datos['nombre']} | {st.session_state.u_datos['peso']}kg")
        st.json(st.session_state.historial) # Aquí supervisas a los discípulos (datos globales)
        if st.button("🗑️ Reiniciar Bucle Semanal"):
            st.session_state.historial = {dia: [] for dia in st.session_state.historial}
            st.rerun()

# --- 8. HIDRATACIÓN ---
st.sidebar.markdown("---")
if st.sidebar.button("➕ Agua"):
    st.session_state.agua += 1
    st.rerun()
st.sidebar.write(f"💧 Vasos: {st.session_state.agua}/12")
