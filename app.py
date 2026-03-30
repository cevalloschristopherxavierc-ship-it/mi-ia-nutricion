import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN DE SISTEMA ---
st.set_page_config(page_title="Jarvis OS | Xavier", layout="wide", page_icon="🦾")

# CSS Profesional (Corregido para evitar TypeError)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stProgress > div > div > div > div { background-color: #4facfe; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        st.error("🚨 Error de enlace con la base de datos.")
        st.stop()

supabase = init_connection()

# --- 2. GESTIÓN DE SESIÓN ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Inicializando Protocolo Jarvis")
    with st.form("perfil_maestro"):
        c1, c2, c3 = st.columns(3)
        nom = c1.text_input("Identificación:", "Xavier")
        pes = c2.number_input("Peso Base (kg):", 30.0, 150.0, 63.0)
        obj = c3.selectbox("Misión:", ["Fútbol", "Hipertrofia", "Definición"])
        if st.form_submit_button("🚀 ACTIVAR SISTEMA"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.session_state.h2o = 0.0
            st.rerun()
    st.stop()

# --- 3. METAS DE ALTO RENDIMIENTO (63kg) ---
hoy = datetime.now()
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. SIDEBAR (Agua con barra de llenado y pasos) ---
with st.sidebar:
    st.title(f"👑 Maestro {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación Diaria")
    p_agua = min(st.session_state.h2o / 3.5, 1.0)
    st.progress(p_agua)
    st.write(f"Consumo: **{st.session_state.h2o:.1f}L** / 3.5L")
    ch1, ch2 = st.columns(2)
    if ch1.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if ch2.button("🧹 Limpiar"): st.session_state.h2o = 0.0; st.rerun()
    
    st.divider()
    st.subheader("👣 Sensor de Pasos")
    pasos = st.number_input("Pasos hoy:", 0, 50000, 0, 500)
    st.metric("Gasto Estimado", f"{(pasos/1000)*38:.0f} Kcal")
    
    st.divider()
    key = st.text_input("🔐 Acceso Creador:", type="password")
    st.session_state.creador = (key == "xavier2210")

# --- 5. SINCRONIZACIÓN DE DATOS ---
k_act, p_act, g_act, c_act = 0.0, 0.0, 0.0, 0.0
df_hoy, df_all = pd.DataFrame(), pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', ini_s).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.date
        df_hoy = df_all[(df_all['usuario'] == st.session_state.u_nom) & (df_all['fecha'] == hoy.date())]
        if not df_hoy.empty:
            k_act, p_act = df_hoy['kcal'].sum(), df_hoy['proteina'].sum()
            g_act = (k_act * 0.25) / 9
            c_act = (k_act * 0.50) / 4
except: pass

# --- 6. DASHBOARD PRINCIPAL ---
st.header("📊 Centro de Mando Nutricional")
st.progress(min(k_act / meta_k, 1.0))

m1, m2, m3, m4 = st.columns(4)
m1.metric("🔥 Kcal", f"{k_act:.0f}", f"Meta: {meta_k:.0f}")
m2.metric("🍗 Prot", f"{p_act:.1f}g", f"Meta: {meta_p:.0f}g")
m3.metric("🥑 Grasa", f"{g_act:.1f}g", f"Meta: {meta_g:.0f}g")
m4.metric("🍚 Carb", f"{c_act:.0f}g", f"Meta: {meta_c:.0f}g")

tabs = st.tabs(["🍽️ REGISTRO", "💪 BIO-ANÁLISIS", "📅 HISTORIAL", "🕵️ CREADOR"])

with tabs[0]:
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("📸 Escáner IA")
        up = st.file_uploader("Captura de plato", type=["jpg","png","jpeg"])
        if up and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img = base64.b64encode(up.read()).decode()
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={st.secrets['GEMINI_API_KEY']}"
                    pay = {"contents":[{"parts":[{"text":"Nombre|Kcal|Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(url, json=pay, timeout=15).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text']
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", raw)
                    if len(nums) >= 2:
                        kv, pv = float(nums[-2]), float(nums[-1])
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":raw.split('|')[0][:20], "kcal":kv, "proteina":pv, "semana":ini_s}).execute()
                        st.rerun()
                except: st.error("❌ Error de lectura. Use entrada manual.")
    with r2:
        st.subheader("✍️ Entrada Manual")
        with st.form("m_form"):
            f_n = st.text_input("Descripción")
            f_k, f_p = st.number_input("Kcal", 0.0), st.number_input("Prot (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":f_n, "kcal":f_k, "proteina":f_p, "semana":ini_s}).execute()
                st.rerun()

with tabs[1]:
    st.subheader("💪 Simulación Bio-Muscular")
    if k_act > 0:
        fig = go.Figure(go.Scatterpolar(
            r=[p_act/meta_p, k_act/meta_k, c_act/meta_c, g_act/meta_g],
            theta=['Músculo', 'Energía', 'Carbo-Fuel', 'Hormonas'],
            fill='toself', line_color='#4facfe'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Esperando registros para iniciar análisis.")

with tabs[2]:
    if not df_hoy.empty:
        st.table(df_hoy[['comida', 'kcal', 'proteina']])
    else: st.write("No hay datos hoy.")

with tabs[3]:
    if st.session_state.get('creador', False):
        st.subheader("🕵️ Panel de Supervisión")
        if not df_all.empty:
            sel = st.selectbox("Sujeto:", df_all['usuario'].unique())
            st.dataframe(df_all[df_all['usuario'] == sel], use_container_width=True)
    else: st.warning("🔒 Privilegios de Creador requeridos.")
