import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception:
    st.error("⚠️ Configura los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PERFIL ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Activación de Núcleo Jarvis")
    with st.form("perfil_inicial"):
        st.write("Configura tus datos para el cálculo de macros:")
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Tu nombre?", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Objetivo", ["Hipertrofia", "Fútbol", "Definición"])
        if st.form_submit_button("🚀 INICIAR SISTEMA"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. TIEMPO Y ESTADO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
hora_actual = hoy.hour

if 'agua_hoy' not in st.session_state: st.session_state.agua_hoy = 0.0
if 'pasos_hoy' not in st.session_state: st.session_state.pasos_hoy = 0

# --- 4. SIDEBAR (METAS Y HERRAMIENTAS v64.2) ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    
    # METAS
    meta_k = 3200.0 if "Fútbol" in modo else 2700.0
    meta_p = st.session_state.u_pes * 2.2 
    meta_agua = (st.session_state.u_pes * 35 / 1000) + (1.5 if "Fútbol" in modo else 0.7)
    meta_pasos = 12000 if "Fútbol" in modo else 8000

    st.success(f"🔥 Meta Calorías: **{meta_k:.0f}**")
    st.info(f"🍗 Prot: **{meta_p:.0f}g** | 💧 Agua: **{meta_agua:.1f}L**")
    
    # Botón de Agua
    st.divider()
    st.subheader("💧 Hidratación")
    if st.button("➕ Beber 500ml"):
        st.session_state.agua_hoy += 0.5
        st.rerun()
    st.progress(min(st.session_state.agua_hoy / meta_agua, 1.0))
    st.write(f"Llevas: {st.session_state.agua_hoy:.1f}L")

    # Registro de Pasos
    st.divider()
    st.subheader("👣 Pasos del Día")
    st.write(f"Meta: **{meta_pasos}**")
    st.session_state.pasos_hoy = st.number_input("Tus pasos:", 0, 40000, st.session_state.pasos_hoy)

    if st.button("🔄 Reiniciar"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard Nutricional: {st.session_state.u_nom}")

# Lógica de Proteína Actual
p_act = 0.0 
try:
    res = supabase.table('registros_comida').select('proteina').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res.data: p_act = sum(float(r['proteina']) for r in res.data)
except: pass

# Alerta de Proteína (Tarde)
if hora_actual >= 16 and p_act < (meta_p * 0.6): 
    st.error(f"🚨 ALERTA: Xavier, vas bajo en proteína ({p_act:.0f}g). ¡No pierdas el progreso de tus piernas!")

# BONUS RECOMPENSA (Frase Editada v64.2)
if p_act >= meta_p and st.session_state.pasos_hoy >= meta_pasos:
    st.balloons()
    st.success("🏆 ¡RECOMPENSA DE RANGO DESBLOQUEADA!")
    st.info("🔥 🔥 **'¡Es hora de ponerte mamado y fuerte!'** 🔥 🔥")
    st.caption("Consejo Orion: Domina la rotación y mantén la presión alta.")
else:
    st.warning(f"🔒 Faltan pasos o proteína para desbloquear el bonus de hoy.")

t1, t2 = st.tabs(["📈 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    try:
        res_db = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df = pd.DataFrame(res_db.data) if res_db.data else pd.DataFrame()
        if not df.empty:
            df['f_dt'] = pd.to_datetime(df['created_at']).dt.date
            h_d = df[df['f_dt'] == hoy.date()]
            kh, ph = h_d['kcal'].sum(), h_d['proteina'].sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Kcal", f"{kh:.0f}", f"/{meta_k:.0f}")
            c2.metric("Prot", f"{ph:.1f}g", f"/{meta_p:.0f}g")
            c3.metric("Agua", f"{st.session_state.agua_hoy:.1f}L", f"/{meta_agua:.1f}L")
            c4.metric("Pasos", f"{st.session_state.pasos_hoy}", f"/{meta_pasos}")
            
            if kh > 0:
                fig = px.pie(values=[ph*4, (kh-(ph*4)-200), 200], names=['Prot', 'Carb', 'Gras'], hole=0.4, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
    except: st.error("Error al cargar datos.")

with t2:
    c_a, c_b = st.columns(2)
    reg = None
    with c_a:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube tu plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR"):
            with st.spinner("🤖 Analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    p = "Responde estrictamente: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":p},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    d = raw.replace(' ','').replace('g','').replace('*','').split('|')
                    reg = {"n":d[0], "k":float(d[1]), "p":float(d[2])}
                except: st.error("Error IA.")
    with c_b:
        st.subheader("✍️ Manual")
        with st.form("f_m", clear_on_submit=True):
            n_m = st.text_input("Comida")
            k_m = st.number_input("Kcal", 0.0)
            p_m = st.number_input("Prot (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: reg = {"n":n_m, "k":k_m, "p":p_m}

    if reg:
        try:
            supabase.table('registros_comida').insert({
                "usuario": st.session_state.u_nom, "comida": str(reg['n']),
                "kcal": float(reg['k']), "proteina": float(reg['p']),
                "semana": str(inicio_sem)
            }).execute()
            st.success("✅ Guardado.")
            st.rerun()
        except: st.error("Error al guardar.")

# --- 6. HISTORIAL ---
st.divider()
if 'df' in locals() and not df.empty:
    with st.expander("Ver historial"):
        st.dataframe(df[['created_at', 'comida', 'kcal', 'proteina']].sort_values(by='created_at', ascending=False))
