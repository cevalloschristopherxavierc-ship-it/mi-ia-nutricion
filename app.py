import streamlit as st
import requests, base64, re, pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis: Maestro Xavier", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("🚨 Error de Secrets.")
    st.stop()

# --- 2. SESIÓN ---
if 'u_nom' not in st.session_state:
    with st.form("reg"):
        st.title("🦾 Activación Jarvis")
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso Actual (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ENTRAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.session_state.h2o = 0.0
            st.rerun()
    st.stop()

# --- 3. METAS DINÁMICAS ---
hoy = datetime.now()
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# Cálculo de Macros para Xavier (63kg)
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 # ~139g Proteína
meta_g = (meta_k * 0.25) / 9          # ~89g Grasa (25% kcal)
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4 # ~460g Carb (Combustible)

# --- 4. SIDEBAR (Agua con Barra de Llenado y Pasos) ---
with st.sidebar:
    st.title(f"👑 Maestro: {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación")
    # Barra de llenado de agua
    progreso_agua = min(st.session_state.h2o / 3.5, 1.0)
    st.progress(progreso_agua)
    st.write(f"Llenado: **{st.session_state.h2o:.1f}L** / 3.5L")
    
    c1, c2 = st.columns(2)
    if c1.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if c2.button("🧹 Reset"): st.session_state.h2o = 0.0; st.rerun()
    
    st.divider()
    st.subheader("👣 Pasos")
    steps = st.number_input("Pasos hoy:", 0, 50000, 0, 500)
    k_steps = (steps / 1000) * 38
    st.metric("Gasto Extra", f"{k_steps:.0f} Kcal")
    st.divider()
    cod = st.sidebar.text_input("🔐 Creador:", type="password")
    st.session_state.creador = (cod == "xavier2210")

# --- 5. DATA ---
k_act, p_act, g_act, c_act = 0.0, 0.0, 0.0, 0.0
df_h, df_a = pd.DataFrame(), pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', ini_s).execute()
    if res.data:
        df_a = pd.DataFrame(res.data)
        df_a['f'] = pd.to_datetime(df_a['created_at']).dt.date
        df_h = df_a[(df_a['usuario'] == st.session_state.u_nom) & (df_a['f'] == hoy.date())]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
        # Distribución estimada de lo consumido
        g_act = (k_act * 0.25) / 9 if k_act > 0 else 0.0
        c_act = (k_act * 0.55) / 4 if k_act > 0 else 0.0
except: pass

# --- 6. UI ---
st.title("📊 Panel Élite Jarvis")
# Barra de llenado de Calorías principal
st.progress(min(k_act / meta_k, 1.0))

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔥 Kcal", f"{k_act:.0f}/{meta_k:.0f}")
col2.metric("🍗 Prot", f"{p_act:.1f}/{meta_p:.0f}g")
col3.metric("🥑 Grasa", f"{g_act:.1f}/{meta_g:.0f}g")
col4.metric("🍚 Carb", f"{c_act:.0f}/{meta_c:.0f}g") # META AÑADIDA AQUÍ

t1, t2, t3, t4 = st.tabs(["🍽️ REGISTRO", "💪 ANÁLISIS", "📝 DIARIO", "🕵️ CREADOR"])

with t1:
    ca, cb = st.columns(2)
    with ca:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    pay = {"contents":[{"parts":[{"text":"Nombre|Kcal|Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pay, timeout=15).json()
                    pts = r['candidates'][0]['content']['parts'][0]['text'].strip().split('|')
                    if len(pts) >= 3:
                        kv, pv = float(re.findall(r"\d+", pts[1])[0]), float(re.findall(r"\d+", pts[2])[0])
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":pts[0], "kcal":kv, "proteina":pv, "semana":ini_s}).execute()
                        st.rerun()
                except: st.error("Error IA. Intenta de nuevo.")
    with cb:
        st.subheader("✍️ Manual")
        with st.form("m_en"):
            cm = st.text_input("Comida")
            pm, km = st.number_input("Prot", 0.0), st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":cm, "kcal":km, "proteina":pm, "semana":ini_s}).execute()
                st.rerun()

with t2:
    st.subheader("💪 Músculo Animado")
    if p_act > 0:
        fig = px.bar_polar(r=[p_act/meta_p, k_act/meta_k, c_act/meta_c, g_act/meta_g], 
                           theta=['Prot', 'Kcal', 'Carb', 'Grasa'],
                           color=['Prot', 'Kcal', 'Carb', 'Grasa'], template="plotly_dark",
                           color_discrete_sequence=['#FF4B4B', '#48FF48', '#3498DB', '#F1C40F'])
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Sin datos suficientes.")

with t3:
    st.subheader("📝 Historial de Hoy")
    if not df_h.empty:
        st.table(df_h[['comida', 'kcal', 'proteina']])
    else: st.write("Aún no hay registros.")

with t4:
    if st.session_state.get('creador', False):
        st.subheader("🕵️ Supervisor Élite")
        if not df_a.empty:
            sel = st.selectbox("Usuario:", df_a['usuario'].unique())
            st.dataframe(df_a[df_a['usuario'] == sel], use_container_width=True)
    else: st.warning("🔒 Código en Sidebar.")
