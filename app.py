import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. NÚCLEO Y ESTILO (RESTAURADO) ---
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
        st.error("🚨 Error de enlace con Base de Datos.")
        st.stop()

supabase = init_connection()

# --- 2. SESIÓN Y PERFIL (63KG) ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Activación Protocolo Jarvis")
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

# --- 3. METAS DE RENDIMIENTO (RESTAURADAS) ---
hoy = datetime.now()
ini_s = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
# Cálculo exacto para Xavier
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 # 138.6g para 63kg
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. SIDEBAR (AGUA, PASOS Y CREADOR) ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación")
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Nivel: **{st.session_state.h2o:.1f}L** / 3.5L")
    ca, cb = st.columns(2)
    if ca.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if cb.button("🧹 Reset"): st.session_state.h2o = 0.0; st.rerun()
    st.divider()
    pas = st.number_input("👣 Pasos hoy:", 0, 50000, 0, 500)
    st.metric("Gasto Estimado", f"{(pas/1000)*38:.0f} Kcal")
    st.divider()
    if st.text_input("🔐 Acceso Creador:", type="password") == "xavier2210":
        st.session_state.creador = True

# --- 5. SINCRONIZACIÓN DE DATOS ---
k_act, p_act, g_act, c_act = 0.0, 0.0, 0.0, 0.0
df_h = pd.DataFrame()
try:
    res = supabase.table('registros_comida').select('*').eq('semana', ini_s).execute()
    if res.data:
        df_a = pd.DataFrame(res.data)
        df_a['f'] = pd.to_datetime(df_a['created_at']).dt.date
        df_h = df_a[(df_a['usuario'] == st.session_state.u_nom) & (df_a['f'] == hoy.date())]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
        g_act, c_act = (k_act * 0.25) / 9, (k_act * 0.50) / 4
except: pass

# --- 6. DASHBOARD PRINCIPAL ---
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
        up = st.file_uploader("Foto", type=["jpg","png","jpeg"])
        if up and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_b64 = base64.b64encode(up.read()).decode()
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={st.secrets['GEMINI_API_KEY']}"
                    payload = {"contents":[{"parts":[{"text":"Nombre, Kcal, Prot. Ejemplo: Manzana, 95, 0.5"},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(url, json=payload, timeout=20)
                    if r.status_code == 200:
                        res_txt = r.json()['candidates'][0]['content']['parts'][0]['text']
                        nums = re.findall(r"\d+\.?\d*", res_txt)
                        if len(nums) >= 2:
                            vals = [float(n) for n in nums]
                            nom_v = res_txt.split(',')[0].strip()[:20]
                            supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":nom_v, "kcal":max(vals), "proteina":min(vals), "semana":ini_s}).execute()
                            st.rerun()
                except: st.error("⚠️ Error de conexión.")

    with c2:
        st.subheader("✍️ Registro Manual")
        with st.form("f_man", clear_on_submit=True):
            in_n = st.text_input("Comida")
            in_k = st.number_input("Kcal", 0.0)
            in_p = st.number_input("Prot (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if in_n:
                    supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom, "comida":in_n, "kcal":in_k, "proteina":in_p, "semana":ini_s}).execute()
                    st.rerun()

with tabs[1]:
    if k_act > 0:
        fig = go.Figure(go.Scatterpolar(r=[p_act/meta_p, k_act/meta_k, c_act/meta_c, g_act/meta_g], theta=['Prot', 'Kcal', 'Carb', 'Grasa'], fill='toself', line_color='#4facfe'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    if not df_h.empty: st.table(df_h[['comida', 'kcal', 'proteina']])

with tabs[3]:
    if st.session_state.get('creador', False):
        try:
            res_admin = supabase.table('registros_comida').select('*').execute()
            if res_admin.data: st.dataframe(pd.DataFrame(res_admin.data))
        except: st.write("Aún no hay datos globales.")
