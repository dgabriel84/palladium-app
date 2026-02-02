# =============================================================================
# AGENTE CONVERSACIONAL PALLADIUM - Groq API
# =============================================================================
# Agente gratuito para demo TFM
# Casos de uso:
#   - Cliente: buscar opciones, comparar precios
#   - Intranet: gestionar reservas de alto riesgo
# =============================================================================

import os
import requests
import pandas as pd
from datetime import datetime

# API Key de Groq (configurar como variable de entorno)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Modelo a usar (Llama 3.3 70B - gratis y potente)
MODEL = "llama-3.3-70b-versatile"


def llamar_groq(mensajes: list, max_tokens: int = 1000) -> str:
    """Llama a la API de Groq y retorna la respuesta."""
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
        return f"Error al conectar con el asistente: {str(e)}"


def obtener_contexto_precios():
    """Genera contexto de precios para el agente cliente."""
    # Precios aproximados por destino/temporada
    return """
PRECIOS PALLADIUM HOTELS 2026 (ADR por noche, All Inclusive):

COSTA MUJERES (Cancún, México):
- Grand Palladium Select Costa Mujeres: desde $280/noche (temporada baja) a $450/noche (temporada alta)
- TRS Coral Hotel (solo adultos): desde $350/noche a $550/noche
- Family Selection Costa Mujeres: desde $320/noche a $500/noche

RIVIERA MAYA (México):
- Grand Palladium Colonial: desde $250/noche a $400/noche
- Grand Palladium Kantenah: desde $260/noche a $420/noche
- Grand Palladium White Sand: desde $270/noche a $430/noche
- TRS Yucatan (solo adultos): desde $340/noche a $520/noche

PUNTA CANA (Rep. Dominicana):
- Grand Palladium Bávaro: desde $220/noche a $380/noche
- Grand Palladium Palace: desde $240/noche a $400/noche
- Grand Palladium Punta Cana: desde $230/noche a $390/noche
- TRS Turquesa (solo adultos): desde $320/noche a $480/noche

TEMPORADAS:
- Alta: Dic-Feb, Jul-Ago, Semana Santa
- Media: Mar-Abr, Nov
- Baja: May-Jun, Sep-Oct

DESCUENTOS:
- Reserva anticipada (>90 días): 10-15%
- No reembolsable: 15%
- Paga Ahora: 5%
- Palladium Rewards: 5% adicional
"""


def obtener_contexto_reservas():
    """Carga y resume las reservas de alto riesgo para el agente intranet."""
    try:
        df = pd.read_csv("reservas_2026.csv")
        df['LLEGADA'] = pd.to_datetime(df['LLEGADA'])
        
        # Filtrar solo activas y ordenar por riesgo
        df_activas = df[df['CANCELADO'] == 0].sort_values('PROB_CANCELACION', ascending=False)
        
        # Top 20 mayor riesgo
        top_riesgo = df_activas.head(20)
        
        resumen = "RESERVAS DE ALTO RIESGO (Top 20):\n\n"
        for _, r in top_riesgo.iterrows():
            prob_pct = r['PROB_CANCELACION'] * 100
            resumen += f"- ID {r['ID_RESERVA']}: {r['NOMBRE_HOTEL']}, {r['LLEGADA'].strftime('%d/%m/%Y')}, "
            resumen += f"{r['PAX']} PAX, ${r['VALOR_RESERVA']:,.0f}, Prob: {prob_pct:.0f}%\n"
        
        # Estadísticas generales
        mes_actual = datetime.now().month
        df_mes = df_activas[df_activas['LLEGADA'].dt.month == mes_actual]
        
        resumen += f"\nESTADÍSTICAS MES ACTUAL ({mes_actual}/2026):\n"
        resumen += f"- Total reservas activas: {len(df_mes)}\n"
        resumen += f"- Valor total: ${df_mes['VALOR_RESERVA'].sum():,.0f}\n"
        resumen += f"- Riesgo alto (>40%): {len(df_mes[df_mes['PROB_CANCELACION'] >= 0.40])}\n"
        resumen += f"- Riesgo medio (25-40%): {len(df_mes[(df_mes['PROB_CANCELACION'] >= 0.25) & (df_mes['PROB_CANCELACION'] < 0.40)])}\n"
        
        return resumen
    except Exception as e:
        return f"Error cargando reservas: {str(e)}"


# =============================================================================
# PROMPTS DEL SISTEMA
# =============================================================================

SYSTEM_PROMPT_CLIENTE = """Eres el asistente virtual de Palladium Hotel Group, una cadena de hoteles de lujo con resorts en México y el Caribe.

Tu rol es ayudar a los clientes a:
1. Encontrar el hotel ideal según sus necesidades
2. Comparar precios y opciones
3. Resolver dudas sobre los hoteles y servicios

INFORMACIÓN DE CONTEXTO:
{contexto}

REGLAS:
- Sé amable, profesional y conciso
- Responde en español
- Si no tienes información exacta, sugiere contactar con reservas
- Recomienda siempre la reserva directa (mejores precios garantizados)
- Menciona los beneficios de Palladium Rewards cuando sea relevante
- Mantén respuestas breves (máximo 3-4 párrafos)
"""

SYSTEM_PROMPT_INTRANET = """Eres el asistente de gestión de reservas para empleados de Palladium Hotel Group.

Tu rol es ayudar a:
1. Identificar reservas con alto riesgo de cancelación
2. Recomendar acciones de retención
3. Analizar patrones y tendencias

DATOS DE RESERVAS:
{contexto}

ACCIONES RECOMENDADAS POR NIVEL DE RIESGO:
- ALTO (>40%): Descuento 15%, Pack experiencias gratis, Cambio fechas sin coste + 10% crédito
- MEDIO (25-40%): Garantía de precio, Upgrade AI Premium, Flexibilidad total
- BAJO (<25%): Upselling (upgrade habitación, Pack VIP, Palladium Rewards)

REGLAS:
- Sé directo y profesional
- Responde en español
- Proporciona recomendaciones accionables
- Incluye IDs de reserva cuando sea relevante
- Mantén respuestas concisas
"""


def chat_cliente(mensaje: str, historial: list = None) -> str:
    """Chat para clientes buscando reservar."""
    if historial is None:
        historial = []
    
    contexto = obtener_contexto_precios()
    system_msg = SYSTEM_PROMPT_CLIENTE.format(contexto=contexto)
    
    mensajes = [{"role": "system", "content": system_msg}]
    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": mensaje})
    
    return llamar_groq(mensajes)


def chat_intranet(mensaje: str, historial: list = None) -> str:
    """Chat para empleados gestionando reservas."""
    if historial is None:
        historial = []
    
    contexto = obtener_contexto_reservas()
    system_msg = SYSTEM_PROMPT_INTRANET.format(contexto=contexto)
    
    mensajes = [{"role": "system", "content": system_msg}]
    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": mensaje})
    
    return llamar_groq(mensajes)


# Test rápido
if __name__ == "__main__":
    print("=== Test Agente Cliente ===")
    respuesta = chat_cliente("¿Cuál es la opción más económica para la primera semana de junio en Cancún para 2 adultos?")
    print(respuesta)
    print()
    print("=== Test Agente Intranet ===")
    respuesta = chat_intranet("¿Cuáles son las 5 reservas con mayor riesgo de cancelación?")
    print(respuesta)
