import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIG ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Error en Secrets. Revisa Streamlit Cloud.")
    st.stop()

# --- 2. ESTILOS ---
st.markdown("""
<style>
    .pizarra { background: #1a1a1a; border: 3px solid #59402a; border-radius: 12px; padding: 15px; color: white; font-family: monospace; margin: 10px 0; }
    .verde { color: #00FF41; font-weight: bold; }
    .macro-box { text-align: center; background: #262626; padding: 8px; border-radius: 8px; width: 22%; border: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
for k in ['kcal_t', 'p_t', 'c_t', 'g_t']:
    if k not in st.session_state: st.session_state[k] = 0.0

# --- 4. SIDEBAR (PERFIL XAVIER) ---
with st.sidebar:
    st.title("🦾 JARVIS OS")
    u_nom = st.text_input("Nombre:", "Xavier")
    u_pes = st.number_input("Peso (kg):", 63.0)
    u_alt = st.number_input("Altura (cm):", 170)
    u_eda = st.number_input("Edad:", 20)
    u_act = st.selectbox("Actividad:", ["Fútbol 2h (Portoviejo)", "Hipertrofia Glúteos/Legs"])
    meta_k = st.number_input("Meta Kcal Diaria:", 2500)
    
    prog = min(st.session_state.kcal_t / meta_k, 1.0)
    st.write(f"🔥 Progreso: {int(prog*100)}%")
    st.progress(prog)
    st.write(f"Consumido: {int(st.session_state.kcal_t)} kcal")
    
    if st.button("🔄 Resetear Día"):
        for k in ['kcal_t', 'p_t', 'c_t', 'g_t']: st.session_state[k] = 0.0
        st.rerun()

# --- 5. MAIN ---
st.title(f"📈 Dashboard: {u_nom}")
t1, t2 = st.tabs(["📊 MIS MACROS", "🍽️ REGISTRAR PLATO"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    
    df_p = pd.DataFrame({'M':['Proteína','Carbos','Grasas'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    st.plotly_chart(px.pie(df_p, values='G', names='M', hole=0.5, template="plotly_dark", 
                          color_discrete_sequence=['#00FF41','#FFC107','#2196F3']), use_container_width=True)

with t2:
    col_f, col_m = st.columns(2)
    res_c =
