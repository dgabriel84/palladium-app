import streamlit as st
import time
import os
import json
from .llm_engine import PalladiumAgent
from .tts import speak
from groq import Groq
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

def get_avatar_html(is_speaking=False):
    animation_class = "pulsing" if is_speaking else ""
    return f"""
    <style>
    .avatar-container {{ display: flex; justify_content: center; align_items: center; margin-bottom: 20px; }}
    .avatar-circle {{ width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #d4af37, #b8860b); box-shadow: 0 0 15px rgba(212, 175, 55, 0.5); position: relative; overflow: hidden; transition: transform 0.3s ease; }}
    .pulsing {{ animation: pulse-gold 1.5s infinite; }}
    @keyframes pulse-gold {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
    .eye {{ position: absolute; top: 35%; width: 10px; height: 10px; background: white; border-radius: 50%; }} .eye.left {{ left: 30%; }} .eye.right {{ right: 30%; }}
    .mouth {{ position: absolute; bottom: 30%; left: 50%; transform: translateX(-50%); width: 30px; height: 3px; background: white; border-radius: 2px; }}
    .pulsing .mouth {{ height: 8px; border-radius: 5px; animation: talk 0.2s infinite alternate; }}
    @keyframes talk {{ from {{ height: 3px; }} to {{ height: 12px; }} }}
    </style>
    <div class="avatar-container"><div class="avatar-circle {animation_class}"><div class="eye left"></div><div class="eye right"></div><div class="mouth"></div></div></div>
    """

def transcribe_audio(audio_bytes):
    if not audio_bytes: return ""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return ""
    
    try:
        # Usar requests para evitar conflictos de types con SDK
        import requests
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav"),
            "model": (None, "whisper-large-v3"),
            "language": (None, "es"),
            "response_format": (None, "text")
        }
        res = requests.post(url, headers=headers, files=files)
        if res.status_code == 200:
            return res.text
        return ""
    except Exception as e:
        print(f"Error STT: {e}")
        return ""

def render_agent_sidebar(mode="client"):
    with st.sidebar:
        st.title("Palladium AI ✨")
        
        # Inicializar
        agent = PalladiumAgent(mode=mode)
        
        # 1. MOSTRAR HISTORIAL (Primero, para que siempre se vea)
        messages_container = st.container(height=400)
        with messages_container:
            if "messages" in st.session_state:
                for msg in st.session_state.messages:
                    if msg["role"] == "system": continue
                    
                    with st.chat_message(msg["role"]):
                        content = msg["content"]
                        # Intentar parsear JSON de assistant
                        if msg["role"] == "assistant":
                            try:
                                if "{" in content:
                                    json_content = json.loads(content)
                                    text_show = json_content.get("mensaje", content)
                                    st.write(text_show)
                                    if json_content.get("acciones"):
                                        st.caption(f"⚙️ {json_content.get('acciones')[0].get('funcion')}")
                                else:
                                    st.write(content)
                            except:
                                st.write(content)
                        else:
                            st.write(content)

        # 2. INPUTS
        st.divider()
        is_speaking = st.session_state.get("agent_speaking", False)
        st.markdown(get_avatar_html(is_speaking), unsafe_allow_html=True)
        
        user_text = st.chat_input("Escribe tu consulta...")
        
        audio_bytes = None
        if hasattr(st, "audio_input"):
            ab = st.audio_input("🎤 Hablar")
            if ab: audio_bytes = ab.read()

        # 3. LÓGICA DE PROCESAMIENTO
        input_content = user_text
        if not input_content and audio_bytes:
            # Solo transcribir si NO hemos procesado este audio ya
            # Usamos session state para no transcribir a lo loco en cada rerun
            if "last_audio_bytes" not in st.session_state or st.session_state.last_audio_bytes != audio_bytes:
                with st.spinner("🎧 Transcribiendo..."):
                    input_content = transcribe_audio(audio_bytes)
                    st.session_state.last_audio_bytes = audio_bytes # Marcar como visto
            else:
                # Audio ya procesado, ignorar
                input_content = None

        # Verificar duplicados con historial para evitar bucle
        if input_content:
            last_msg_content = ""
            if "messages" in st.session_state and st.session_state.messages:
                last_msg = st.session_state.messages[-1]
                if last_msg["role"] == "user":
                    last_msg_content = last_msg["content"]
                # Si el ultimo fue assistant, mirar el anterior user
                elif len(st.session_state.messages) > 1:
                     last_msg_content = st.session_state.messages[-2]["content"]
            
            if input_content.strip() == last_msg_content.strip():
                # Input duplicado, ignorar
                pass
            else:
                # --- PROCESAR NUEVO MENSAJE ---
                with st.spinner("🤖 Generando respuesta..."):
                    try:
                        response_json = agent.get_response(input_content)
                    except Exception as e:
                        st.error(f"Error: {e}")
                        response_json = {"mensaje": "Error de conexión.", "acciones": []}
                
                # Acciones (Visual feedback)
                msg_text = response_json.get("mensaje", "")
                actions = response_json.get("acciones", [])
                
                if actions:
                    st.toast(f"Acción: {actions[0].get('funcion')}")
                
                # Hablar
                st.session_state["agent_speaking"] = True
                speak(msg_text, mode=mode)
                
                # Recargar para mostrar historial actualizado
                st.rerun()
