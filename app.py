import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Configura la API Key en Secrets.")
    st.stop()

st.set_page_config(page_title="FitIA Pro", page_icon="💪", layout="centered")

# 2. Estilo Azul y Blanco (Premium)
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; color: #1a365d; }
    .stButton>button { 
        background-color: #2b6cb0; color: white; border-radius: 25px; 
        width: 100%; height: 50px; font-weight: bold; border: none;
    }
    .macro-card { 
        background-color: #ffffff; padding: 15px; border-radius: 15px; 
        text-align: center; border-left: 8px solid #2b6cb0; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .val { font-size: 24px; font-weight: bold; color: #2c5282; }
    .lab { font-size: 12px; color: #718096; text-transform: uppercase; }
    h1, h2 { color: #2a4365; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE NAVEGACIÓN PASO A PASO ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.datos = {}

def siguiente_paso(): st.session_state.paso += 1
def reiniciar(): st.session_state.paso = 1

# PANTALLAS DE CONFIGURACIÓN
if st.session_state.paso == 1:
    st.title("👨‍💼 Paso 1: Género")
    st.session_state.datos['genero'] = st.radio("Selecciona tu sexo:", ["Masculino", "Femenino"])
    st.button("Siguiente ➡️", on_click=siguiente_paso)

elif st.session_state.paso == 2:
    st.title("🎂 Paso 2: Tu Edad")
    st.session_state.datos['edad'] = st.number_input("¿Cuántos años tienes?", 10, 100, 25)
    st.button("Siguiente ➡️", on_click=siguiente_paso)

elif st.session_state.paso == 3:
    st.title("📏 Paso 3: Estatura")
    st.session_state.datos['altura'] = st.number_input("Estatura en Centímetros (cm)", 100, 250, 170)
    st.button("Siguiente ➡️", on_click=siguiente_paso)

elif st.session_state.paso == 4:
    st.title("⚖️ Paso 4: Peso actual")
    st.session_state.datos['peso'] = st.number_input("Tu peso en Kilogramos (kg)", 30.0, 200.0, 70.0)
    st.button("Siguiente ➡️", on_click=siguiente_paso)

elif st.session_state.paso == 5:
    st.title("🎯 Paso 5: Objetivo")
    st.session_state.datos['objetivo'] = st.selectbox("¿Qué buscas?", ["Ganar masa muscular", "Perder grasa", "Salud"])
    
    if st.button("CALCULAR MIS METAS 🚀"):
        # CÁLCULOS CIENTÍFICOS (Harris-Benedict)
        d = st.session_state.datos
        # TMB básica
        if d['genero'] == "Masculino":
            tmb = 88.36 + (13.4 * d['peso']) + (4.8 * d['altura']) - (5.7 * d['edad'])
        else:
            tmb = 447.59 + (9.2 * d['peso']) + (3.1 * d['altura']) - (4.3 * d['edad'])
        
        calorias = int(tmb * 1.55) # Factor actividad moderada
        if d['objetivo'] == "Ganar masa muscular": calorias += 400
        
        # Guardar metas fijas
        st.session_state.metas = {
            "cal": calorias,
            "prot": int(d['peso'] * 2.2), # Alta proteína para tus piernas
            "gras": int(d['peso'] * 0.9),
            "fibra": 30,
            "agua": round(d['peso'] * 0.035, 1)
        }
        st.session_state.paso = 6
        st.rerun()

# --- PANTALLA PRINCIPAL (DIARIO Y ESCÁNER) ---
elif st.session_state.paso == 6:
    st.title("🥗 Mi Resumen Diario")
    m = st.session_state.metas
    
    # MOSTRAR REQUERIMIENTOS TOTALES
    st.markdown("### Tus necesidades diarias:")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(f"<div class='macro-card'><div class='lab'>Cal</div><div class='val'>{m['cal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='macro-card'><div class='lab'>Prot</div><div class='val'>{m['prot']}g</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='macro-card'><div class='lab'>Gras</div><div class='val'>{m['gras']}g</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='macro-card'><div class='lab'>Fibra</div><div class='val'>{m['fibra']}g</div></div>", unsafe_allow_html=True)
    with c5: st.markdown(f"<div class='macro-card'><div class='lab'>Agua</div><div class='val'>{m['agua']}L</div></div>", unsafe_allow_html=True)

    st.divider()
    
    archivo = st.file_uploader("📸 ESCANEAR COMIDA", type=["jpg", "png"])
    if archivo:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)
        with st.spinner("JARVIS analizando..."): # Un toque de estilo
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Analiza y responde SOLO: Plato|Calorías|Proteína|Carbohidrato|Grasa|Fibra"
            response = model.generate_content([prompt, img])
            r = response.text.split('|')
            
            st.success(f"Detección: {r[0]}")
            # Mostrar lo que aporta esta comida
            cols = st.columns(5)
            labels = ["Kcal", "Prot", "Carb", "Gras", "Fibra"]
            for i, col in enumerate(cols):
                with col:
                    st.markdown(f"<div class='macro-card'><div class='lab'>{labels[i]}</div><div class='val'>{r[i+1]}</div></div>", unsafe_allow_html=True)
    
    if st.button("Resetear Perfil"): reiniciar(); st.rerun()
