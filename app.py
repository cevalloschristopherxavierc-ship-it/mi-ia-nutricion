import streamlit as st
import requests, base64, re, pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN DE SISTEMA ---
st.set_page_config(page_title="Jarvis OS | Xavier", layout="wide", page_icon="🦾")

# CSS Profesional Estático
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
meta_p = st.session_state.u_pes * 2.2 # Foco Hipertrofia
meta_g = (meta_k * 0.25) / 9          # Salud Hormonal
meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4 # Energía Fútbol

# --- 4. SIDEBAR (Agua y Pasos) ---
with st.sidebar:
    st.title(f"👑 Maestro {st.session_state.u_nom}")
    st.divider()
    st.subheader("💧 Hidratación Diaria")
    p_agua = min(st.session_state.h2o / 3.5, 1.0)
    st.progress(p_agua)
    st.write(f"Nivel: **{st.session_state.h2o:.1f}L** / 3.5L")
    ch1, ch2 = st.columns(2)
    if ch1.button("➕ 0.5L"): st.session_state.h2o += 0.5; st.rerun()
    if ch2.button("🧹 Limpiar"): st.session_state.h2o = 0.0; st.rerun()
    
    st.divider()
    st.subheader("👣 Sensor de Pasos")
    pasos = st.number_input("Pasos hoy:", 0, 50000, 0, 500)
    st.metric("Gasto Extra", f"{(pasos/1000)*38:.0f} Kcal")
    
    st.divider()
    key = st.text_input("🔐 Acceso Creador:", type="password")
    st.session_state.creador = (key == "xavier2210")

# --- 5. MOTOR DE DATOS ---
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
m1.metric("🔥 Kcal", f"{k_act:.0f}", f"/{meta_k:.0f}")
m2.metric("🍗 Prot", f"{p_act:.1f}g", f"/{meta_p:.1f}g")
m3.metric("🥑 Grasa", f"{g_act:.1f}g", f"/{meta_g:.1f}g")
m4.metric("🍚 Carb", f"{c_act:.0f}g", f"/{meta_c:.0f}g")

tabs = st.tabs(["🍽️ REGISTRO", "💪 BIO-ANÁLISIS", "📅 HISTORIAL", "🕵️ CREADOR"])

with tabs[0]:
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("📸 Escáner IA")
        up = st.file_uploader("Captura de plato", type=["jpg","png","jpeg"])
        if up and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Jarvis analizando..."):
                try:
                    img_b64 = base64.b64encode(up.read()).decode()
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={st.secrets['GEMINI_API_KEY']}"
                    # Prompt ultra-directo para evitar texto basura de la IA
                    pay = {"contents":[{"parts":[{"text":"Analiza. Responde solo: Nombre|Kcal|Prot"},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                    r = requests.post(url, json=pay, timeout=20).json()
                    
                    raw = r['candidates'][0]['content']['parts'][0]['text']
                    # Extracción inteligente de números (busca cualquier dígito)
                    nums = re.findall(r"\d+\.?\d*", raw)
                    
                    if len(nums) >= 2:
                        # El número más grande suele ser la caloría, el menor la proteína
                        vals = [float(n) for n in nums]
                        kcal_v, prot_v = max(vals), min(vals)
                        # Si hay 3 números, el último suele ser la proteína
                        if len(vals) >= 3: kcal_v, prot_v = vals[-2], vals[-1]
                        
                        supabase.table('registros_comida').insert({
                            "usuario": st.session_state.u_nom, "comida": raw.split('|')[0][:20], 
                            "kcal": kcal_v, "proteina": prot_v, "semana": ini_s
                        }).execute()
                        st.rerun()
                    else: st.error("⚠️ Datos insuficientes en la imagen.")
                except: st.error("❌ Error de lectura. Intente de nuevo.")
