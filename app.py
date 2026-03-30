import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. NÚCLEO Y ESTILO (DETALLES JARVIS) ---
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

# --- 2. PERFIL XAVIER (63KG - PORTOVIEJO) ---
if 'u_nom' not in st.session_state:
    st.title("🦾 Activación Protocolo Jarvis")
    with st.form("p_ini"):
        c1, c2, c3 = st.columns(3)
        nom = c1.text_input("ID:", "Xavier")
        pes = c2.number_input("Peso (kg):", 30.0, 150.0, 63.0)
        obj = st.selectbox("Misión Hoy:", ["Fútbol", "Hipertrofia", "Descanso"])
        if st.form_submit_button("🚀 ENTRAR"):
            st.session_state.u_nom, st.session_state.u_pes, st.session_state.u_obj = nom.strip(), pes, obj
            st.session_state.h2o = 0.0
            st.rerun()
    st.stop()

# --- 3. METAS DE ALTO RENDIMIENTO (DETALLE CLAVE) ---
# Si juegas fútbol, necesitas más energía
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2800.0
meta_p = st.session_state.u_pes * 2.2 # Los 138.6g de proteína exactos
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. SIDEBAR (AGUA, PASOS Y CREADOR) ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación (Meta 3.5L)")
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Nivel Actual: **{st.session_state.h2o:.1f}L**")
    col_a, col_b = st.columns(2)
    if col_a.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if col_b.button("🧹 Reset"): st.session_state.h2o = 0.0; st.rerun()
    st.divider()
    pasos = st.number_input("👣 Pasos hoy:", 0, 50000, 0, 500)
    # Cálculo de quema calórica por pasos para Xavier
    gasto_pasos = (pasos/1000) * 40 
    st.metric("Gasto por Pasos", f"{gasto_pasos:.0f} Kcal")
    st.divider()
    # ACCESO CREADOR
    if st.text_input("🔐 Acceso Creador:", type="password") == "xavier2210":
        st.session_state.creador = True

# --- 5. SINCRONIZACIÓN Y CÁLCULOS ---
k_act, p_act, g_act, c_act = 0.0, 0.0, 0.0, 0.0
df_hoy = pd.DataFrame()
try:
    hoy_str = datetime.now().strftime('%Y-%m-%d')
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).execute()
    if res.data:
        df_all = pd.DataFrame(res.data)
        df_all['fecha'] = pd.to_datetime(df_all['created_at']).dt.strftime('%Y-%m-%d')
        df_hoy = df_all[df_all['fecha'] == hoy_str]
        k_act = df_hoy['kcal'].sum()
        p_act = df_hoy['proteina'].sum()
        # Estimación simple de macros si no se registran
        g_act, c_act = (k_act * 0.25) / 9, (k_act * 0.45) / 4
except: pass

# --- 6. DASHBOARD CENTRAL (RADAR Y MÉTRICAS) ---
st.header("📊 Centro de Mando Jarvis")
st.progress(min(k_act / meta_k, 1.0) if meta_k > 0 else 0)
m1, m2, m3, m4 = st.columns(4)
m1.metric("🔥 Calorías", f"{k_act:.0f}/{meta_k:.0f}")
m2.metric("🍗 Proteína", f"{p_act:.1f}/{meta_p:.1f}g")
m3.metric("🥑 Grasa (Est.)", f"{g_act:.1f}g")
m4.metric("🍚 Carb (Est.)", f"{c_act:.0f}g")

tabs = st.tabs(["🍽️ REGISTRO", "💪 ANÁLISIS", "📅 HISTORIAL", "🕵️ CREADOR"])

with tabs[0]:
    c_ia, c_man = st.columns(2)
    with c_ia:
        st.subheader("📸 Escáner IA (V1-PRO)")
        up = st.file_uploader("Foto", type=["jpg","png","jpeg"])
        if up and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis forzando conexión..."):
                try:
                    img_64 = base64.b64encode(up.read()).decode()
                    key = st.secrets["GEMINI_API_KEY"]
                    # URL V1BETA CON MODELO PRO (Para evitar el 404 del Flash)
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={key}"
                    payload = {"contents":[{"parts":[{"text":"Responde solo: NombreComida, Kcal, Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img_64}}]}]}
                    r = requests.post(url, json=payload, timeout=30)
                    if r.status_code == 200:
                        txt = r.json()['candidates'][0]['content']['parts'][0]['text']
                        nums = re.findall(r"\d+", txt)
                        if len(nums) >= 2:
                            supabase.table('registros_comida').insert({
                                "usuario": st.session_state.u_nom, "comida": "IA_Scan",
                                "kcal": float(nums[0]), "proteina": float(nums[1]),
                                "semana": hoy_str
                            }).execute()
                            st.rerun()
                    else: st.error(f"Error {r.status_code}: Google no encuentra el modelo.")
                except: st.error("Sin respuesta del servidor.")

    with c_man:
        st.subheader("✍️ Registro Manual")
        with st.form("f_man", clear_on_submit=True):
            n = st.text_input("Comida")
            k = st.number_input("Kcal", 0.0)
            p = st.number_input("Prot", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n:
                    supabase.table('registros_comida').insert({"usuario":st.session_state.u_nom,"comida":n,"kcal":k,"proteina":p,"semana":hoy_str}).execute()
                    st.rerun()

with tabs[1]:
    if k_act > 0:
        st.subheader("🎯 Radar de Macros")
        fig = go.Figure(go.Scatterpolar(
            r=[p_act/meta_p if meta_p > 0 else 0, k_act/meta_k if meta_k > 0 else 0, 0.8, 0.7],
            theta=['Proteína', 'Calorías', 'Carbohidratos', 'Grasas'], fill='toself', line_color='#4facfe'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    if not df_hoy.empty: st.table(df_hoy[['comida', 'kcal', 'proteina']])

with tabs[3]:
    if st.session_state.get('creador', False):
        st.subheader("🕵️ Datos Maestros")
        try:
            res_all = supabase.table('registros_comida').select('*').execute()
            if res_all.data: st.dataframe(pd.DataFrame(res_all.data))
        except: st.write("Aún no hay datos globales.")
