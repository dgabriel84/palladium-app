import os
import json
import requests
import time
import streamlit as st
from groq import Groq

# Importar info turística
try:
    from tourist_info import TOURIST_INFO
except ImportError:
    TOURIST_INFO = {}

# Configuración
GROQ_MODEL = "llama-3.3-70b-versatile"
TTS_VOICE_CLIENTE = "es-MX-DaliaNeural"
TTS_VOICE_INTRANET = "es-ES-XimenaNeural"

# =============================================================================
# PROMPTS Y DATA
# =============================================================================

FUNCIONES_DISPONIBLES = """
FUNCIONES QUE PUEDES EJECUTAR (Responde en JSON):

--- MODO CLIENTE (Reservas) ---
1. seleccionar_destino(pais) - México o República Dominicana
2. seleccionar_hotel(hotel) - Elige un hotel específico
3. configurar_fechas(llegada) - YYYY-MM-DD
4. configurar_huespedes(adultos, ninos)
5. confirmar_reserva()
6. mostrar_info_hotel(hotel) - Muestra foto e info

--- MODO INTRANET ---
7. consultar_ocupacion(mes, anio)
8. analizar_cancelaciones(mes)
"""

HOTELES_INFO = """
COSTA MUJERES (Cancún):
- Grand Palladium Select Costa Mujeres: Lujo, playa.
- Family Selection: Familias VIP.
- TRS Coral: Adultos.

RIVIERA MAYA:
- Kantenah/Colonial: Mayan Riviera clásica.
- TRS Yucatan: Adultos lujo.

PUNTA CANA:
- Bavaro/Palace/Punta Cana: Complejo enorme.
- TRS Turquesa: Adultos playa privada.
"""

SYSTEM_PROMPT_TEMPLATE = """Eres Sophie, Asistente Virtual de Palladium.
Objetivo: Ayudar con reservas (Clientes) o análisis (Empleados).

CRÍTICO:
- RESPUESTAS BREVES (Max 40 palabras).
- HABLA NATURAL.
- NO INVENTES PRECIOS.

FORMATO DE RESPUESTA JSON OBLIGATORIO:
{{
  "mensaje": "Texto para el usuario.",
  "acciones": [ {{ "funcion": "nombre", "parametros": {{...}} }} ],
  "imagen": "Nombre hotel opcional"
}}

INFORMACIÓN:
{hoteles_info}

{funciones}
"""

class PalladiumAgent:
    def __init__(self, mode="client"):
        self.mode = mode
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            hoteles_info=HOTELES_INFO,
            funciones=FUNCIONES_DISPONIBLES
        )
        
        # Inicializar historial robusto
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if not st.session_state.messages or st.session_state.messages[0].get("role") != "system":
            st.session_state.messages = [{"role": "system", "content": self.system_prompt}]

    def get_response(self, user_input):
        """
        Procesa el input del usuario y devuelve:
        - dict con {mensaje, acciones, imagen}
        """
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return {"mensaje": "Error: Falta API Key.", "acciones": []}

        # Añadir usuario al historial
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            client = Groq(api_key=api_key)
            
            completion = client.chat.completions.create(
                messages=[{"role": m["role"], "content": str(m["content"])} for m in st.session_state.messages],
                model=GROQ_MODEL,
                temperature=0.5,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
            response_content = completion.choices[0].message.content
            
            # Parsear JSON
            try:
                response_json = json.loads(response_content)
            except json.JSONDecodeError:
                response_json = {
                    "mensaje": response_content, # Fallback si no es JSON
                    "acciones": []
                }
            
            # Guardar en historial (como string json para mantener contexto)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            
            return response_json

        except Exception as e:
            error_msg = f"Error IA: {str(e)}"
            st.error(error_msg)
            return {"mensaje": error_msg, "acciones": []}
