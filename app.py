import streamlit as st
import requests, base64, re, pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIG ---
st.set_page_config(page_title="Jarvis: Xavier", layout="wide", page_icon="🦾")
try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("🚨 Revisa Secrets.")
    st.stop()

# --- 2. SESIÓN ---
if 'u_nom' not in st.session_state:
    with st.form("reg"):
        nom = st.text_input("Usuario:", "Xavier")
        pes = st.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Objetivo:", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 ENTRAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.rerun()
    st.stop()

# --- 3. RUTINA ---
hoy = datetime.now()
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_h = dias[hoy.weekday()]
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
rut = {
    "Lunes": {"e": "🍗 Piernas/Glúteo", "c": "🍳 Huevos/Avena | 🍗 Pollo"},
    "Martes": {"e": "👕 Tren Superior", "c": "🥤 Batido | 🥩 Carne/Pasta"},
    "Miércoles": {"e": "🔙 Espalda/Bíceps", "c": "🍳 Claras | 🦃 Pavo/Arroz"},
    "Jueves": {"e": "🍗 Pierna (Hipertrofia)", "c": "🥣 Yogur | 🍗 Pollo"},
    "Viernes": {"e": "⚽ Fútbol", "c": "🍝 Pasta/Pollo | 🥤 Post-Entreno"},
    "Sábado": {"e": "💪 Torso", "c": "🥞 Pancakes | 🐟 Pescado"},
    "Domingo": {"e": "🛌 Descanso", "c": "🥗 Proteína limpia"}
}
m_k = 3200 if st.session_state.u_obj == "Fútbol" else 2750
m_p = st.session_state.u_pes * 2.2
if 'agua' not in st.session_state: st.session_state.agua = 0.0
if 'pasos' not in st.session_state: st.session_state.pasos = 0

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.info(f"🏋️ {rut[dia_h]['e']}")
    c1, c2 = st.columns(2)
    if c1.button("➕ 0.5L"): st.session_state.agua += 0.5; st.rerun()
    if c2.button("🧹 Reset"): st.session_state.agua = 0.0; st.rerun()
    st.write(f"💧 Agua: **{st.session_state.agua}L**")
    st.session_state.pasos = st.number_input("👣 Pasos:", 0, 50000, st.session_state.pasos, 500)
    st.divider()
    cod = st.text_input("🔐 Creador:", type="password")
    st.session_state.creador = (cod == "xavier2210")

# --- 5. DATA ---
p_act, k_act = 0.0, 0.0
df_h, df_a = pd.DataFrame(), pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', ini_s).execute()
    if res.data:
        df_a = pd.DataFrame(res.data)
        df_a['f'] = pd.to_datetime(df_a['created_at']).dt.date
        df_h = df_a[(df_a['usuario'] == st.session_state.u_nom) & (df_a['f'] == hoy.date())]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
except: pass

# --- 6. DASHBOARD ---
st.title("📊 Panel Xavier")
col1, col2, col3 = st.columns(3)
col1.metric("🔥 Kcal", f"{k_act:.0f}/{m_k}")
col2.metric("🍗 Prot", f"{p_act:.1f}/{m_p:.0f}g")
col3.metric("🏃 Quemado", f"{(st.session_state.pasos/1000)*38:.0f} kcal")

t1, t2, t3, t4 = st.tabs(["🍽️ REGISTRO", "📈 ANÁLISIS", "📅 DIARIO", "🕵️ CREADOR"])

with t1:
    ca, cb = st.columns(2)
    with ca:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    pay = {"contents": [{"parts": [{"text": "Nombre|Kcal|Prot"},{"inline_data": {"mime_type": "image/jpeg", "data": img}}]}]}
                    r = requests.post(URL_AI, json=pay, timeout=15).json()
                    pts = r['candidates'][0]['content']['parts'][0]['text'].strip().split('|')
                    if len(pts) >= 3:
                        kv, pv = float(re.findall(r"\d+", pts[1])[0]), float(re.findall(r"\d+", pts[2])[0])
                        supabase.table('registros_comida').insert({"usuario": st.session_state.u_nom, "comida": pts[0], "kcal": kv, "proteina": pv, "semana": ini_s}).execute()
                        st.rerun()
                except: st.error("Error IA.")
    with cb:
        st.subheader("✍️ Manual")
        with st.form("m_en"):
            cm = st.text_input("Comida")
            pm, km = st.number_input("Prot (g)", 0.0), st.number_input("Kcal", 0.0)
            if st.form_submit_button("💾"):
                supabase.table('registros_comida').insert({"usuario": st.session_state.u_nom, "comida": cm, "kcal": km, "proteina": pm, "semana": ini_s}).execute()
                st.rerun()

with t2:
    if k_act > 0: st.plotly_chart(px.pie(values=[p_act*4, k_act*0.5, k_act*0.25], names=['Prot', 'Carb', 'Gras'], hole=0.5, template="plotly_dark"))

with t3:
    st.subheader("📝 Diario y Horario")
    st.dataframe(df_h[['comida', 'kcal', 'proteina']], use_container_width=True)
    st.table(pd.DataFrame([{"Día": d, "Entreno": rut[d]['e'], "Comida": rut[d]['c']} for d in dias]))

with t4:
    if st.session_state.get('creador', False):
        st.subheader("🕵️ Panel Creador")
        if not df_a.empty:
            sel = st.selectbox("Usuario:", df_a['usuario'].unique())
            st.dataframe(df_a[df_a['usuario'] == sel], use_container_width=True)
    else: st.warning("🔒 Ingresa 'xavier2210' en el Sidebar.")
