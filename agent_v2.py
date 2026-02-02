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
- Grand Palladium Select Costa Mujeres: Resort de lujo frente al mar Caribe. Desde $280/noche.
- Family Selection Costa Mujeres: Ideal para familias con niños. Desde $320/noche.
- TRS Coral Hotel: Solo adultos, experiencia premium. Desde $350/noche.

MÉXICO - RIVIERA MAYA:
- Grand Palladium Colonial Resort & Spa: Arquitectura colonial junto a cenotes. Desde $250/noche.
- Grand Palladium Kantenah Resort & Spa: Acceso a cenote privado. Desde $260/noche.
- Grand Palladium Select White Sand: Playa de arena blanca. Desde $270/noche.
- TRS Yucatan Hotel: Solo adultos, spa de lujo. Desde $340/noche.

REPÚBLICA DOMINICANA - PUNTA CANA:
- Grand Palladium Select Bavaro: Servicios Select exclusivos. Desde $220/noche.
- Grand Palladium Palace Resort & Spa: Arquitectura elegante. Desde $240/noche.
- Grand Palladium Punta Cana Resort & Spa: Familiar con actividades. Desde $230/noche.
- TRS Turquesa Hotel: Solo adultos, playa privada. Desde $320/noche.

TEMPORADAS:
- Alta (Dic-Feb, Jul-Ago): +30% precio
- Media (Mar-Abr, Nov): +15% precio
- Baja (May-Jun, Sep-Oct): Precio base

DESCUENTOS:
- No Reembolsable: 15% dto
- Paga Ahora: 5% dto
- Reserva anticipada (>90 días): 10% dto
"""

# =============================================================================
# PROMPT DEL SISTEMA
# =============================================================================

SYSTEM_PROMPT = """Eres el asistente virtual avanzado de Palladium Hotel Group. 
Tienes dos modos de operación según el usuario: CLIENTE o EMPLEADO (Intranet).

INFORMACIÓN DE HOTELES:
{hoteles_info}

{funciones}

REGLAS IMPORTANTES (MODO CLIENTE):
1. Tu objetivo es VENDER y RESERVAR.
2. Guía al usuario paso a paso (Destino -> Complejo -> Hotel -> Fechas -> Habitación).
3. Nunca inventes códigos. La confirmación real se hace con el botón "CONFIRMAR".
4. Sé persuasivo y amable.

REGLAS IMPORTANTES (MODO EMPLEADO/INTRANET):
1. Tu objetivo es ANALIZAR DATOS y ayudar en la gestión.
2. Usa las funciones de 'MODO INTRANET' para consultar datos reales.
3. Si te preguntan por predicciones o riesgos, usa 'analizar_cancelaciones'.
4. Sé profesional, técnico y directo.
5. Si el usuario pide buscar una reserva específica, pide el ID si no lo da.

FORMATO DE RESPUESTA:
Siempre responde en formato JSON con esta estructura:
{{
    "mensaje": "Tu respuesta textual",
    "acciones": [
        {{"funcion": "nombre_funcion", "parametros": {{"param1": "valor1"}}}}
    ],
    "imagen": "nombre_hotel" (opcional/null)
}}

Si no hay acciones, deja "acciones": [].
"""

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def llamar_groq(mensajes: list, max_tokens: int = 1500) -> str:
    """Llama a la API de Groq."""
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
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return json.dumps({
            "mensaje": f"Lo siento, hubo un error de conexión. Por favor, intenta de nuevo.",
            "acciones": [],
            "error": str(e)
        })


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
    
    system_msg = SYSTEM_PROMPT.format(
        hoteles_info=HOTELES_INFO + contexto_estado,
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
