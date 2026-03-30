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
except:
    st.error("⚠️ Configura los Secrets (URL y KEY) en Streamlit Cloud.")
    st.stop()

# --- 2. PREGUNTAS DE INICIO (PERFIL DINÁMICO) ---
if 'perfil_listo' not in st.session_state:
    st.session_state.perfil_listo = False

if not st.session_state.perfil_listo:
    st.title("🦾 Configuración de Núcleo Jarvis")
    st.subheader("Ingresa tus datos para personalizar la IA:")
    with st.form("perfil_inicial"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("¿Cómo te llamas?", "Xavier")
        pes = c2.number_input("Peso actual (kg)", 30.0, 150.0, 63.0)
        alt = c1.number_input("Altura (cm)", 100, 230, 170)
        obj = c2.selectbox("Tu objetivo principal", ["Hipertrofia (Ganar Músculo)", "Definición (Perder Grasa)", "Rendimiento Deportivo"])
        
        if st.form_submit_button("🔥 ACTIVAR JARVIS"):
            st.session_state.u_nom = nom.strip()
            st.session_state.u_pes = pes
            st.session_state.u_alt = alt
            st.session_state.u_obj = obj
            st.session_state.perfil_listo = True
            st.rerun()
    st.stop()

# --- 3. LÓGICA DE TIEMPO (REINICIO SEMANAL) ---
hoy = datetime.now()
# Calculamos el lunes de esta semana
inicio_sem = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
dias_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# --- 4. SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.title(f"🦾 Perfil: {st.session_state.u_nom}")
    st.write(f"⚖️ **Peso:** {st.session_state.u_pes}kg | 📏 **Alt:** {st.session_state.u_alt}cm")
    st.divider()
    
    modo = st.radio("¿Qué actividad haces hoy?", ["Gym (Pierna/Glúteo)", "Fútbol (Partido 2h)"])
    
    # Metas dinámicas
    meta_k = 3200.0 if modo == "Fútbol (Partido 2h)" else 2600.0
    # Hidratación (35ml x kg) + extra por deporte
    agua_base = (st.session_state.u_pes * 35) / 1000
    agua_total = agua_base + (1.2 if modo == "Fútbol (Partido 2h)" else 0.5)
    
    st.info(f"💧 Objetivo Agua: **{agua_total:.2f} Litros**")
    if modo == "Fútbol (Partido 2h)":
        st.warning("⚽ Modo Fútbol: Sube los carbos y el agua.")
        
    if st.button("🔄 Cambiar de Usuario"):
        st.session_state.perfil_listo = False
        st.rerun()

# --- 5. DASHBOARD PRINCIPAL ---
st.title(f"📈 {dias_esp[hoy.weekday()]} de {st.session_state.u_nom}")

t1, t2 = st.tabs(["📊 ESTADÍSTICAS SEMANALES", "🍽️ REGISTRAR COMIDA"])

with t1:
    try:
        # Traemos solo registros de este usuario Y de esta semana
        res_h = supabase.table('registros_comida').select('*').eq('usuario', st.session_state.u_nom).eq('semana', inicio_sem).execute()
        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()
        
        if not df_h.empty:
            # Filtro para solo HOY
            df_h['fecha_solo'] = pd.to_datetime(df_h['created_at']).dt.date
            k_hoy = df_h[df_h['fecha_solo'] == hoy.date()]['kcal'].sum()
            p_hoy = df_h[df_h['fecha_solo'] == hoy.date()]['proteina'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("Calorías Hoy", f"{k_hoy:.0f} / {meta_k:.0f}")
            c2.metric("Proteína Hoy", f"{p_hoy:.1f}g")
            st.progress(min(k_hoy/meta_k, 1.0))
            
            # Gráfica de Macros
            fig = px.pie(values=[p_hoy, 100, 50], names=['Prot', 'Carb', 'Gras'], hole=0.5, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Hola {st.session_state.u_nom}, aún no hay registros en esta semana (desde el {inicio_sem}).")
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

with t2:
    col_foto, col_manual = st.columns(2)
    res_final = None

    with col_foto:
        st.subheader("📸 Foto IA")
        foto = st.file_uploader("Sube tu plato", type=["jpg","jpeg","png"])
        if foto and st.button("🔍 ANALIZAR CON JARVIS"):
            with st.spinner("🤖 Analizando..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    prompt = "Responde solo en este formato: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    d = raw.replace(' ','').replace('g','').replace('*','').split('|')
                    res_final = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
                except: st.error("IA ocupada o imagen no clara. Usa el manual.")

    with col_manual:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_form", clear_on_submit=True):
            n_m = st.text_input("¿Qué comiste?")
            k_m = st.number_input("Calorías (kcal)", 0.0)
            p_m = st.number_input("Proteína (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: res_final = {"n":n_m, "k":k_m, "p":p_m, "c":0.0, "g":0.0}

    if res_final:
        try:
            # GUARDADO SEGURO
            supabase.table('registros_comida').insert({
                "usuario": st.session_state.u_nom,
                "comida": str(res_final['n']),
                "kcal": float(res_final['k']),
                "proteina": float(res_final['p']),
                "carbos": float(res_final['c']),
                "grasas": float(res_final['g']),
                "semana": str(inicio_sem)
            }).execute()
            st.success(f"✅ {res_final['n']} guardado exitosamente.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al guardar. ¿Corriste el SQL de la columna 'semana'? Detalle: {e}")

# --- 6. HISTORIAL SEMANAL PROFESIONAL ---
st.divider()
st.subheader("📋 Tu Historial de Comidas")
if not df_h.empty:
    # Ordenar por el más reciente
    for _, r in df_h.sort_values(by='created_at', ascending=False).iterrows():
        with st.expander(f"🍴 {r['comida']} — {r['kcal']:.0f} kcal"):
            st.write(f"📅 **Hora:** {pd.to_datetime(r['created_at']).strftime('%H:%M')} | **Día:** {pd.to_datetime(r['created_at']).strftime('%A')}")
            st.write(f"🍗 **P:** {r['proteina']}g | 🍚 **C:** {r['carbos']}g | 🥑 **G:** {r['grasas']}g")
else:
    st.info("No hay registros para mostrar todavía.")
