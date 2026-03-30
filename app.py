import streamlit as st
import requests
import base64

# 1. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="FitIA Pro", layout="centered", page_icon="🥗")

# Estilo visual rápido
st.markdown("# 🥗 Jarvis Nutrición Pro")
st.info("📍 Portoviejo | 👤 170cm | ⚖️ 63kg")

# --- ESCÁNER ---
f = st.file_uploader("📸 Sube la foto de tu plato", type=["jpg", "jpeg", "png"])

if f:
    img_bytes = f.read()
    st.image(img_bytes, use_container_width=True, caption="Tu plato listo para analizar")
    
    if st.button("🔍 ANALIZAR MACROS"):
        with st.spinner("🤖 Jarvis conectando al motor Flash-Lite..."):
            try:
                # Usamos gemini-2.0-flash-lite (El más rápido de tu lista)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={API_KEY}"
                
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analiza la comida. Responde estrictamente: Nombre|Kcal|Prot|Carb|Gras"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                        ]
                    }]
                }
                
                # Petición al servidor
                r = requests.post(url, json=payload)
                data = r.json()
                
                if 'candidates' in data:
                    texto = data['candidates'][0]['content']['parts'][0]['text']
                    stats = texto.split('|')
                    
                    if len(stats) >= 5:
                        st.balloons() # ¡Celebración si funciona!
                        st.success(f"🍴 Plato detectado: **{stats[0]}**")
                        
                        # Mostrar métricas profesionales
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("🔥 Calorías", f"{stats[1]} kcal")
                        c2.metric("🍗 Proteína", f"{stats[2]}g")
                        c3.metric("🍚 Carbos", f"{stats[3]}g")
                        c4.metric("🥑 Grasas", f"{stats[4]}g")
                        
                        st.caption("Nota: Valores estimados por IA para apoyo nutricional.")
                    else:
                        st.warning(f"Respuesta inesperada: {texto}")
                
                elif 'error' in data:
                    if data['error']['code'] == 429:
                        st.warning("⏳ Casi listo... Google está terminando de activar tu cuota. Espera 15 segundos y presiona el botón de nuevo.")
                    else:
                        st.error(f"Error {data['error']['code']}: {data['error']['message']}")
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")

if st.button("🔄 Reiniciar Escáner"):
    st.rerun()
