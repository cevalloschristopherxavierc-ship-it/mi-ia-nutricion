import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- 1. CONFIG & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Fitness AI", layout="wide", page_icon="🦾")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. PERFIL (PREGUNTAS) ---
if 'perfil_listo' not in st.session_state: st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Configuración de Jarvis")
    with st.form("perfil"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("Nombre", "Xavier")
        pes = c2.number_input("Peso (kg)", 30.0, 150.0, 63.0)
        if st.form_submit_button("🚀 ACTIVAR"):
            st.session_state.u_nom, st.session_state.u_pes = nom.strip(), pes
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. TIEMPO ---
hoy = datetime.now()
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title(f"🦾 {st.session_state.u_nom}")
    modo = st.radio("Hoy toca:", ["Gym (Pierna/Glúteo)", "Fútbol (2h+)"])
    meta_k = 3000.0 if modo == "Fútbol (2h+)" else 2500.0
    st.info(f"💧 Agua: **{((st.session_state.u_pes*35)/1000 + (1 if 'Fútbol' in modo else 0.5)):.2f}L**")

# --- 5. DASHBOARD ---
st.title(f"📊 Dashboard de {st.session_state.u_nom}")
t1, t2 = st.tabs(["ESTADÍSTICAS", "REGISTRAR"])

with t1:
    try:
        # Traemos solo lo de este usuario y esta semana
        res_h = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        if not df_h.empty:
            k_hoy = df_h[pd.to_datetime(df_h['created_at']).dt.date == hoy.date()]['kcal'].sum()
            st.metric("Kcal Hoy", f"{k_hoy:.0f} / {meta_k:.0f}")
            st.progress(min(k_hoy/meta_k, 1.0))
        else: st.info("Sin registros hoy.")
    except Exception as e: st.error(f"Error cargando datos: {e}")

with t2:
    col_a, col_b = st.columns(2)
    res_final = None
    with col_a:
        st.subheader("📸 Foto")
        foto = st.file_uploader("Escanear", type=["jpg","png"])
        if foto and st.button("🔍 ANALIZAR"):
            try:
                img = base64.b64encode(foto.read()).decode()
                p = "Responde solo: Nombre|Kcal|Prot|Carb|Gras"
                pld = {"contents":[{"parts":[{"text":p},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                r = requests.post(URL_AI, json=pld).json()
                d = r['candidates'][0]['content']['parts'][0]['text'].strip().replace(' ','').replace('g','').replace('*','').split('|')
                res_final = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
            except: st.error("Fallo en IA. Usa manual.")

    with col_b:
        st.subheader("✍️ Manual")
        with st.form("f_m", clear_on_submit=True):
            n_m = st.text_input("Comida")
            k_m = st.number_input("Kcal", 0.0)
            p_m = st.number_input("Prot", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: res_final = {"n":n_m, "k":k_m, "p":p_m, "c":0.0, "g":0.0}

    if res_final:
        try:
            # LIMPIEZA DE DATOS ANTES DE ENVIAR
            data_to_save = {
                "usuario": str(st.session_state.u_nom),
                "comida": str(res_final['n']),
                "kcal": float(res_final['k']),
                "proteina": float(res_final['p']),
                "carbos": float(res_final['c']),
                "grasas": float(res_final['g']),
                "semana": str(inicio_sem)
            }
            supabase.table('registros_comida').insert(data_to_save).execute()
            st.success("✅ ¡Guardado en la Nube!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error real de Supabase: {e}")

# --- 6. HISTORIAL ---
st.divider()
if not df_h.empty:
    for _, r in df_h.iterrows():
        with st.expander(f"🍴 {r['comida']} - {r['kcal']} kcal"):
            st.write(f"🍗 P: {r['proteina']}g | 🍚 C: {r['carbos']}g | 🥑 G: {r['grasas']}g")
