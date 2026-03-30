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

# --- 2. PERFIL DE USUARIO ---
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

# --- 3. TIEMPO Y DÍAS ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dia_hoy_nombre = dias_semana[hoy.weekday()]
hora_actual = hoy.hour

# --- 4. SIDEBAR (METAS COMPLETAS) ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    st.write(f"⚖️ {st.session_state.u_pes}kg | 📏 {st.session_state.u_alt}cm")
    st.divider()
    modo = st.radio("Actividad hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    
    meta_k = 3200.0 if "Fútbol" in modo else 2700.0
    meta_p = st.session_state.u_pes * 2.2 
    meta_g = st.session_state.u_pes * 1.0 
    meta_c = (meta_k - (meta_p * 4) - (meta_g * 9)) / 4 
    
    agua = (st.session_state.u_pes * 35 / 1000) + (1.2 if "Fútbol" in modo else 0.6)
    
    st.success(f"📅 Hoy es: **{dia_hoy_nombre}**")
    st.info(f"💧 Agua: **{agua:.2f}L**")
    st.info(f"🍗 Prot: **{meta_p:.0f}g** | 🍚 Carb: **{meta_c:.0f}g** | 🥑 Gras: **{meta_g:.0f}g**")
    
    if st.button("🔄 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard Nutricional: {st.session_state.u_nom}")

# Lógica de Alarma de Proteína (Línea 79 Corregida)
p_actual = 0.0 
try:
    res_c = supabase.table('registros_comida').select('proteina').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
    if res_c.data:
        p_actual = sum(float(r['proteina']) for r in res_c.data)
except: 
    pass

if hora_actual >= 16 and p_actual < (meta_p * 0.6): 
    st.error(f"🚨 ALERTA: Xavier, vas bajo en proteína ({p_actual:.0f}g de {meta_p:.0f}g). ¡Come huevos o pollo!")

t1, t2 = st.tabs(["📈 ESTADÍSTICAS", "🍽️ REGISTRAR"])

with t1:
    try:
        res_db = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_hist = pd.DataFrame(res_db.data) if res_db.data else pd.DataFrame()
        
        if not df_hist.empty:
            df_hist['f_dt'] = pd.to_datetime(df_hist['created_at']).dt.date
            h_d = df_hist[df_hist['f_dt'] == hoy.date()]
            kh, ph, ch, gh = h_d['kcal'].sum(), h_d['proteina'].sum(), h_d['carbos'].sum(), h_d['grasas'].sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calorías", f"{kh:.0f}", f"Meta: {meta_k:.0f}")
            c2.metric("Proteína", f"{ph:.1f}g", f"Meta: {meta_p:.0f}g")
            c3.metric("Carbos", f"{ch:.1f}g", f"Meta: {meta_c:.0f}g")
            c4.metric("Grasas", f"{gh:.1f}g", f"Meta: {meta_g:.0f}g")
            st.progress(min(float(kh/meta_k), 1.0) if meta_k > 0 else 0.0)
            
            if kh > 0:
                fig = px.pie(values=[ph*4, ch*4, gh*9], names=['Proteína', 'Carbos', 'Grasas'], hole=0.4, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Sin registros para este {dia_hoy_nombre}.")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

with t2:
    col_a, col_b = st.columns(2)
    reg = None
    with col_a:
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
                    reg = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
                except Exception: st.error("Error en IA.")
    with col_b:
        st.subheader("✍️ Manual")
        with st.form("f_manual", clear_on_submit=True):
            n_m = st.text_input("Comida")
            k_m = st.number_input("Kcal", 0.0)
            p_m = st.number_input("Prot (g)", 0.0)
            c_m = st.number_input("Carb (g)", 0.0)
            g_m = st.number_input("Gras (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: reg = {"n":n_m, "k":k_m, "p":p_m, "c":c_m, "g":g_m}

    if reg:
        try:
            supabase.table('registros_comida').insert({
                "usuario": st.session_state.u_nom, "comida": str(reg['n']),
                "kcal": float(reg['k']), "proteina": float(reg['p']),
                "carbos": float(reg['c']), "grasas": float(reg['g']),
                "semana": str(inicio_sem)
            }).execute()
            st.success(f"✅ Guardado.")
            st.rerun()
        except Exception: st.error("Error al guardar.")

# --- 6. HISTORIAL SEMANAL ---
st.divider()
st.subheader(f"📋 Historial: {st.session_state.u_nom}")
if 'df_hist' in locals() and not df_hist.empty:
    for fecha, grupo in df_hist.sort_values(by='created_at', ascending=False).groupby('f_dt'):
        dia_n = dias_semana[pd.to_datetime(fecha).weekday()]
        with st.expander(f"📅 {dia_n} — {grupo['kcal'].sum():.0f} kcal"):
            for _, r in grupo.iterrows():
                st.write(f"🍴 **{r['comida']}** | 🔥 {r['kcal']:.0f} kcal | 🍗 P: {r['proteina']}g")
