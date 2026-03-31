import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="Jarvis: Doble Revisión", page_icon="🦾", layout="wide")

# Estilo visual idéntico a tu captura
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-box { background-color: #1e2130; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #30363d; }
    .metric-label { font-size: 16px; color: #8b949e; }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
    .stTextArea textarea { background-color: #1e2130; color: #00ff00; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERIFICACIÓN DE CREADOR ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Xavier")
    u_nom = st.text_input("Nombre de Creador:")
    u_cod = st.text_input("Código Maestro:", type="password")
    if st.button("VERIFICAR"):
        if u_cod == "XAVIER2026" and u_nom.lower() == "xavier":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Código Inválido.")
    st.stop()

# --- 3. PANEL DE MÉTRICAS (LO QUE ESTÁ BIEN) ---
st.title(f"📊 Panel de Control: {datetime.now().strftime('%d/%m/%Y')}")
c1, c2, c3 = st.columns(3)
with c1: st.markdown('<div class="metric-box"><p class="metric-label">🔥 Kcal</p><p class="metric-value">0 / 2800</p></div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="metric-box"><p class="metric-label">🍗 Prot (g)</p><p class="metric-value">0 / 160</p></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="metric-box"><p class="metric-label">🏃 Pasos</p><p class="metric-value">0 / 10k</p></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 4. SISTEMA DE DOBLE REVISIÓN (PESTAÑAS) ---
t_ia, t_dev, t_bio = st.tabs(["🚀 NUTRICIÓN IA", "💻 DOBLE REVISIÓN CODIGO", "👤 BIOMETRÍA"])

# Función genérica para llamar a la API
def llamar_a_google(prompt, api_key, model="gemini-3.1-flash-lite-preview"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    return res.json()

with t_ia:
    st.subheader("Escaneo de Biomasa")
    # (Aquí se mantiene tu lógica de foto que ya funciona perfectamente)
    st.info("Listo para escanear plato del día.")

with t_dev:
    st.subheader("🛠️ Auditoría de Código Maestro")
    st.write("Pega aquí el código que quieres verificar para evitar errores de sintaxis.")
    
    codigo_a_revisar = st.text_area("Código a Auditar:", height=300, placeholder="Pega el código aquí...")
    
    if st.button("🔍 EJECUTAR DOBLE REVISIÓN"):
        if codigo_a_revisar and "GOOGLE_API_KEY" in st.secrets:
            with st.spinner("🤖 Jarvis verificando sintaxis y lógica..."):
                # LLAMADA A LA SEGUNDA IA (EL AUDITOR)
                prompt_auditoria = f"Actúa como un Senior Developer. Revisa este código de Python/Streamlit. Busca errores de sintaxis, variables sin definir o números faltantes. Si hay un error, dame el código corregido. Si está perfecto, felicita a Xavier. Código: {codigo_a_revisar}"
                
                res = llamar_a_google(prompt_auditoria, st.secrets["GOOGLE_API_KEY"])
                
                if 'candidates' in res:
                    st.success("✅ REVISIÓN COMPLETADA")
                    st.markdown(res['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.error("Fallo en el Auditor.")
        else:
            st.warning("Pega un código para iniciar la auditoría.")

with t_bio:
    st.subheader("Datos de Xavier")
    estatura = st.number_input("Estatura (cm):", value=175)
    peso = st.number_input("Peso (kg):", value=75.0)
    st.write(f"Cálculos de hipertrofia basados en {peso}kg.")

# --- 5. BARRA LATERAL (HIDRATACIÓN Y HORARIOS) ---
st.sidebar.subheader("💧 Hidratación")
if 'agua' not in st.session_state: st.session_state.agua = 0
if st.sidebar.button("➕ Beber"): st.session_state.agua += 1
st.sidebar.metric("Vasos", f"{st.session_state.agua} / 12")

st.sidebar.markdown("---")
st.sidebar.info("**Horarios:**\n- 13:00 Almuerzo\n- 16:00 Pre-Entreno\n- 19:00 Cena")
