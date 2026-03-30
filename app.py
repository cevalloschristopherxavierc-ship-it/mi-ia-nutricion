import streamlit as st
import requests, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from supabase import create_client, Client

# --- 1. ADN XAVIER (63KG - DETALLES BLINDADOS) ---
st.set_page_config(page_title="Jarvis OS | Xavier", layout="wide", page_icon="🦾")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stProgress > div > div > div > div { background-color: #4facfe; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- 2. CONFIGURACIÓN DE MISIÓN ---
if 'u_nom' not in st.session_state:
    st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = "Xavier", 63.0, "Fútbol"
    st.session_state.h2o = 0.0

meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2800.0
meta_p = 138.6 # Tu meta de proteína crítica para 63kg
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 3. SIDEBAR (HIDRATACIÓN 3.5L Y CREADOR) ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación (Meta 3.5L)")
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Nivel Actual: **{st.session_state.h2o:.1f}L**")
    if st.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if st.button("🧹 Reset"): st.session_state.h2o = 0.0; st.rerun()
    st.divider()
    pasos = st.number_input("👣 Pasos hoy:", 0, 50000, 0, 500)
    st.metric("Gasto por Pasos", f"{(pasos/1000)*40:.0f} Kcal")
    if st.text_input("🔐 Acceso Creador:", type="password") == "xavier2210":
        st.session_state.creador = True

# --- 4. DATA SYNC ---
k_act, p_act = 0.0, 0.0
hoy_str = datetime.now().strftime('%Y-%m-%d')
try:
    res = supabase.table('registros_comida').select('*').eq('usuario', "Xavier").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['f'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        df_h = df[df['f'] == hoy_str]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
except: pass

# --- 5. DASHBOARD CENTRAL ---
st.header("📊 Centro de Mando")
m1, m2 = st.columns(2)
m1.metric("🔥 Calorías", f"{k_act:.0f}/{meta_k:.0f}")
m2.metric("🍗 Proteína", f"{p_act:.1f}/{meta_p:.1f}g")

tabs = st.tabs(["🍽️ REGISTRO RÁPIDO", "💪 ANÁLISIS", "📅 HISTORIAL"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🤖 Buscador de Macros (Texto)")
        st.write("Escribe tu comida para saltar el error de la cámara.")
        txt_comida = st.text_input("Ej: 2 pechugas de pollo y ensalada")
        if st.button("🔍 CALCULAR") and txt_comida:
            with st.spinner("🤖 Jarvis calculando..."):
                try:
                    key = st.secrets["GEMINI_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={key}"
                    payload = {"contents":[{"parts":[{"text": f"Calcula Kcal y Proteína para: {txt_comida}. Responde solo: Comida, Kcal, Prot"}]}]}
                    r = requests.post(url, json=payload, timeout=20)
                    if r.status_code == 200:
                        txt = r.json()['candidates'][0]['content']['parts'][0]['text']
                        nums = re.findall(r"\d+", txt)
                        if len(nums) >= 2:
                            supabase.table('registros_comida').insert({"usuario":"Xavier","comida":txt_comida,"kcal":float(nums[0]),"proteina":float(nums[1]),"semana":hoy_str}).execute()
                            st.success(f"✅ Registrado: {nums[0]} Kcal y {nums[1]}g Prot")
                            st.rerun()
                except: st.error("Fallo de red. Usa el manual.")

    with c2:
        st.subheader("✍️ Registro Manual")
        with st.form("f_man", clear_on_submit=True):
            n = st.text_input("Nombre Comida")
            k = st.number_input("Calorías", 0.0)
            p = st.number_input("Proteína (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":"Xavier","comida":n,"kcal":k,"proteina":p,"semana":hoy_str}).execute()
                st.rerun()

with tabs[1]:
    if k_act > 0:
        fig = go.Figure(go.Scatterpolar(r=[p_act/meta_p, k_act/meta_k, 0.8, 0.7], theta=['Prot', 'Kcal', 'Carb', 'Grasa'], fill='toself', line_color='#4facfe'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
