# =============================================================================
# AGENTE CONVERSACIONAL V2 - CON ACCIONES (Function Calling)
# =============================================================================
# Agente que puede:
# 1. Responder preguntas sobre hoteles/precios
# 2. Ejecutar acciones (seleccionar destino, hotel, fechas, etc.)
# 3. Mostrar fotos de hoteles
# 4. Completar reservas paso a paso
# =============================================================================

import os
import json
import requests
from datetime import datetime, timedelta
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: leer .env manualmente si no existe python-dotenv
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception:
        pass
# Importar información turística
from tourist_info import TOURIST_INFO

# API Key de Groq (configurar como variable de entorno)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# =============================================================================
# FUNCIONES DISPONIBLES PARA EL AGENTE
# =============================================================================

FUNCIONES_DISPONIBLES = """
FUNCIONES QUE PUEDES EJECUTAR:

--- MODO CLIENTE (Reservas) ---
1. seleccionar_destino(pais) - Selecciona México o República Dominicana
2. seleccionar_complejo(complejo) - Selecciona: Costa Mujeres, Riviera Maya, Punta Cana
3. seleccionar_hotel(hotel) - Selecciona un hotel específico
4. configurar_fechas(llegada, noches) - Establece fechas (formato: YYYY-MM-DD)
5. configurar_huespedes(adultos, ninos) - Número de huéspedes
6. seleccionar_habitacion(habitacion) - Nombre de la habitación
7. seleccionar_regimen(regimen) - "All Inclusive"
8. seleccionar_tarifa(tarifa) - "No Reembolsable", "Flexible - Paga Ahora", "Flexible - Paga en Destino"
9. confirmar_reserva() - Finaliza la reserva (paso final)
10. mostrar_info_hotel(hotel) - Muestra foto e info del hotel
11. marcar_fidelidad(es_fidelizado) - Marca si es cliente Rewards (true/false)

--- MODO INTRANET (Empleados) ---
12. consultar_ocupacion(mes, anio) - Consulta ocupación y ventas de un mes específico (ej: "junio", 2026)
13. analizar_cancelaciones(mes, top) - Analiza riesgo de cancelaciones. Parámetros: mes="junio", top=3 para top 3
14. consultar_reserva_especifica(id_reserva) - Busca detalles de una reserva por ID
15. resumen_general() - Da un resumen global del estado del hotel
"""

# =============================================================================
# INFORMACIÓN DE CONTEXTO
# =============================================================================

HOTELES_INFO = """
HOTELES DISPONIBLES:

MÉXICO - COSTA MUJERES (Cancún):
- Grand Palladium Select Costa Mujeres: Resort de lujo frente al mar Caribe.
- Family Selection Costa Mujeres: Ideal para familias con niños.
- TRS Coral Hotel: Solo adultos, experiencia premium.

MÉXICO - RIVIERA MAYA:
- Grand Palladium Colonial Resort & Spa: Arquitectura colonial junto a cenotes.
- Grand Palladium Kantenah Resort & Spa: Acceso a cenote privado.
- Grand Palladium Select White Sand: Playa de arena blanca.
- TRS Yucatan Hotel: Solo adultos, spa de lujo.

REPÚBLICA DOMINICANA - PUNTA CANA:
- Grand Palladium Select Bavaro: Servicios Select exclusivos.
- Grand Palladium Palace Resort & Spa: Arquitectura elegante.
- Grand Palladium Punta Cana Resort & Spa: Familiar con actividades.
- TRS Turquesa Hotel: Solo adultos, playa privada.

⚠️ IMPORTANTE SOBRE PRECIOS:
- NUNCA menciones precios específicos (ni por noche ni totales).
- Los precios varían según fechas, habitación, huéspedes y tarifa.
- Di cosas como: "Puedes ver el precio actualizado en la pantalla de reserva" o "El sistema te calculará el mejor precio".
- Si te preguntan cuánto cuesta, di que depende de las fechas y configuración, e invítalos a completar los datos.
"""

# =============================================================================
# PROMPT DEL SISTEMA
# =============================================================================

