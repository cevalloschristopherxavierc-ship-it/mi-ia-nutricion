import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# --- 1. CONFIG & SEGURIDAD ---
st.set_page_config(page_title="Jarvis Nutrición", layout="wide")

try:
    S_URL, S_KEY = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- 2. ESTILOS XAVIER ---
st.markdown("""
<style>
    .pizarra { background: #1a1a1a; border: 3px solid #59402a; border-radius: 12px; padding: 15px; color: white; font-family: monospace; }
    .verde { color: #00FF41; font-weight: bold; }
    .m-box { text-align: center; background: #262626; padding: 8px; border-radius: 8px; width: 23%; border: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- 3. MEMORIA DE SESIÓN ---
for k in ['k_t', 'p_t', 'c_t', 'g_t']:
    if k not in st.session_state: st.session_state[k] = 0.0

# --- 4. SIDEBAR (PREGUNTAS USUARIO NUEVO) ---
with st.sidebar:
    st.title("🦾 PERFIL ATLETA")
    u_nom = st.text_input("Nombre:", "Xavier")
    u_pes = st.number_input("Peso (kg):", 63.0)
    u_alt = st.number_input("Altura (cm):", 170)
    u_eda = st.number_input("Edad:", 20)
    u_act = st.selectbox("Actividad:", ["Fútbol 2h", "Hipertrofia Glúteos", "Gym General"])
    meta_k = st.number_input("Meta Kcal Diaria:", 2500)
    
    st.divider()
    prog = min(st.session_state.k_t / meta_k, 1.0)
    st.write(f"🔥 Progreso: {int(prog*100)}%")
    st.progress(prog)
    if st.button("🔄 Reiniciar Contador"):
        for k in ['k_t', 'p_t', 'c_t', 'g_t']: st.session_state[k] = 0.0
        st.rerun()

# --- 5. PANEL PRINCIPAL ---
st.title(f"📈 Dashboard Nutricional: {u_nom}")
t1, t2 = st.tabs(["📊 MIS ESTADÍSTICAS", "🍽️ REGISTRAR ALIMENTO"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Proteína", f"{st.session_state.p_t:.1f}g")
    c2.metric("Carbos", f"{st.session_state.c_t:.1f}g")
    c3.metric("Grasas", f"{st.session_state.g_t:.1f}g")
    
    df_m = pd.DataFrame({'Macro':['Prot','Carb','Gras'], 'Gramos':[st.session_state.p_t, st.session_state.c_t, st.session_state.g_t]})
    st.plotly_chart(px.pie(df_m, values='Gramos', names='Macro', hole=0.5, template="plotly_dark", 
                          color_discrete_sequence=['#00FF41','#FFC107','#2196F3']), use_container_width=True)

with t2:
    col_f, col_m = st.columns(2)
    res_c = None

    with col_f:
        st.subheader("📸 Análisis por Foto")
        foto = st.file_uploader("Sube tu plato", type=["jpg","png","jpeg"])
        if foto and st.button("🔍 ESCANEAR PLATO"):
            with st.spinner("🤖 Jarvis analizando ración..."):
                img_b64 = base64.b64encode(foto.read()).decode()
                # Prompt más estricto para evitar errores de formato
                prompt = f"Usuario: {u_pes}kg, {u_alt}cm. Analiza la foto y responde UNICAMENTE en este formato: Nombre|Calorias|Proteinas|Carbos|Grasas. Ejemplo: Pasta con carne|600|35|70|15"
                pld = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                try:
                    r = requests.post(URL_AI, json=pld).json()
                    raw = r['candidates'][0]['content']['parts'][0]['text'].strip()
                    # Limpieza de carácteres que suelen romper el código
                    d = raw.replace(' ','').replace('g','').replace('kcal','').split('|')
                    res_c = {"n":d[0], "k":float(d[1]), "p":float(d[2]), "c":float(d[3]), "g":float(d[4])}
                except Exception as e:
                    st.error(f"❌ Error IA: La imagen no es clara o el formato falló. Intenta Manual.")

    with col_m:
        st.subheader("✍️ Registro Manual")
        with st.form("manual_form"):
            n_m = st.text_input("Nombre del Plato")
            k_m = st.number_input("Kcal", 0.0)
            p_m = st.number_input("Proteína (g)", 0.0)
            c_m = st.number_input("Carbos (g)", 0.0)
            g_m = st.number_input("Grasas (g)", 0.0)
            if st.form_submit_button("💾 GUARDAR"):
                if n_m: res_c = {"n":n_m, "k":k_m, "p":p_m, "c":c_m, "g":g_m}

    if res_c:
        # Actualización de estados
        st.session_state.k_t += res_c['k']
        st.session_state.p_t += res_c['p']
        st.session_state.c_t += res_c['c']
        st.session_state.g_t += res_c['g']
        
        # Guardado en Base de Datos
        try:
            supabase.table('registros_comida').insert({
                "usuario": u_nom, "comida": res_c['n'], "kcal": res_c['k'],
                "proteina": res_c['p'], "carbos": res_c['c'], "grasas": res_c['g']
            }).execute()
            st.success("✅ ¡Registrado!")
        except: pass
        
        # Pizarra de Resultados Visuales
        st.markdown(f"""
        <div class="pizarra">
