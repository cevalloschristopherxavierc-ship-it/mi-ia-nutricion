import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered", page_icon="💪")

# --- INTERFAZ PERSONALIZADA ---
st.title("💪 Jarvis: Modo Hipertrofia")
st.markdown(f"**Usuario:** 170cm | 63kg | Portoviejo")

# Meta diaria de proteína (ejemplo: 2g por kilo = 126g)
meta_proteina = 126 
if 'prot_total' not in st.session_state:
    st.session_state.prot_total = 0

# Barra de progreso
st.write(f"### Tu Proteína de hoy: {st.session_state.prot_total}g / {meta_proteina}g")
progreso = min(st.session_state.prot_total / meta_proteina, 1.0)
st.progress(progreso)

st.divider()

# --- ESCÁNER ---
f = st.file_uploader("📸 Escanea tu comida", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True)
    
    if st.button("🔍 ANALIZAR Y SUMAR"):
        with st.spinner("🤖 Jarvis calculando..."):
            try:
                # Mantenemos el modelo que YA funcionó
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
                
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la comida. Responde estrictamente: Nombre|Kcal|Prot|Carb|Gras"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                        ]
                    }]
                }
                
                r = requests.post(url, json=payload)
                data = r.json()
                
                if 'candidates' in data:
                    res = data['candidates'][0]['content']['parts'][0]['text']
                    stats = res.split('|')
                    if len(stats) >= 5:
                        nombre = stats[0]
                        prot = float(stats[2].replace('g',''))
                        
                        # Sumar al total de la sesión
                        st.session_state.prot_total += prot
                        
                        st.success(f"✅ ¡{nombre} analizado!")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Calorías", stats[1])
                        col2.metric("Proteína", f"{prot}g")
                        col3.metric("Carbos", stats[3])
                        
                        # Consejo dinámico
                        st.info("💡 **Consejo de Jarvis:** Mañana toca lunes de piernas/glúteos. ¡Asegúrate de llegar a tu meta de proteína hoy!")
                        st.balloons()
                else:
                    st.error("Error en el escaneo.")
            except Exception as e:
                st.error(f"Hubo un problema: {e}")

if st.button("🗑️ Reiniciar Día"):
    st.session_state.prot_total = 0
    st.rerun()
