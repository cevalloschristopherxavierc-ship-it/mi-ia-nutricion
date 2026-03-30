import streamlit as st
import requests
import base64
import time
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE SEGURIDAD
try:
    S_URL = st.secrets["SUPABASE_URL"]
    S_KEY = st.secrets["SUPABASE_KEY"]
    G_KEY = st.secrets["GEMINI_API_KEY"]
    URL_AI = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={G_KEY}"
    supabase: Client = create_client(S_URL, S_KEY)
except Exception as e:
    st.error("⚠️ Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# 2. ANIMACIÓN DE CARGA (FIRMA DE AUTOR)
if 'intro' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h1 style='text-align: center; color: #00FF41;'>🦾 JARVIS OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>SISTEMA BY: XAVIER CEVALLOS</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(101):
            bar.progress(i)
            time.sleep(0.01)
    placeholder.empty()
    st.session_state.intro = True

# 3. ESTILOS VISUALES - ¡AQUÍ ESTÁ TU PIZARRA!
st.markdown("""
<style>
    /* Estilo general de la pizarra */
    .pizarra-contenedor {
        display: flex;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    .pizarra-fondo {
        background-color: #262626; /* Negro pizarra */
        border: 10px solid #59402a; /* Borde de madera */
        border-radius: 15px;
        padding: 25px;
        width: 90%;
        max-width: 500px;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.5);
        font-family: 'Courier New', Courier, monospace; /* Fuente estilo tiza */
        color: white;
    }

    /* Título del plato */
    .pizarra-titulo {
        color: #00FF41; /* Verde Jarvis */
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        border-bottom: 2px solid #444;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Filas de datos */
    .pizarra-fila {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 15px;
        font-size: 18px;
    }

    /* Contenedor de icono y nombre */
    .pizarra-seccion-izquierda {
        display: flex;
        align-items: center;
    }

    /* Iconos emoji a color */
    .pizarra-icono {
        font-size: 22px;
        margin-right: 15px;
    }

    /* Nombres de los macronutrientes */
    .pizarra-nombre {
        color: #ddd;
    }

    /* Valores numéricos resaltados */
    .pizarra-valor {
        color: #00FF41; /* Verde Jarvis */
        font-weight: bold;
        font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE REGISTRO (PREGUNTAS)
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>📋 REGISTRO INICIAL</h2>", unsafe_allow_html=True)
    with st.form("registro_final"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre:")
            edad = st.number_input("Edad:", min_value=10, max_value=100, value=20)
        with c2:
            peso = st.number_input("Peso (kg):", min_value=30.0, value=63.0)
            altura = st.number_input("Altura (cm):", min_value=100, max_value=250, value=170)
        
        if st.form_submit_button("ACTIVAR JARVIS 🚀"):
            if nombre:
                m_p = peso * 2
                imc = round(peso / ((altura/100)**2), 1)
                u_data = {"nombre": nombre, "peso": peso, "altura": altura, "edad": edad, "meta_p": m_p, "imc": imc}
                try:
                    supabase.table('usuarios').insert({"nombre": nombre, "peso": peso, "altura": altura, "edad": edad, "meta_proteina": m_p}).execute()
                except: pass
                st.session_state.usuario = u_data
                st.rerun()
            else:
                st.error("⚠️ El nombre es necesario.")
    st.stop()

# 5. INTERFAZ PRINCIPAL
u = st.session_state.usuario
with st.sidebar:
    st.title("📂 BIOMETRÍA")
    st.success(f"AGENTE: {u.get('nombre', '').upper()}")
    st.write(f"⚖️ Peso: {u.get('peso')}kg | 📏 Altura: {u.get('altura')}cm")
    st.write(f"📊 IMC: {u.get('imc')}")
    st.divider()
    st.write(f"🎯 Meta Proteína: {u.get('meta_p', 0)}g")
    
    if "xavier" in u.get('nombre', '').lower():
        st.divider()
        st.markdown("### 👑 MODO CREADOR")
        if st.button("📊 VER USUARIOS"):
            res = supabase.table('usuarios').select('*').execute()
            st.dataframe(res.data)
            
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

st.subheader("📸 ESCÁNER NUTRICIONAL")
foto = st.file_uploader("Sube tu comida", type=["jpg", "png", "jpeg"])

if foto:
    img_64 = base64.b64encode(foto.read()).decode('utf-8')
    st.image(foto, use_container_width=True)
    if st.button("🔍 ANALIZAR AHORA"):
        with st.spinner("🤖 Analizando..."):
            # LÓGICA DE IA
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Responde solo: Nombre|Kcal|Prot|Carb|Gras"},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_64}}
                    ]
                }]
            }
            try:
                r = requests.post(URL_AI, json=payload)
                data = r.json()
                res = data['candidates'][0]['content']['parts'][0]['text'].split('|')
                
                # --- AQUÍ CONSTRUIMOS TU PIZARRA DESEADA ---
                if len(res) == 5:
                    nombre_plato = res[0]
                    kcal = res[1]
                    proteina = res[2]
                    carbos = res[3]
                    grasas = res[4]

                    # Mapeo de iconos a color (puedes cambiarlos)
                    iconos = {
                        "kcal": "🔥",
                        "prot": "🍗",
                        "carb": "🍚",
                        "gras": "🥑"
                    }

                    # HTML de la pizarra, igualita a tu imagen
                    pizarra_html = f"""
                    <div class="pizarra-contenedor">
                        <div class="pizarra-fondo">
                            <div class="pizarra-titulo">{nombre_plato.upper()}</div>
                            
                            <div class="pizarra-fila">
                                <div class="pizarra-seccion-izquierda">
                                    <span class="pizarra-icono">{iconos['prot']}</span>
                                    <span class="pizarra-nombre">PROTEÍNA</span>
                                </div>
                                <span class="pizarra-valor">{proteina}</span>
                            </div>

                            <div class="pizarra-fila">
                                <div class="pizarra-seccion-izquierda">
                                    <span class="pizarra-icono">{iconos['gras']}</span>
                                    <span class="pizarra-nombre">GRASAS</span>
                                </div>
                                <span class="pizarra-valor">{grasas}</span>
                            </div>

                            <div class="pizarra-fila">
                                <div class="pizarra-seccion-izquierda">
                                    <span class="pizarra-icono">{iconos['carb']}</span>
                                    <span class="pizarra-nombre">CARBOS</span>
                                </div>
                                <span class="pizarra-valor">{carbos}</span>
                            </div>

                            <div class="pizarra-fila">
                                <div class="pizarra-seccion-izquierda">
                                    <span class="pizarra-icono">{iconos['kcal']}</span>
                                    <span class="pizarra-nombre">CALORÍAS</span>
                                </div>
                                <span class="pizarra-valor">{kcal}</span>
                            </div>

                        </div>
                    </div>
                    """
                    st.markdown(pizarra_html, unsafe_allow_html=True)
                else:
                    st.error("La IA no respondió en el formato correcto.")
                    
            except:
                st.error("Error al analizar. Intenta de nuevo.")