SYSTEM_PROMPT = """Eres Sophie, la Asistente Virtual de Palladium.
Tu objetivo es ayudar con reservas (Clientes) o análisis (Empleados).

CRÍTICO: TUS RESPUESTAS DEBEN SER MUY BREVES.
- MÁXIMO 2 FRASES O 40 PALABRAS POR TURNO.
- Sé directa y natural. Habla como una persona, no un robot.
- No sueltes parrafadas. Haz una pregunta al final para mantener la charla.

⚠️ MUY IMPORTANTE - NO REPITAS ACCIONES:
- Si ya has mostrado info de un hotel (mostrar_info_hotel), NO lo vuelvas a ejecutar.
- Avanza la conversación: después de mostrar un hotel, pregunta por fechas o huéspedes.
- Flujo ideal: 1) Destino → 2) Hotel → 3) Fechas/Huéspedes → 4) Confirmar reserva

🚫 NUNCA MENCIONES PRECIOS:
- No digas "$X/noche" ni "desde $X" ni "total $X".
- Si preguntan precio, di: "El precio depende de fechas y configuración. Mira la pantalla de reserva."

MODOS:
--- CLIENTE (Ventas) ---
1. Descubre qué buscan: "¿Playa o aventura?", no "¿Fechas?".
2. SOLO la PRIMERA vez que menciones un hotel, ejecuta 'mostrar_info_hotel(nombre_hotel)'.
3. Después de mostrar hotel, pregunta: "¿Para qué fechas te gustaría?" o "¿Cuántas personas viajáis?"
4. Cuando tengas: hotel + fechas + huéspedes, ofrece confirmar con 'confirmar_reserva()'.

--- EMPLEADO (Datos) ---
1. Dato exacto + Acción recomendada. Nada de relleno.

INFORMACIÓN:
{hoteles_info}

{funciones}

FORMATO DE RESPUESTA OBLIGATORIO (JSON):
Debes responder SIEMPRE con un bloque JSON válido.
Formato:
{{
  "mensaje": "Tu respuesta breve al usuario (máx 40 palabras).",
  "acciones": [
      {{
        "funcion": "nombre_funcion",
        "parametros": {{ "param1": "valor" }}
      }}
  ],
  "imagen": "Nombre del hotel exacto si quieres mostrar foto en el chat (opcional)"
}}

Si no necesitas ejecutar acción, manda "acciones": [].
Si no muestras imagen, no incluyas el campo "imagen".
NO escribas nada fuera del JSON.
NO repitas acciones que ya hayas ejecutado en mensajes anteriores.
"""

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def llamar_groq(mensajes: list, max_tokens: int = 1500) -> str:
    """Llama a la API de Groq con retry automático para rate limits."""
    import time
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": mensajes,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    if not GROQ_API_KEY:
        return json.dumps({
            "mensaje": "⚠️ **Error de Configuración:** No se ha detectado la API Key de Groq. Por favor, configura la variable de entorno `GROQ_API_KEY` en `.env` o `.streamlit/secrets.toml`.",
            "acciones": []
        })

    # Retry con backoff exponencial para rate limits (429)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            
            # Si es rate limit, esperar y reintentar
            if response.status_code == 429:
                wait_time = (2 ** attempt)  # 1s, 2s, 4s
                print(f"[GROQ] Rate limit hit. Esperando {wait_time}s antes de reintentar ({attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429 and attempt < max_retries - 1:
                wait_time = (2 ** attempt)
                print(f"[GROQ] Rate limit error. Esperando {wait_time}s...")
                time.sleep(wait_time)
                continue
            return json.dumps({
                "mensaje": f"⏳ La API está ocupada. Espera unos segundos e intenta de nuevo.",
                "acciones": []
            })
        except Exception as e:
            return json.dumps({
                "mensaje": f"Lo siento, hubo un error de conexión. Intenta de nuevo en unos segundos.",
                "acciones": [],
                "error": str(e)
            })
    
    return json.dumps({
        "mensaje": "⏳ Demasiadas peticiones. Espera un momento e intenta de nuevo.",
        "acciones": []
    })


def stt_groq_whisper(audio_bytes):
    """Transcribe audio usando Groq Whisper (stt)."""
    if not GROQ_API_KEY:
        return ""
        
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    # Preparar archivo para envío (multipart/form-data)
    files = {
        "file": ("audio.wav", audio_bytes, "audio/wav"),
        "model": (None, "whisper-large-v3"),
        "language": (None, "es"), # Forzar español
        "response_format": (None, "json")
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, timeout=30)
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        print(f"Error transcripción: {e}")
        return ""


def generar_audio_edge(texto):
    """Genera audio MP3 usando Edge TTS (Neural Voice)."""
    try:
        import edge_tts
        import asyncio
        import io
        
        # Voz neuronal española muy natural (Elvira o Alvaro)
        # Velocidad aumentada un 10%
        voice = "es-ES-ElviraNeural"
        rate = "+10%" 
        
        async def _save_audio():
            communicate = edge_tts.Communicate(texto, voice, rate=rate)
            # Guardar en memoria
            mp3_fp = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    mp3_fp.write(chunk["data"])
            mp3_fp.seek(0)
            return mp3_fp

        return asyncio.run(_save_audio())
        
    except ImportError:
        print("edge-tts no instalado")
        return None
    except Exception as e:
        print(f"Error Edge TTS: {e}")
        return None


def parsear_respuesta(respuesta_raw: str) -> dict:
    """Extrae el JSON de la respuesta del modelo."""
    try:
        # Buscar JSON en la respuesta
        inicio = respuesta_raw.find('{')
        fin = respuesta_raw.rfind('}') + 1
        if inicio != -1 and fin > inicio:
            json_str = respuesta_raw[inicio:fin]
            return json.loads(json_str)
    except:
        pass
    
    # Si no es JSON válido, devolver como mensaje simple
    return {
        "mensaje": respuesta_raw,
        "acciones": []
    }


def chat_con_acciones(mensaje: str, historial: list = None, estado_reserva: dict = None) -> dict:
    """
    Chat principal con capacidad de ejecutar acciones.
    
    Args:
        mensaje: Mensaje del usuario
        historial: Lista de mensajes anteriores
        estado_reserva: Estado actual de la reserva en curso
    
    Returns:
        dict con:
            - mensaje: Respuesta para mostrar al usuario
            - acciones: Lista de acciones a ejecutar
            - imagen: Hotel del que mostrar foto (opcional)
    """
    if historial is None:
        historial = []
    
    # Añadir contexto del estado actual si existe
    contexto_estado = ""
    modo_actual = "CLIENTE"  # Default
    
    # Extraer acciones ya ejecutadas del historial para evitar repeticiones
    acciones_previas = []
    for msg in historial:
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            # Buscar si el mensaje menciona acciones ejecutadas
            if "mostrar_info_hotel" in content.lower() or "TRS" in content or "Grand Palladium" in content:
                acciones_previas.append("mostrar_info_hotel")
            if "reserva confirmada" in content.lower() or "tu reserva" in content.lower():
                acciones_previas.append("confirmar_reserva")
    
    if estado_reserva:
        modo_actual = estado_reserva.get("modo", "Reservas")
        if modo_actual == "Intranet":
            modo_actual = "EMPLEADO/INTRANET"
            contexto_estado = f"\n\n⚠️ MODO ACTUAL: {modo_actual}\nDebes usar SOLO las funciones de MODO INTRANET (consultar_ocupacion, analizar_cancelaciones, consultar_reserva_especifica, resumen_general).\nNO uses funciones de reservas (seleccionar_destino, confirmar_reserva, etc.) en este modo.\n"
        else:
            modo_actual = "CLIENTE"
            contexto_estado = f"\n\nMODO ACTUAL: {modo_actual}\nEstás ayudando a un cliente a hacer una reserva.\n"
            contexto_estado += "ESTADO ACTUAL DE LA RESERVA:\n"
            for key, value in estado_reserva.items():
                if value and key != "modo":
                    contexto_estado += f"- {key}: {value}\n"
            
            # Añadir acciones ya ejecutadas
            if acciones_previas:
                contexto_estado += f"\n⚠️ ACCIONES YA EJECUTADAS (NO REPETIR): {', '.join(set(acciones_previas))}\n"
                contexto_estado += "Ahora debes AVANZAR: pregunta por fechas, huéspedes, o confirma la reserva.\n"
    
    # Preparar info turística
    info_turistica_str = "\n\nINFORMACIÓN TURÍSTICA Y DEL DESTINO:\n"
    for zona, info in TOURIST_INFO.items():
        info_turistica_str += f"{info}\n"

    system_msg = SYSTEM_PROMPT.format(
        hoteles_info=HOTELES_INFO + info_turistica_str + contexto_estado,
        funciones=FUNCIONES_DISPONIBLES
    )
    
    mensajes = [{"role": "system", "content": system_msg}]
    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": mensaje})
    
    respuesta_raw = llamar_groq(mensajes)
    return parsear_respuesta(respuesta_raw)


# =============================================================================
# MAPEO DE HOTELES A IMÁGENES
# =============================================================================

IMAGENES_HOTELES = {
    "Grand Palladium Select Costa Mujeres": "media/hoteles/costa_mujeres/gp_select_costa_mujeres.jpg",
    "Family Selection Costa Mujeres": "media/hoteles/costa_mujeres/family_selection_costa_mujeres.jpg",
    "TRS Coral Hotel": "media/hoteles/costa_mujeres/trs_coral.jpg",
    "Grand Palladium Colonial Resort & Spa": "media/hoteles/riviera_maya/gp_colonial.jpg",
    "Grand Palladium Kantenah Resort & Spa": "media/hoteles/riviera_maya/gp_kantenah.jpg",
    "Grand Palladium Select White Sand": "media/hoteles/riviera_maya/gp_white_sand.jpg",
    "TRS Yucatan Hotel": "media/hoteles/riviera_maya/trs_yucatan.jpg",
    "Grand Palladium Select Bavaro": "media/hoteles/punta_cana/gp_select_bavaro.jpg",
    "Grand Palladium Palace Resort & Spa": "media/hoteles/punta_cana/gp_palace.jpg",
    "Grand Palladium Punta Cana Resort & Spa": "media/hoteles/punta_cana/gp_punta_cana.jpg",
    "TRS Turquesa Hotel": "media/hoteles/punta_cana/trs_turquesa.jpg",
}

def obtener_imagen_hotel(nombre_hotel: str) -> str:
    """Devuelve la ruta de la imagen del hotel."""
    # Buscar coincidencia parcial
    for hotel, imagen in IMAGENES_HOTELES.items():
        if nombre_hotel.lower() in hotel.lower() or hotel.lower() in nombre_hotel.lower():
            return imagen
    return None


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Test Agente V2 ===")
    resultado = chat_con_acciones("Quiero reservar en Cancún para la primera semana de junio")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
