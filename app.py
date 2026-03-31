import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Inicializar base de datos y estados
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# Función para determinar el bloque de comida según la hora exacta
def obtener_bloque_comida():
    hora = datetime.now().hour
    if 6 <= hora < 12: return "Desayuno"
    elif 12 <= hora < 17: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; }
    .metric-label { font-size: 14px; color: #8b949e; }
    .metric-value { font-size: 20px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. IDENTIFICACIÓN Y BIOMETRÍA (PÁGINA DE INICIO - SOLO UNA VEZ) ---
if not st.session_state.biometria_completada:
    st.title("👤 Identificación y Biometría")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_edad = st.number_input("Edad:", value=20)
    with col_b2:
        u_peso = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 INICIAR PANEL DE CONTROL"):
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_peso, "altura": u_alt, "edad": u_edad}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL: 31/03/2026 ---
st.sidebar.title("🔋 ESTADO")
with st.sidebar.expander("📝 Reporte", expanded=True):
    st.select_slider("Energía:", options=["Baja", "Normal", "Alta", "Máxima"])
    if st.button("🔄 Repetir Biometría"):
        st.session_state.biometria_completada = False
        st.rerun()

st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
dia_hoy = obtener_dia_actual()

# Cálculos dinámicos
regs_hoy = st.session_state.historial[dia_hoy]
tkcal = sum(r.get('kcal', 0) for r in regs_hoy)
tprot = sum(r.get('prot', 0) for r in regs_hoy)

# 4 Columnas con todos los nutrientes requeridos
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/2800</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">{tprot}g/160g</p></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="metric-box"><p class="metric-label">🍝 Carbos</p><p class="metric-value">0g</p></div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">0g</p></div>', unsafe_allow_html=True)

# --- 4. ACCESO DISCRETO ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización"):
    m_key = st.text_input("Código:", type="password")
    if m_key == "xavier2210": es_maestro = True

# --- 5. PESTAÑAS DINÁMICAS ---
if es_maestro:
    tabs = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL", "👥 CREADOR", "💻 REVISIÓN"])
else:
    tabs = st.tabs(["🚀 PRUEBA IA", "📅 REGISTRO SEMANAL"])

# --- 6. ESCANEO CON PESO Y NUTRIENTES ---
def analizar_y_agendar(img, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    prompt = "Dame el peso aprox y nutrientes: Calorías, Carbohidratos (Azúcares/Fructosa), Fibra, Proteína. Sé conciso."
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    
    try:
        res = requests.post(url, json=payload).json()
        texto = res['candidates'][0]['content']['parts'][0]['text']
        bloque = obtener_bloque_comida()
        # SE AGREGA 'bloque' PARA EVITAR KEYERROR
        nuevo = {"hora": datetime.now().strftime("%H:%M"), "bloque": bloque, "detalle": texto, "kcal": 0, "prot": 0}
        st.session_state.historial[dia_hoy].append(nuevo)
        return texto, bloque
    except:
        return "Fallo en análisis.", "Error"

# --- 7. CONTENIDO DE PESTAÑAS ---
with tabs[0]:
    st.subheader("📷 Escaneo de Nutrientes")
    archivo = st.file_uploader("Subir foto del plato...", type=["jpg", "png", "jpeg"])
    if archivo and st.button("ANALIZAR Y REGISTRAR"):
        res, blq = analizar_y_agendar(Image.open(archivo), st.secrets["GOOGLE_API_KEY"])
        st.success(f"Registrado en **{blq}**: {res}")

with tabs[1]:
    st.subheader("📅 Registro Semanal")
    for dia, regs in st.session_state.historial.items():
        with st.expander(f"📍 {dia}", expanded=(dia == dia_hoy)):
            for b in ["Desayuno", "Merienda", "Cena"]:
                st.markdown(f"**--- {b} ---**")
                # .get('bloque') es el escudo contra el KeyError
                comidas_bloque = [r for r in regs if r.get('bloque') == b]
                if comidas_bloque:
                    for c in comidas_bloque: st.info(f"{c['hora']}: {c['detalle']}")
                else: st.write("Sin registros en este bloque.")

if es_maestro:
    with tabs[2]: # PANEL DE CREADOR PARA VER DISCÍPULOS
        st.subheader("👥 Panel de Creador - Supervisión")
        st.write(f"Viendo perfil activo: **{st.session_state.u_datos['nombre']}**")
        st.json(st.session_state.historial) # Aquí supervisas todos los movimientos
        if st.button("🗑️ Resetear Historial Semanal"):
            st.session_state.historial = {dia: [] for dia in st.session_state.historial}
            st.rerun()

# --- 8. HIDRATACIÓN ---
st.sidebar.markdown("---")
if st.sidebar.button("➕ Agua"):
    st.session_state.agua += 1
    st.rerun()
st.sidebar.write(f"💧 Vasos: {st.session_state.agua}/12")
