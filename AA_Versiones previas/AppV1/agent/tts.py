import asyncio
import edge_tts
import io
import streamlit as st
from .config import TTS_VOICE_CLIENTE, TTS_VOICE_INTRANET

async def generate_speech_bytes(text, voice):
    """Genera audio MP3 en memoria usando Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    audio_bytes = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.write(chunk["data"])
    audio_bytes.seek(0)
    return audio_bytes.getvalue()

def speak(text, mode="client"):
    """Función síncrona wrapper para Streamlit."""
    voice = TTS_VOICE_CLIENTE if mode == "client" else TTS_VOICE_INTRANET
    
    # Ejecutar asíncronamente
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    audio_data = loop.run_until_complete(generate_speech_bytes(text, voice))
    
    # Reproducir audio automáticamente (HTML5)
    # Codificar en base64 para insertar en HTML
    import base64
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
        <audio autoplay class="agent-voice">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
