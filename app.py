import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la clave API en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="🥗", layout="centered")

# 2. Estilos Visuales Fitia (Bordes de colores y diseño limpio)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1d1d1f; }
    .macro-card { 
        background-color: #f8f9fa; padding: 10px; border-radius: 10px; 
        text-align: center; border: 1px solid #e0e0e0; margin-bottom: 5px;
    }
    .prot { border-bottom: 5px solid #3498db; } /* Azul Proteína */
    .carb { border-bottom: 5px solid #f39c12; } /* Naranja Carbos */
    .gras { border-bottom: 5px solid #2ecc71; } /* Verde Grasas */
    .val { font-size: 22px; font-weight: bold; color: #2c3e50; }
    .lab { font-size: 12px; color: #7f8c8d; text-transform: uppercase; font-weight: bold; }
    h1 { color: #2ecc71; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- PANTALLA DE PERFIL DETALLADO ---
if 'configurado' not in st.session_state:
    st.session_state.configurado = False

if not st.session_state.configurado:
    st.title("🎯 Perfil de Usuario")
    st.write("Configura tus parámetros físicos para un análisis exacto.")
    
    col1, col2 = st.columns(2)
    with col1:
        genero = st.selectbox("Género", ["Masculino", "Femenino"])
        # Aquí tienes los centímetros detallados
        altura = st.number_input("Estatura (cm)", min_value=100, max_value=250, value=170)
        edad = st.number_input("Edad", min_value=10, max_value=100, value=20)
    with col2:
        peso = st.number_input("Peso actual (kg)", min_value=30.0, max_value=200.0, value=70.0)
        objetivo = st.selectbox("Objetivo", ["Ganar masa muscular", "Perder grasa", "Mantenimiento"])
        actividad = st.selectbox("Nivel de Actividad", ["Baja", "Moderada (Gym 3-4 días)", "Intensa (Gym 5-6 días)"])

    if st.button("GUARDAR Y ACTIVAR IA"):
        st.session_state.user_data = {
            "genero": genero, "altura": altura, "peso": peso, 
            "edad": edad, "objetivo": objetivo, "actividad": actividad
        }
        st.session_state.configurado = True
        st.rerun()

# --- APP PRINCIPAL ---
else:
    st.title("🥗 Mi FitIA")
    
    # Resumen rápido del perfil
    st.info(f"👤 {st.session_state.user_data['altura']}cm | {st.session_state.user_data['peso']}kg | {st.session_state.user_data['objetivo']}")

    archivo = st.file_uploader("📸 ESCANEAR COMIDA", type=["jpg", "jpeg", "png"])

    if archivo:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        
        with st.spinner("Calculando macros..."):
            # Animación de transformación
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2k0NmR2OGJ5bzFwNjh5OW8ydWpxYzN6bjlsNWlscml6MXR5OWR3dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3orieXpX39T7b3u7e8/giphy.gif", width=200)
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                # Le pasamos tus datos a la IA para que el consejo sea personalizado
                u = st.session_state.user_data
                prompt = f"""
                Usuario: {u['genero']}, {u['altura']}cm, {u['peso']}kg, Objetivo: {u['objetivo']}.
                Analiza la imagen y responde SOLO: Nombre|Calorías|Proteínas|Carbohidratos|Grasas
                """
                
                response = model.generate_content([prompt, img])
                res = response.text.split('|')
                
                st.balloons()
                st.success(f"Detección: {res[0]}")
                
                # Tarjetas con bordes de colores (Igual a tu foto de Fitia)
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f"<div class='macro-card'><div class='lab'>Kcal</div><div class='val'>{res[1]}</div></div>", unsafe_allow_html=True)
                with c2: st.markdown(f"<div class='macro-card prot'><div class='lab'>Prot</div><div class='val'>{res[2]}</div></div>", unsafe_allow_html=True)
                with c3: st.markdown(f"<div class='macro-card carb'><div class='lab'>Carb</div><div class='val'>{res[3]}</div></div>", unsafe_allow_html=True)
                with c4: st.markdown(f"<div class='macro-card gras'><div class='lab'>Gras</div><div class='val'>{res[4]}</div></div>", unsafe_allow_html=True)
                
            except:
                st.error("Error al procesar la imagen.")

    if st.button("🔄 Cambiar datos físicos"):
        st.session_state.configurado = False
        st.rerun()
