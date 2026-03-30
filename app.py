import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PERFIL DE USUARIO ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Activación de Núcleo Jarvis")
    with st.form("perfil_inicial"):
        st.write("Configura tus datos para el cálculo de macros:")
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Tu nombre?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 INICIAR SISTEMA"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. LÓGICA DE TIEMPO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy_nombre = dias_semana[hoy.weekday()]

# --- 4. SIDEBAR (METAS DE MACROS) ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    
    # METAS CALCULADAS (CIENCIA DEPORTIVA)
    meta_k = 3200.0 if "Fútbol" in modo else 2700.0
    meta_p = st.session_state.u_pes * 2.2 # 2.2g/kg
    meta_g = st.session_state.u_pes * 1.0 # 1g/kg
    meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4 # Resto en carbos
    
    agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if "Fútbol" in modo else 0.6)
    
    st.success(f"📅 {dia_hoy_nombre}")
    st.info(f"💧 Agua: **{agua:.2f}L**")
    st.info(f"🍗 Prot: **{meta_p:.0f}g** | 🍚 Carb: **{meta_c:.0f}g** | 🥑 Gras: **{meta_g:.0f}g**")
    
    if st.button("🔄 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Panel Nutricional: {st.session_state.u_nom}")
t1, t2 = st.tabs(["📈 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    try:
        res_h = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        if not df_h.empty:
            df_h['fecha_dt'] = pd.to_datetime(df_h['created_at']).dt.date
            h_data = df_h[df_h['fecha_dt'] == hoy.date()]
            
            k_h, p_h, c_h, g_h = h_data['kcal'].sum(), h_data['proteina'].sum(), h_data['carbos'].sum(), h_data['grasas'].sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calorías", f"{k_h:.0f}", f"{meta_k:.0f}")
            c2.metric("Proteína", f"{p_h:.1f}g", f"{meta_p:.0f}g")
            c3.metric("Carbos", f"{c_h:.1f}g", f"{meta_c:.0f}g")
            c4.metric("Grasas", f"{g_h:.1f}g", f"{meta_g:.0f}g")
            st.progress(min(float(k_h/meta_k), 1.0))
            
            if k_h > 0:
                fig = px.pie(values=[p_h*4, c_h*4, g_h*9], names=['Proteína', 'Carbos', 'Grasas'], 
                             hole=0.4, title="Distribución de hoy", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Sin registros para este {dia_hoy_nombre}.")
    except Exception:
        st.warning("No se pudo cargar el historial diario.")

with t2:
    col_a, col_b = st.columns(2)
    res_f = None
    with col_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Subir plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    p = "Responde estrictamente: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":p},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw =
