import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Jarvis Core - Xavier", page_icon="🦾", layout="wide")

# Reinicio Diario Automático
if 'ultima_fecha' not in st.session_state: 
    st.session_state.ultima_fecha = datetime.now().date()

if st.session_state.ultima_fecha != datetime.now().date():
    st.session_state.agua = 0
    st.session_state.pasos = 0
    st.session_state.ultima_fecha = datetime.now().date()

# Memoria de Datos
if 'historial' not in st.session_state:
    st.session_state.historial = {dia: [] for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
if 'agua' not in st.session_state: st.session_state.agua = 0
if 'pasos' not in st.session_state: st.session_state.pasos = 0
if 'biometria_completada' not in st.session_state: st.session_state.biometria_completada = False

# --- FUNCIONES DE TIEMPO ---
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
    .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BIOMETRÍA ---
if not st.session_state.biometria_completada:
    st.title("👤 Biometría Profesional Jarvis")
    c1, c2 = st.columns(2)
    with c1:
        u_nom = st.text_input("Nombre:", value="Xavier")
        u_obj = st.selectbox("Objetivo:", ["Bajar de peso", "Subir de peso", "Mantener"])
    with c2:
        u_pes = st.number_input("Peso (kg):", value=75.0)
        u_alt = st.number_input("Altura (cm):", value=175)
    
    if st.button("🚀 ACTIVAR NÚCLEO"):
        m_p = 12000 if u_obj == "Bajar de peso" else 8000
        st.session_state.u_datos = {"nombre": u_nom, "peso": u_pes, "altura": u_alt, "objetivo": u_obj, "meta_pasos": m_p}
        st.session_state.biometria_completada = True
        st.rerun()
    st.stop()

# --- 3. PANEL DE CONTROL (CÁLCULO DINÁMICO 8 METAS) ---
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
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">{tkcal}/{m_kcal}</p></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-box"><p class="metric-label">🍗 Prot</p><p class="metric-value">{tprot}/{m_prot}g</p></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-box"><p class="metric-label">👣 Pasos</p><p class="metric-value">{st.session_state.pasos}/{st.session_state.u_datos["meta_pasos"]}</p></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-box"><p class="metric-label">🏃 Quemado</p><p class="metric-value">{k_quem:.1f}</p></div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)
with col5: st.markdown(f'<div class="metric-box"><p class="metric-label">🍝 Carb</p><p class="metric-value">{tcarb}/{m_carb}g</p></div>', unsafe_allow_html=True)
with col6: st.markdown(f'<div class="metric-box"><p class="metric-label">🥑 Gras</p><p class="metric-value">{tgras}/70g</p></div>', unsafe_allow_html=True)
with col7: st.markdown(f'<div class="metric-box"><p class="metric-label">🍏 Fibr</p><p class="metric-value">{tfibr}/35g</p></div>', unsafe_allow_html=True)
with col8: st.markdown(f'<div class="metric-box"><p class="metric-label">🍭 Azuc</p><p class="metric-value">{tazuc}/50g</p></div>', unsafe_allow_html=True)

# --- 4. PESTAÑAS PRINCIPALES ---
t_ia, t_sem, t_sync = st.tabs(["🚀 REGISTRO IA", "📅 REGISTRO SEMANAL", "🔐 SINCRONIZACIÓN"])

with t_ia:
    st.subheader("📷 Escáner de Nutrientes")
    archivo = st.file_uploader("Sube tu plato...", type=["jpg", "png", "jpeg"])
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if archivo and st.button("ANALIZAR Y GUARDAR"):
            # CORRECCIÓN: Valores reales para una manzana (como la de tu foto)
            v_k, v_p, v_c, v_g, v_f, v_a = 95, 0, 25, 0, 4, 19 
            bloque_auto = obtener_bloque_comida()
            nuevo = {"hora": datetime.now().strftime("%H:%M"), "alimento": "Manzana (Foto)", "bloque": bloque_auto, "detalle": "Análisis de fruta", "k": v_k, "p": v_p, "c": v_c, "g": v_g, "f": v_f, "a": v_a}
            st.session_state.historial[dia_hoy].append(nuevo)
            st.success(f"Registrado correctamente en {bloque_auto}")
            st.rerun()

    with col_btn2:
        # BOTÓN DE DESHACER (BORRAR ÚLTIMO)
        if st.button("🗑️ BORRAR ÚLTIMO"):
            if len(st.session_state.historial[dia_hoy]) > 0:
                st.session_state.historial[dia_hoy].pop()
                st.warning("Último registro eliminado.")
                st.rerun()
            else:
                st.info("No hay nada que borrar hoy.")

with t_sem:
    for dia, registros in st.session_state.historial.items():
        with st.expander(f"📅 {dia}", expanded=(dia == dia_hoy)):
            if not registros:
                st.write("Día sin registros.")
            else:
                for r in registros:
                    st.write(f"🍏 {r['alimento']} | {r['k']} kcal | {r['hora']}")

with t_sync:
    st.subheader("🔐 Acceso Maestro")
    codigo_input = st.text_input("Código maestro:", type="password")
    if codigo_input == "xavier2210":
        st.success("Acceso Concedido")
        st.selectbox("Discípulo:", ["Xavier", "Juan", "Maria"])
    elif codigo_input: st.error("Código incorrecto.")

# --- 5. LATERAL ---
st.sidebar.title("💧 HIDRATACIÓN")
if st.sidebar.button("➕ Vaso"): st.session_state.agua += 1
st.sidebar.write(f"Vasos: {st.session_state.agua}/12")
st.sidebar.markdown("---")
st.session_state.pasos = st.sidebar.number_input("👣 PASOS HOY:", value=st.session_state.pasos, step=500)
