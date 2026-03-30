import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Jarvis Nutrición Pro", layout="wide")

try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Error en Secrets. Revisa tu configuración en Streamlit Cloud.")
    st.stop()

# --- 2. ESTILOS (PIZARRA XAVIER) ---
st.markdown("""
<style>
    .pizarra { background-color: #1a1a1a; border: 4px solid #59402a; border-radius: 15px; padding: 20px; color: white; font-family: monospace; }
    .titulo-p { color: #00FF41; text-align: center; font-weight: bold; font-size: 22px; border-bottom: 1px solid #333; margin-bottom: 15px; }
    .verde { color: #00FF41; font-weight: bold; }
    .card-comida { background: #262626; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 6px solid #00FF41; }
</style>
""", unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE MEMORIA ---
if 'kcal_total' not in st.session_state: st.session_state.kcal_total = 0.0

# --- 4. SIDEBAR: PERFIL COMPLETO (TUS PREGUNTAS) ---
with st.sidebar:
    st.title("🦾 PERFIL DE ATLETA")
    st.success("AGENTE: XAVIER")
    
    # Aquí recuperamos tus datos de cm y kg
    st.subheader("📊 Datos Físicos")
    peso = st.number_input("Peso Actual (kg):", value=63.0, step=0.1)
    altura = st.number_input("Altura (cm):", value=170)
    meta_kcal = st.number_input("Meta Diaria (kcal):", value=2500)
    
    st.divider()
    
    # Barra de progreso dinámica
    progreso = min(st.session_state.kcal_total / meta_kcal, 1.0)
    st.write(f"🔥 Progreso: {int(progreso * 100)}%")
    st.progress(progreso)
    st.write(f"Consumido: {int(st.session_state.kcal_total)} / {int(meta_kcal)} kcal")
    
    if st.button("🔄 Reiniciar Contador"):
        st.session_state.kcal_total = 0.0
        st.rerun()

# --- 5. PANEL PRINCIPAL ---
st.title("📈 Dashboard Nutricional - Portoviejo")
tab_stats, tab_reg = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with tab_stats:
    c1, c2 = st.columns(2)
    with c1:
        # Gráfica de Calorías Semanales
        df_c = pd.DataFrame({'Día': ['L','M','X','J','V','S','D'], 'Kcal': [2530, 2250, 2310, 2440, 2630, 2350, 2500]})
        st.plotly_chart(px.bar(df_c, x='Día', y='Kcal', title="Calorías Semanales", template="plotly_dark", color_discrete_sequence=['#FFC107']), use_container_width=True)
    with c2:
        # Historial de Peso (Recuerda tus 63kg)
        df_p = pd.DataFrame({'Mes': ['Ene','Feb','Mar','Abr','May','Jun','Jul'], 'Kg': [60,61,62,63,63,64,63]})
