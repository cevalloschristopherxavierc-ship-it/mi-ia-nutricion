import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Reinicio Diario Automático
if 'ultima_fecha' not in st.session_state: st.session_state.ultima_fecha = datetime.now().date()
if st.session_state.ultima_fecha != datetime.now().date():
    st.session_state.agua = 0
    st.session_state.pasos = 0
    st.session_state.ultima_fecha = datetime.now().date()

# Memoria del Sistema
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# --- FUNCIÓN DE HORARIOS ---
def obtener_bloque_comida():
    h = datetime.now().hour
    if 5 <= h < 12: return "Desayuno"
    elif 12 <= h < 18: return "Merienda"
    else: return "Cena"

def obtener_dia_actual():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return dias[datetime.now().weekday()]

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #30363d; margin-bottom: 10px; }
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA ---
if not st.session_state.biometria_completada:
    st.title("👤 Biometría Profesional")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_obj = st.selectbox("Objetivo:", ["Bajar de peso", "Subir de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 INICIAR"):
        m_p = 12000 if u_obj == "Bajar de peso" else 8000
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "objetivo": u_obj, "meta_pasos": m_p}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (8 METAS) ---
dia_hoy = obtener_dia_actual()
regs_hoy = st.session_state.historial[dia_hoy]

tkcal = sum(r.get('k', 0) for r in regs_hoy)
tprot = sum(r.get('p', 0) for r in regs_hoy)
tcarb = sum(r.get('c', 0) for r in regs_hoy)
tgras = sum(r.get('g', 0) for r in regs_hoy)
tfibr = sum(r.get('f', 0) for r in regs_hoy)
tazuc = sum(r.get('a', 0) for r in regs_hoy)
k_quem = (st.session_state.pasos * 0.04)

m_kcal = 3000 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 2300
m_prot = int(st.session_state.u_datos['peso'] * 2.2)
m_carb = 350 if st.session_state.u_datos['objetivo'] == "Subir de peso" else 200

st.title(f"📊 Panel: {datetime.now().strftime('%d/%m/%Y')}")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/{m_kcal}</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">{tprot}/{m_prot}g</p></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-box"><p class="metric-label">👣 Pasos</p><p class="metric-value">{st.session_state.pasos}/{st.session_state.u_datos["meta_pasos"]}</p></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">{k_quem:.1f}</p></div>', unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
with c5: st.markdown(f'<div class="metric-box"><p class="metric-label">🍝 Carb</p><p class="metric-value">{tcarb}/{m_carb}g</p></div>', unsafe_allow_html=True)
with c6: st.markdown(f'<div class="metric-box"><p class="metric-label">🥑 Gras</p><p class="metric-value">{tgras}/70g</p></div>', unsafe_allow_html=True)
with c7: st.markdown(f'<div class="metric-box"><p class="metric-label">🍏 Fibr</p><p class="metric-value">{tfibr}/35g</p></div>', unsafe_allow_html=True)
with c8: st.markdown(f'<div class="metric-box"><p class="metric-label">🍭 Azuc</p><p class="metric-value">{tazuc}/50g</p></div>', unsafe_allow_html=True)

# --- 4. PESTAÑAS ---
t_ia, t_sem, t_sync = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL", "🔐 SINCRONIZACIÓN"])

with t_ia:
    archivo = st.file_uploader("Escanear...", type=["jpg", "png", "jpeg"])
    if archivo and st.button("ANALIZAR Y GUARDAR"):
        bloque_actual = obtener_bloque_comida()
        nuevo = {"hora": datetime.now().strftime("%H:%M"), "alimento": "Alimento Registrado", "bloque": bloque_actual, "detalle": "Análisis IA", "k": 180, "p": 12, "c": 25, "g": 4, "f": 2, "a": 3}
        st.session_state.historial[dia_hoy].append(nuevo)
        st.success(f"Guardado en {bloque_actual}")

with t_sem:
    for dia, registros in st.session_state.historial.items():
        with st.expander(f"📅 {dia}", expanded=(dia == dia_hoy)):
            for b in ["Desayuno", "Merienda", "Cena"]:
                items = [r for r in registros if r.get('bloque') == b]
                for i, it in enumerate(items):
                    cx, cb = st.columns([3, 1])
                    cx.write(f"🍏 {it['alimento']} ({it['hora']})")
                    if cb.button("Ver", key=f"v_{dia}_{b}_{i}"): st.info(it['detalle'])

with t_sync:
    st.subheader("🔐 Acceso Creador Maestro")
    # Validación mejorada para evitar el mensaje de error al estar vacío
    codigo_input = st.text_input("Ingresa tu código maestro:", type="password", key="master_key")
    
    if codigo_input:
        if codigo_input == "xavier2210":
            st.success("✅ Acceso Concedido: Modo Creador")
            st.markdown("---")
            disc = st.selectbox("Seleccionar Perfil:", ["Xavier", "Juan (ID-002)", "Maria (ID-003)"])
            st.write(f"Auditoría activa para: **{disc}**")
            if "Juan" in disc:
                st.error("⚠️ Juan: Proteína Crítica (Faltan 45g)")
        else:
            st.error("❌ Código incorrecto. Inténtalo de nuevo.")
    else:
        st.info("Introduce el código 'xavier2210' para desbloquear los perfiles.")

# --- 5. LATERAL ---
st.sidebar.title("💧 HIDRATACIÓN")
ca1, ca2 = st.sidebar.columns(2)
if ca1.button("➕"): st.session_state.agua += 1
if ca2.button("🔄"): st.session_state.agua = 0
st.sidebar.write(f"Vasos: {st.session_state.agua}/12")
st.sidebar.markdown("---")
st.session_state.pasos = st.sidebar.number_input("👣 PASOS:", value=st.session_state.pasos, step=500)
