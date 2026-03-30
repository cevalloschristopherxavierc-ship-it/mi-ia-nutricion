import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN INICIAL & CONEXIÓN ---
st.set_page_config(page_title="Jarvis Fit Xavier", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error(f"⚠️ Error Crítico de Configuración. Revisa los Secrets: {e}")
    st.stop()

# --- 2. ESTADO DE SESIÓN & MEMORIA (Blindado) ---
for k in ['k_t', 'p_t', 'c_t', 'g_t', 'des_sueño', 'des_energia']:
    if k not in st.session_state:
        if isinstance(k, str) and k.startswith('des_'):
            st.session_state[k] = None # Para las preguntas
        else:
            st.session_state[k] = 0.0 # Para los macros

# --- 3. SIDEBAR: PERFIL, PREGUNTAS & HIDRATACIÓN ---
with st.sidebar:
    st.title("🦾 NÚCLEO DE JARVIS")
    u_nom = "Xavier"
    
    # Fecha Actual
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    hoy_idx = datetime.now().weekday()
    st.subheader(f"📅 Hoy es {dias[hoy_idx]}")
    st.write("---")

    # --- IDEA: Preguntas de Inicio Blindadas ---
    st.subheader("📋 Estado Actual")
    st.session_state.des_sueño = st.slider("¿Cómo dormiste? (1-10)", 1, 10, 8, key="sueño_slider")
    st.session_state.des_energia = st.select_slider("Nivel de energía", ["Baja", "Media", "Alta"], key="energia_slider")
    
    st.write("---")
    # Selector de Entrenamiento (Influye en Meta y Agua)
    modo = st.radio("Entrenamiento de hoy:", ["Gym (Pierna/Glúteo)", "Fútbol (Partido 2h)"])
    meta_k = 3000.0 if modo == "Fútbol (Partido 2h)" else 2500.0
    
    # Hidratación Blindada (63kg base)
    agua_total = ((63 * 35) / 1000) + (1.0 if modo == "Fútbol (Partido 2h)" else 0.5)
    st.info(f"💧 Objetivo de Agua: **{agua_total:.2f} Litros**")
    if modo == "Fútbol (Partido 2h)":
        st.error("🔥 ALERTA MANABÍ: Toma agua constante durante el partido.")
    
    st.divider()
    st.write(f"🔥 Progreso: {st.session_state.k_t:.0f} / {meta_k:.0f} kcal")
    st.progress(min(st.session_state.k_t / meta_k, 1.0))

# --- 4. DASHBOARD PRINCIPAL ---
st.title(f"📈 {dias[hoy_idx]} de {u_nom}")

# Alerta de Proteína (Después de las 4 PM)
if datetime.now().hour >= 16 and st.session_state.p_t < 60:
    st.warning(f"🚨 ¡XAVIER! Son más de las 4 PM y solo llevas {st.session_state.p_t:.1f}g de proteína. ¡Busca huevos, pollo o atún!")

t1, t2 = st.tabs(["📊 ESTADÍSTICAS", "🍽️ REGISTRAR COMIDA"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    
    # Gráfica de Macros Corregida
    df_macros = pd.DataFrame({'M':['Prot','Carb','Gras'], 'G':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    if df_macros['G'].sum() > 0:
        fig = px.pie(df_macros, values='G', names='M', hole=0.5, template="plotly_dark", color_discrete_sequence=['#00FF41','#FFC107','#2196F3'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra tu primera comida para ver la gráfica de macros.")

with t2:
    col_foto, col_manual = st.columns(2)
    comida_final = None

    # --- A. REGISTRO POR FOTO (Blindado) ---
    with col_foto:
        st.subheader("📸 Análisis por Foto")
        foto = st.file_uploader("Sube una foto de tu plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ANALIZAR FOTO"):
            with st.spinner("🤖 Jarvis analizando imagen..."):
                try:
                    img = base64.b64encode(foto.read()).decode()
                    prompt = f"Analiza para un usuario de 63kg. Responde SOLO con este formato exacto: Nombre|Kcal|Prot|Carb|Gras"
                    pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img}}]}]}
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    # Limpiador profundo de texto (quita espacios, asteriscos, g, kcal)
                    d = raw.replace(' ','').replace('g','').replace('kcal','').replace('*','').split('|')
                    comida_final = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
                except Exception as e:
                    st.error(f"❌ La IA no pudo analizar la foto. Por favor, usa el Registro Manual a la derecha.")
                    st.write(f"(Detalle técnico: {e})") # Muestra el error para depurar pero no rompe la app

    # --- B. REGISTRO MANUAL (Siempre Funcional) ---
    with col_manual:
        st.subheader("✍️ Registro Manual")
        with st.form("f_manual", clear_on_submit=True):
            n_m = st.text_input("¿Qué comiste?", help="Ej: Batido de proteína, Arroz con pollo, etc.")
            k_m = st.number_input("Calorías (Kcal)", min_value=0.0, step=10.0, value=0.0)
            c1, c2, c3 = st.columns(3)
            p_m = c1.number_input("Proteína (g)", min_value=0.0, step=1.0, value=0.0)
            c_m = c2.number_input("Carbos (g)", min_value=0.0, step=1.0, value=0.0)
            g_m = c3.number_input("Grasas (g)", min_value=0.0, step=1.0, value=0.0)
            
            if st.form_submit_button("💾 GUARDAR REGISTRO MANUAL"):
                if n_m and k_m > 0: # Validación básica
                    comida_final = {"n":n_m, "k":k_m, "p":p_m, "c":c_m, "g":g_m}
                else:
                    st.warning("Completa al menos el nombre de la comida y las calorías.")

    # --- 5. PROCESO DE GUARDADO UNIFICADO ---
    if comida_final:
        try:
            # 1. Guardar en Supabase (Base de Datos)
            supabase.table('registros_comida').insert({
                "usuario": u_nom, 
                "comida": comida_final['n'], 
                "kcal": comida_final['k'],
                "proteina": comida_final['p'], 
                "carbos": comida_final['c'], 
                "grasas": comida_final['g']
            }).execute()
            
            # 2. Sumar a la sesión visual
            st.session_state.k_t += comida_final['k']
            st.session_state.p_t += comida_final['p']
            st.session_state.c_t += comida_final['c']
            st.session_state.g_t += comida_final['g']
            
            st.success(f"✅ ¡{comida_final['n']} guardado exitosamente!")
            st.rerun() # Refresca para mostrar los cambios
        except Exception as e:
            st.error(f"❌ Error al conectar con Supabase. Revisa tus credenciales o el estado de la tabla.")
            st.write(f"(Detalle técnico: {e})")

# --- 6. HISTORIAL DE HOY ---
st.divider()
st.subheader(f"📋 Comidas de este {dias[hoy_idx]}")
try:
    hist = supabase.table('registros_comida').select('*').order('created_at', desc=True).limit(15).execute()
    if hist.data:
        df_hist = pd.DataFrame(hist.data)
        # Formatear la hora para que se vea bien en Ecuador
        df_hist['Hora'] = pd.to_datetime(df_hist['created_at']).dt.strftime('%H:%M')
        # Mostrar tabla limpia
        st.table(df_hist[['Hora', 'comida', 'kcal', 'proteina', 'carbos', 'grasas']])
    else:
        st.info("Aún no has registrado ninguna comida hoy. ¡Dale gas!")
except Exception as e:
    st.warning(f"No se pudo cargar el historial de la base de datos.")
    st.write(f"(Detalle técnico: {e})")
