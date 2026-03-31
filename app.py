import streamlit as st
import requests
import base64
from PIL import Image
import io
import re
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Lógica de Reinicio Diario (Agua y Pasos)
if 'ultima_fecha' not in st.session_state:
    st.session_state.ultima_fecha = datetime.now().date()

if st.session_state.ultima_fecha != datetime.now().date():
    st.session_state.agua = 0
    st.session_state.pasos = 0
    st.session_state.ultima_fecha = datetime.now().date()

# Memoria de historial y biometría
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

def obtener_bloque_comida():
    h = datetime.now().hour
    if 6 <= h < 12: return "Desayuno"
    elif 12 <= h < 17: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

# Estilo visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 12px; color: #8b949e; text-transform: uppercase; }
    .metric-value { font-size: 20px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA Y OBJETIVO ---
if not st.session_state.biometria_completada:
    st.title("👤 Configuración de Perfil Profesional")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_eda = st.number_input("Edad:", value=20)
        u_obj = st.selectbox("Objetivo:", ["Bajar de peso", "Subir de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso Actual (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 ACTIVAR JARVIS"):
        meta_p = 12000 if u_obj == "Bajar de peso" else 8000
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "objetivo": u_obj, "meta_pasos": meta_p}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (8 MÉTRICAS TOTALES) ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
dia_hoy = obtener_dia_actual()
regs_hoy = st.session_state.historial[dia_hoy]

# Sumar nutrientes registrados hoy
tkcal = sum(r.get('k', 0) for r in regs_hoy)
tprot = sum(r.get('p', 0) for r in regs_hoy)
tcarb = sum(r.get('c', 0) for r in regs_hoy)
tgras = sum(r.get('g', 0) for r in regs_hoy)
tfibr = sum(r.get('f', 0) for r in regs_hoy)
tazuc = sum(r.get('a', 0) for r in regs_hoy)
k_quem = (st.session_state.pasos * 0.04)

# Renderizado de cajas
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/2300</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Proteína</p><p class="metric-value">{tprot}g/160g</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">👣 Pasos</p><p class="metric-value">{st.session_state.pasos}/{st.session_state.u_datos["meta_pasos"]}</p></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">{k_quem:.1f} kcal</p></div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)
with col5: st.markdown(f'<div class="metric-box"><p class="metric-label">🍝 Carbos</p><p class="metric-value">{tcarb}g</p></div>', unsafe_allow_html=True)
with col6: st.markdown(f'<div class="metric-box"><p class="metric-label">🥑 Grasas</p><p class="metric-value">{tgras}g</p></div>', unsafe_allow_html=True)
with col7: st.markdown(f'<div class="metric-box"><p class="metric-label">🍏 Fibra</p><p class="metric-value">{tfibr}g</p></div>', unsafe_allow_html=True)
with col8: st.markdown(f'<div class="metric-box"><p class="metric-label">🍭 Azúcar</p><p class="metric-value">{tazuc}g</p></div>', unsafe_allow_html=True)

# --- 4. SINCRONIZACIÓN Y PERFILES ---
st.markdown("---")
es_maestro = False
with st.expander("🔐 Sincronización de Perfiles"):
    if st.text_input("Código Maestro:", type="password") == "xavier2210":
        es_maestro = True
        st.success("Modo Creador Activo")
        perfil = st.selectbox("Seleccionar Perfil a visualizar:", ["Mi Perfil (Xavier)", "Discípulo: Juan", "Discípulo: Maria"])
        if "Juan" in perfil:
            st.warning("Visualizando datos remotos de Juan... (Peso: 80kg | Meta: 12k pasos)")

# --- 5. REGISTRO IA CON SUMA AUTOMÁTICA ---
t_ia, t_sem = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL"])

def extraer_numero(texto, clave):
    match = re.search(rf"{clave}:\s*(\d+)", texto, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def analizar_y_sumar(img, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    img_b64 = base64.b64encode(io.BytesIO(img.tobytes()).getvalue()).decode('utf-8') # Simplificado para el ejemplo
    
    # Prompt estricto para que la IA devuelva números que el código pueda leer
    prompt = "Analiza el plato. Formato: Nombre: [X] | Kcal: [X] | Prot: [X] | Carb: [X] | Gras: [X] | Fibra: [X] | Azucar: [X]"
    
    # (Simulación de respuesta para asegurar que veas cómo suma)
    texto_res = "Nombre: Manzana\nKcal: 95 | Prot: 1 | Carb: 25 | Gras: 0 | Fibra: 4 | Azucar: 19"
    
    nuevo = {
        "hora": datetime.now().strftime("%H:%M"), "alimento": "Manzana", "bloque": obtener_bloque_comida(),
        "detalle": texto_res, "k": 95, "p": 1, "c": 25, "g": 0, "f": 4, "a": 19
    }
    st.session_state.historial[dia_hoy].append(nuevo)
    return texto_res

with t_ia:
    archivo = st.file_uploader("Escanear comida...", type=["jpg", "png", "jpeg"])
    if archivo and st.button("ANALIZAR Y SUMAR"):
        res = analizar_y_sumar(Image.open(archivo), st.secrets["GOOGLE_API_KEY"])
        st.success("¡Datos inyectados al Panel de Control!")

with t_sem:
    for dia, registros in st.session_state.historial.items():
        with st.expander(f"📅 {dia}", expanded=(dia == dia_hoy)):
            for b in ["Desayuno", "Merienda", "Cena"]:
                st.markdown(f"**--- {b} ---**")
                items = [r for r in registros if r.get('bloque') == b]
                for i, it in enumerate(items):
                    c_txt, c_btn = st.columns([3, 1])
                    c_txt.write(f"🍏 {it['alimento']} ({it['hora']})")
                    if c_btn.button("Ver Detalles", key=f"btn_{dia}_{b}_{i}"):
                        st.info(it['detalle'])

# --- 6. BARRA LATERAL (AGUA Y PASOS) ---
st.sidebar.title("💧 HIDRATACIÓN")
col_add, col_res = st.sidebar.columns(2)
if col_add.button("➕ Añadir"): st.session_state.agua += 1
if col_res.button("🔄 Reset"): st.session_state.agua = 0
st.sidebar.write(f"Vasos hoy: {st.session_state.agua}/12")
st.sidebar.progress(min(st.session_state.agua/12, 1.0))

st.sidebar.markdown("---")
st.session_state.pasos = st.sidebar.number_input("👣 PASOS HOY:", min_value=0, value=st.session_state.pasos, step=500)
