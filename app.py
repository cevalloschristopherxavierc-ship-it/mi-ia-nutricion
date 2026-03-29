import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API (Asegúrate de tener tu clave en Secrets)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la clave API en Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilos Visuales (Estilo Fitia: Blanco y Verde)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1d1d1f; }
    .macro-card { 
        background-color: #f8f9fa; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        border: 1px solid #e0e0e0; 
        margin-bottom: 5px;
    }
    .prot { border-bottom: 4px solid #3498db; } /* Azul Proteína */
    .carb { border-bottom: 4px solid #f39c12; } /* Naranja Carbos */
    .gras { border-bottom: 4px solid #2ecc71; } /* Verde Grasas */
    .val { font-size: 20px; font-weight: bold; color: #2c3e50; }
    .lab { font-size: 11px; color: #7f8c8d; text-transform: uppercase; font-weight: bold; }
    h1 { color: #2ecc71; text-align: center; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- PANTALLA DE PERFIL ---
if 'configurado' not in st.session_state:
    st.session_state.configurado = False

if not st.session_state.configurado:
    st.title("🎯 Configura tu Perfil")
    col1, col2 = st.columns(2)
    with col1:
        peso = st.number_input("Peso (kg)", value=70.0)
        altura = st.number_input("Altura (cm)", value=170)
    with col2:
        objetivo = st.selectbox("Objetivo", ["Ganar masa muscular", "Perder grasa"])
        actividad = st.selectbox("Actividad", ["Baja", "Media", "Alta (Gym)"])

    if st.button("GUARDAR Y COMENZAR"):
        st.session_state.user_data = {"peso": peso, "objetivo": objetivo}
        st.session_state.configurado = True
        st.rerun()

# --- APP PRINCIPAL ---
else:
    st.title("🥗 FitIA Pro")
    
    archivo = st.file_uploader("📸 TOMA UNA FOTO DE TU COMIDA", type=["jpg", "jpeg", "png"])

    if archivo:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        
        with st.spinner("Analizando..."):
            # Animación de Power-Up (Crecimiento muscular)
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2k0NmR2OGJ5bzFwNjh5OW8ydWpxYzN6bjlsNWlscml6MXR5OWR3dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3orieXpX39T7b3u7e8/giphy.gif", width=250)
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Analiza rápido: Nombre plato, Calorías, Proteínas(g), Carbohidratos(g), Grasas(g). Responde solo: Plato|Calorías|Proteínas|Carbos|Grasas"
                
                response = model.generate_content([prompt, img])
                res = response.text.split('|')
                
                st.balloons()
                st.success(f"✅ {res[0]} detectado")
                
                # Tarjetas de Macros (Igual a la foto de Fitia)
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f"<div class='macro-card'><div class='lab'>Kcal</div><div class='val'>{res[1]}</div></div>", unsafe_allow_html=True)
                with c2: st.markdown(f"<div class='macro-card prot'><div class='lab'>Prot</div><div class='val'>{res[2]}</div></div>", unsafe_allow_html=True)
                with c3: st.markdown(f"<div class='macro-card carb'><div class='lab'>Carb</div><div class='val'>{res[3]}</div></div>", unsafe_allow_html=True)
                with c4: st.markdown(f"<div class='macro-card gras'><div class='lab'>Gras</div><div class='val'>{res[4]}</div></div>", unsafe_allow_html=True)
                
            except:
                st.error("Error al escanear. Intenta con otra foto.")
