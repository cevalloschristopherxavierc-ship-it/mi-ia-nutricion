import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. SISTEMA ---
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
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        st.error("🚨 Error de Base de Datos.")
        st.stop()

supabase = init_connection()

# --- 2. PERFIL ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Activación Jarvis")
    with st.form("p_ini"):
        c1, c2, c3 = st.columns(3)
        nom = c1.text_input("ID:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = c3.selectbox("Misión:", ["Fútbol", "Hipertrofia", "Definición"])
        if st.form_submit_button("🚀 ENTRAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.session_state.h2o = 0.0
            st.rerun()
    st.stop()

# --- 3. METAS (63kg) ---
hoy = datetime.now()
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación")
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Llenado: **{st.session_state.h2o:.1f}L** / 3.5L")
    ca, cb = st.columns(2)
    if ca.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if cb.button("🧹 Reset"): st.session_state.h2o = 0.0; st.rerun()
    st.divider()
    pas = st.number_input("👣 Pasos:", 0, 50000, 0, 500)
    st.metric("Gasto", f"{(pas/1000)*38:.0f} Kcal")
    st.divider()
    if st.text_input("🔐 Creador:", type="password") == "xavier2210":
        st.session_state.creador = True

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
        g_act, c_act = (k_act * 0.25) / 9, (k_act * 0.50) / 4
except: pass

# --- 6. DASHBOARD ---
st.header("📊 Centro de Mando")
st.progress(min(k_act / meta_k, 1.0))
m1, m2, m3, m4 = st.columns(4)
m1.metric("🔥 Kcal", f"{k_act:.0f}/{meta_k:.0f}")
m2.metric("🍗 Prot", f"{p_act:.1f}/{meta_p:.1f}g")
m3.metric("🥑 Grasa", f"{g_act:.1f}/{meta_g:.1f}g")
m4.metric("🍚 Carb", f"{c_act:.0f}/{meta_c:.0f}g")

tabs = st.tabs(["🍽️ REGISTRO", "💪 ANÁLISIS", "📅 HISTORIAL", "🕵️ CREADOR"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📸 Escáner IA")
        up = st.file_uploader("Subir foto", type=["jpg","png","jpeg"])
        if up and st.button("🔍 ANALIZAR PLATO"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    b64 = base64.b64encode(up.read()).decode()
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={st.secrets['GEMINI_API_KEY']}"
                    prompt = "Analiza. Devuelve SOLO: Nombre, Calorias, Proteina. Ejemplo: Arroz con Pollo, 500, 35"
                    pay = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":b64}}]}]}
                    r = requests.post(url, json=pay, timeout=25).json()
                    txt = r['candidates'][0]['content']['parts'][0]['text']
                    
                    # Limpieza interna para que no falle el sensor
                    txt_clean = txt.replace("\n", "").replace("*", "").strip()
                    parts = txt_clean.split(",")
                    
                    if len(parts) >= 3:
                        nom_ia = parts[0].strip()
                        kcal_ia = float(re.findall(r"\d+", parts[1])[0])
                        prot_ia = float(re.findall(r"\d+", parts[2])[0])
                        supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":nom_ia[:25], "kcal":kcal_ia, "proteina":prot_ia, "semana":ini_s}).execute()
                        st.rerun()
                except: st.error("⚠️ Sensor IA saturado. Intente otra vez o use Manual.")

    with c2:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_f", clear_on_submit=True):
            m_nom = st.text_input("Comida")
            m_kcal = st.number_input("Kcal", 0.0, 4000.0)
            m_prot = st.number_input("Proteína (g)", 0.0, 300.0)
            if st.form_submit_button("💾 GUARDAR"):
                if m_nom:
                    supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":m_nom, "kcal":m_kcal, "proteina":m_prot, "semana":ini_s}).execute()
                    st.success("¡Guardado!")
                    st.rerun()
                else: st.warning("Escriba el nombre.")

with tabs[1]:
    if k_act > 0:
        fig = go.Figure(go.Scatterpolar(r=[p_act/meta_p, k_act/meta_k, c_act/meta_c, g_act/meta_g], theta=['Prot', 'Kcal', 'Carb', 'Grasa'], fill='toself', line_color='#4facfe'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    if not df_h.empty: st.table(df_h[['comida', 'kcal', 'proteina']])

with tabs[3]:
    if st.session_state.get('creador', False):
        if not df_a.empty:
            sel = st.selectbox("Usuario:", df_a['usuario'].unique())
            st.dataframe(df_a[df_a['usuario'] == sel], use_container_width=True)
