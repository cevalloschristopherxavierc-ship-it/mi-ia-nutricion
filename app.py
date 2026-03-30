import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN XAVIER (ESTILO JARVIS) ---
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

# --- 2. SESIÓN (63KG - PORTOVIEJO) ---
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

# --- 3. METAS DINÁMICAS (RESTAURADAS) ---
meta_k = 3200.0 if st.session_state.u_obj == "Fútbol" else 2750.0
meta_p = st.session_state.u_pes * 2.2 # 138.6g para 63kg
meta_g = (meta_k * 0.25) / 9
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4

# --- 4. SIDEBAR (DETALLES COMPLETOS) ---
with st.sidebar:
    st.title(f"👑 {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación (Meta 3.5L)")
    st.progress(min(st.session_state.h2o / 3.5, 1.0))
    st.write(f"Nivel: **{st.session_state.h2o:.1f}L**")
    if st.button("➕ 0.5L"): 
        st.session_state.h2o += 0.5
        st.rerun()
    st.divider()
    pasos = st.number_input("👣 Pasos hoy:", 0, 50000, 0, 500)
    st.metric("Gasto Estimado", f"{(pasos/1000)*38:.0f} Kcal")
    if st.text_input("🔐 Creador:", type="password") == "xavier2210":
        st.session_state.creador = True

# --- 5. SINCRONIZACIÓN Y CÁLCULOS ---
k_act, p_act, g_act, c_act = 0.0, 0.0, 0.0, 0.0
df_h = pd.DataFrame()
try:
    hoy = datetime.now().strftime('%Y-%m-%d')
    res = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['fecha'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        df_h = df[df['fecha'] == hoy]
        k_act, p_act = df_h['kcal'].sum(), df_h['proteina'].sum()
        g_act, c_act = (k_act * 0.25) / 9, (k_act * 0.50) / 4
except: pass

# --- 6. DASHBOARD CENTRAL ---
st.header("📊 Centro de Mando")
st.progress(min(k_act / meta_k, 1.0) if meta_k > 0 else 0)
m1, m2, m3, m4 = st.columns(4)
m1.metric("🔥 Kcal", f"{k_act:.0f}/{meta_k:.0f}")
m2.metric("🍗 Prot", f"{p_act:.1f}/{meta_p:.1f}g")
m3.metric("🥑 Grasa", f"{g_act:.1f}/{meta_g:.1f}g")
m4.metric("🍚 Carb", f"{c_act:.0f}/{meta_c:.0f}g")

tabs = st.tabs(["🍽️ REGISTRO", "💪 ANÁLISIS", "📅 HISTORIAL"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📸 Escáner IA")
        up = st.file_uploader("Foto del plato", type=["jpg","png","jpeg"])
        if up and st.button("🔍 PROCESAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_64 = base64.b64encode(up.read()).decode()
                    key = st.secrets["GEMINI_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents":[{"parts":[{"text":"NombreComida, Kcal, Prot. Ejemplo: Pollo, 300, 25"},{"inline_data":{"mime_type":"image/jpeg","data":img_64}}]}]}
                    r = requests.post(url, json=payload, timeout=25)
                    if r.status_code == 200:
                        txt = r.json()['candidates'][0]['content']['parts'][0]['text']
                        nums = re.findall(r"\d+", txt)
                        if len(nums) >= 2:
                            supabase.table('registros_comida').insert({
                                "usuario": st.session_state.u_nom, "comida": "IA_Scan",
                                "kcal": float(nums[0]), "proteina": float(nums[1]),
                                "semana": datetime.now().strftime('%Y-%m-%d')
                            }).execute()
                            st.success("✅ ¡Guardado!")
                            st.rerun()
                    else: st.error(f"Error Google {r.status_code}")
                except: st.error("Sin respuesta IA.")

    with c2:
        st.subheader("✍️ Registro Manual")
        with st.form("f_manual", clear_on_submit=True):
            in_n = st.text_input("Comida")
            in_k = st.number_input("Kcal", 0.0)
            in_p = st.number_input("Prot (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if in_n:
                    supabase.table('registros_comida').insert({
                        "usuario": st.session_state.u_nom, "comida": in_n,
                        "kcal": in_k, "proteina": in_p,
                        "semana": datetime.now().strftime('%Y-%m-%d')
                    }).execute()
                    st.rerun()

with tabs[1]:
    if k_act > 0:
        st.subheader("🎯 Balance de Macros")
        fig = go.Figure(go.Scatterpolar(
            r=[p_act/meta_p if meta_p > 0 else 0, k_act/meta_k if meta_k > 0 else 0, c_act/meta_c if meta_c > 0 else 0, g_act/meta_g if meta_g > 0 else 0],
            theta=['Prot', 'Kcal', 'Carb', 'Grasa'], fill='toself', line_color='#4facfe'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1.2])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    if not df_h.empty: st.table(df_h[['comida', 'kcal', 'proteina']])
