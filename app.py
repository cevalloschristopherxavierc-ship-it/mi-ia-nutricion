import streamlit as st
import requests
import base64
import time
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# 1. SEGURIDAD
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error("⚠️ Error en Secrets.")
    st.stop()

# 2. ESTILOS DE LA PIZARRA Y DASHBOARD
st.markdown("""
<style>
    .pizarra-contenedor { display: flex; justify-content: center; margin: 20px 0; }
    .pizarra-fondo {
        background-color: #262626; border: 8px solid #59402a; border-radius: 15px;
        padding: 25px; width: 100%; max-width: 450px; color: white; font-family: monospace;
    }
    .pizarra-titulo { color: #00FF41; text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid #444; margin-bottom: 15px; }
    .pizarra-fila { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 18px; }
    .pizarra-valor { color: #00FF41; font-weight: bold; }
    .metric-card { background: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# 3. REGISTRO / LOGIN
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<h1 style='text-align: center;'>🦾 Jarvis Nutrición</h1>", unsafe_allow_html=True)
    with st.form("registro"):
        nombre = st.text_input("Ingresa tu nombre:")
        peso = st.number_input("Peso Actual (kg):", value=75.0)
        altura = st.number_input("Altura (cm):", value=170)
        enviar = st.form_submit_button("ENTRAR AL SISTEMA")
        if enviar and nombre:
            m_p = peso * 2
            imc = round(peso / ((altura/100)**2), 1)
            st.session_state.usuario = {"nombre": nombre, "peso": peso, "meta_p": m_p, "imc": imc}
            st.rerun()
    st.stop()

# 4. DASHBOARD DE PROGRESO (SIDEBAR Y GRÁFICAS)
u = st.session_state.usuario

with st.sidebar:
    st.title("👤 PERFIL")
    st.success(f"Hola, {u['nombre'].upper()}!")
    st.write(f"⚖️ Peso: {u['peso']}kg")
    st.write(f"📊 IMC: {u['imc']}")
    st.progress(0.8, text="Objetivo: 80%") # Simulación de barra de progreso
    if st.button("🚪 Salir"):
        st.session_state.clear()
        st.rerun()

# --- SECCIÓN DE GRÁFICAS (DASHBOARD) ---
st.title("📈 Tu Progreso")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="metric-card"><h3>78 kg</h3><p>Actual</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h3>75 kg</h3><p>Objetivo</p></div>', unsafe_allow_html=True)

# Gráfica de Calorías Semanal (Simulada)
st.subheader("🔥 Calorías Semanales")
data_cal = pd.DataFrame({
    'Día': ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB', 'DOM'],
    'Kcal': [2530, 2250, 2310, 2440, 2630, 2350, 2500]
})
fig_cal = px.bar(data_cal, x='Día', y='Kcal', color_discrete_sequence=['#FFC107'])
fig_cal.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
st.plotly_chart(fig_cal, use_container_width=True)

# Gráfica de Peso (Simulada)
st.subheader("⚖️ Evolución de Peso")
data_peso = pd.DataFrame({
    'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'],
    'Kg': [90, 87, 88, 85, 84, 86, 78]
})
fig_peso = px.area(data_peso, x='Mes', y='Kg', color_discrete_sequence=['#FFC107'])
fig_peso.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
st.plotly_chart(fig_peso, use_container_width=True)

st.divider()

# 5. ESCÁNER NUTRICIONAL
st.subheader("📸 Escanea tu plato")
foto = st.file_uploader("Sube una imagen...", type=["jpg", "png", "jpeg"])

if foto:
    img_64 = base64.b64encode(foto.read()).decode('utf-8')
    st.image(foto, use_container_width=True)
    if st.button("🔍 ANALIZAR"):
        with st.spinner("🤖 Jarvis analizando..."):
            payload = {
                "contents": [{"parts": [
                    {"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_64}}
                ]}]
            }
            try:
                r = requests.post(URL_AI, json=payload)
                res = r.json()['candidates'][0]['content']['parts'][0]['text'].split('|')
                
                # HTML de la Pizarra
                st.markdown(f"""
                <div class="pizarra-contenedor">
                    <div class="pizarra-fondo">
                        <div class="pizarra-titulo">{res[0].upper()}</div>
                        <div class="pizarra-fila"><span>🍗 PROTEÍNA</span><span class="pizarra-valor">{res[2]}</span></div>
                        <div class="pizarra-fila"><span>🥑 GRASAS</span><span class="pizarra-valor">{res[4]}</span></div>
                        <div class="pizarra-fila"><span>🍚 CARBOS</span><span class="pizarra-valor">{res[3]}</span></div>
                        <div class="pizarra-fila"><span>🔥 CALORÍAS</span><span class="pizarra-valor">{res[1]}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.error("Error al analizar.")
