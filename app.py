# =============================================================================
# PALLADIUM HOTEL GROUP - SISTEMA DE RESERVAS
# =============================================================================
# TFM Grupo 4 - Master en Data Science
# 
# Flujo de reserva:
#   Paso 1: Seleccionar pais y ver mapa con hoteles
#   Paso 2: Elegir hotel, fechas y huespedes
#   Paso 3: Seleccionar habitacion, regimen y tipo de tarifa
#   Paso 4: Confirmacion de reserva
# =============================================================================

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random
import string
import os

# Path absoluto al directorio de la app
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_RESERVAS = os.path.join(APP_DIR, "reservas_2026.csv")

# Importar agente conversacional V2 (con acciones)
try:
    from agent_v2 import chat_con_acciones, obtener_imagen_hotel
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

# =============================================================================
# CONFIGURACION
# =============================================================================

st.set_page_config(
    page_title="Palladium Hotel Group - Reservas",
    page_icon="https://www.palladiumhotelgroup.com/content/dam/Palladium/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ESTRUCTURA DE DESTINOS, COMPLEJOS, HOTELES Y HABITACIONES
# =============================================================================
# 
# CÓDIGOS DE HOTEL (para buscar precios en precios_data.py):
#   CANA_BAV, CANA_PAL, CANA_PC, CANA_TRS (Punta Cana)
#   MAYA_COL, MAYA_KAN, MAYA_TRS, MAYA_WS (Riviera Maya)
#   MUJE_CMU, MUJE_CMU_FS, MUJE_TRS, MUJE_TRSC (Costa Mujeres)
#
# ESTRUCTURA DE HABITACIONES:
#   Cada habitación tiene: nombre, descripcion, max_pax, imagen
#   Las fotos van en: media/habitaciones/{hotel_code}/{NOMBRE_HAB}.jpg
#
# =============================================================================

from precios_data import PRECIOS_ADR

DESTINOS = {
    # =========================================================================
    # MEXICO
    # =========================================================================
    "Mexico": {
        "complejos": {
            # -----------------------------------------------------------------
            # COSTA MUJERES - Cancún
            # -----------------------------------------------------------------
            "Costa Mujeres": {
                "ubicacion": "Cancún, Quintana Roo",
                "mapa_imagen": "media/hoteles/costa_mujeres/mapa.jpg",
                "hoteles": {
                    # .........................................................
                    # Grand Palladium Select Costa Mujeres
                    # .........................................................
                    "Grand Palladium Select Costa Mujeres": {
                        "hotel_code": "MUJE_CMU",
                        "imagen": "media/hoteles/costa_mujeres/gp_select_costa_mujeres.jpg",
                        "descripcion": "Resort de lujo frente al mar Caribe con playa privada y servicios premium",
                        "solo_adultos": False,
                        "habitaciones": {
                            "CMU JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 8},
                            "CMU JUNIOR SUITE PS": {"descripcion": "Junior Suite junto a la piscina", "max_pax": 8},
                            "CMU JUNIOR SUITE PS OV": {"descripcion": "Junior Suite piscina con vista oceánica", "max_pax": 7},
                            "CMU LOFT SUITE JT": {"descripcion": "Loft Suite con jacuzzi en terraza", "max_pax": 5},
                        }
                    },
                    # .........................................................
                    # Family Selection at Grand Palladium Costa Mujeres
                    # .........................................................
                    "Family Selection Costa Mujeres": {
                        "hotel_code": "MUJE_CMU_FS",
                        "imagen": "media/hoteles/costa_mujeres/family_selection_costa_mujeres.jpg",
                        "descripcion": "Experiencia familiar exclusiva con servicios especiales para familias con niños",
                        "solo_adultos": False,
                        "habitaciones": {
                            "CMU FS JUNIOR SUITE BS": {"descripcion": "Junior Suite familiar junto a la playa", "max_pax": 8},
                            "CMU FS JUNIOR SUI BS POV": {"descripcion": "Junior Suite familiar con vista panorámica oceánica", "max_pax": 6},
                        }
                    },
                    # .........................................................
                    # TRS Coral Hotel (Solo Adultos)
                    # .........................................................
                    "TRS Coral Hotel": {
                        "hotel_code": "MUJE_TRS",
                        "imagen": "media/hoteles/costa_mujeres/trs_coral.jpg",
                        "descripcion": "Hotel solo adultos con experiencia premium y servicios exclusivos",
                        "solo_adultos": True,
                        "habitaciones": {
                            "TRS JUNIOR SUITE BS OV": {"descripcion": "Junior Suite playa con vista oceánica", "max_pax": 3},
                            "TRS JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 3},
                            "TRS JUNIOR SUITE OV": {"descripcion": "Junior Suite con vista al océano", "max_pax": 3},
                            "TRS JUNIOR SUITE SW": {"descripcion": "Junior Suite Swim Up con piscina privada", "max_pax": 3},
                            "TRS LOFT SUITE JT": {"descripcion": "Loft Suite con jacuzzi en terraza", "max_pax": 3},
                            "TRS LOFT SUITE JT OV": {"descripcion": "Loft Suite jacuzzi con vista oceánica", "max_pax": 3},
                        }
                    }
                }
            },
            # -----------------------------------------------------------------
            # RIVIERA MAYA
            # -----------------------------------------------------------------
            "Riviera Maya": {
                "ubicacion": "Riviera Maya, Quintana Roo",
                "mapa_imagen": "media/hoteles/riviera_maya/mapa.jpg",
                "hoteles": {
                    # .........................................................
                    # Grand Palladium Colonial Resort & Spa
                    # .........................................................
                    "Grand Palladium Colonial Resort & Spa": {
                        "hotel_code": "MAYA_COL",
                        "imagen": "media/hoteles/riviera_maya/gp_colonial.jpg",
                        "descripcion": "Resort con arquitectura colonial junto a la playa y cenotes naturales",
                        "solo_adultos": False,
                        "habitaciones": {
                            "COL DELUXE GARDEN VIEW": {"descripcion": "Habitación Deluxe con vistas al jardín", "max_pax": 6},
                            "COL JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 8},
                            "COL JUNIOR SUITE PS": {"descripcion": "Junior Suite junto a la piscina", "max_pax": 8},
                            "COL ROMANCE VILLA SUI PS": {"descripcion": "Villa romántica junto a la piscina", "max_pax": 3},
                        }
                    },
                    # .........................................................
                    # Grand Palladium Kantenah Resort & Spa
                    # .........................................................
                    "Grand Palladium Kantenah Resort & Spa": {
                        "hotel_code": "MAYA_KAN",
                        "imagen": "media/hoteles/riviera_maya/gp_kantenah.jpg",
                        "descripcion": "Resort frente al mar con acceso a cenote privado y actividades acuáticas",
                        "solo_adultos": False,
                        "habitaciones": {
                            "KAN DELUXE GARDEN VIEW": {"descripcion": "Habitación Deluxe con vistas al jardín", "max_pax": 4},
                            "KAN JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 8},
                            "KAN ROMANCE VILLA SUI BS": {"descripcion": "Villa romántica junto a la playa", "max_pax": 2},
                        }
                    },
                    # .........................................................
                    # TRS Yucatan Hotel (Solo Adultos)
                    # .........................................................
                    "TRS Yucatan Hotel": {
                        "hotel_code": "MAYA_TRS",
                        "imagen": "media/hoteles/riviera_maya/trs_yucatan.jpg",
                        "descripcion": "Hotel solo adultos con experiencia gourmet y spa de lujo",
                        "solo_adultos": True,
                        "habitaciones": {
                            "TRS JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 5},
                            "TRS JUNIOR SUITE PS": {"descripcion": "Junior Suite junto a la piscina", "max_pax": 4},
                            "TRS JUNIOR SUITE PS OV": {"descripcion": "Junior Suite piscina con vista oceánica", "max_pax": 3},
                            "TRS JUNIOR SUITE PP GV": {"descripcion": "Junior Suite Premium Plus Garden View", "max_pax": 4},
                            "TRS JUNIOR SUITE PP PS": {"descripcion": "Junior Suite Premium Plus Poolside", "max_pax": 3},
                            "TRS JS JACUZZI TERR PS": {"descripcion": "Junior Suite con jacuzzi en terraza", "max_pax": 3},
                            "TRS ST JACUZZI TERR PS": {"descripcion": "Suite con jacuzzi en terraza junto a piscina", "max_pax": 3},
                            "TRS ROMANCE BW BYTHE LAKE": {"descripcion": "Suite romántica junto al lago", "max_pax": 2},
                        }
                    },
                    # .........................................................
                    # Grand Palladium Select White Sand
                    # .........................................................
                    "Grand Palladium Select White Sand": {
                        "hotel_code": "MAYA_WS",
                        "imagen": "media/hoteles/riviera_maya/gp_white_sand.jpg",
                        "descripcion": "Resort premium con playa de arena blanca y servicios exclusivos",
                        "solo_adultos": False,
                        "habitaciones": {
                            "WS JUNIOR SUITE BS": {"descripcion": "Junior Suite junto a la playa", "max_pax": 8},
                            "WS JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 8},
                            "WS SUITE GARDEN VIEW": {"descripcion": "Suite con vistas al jardín tropical", "max_pax": 7},
                        }
                    }
                }
            }
        }
    },
    # =========================================================================
    # REPÚBLICA DOMINICANA
    # =========================================================================
    "Republica Dominicana": {
        "complejos": {
            # -----------------------------------------------------------------
            # PUNTA CANA
            # -----------------------------------------------------------------
            "Punta Cana": {
                "ubicacion": "Bávaro, Punta Cana",
                "mapa_imagen": "media/hoteles/punta_cana/mapa.jpg",
                "hoteles": {
                    # .........................................................
                    # Grand Palladium Select Bávaro
                    # .........................................................
                    "Grand Palladium Select Bavaro": {
                        "hotel_code": "CANA_BAV",
                        "imagen": "media/hoteles/punta_cana/gp_select_bavaro.jpg",
                        "descripcion": "Resort premium en playa Bávaro con servicios Select exclusivos",
                        "solo_adultos": False,
                        "habitaciones": {
                            "BAV JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 8},
                            "BAV PREMIUM JS GV": {"descripcion": "Junior Suite Premium con vistas al jardín", "max_pax": 7},
                            "BAV SUPERIOR JS GV": {"descripcion": "Junior Suite Superior con vistas al jardín", "max_pax": 6},
                            "BAV ROMANCE SUITE GV": {"descripcion": "Suite romántica con vistas al jardín", "max_pax": 4},
                            "BAV ROOFTOP JT JS": {"descripcion": "Junior Suite con jacuzzi en rooftop", "max_pax": 4},
                        }
                    },
                    # .........................................................
                    # Grand Palladium Palace Resort & Spa
                    # .........................................................
                    "Grand Palladium Palace Resort & Spa": {
                        "hotel_code": "CANA_PAL",
                        "imagen": "media/hoteles/punta_cana/gp_palace.jpg",
                        "descripcion": "Resort emblemático con arquitectura elegante y spa de clase mundial",
                        "solo_adultos": False,
                        "habitaciones": {
                            "PAL DELUXE BEACHSIDE": {"descripcion": "Habitación Deluxe junto a la playa", "max_pax": 5},
                            "PAL DELUXE GARDEN VIEW": {"descripcion": "Habitación Deluxe con vistas al jardín", "max_pax": 5},
                            "PAL JUNIOR SUITE BS": {"descripcion": "Junior Suite junto a la playa", "max_pax": 4},
                            "PAL JUNIOR SUITE BS OV": {"descripcion": "Junior Suite playa con vista oceánica", "max_pax": 7},
                            "PAL JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 5},
                            "PAL JUNIOR SUITE SW BS": {"descripcion": "Junior Suite Swim Up junto a la playa", "max_pax": 4},
                            "PAL LOFT SUITE GV": {"descripcion": "Loft Suite con vistas al jardín tropical", "max_pax": 8},
                            "PAL LOFT SUITE BS POV": {"descripcion": "Loft Suite playa con vista panorámica", "max_pax": 4},
                        }
                    },
                    # .........................................................
                    # Grand Palladium Punta Cana Resort & Spa
                    # .........................................................
                    "Grand Palladium Punta Cana Resort & Spa": {
                        "hotel_code": "CANA_PC",
                        "imagen": "media/hoteles/punta_cana/gp_punta_cana.jpg",
                        "descripcion": "Resort familiar con amplia oferta de actividades y entretenimiento",
                        "solo_adultos": False,
                        "habitaciones": {
                            "PC DELUXE GARDEN VIEW": {"descripcion": "Habitación Deluxe con vistas al jardín", "max_pax": 6},
                            "PC DELUXE POOLSIDE": {"descripcion": "Habitación Deluxe junto a la piscina", "max_pax": 4},
                            "PC JUNIOR SUITE GV": {"descripcion": "Junior Suite con vistas al jardín", "max_pax": 6},
                            "PC JUNIOR SUITE POOLSIDE": {"descripcion": "Junior Suite junto a la piscina", "max_pax": 4},
                            "PC LOFT SUITE GV": {"descripcion": "Loft Suite con vistas al jardín tropical", "max_pax": 7},
                        }
                    },
                    # .........................................................
                    # TRS Turquesa Hotel (Solo Adultos)
                    # .........................................................
                    "TRS Turquesa Hotel": {
                        "hotel_code": "CANA_TRS",
                        "imagen": "media/hoteles/punta_cana/trs_turquesa.jpg",
                        "descripcion": "Hotel solo adultos con playa privada y experiencia gastronómica exclusiva",
                        "solo_adultos": True,
                        "habitaciones": {
                            "TRS JUNIOR SUITE GV/PV": {"descripcion": "Junior Suite con vistas al jardín/piscina", "max_pax": 4},
                            "TRS JUNIOR SUITE PS": {"descripcion": "Junior Suite junto a la piscina", "max_pax": 3},
                            "TRS JUNIOR SUITE SWIM UP": {"descripcion": "Junior Suite Swim Up con piscina privada", "max_pax": 3},
                            "TRS ROMANCE SUITE PS": {"descripcion": "Suite romántica junto a la piscina", "max_pax": 3},
                        }
                    }
                }
            }
        }
    }
}

# =============================================================================
# REGÍMENES DE ALIMENTACIÓN
# =============================================================================
# Suplemento diario por persona sobre el precio base de la habitación
# =============================================================================

REGIMENES = {
    "All Inclusive": {
        "descripcion": "Todo incluido: comidas, bebidas premium, snacks 24h y actividades",
        "suplemento": 80
    }
}

TARIFAS = {
    "No Reembolsable": {
        "descripcion": "El mejor precio garantizado. No permite cancelaciones ni modificaciones.",
        "descuento": 0.15,
        "color": "#dc3545"
    },
    "Flexible - Paga Ahora": {
        "descripcion": "Cancelacion gratuita hasta 7 dias antes. Pago completo en el momento de la reserva.",
        "descuento": 0.05,
        "color": "#28a745"
    },
    "Flexible - Paga en Destino": {
        "descripcion": "Cancelacion gratuita hasta 7 dias antes. Pago al llegar al hotel.",
        "descuento": 0,
        "color": "#ffc107"
    }
}

# =============================================================================
# ESTADO DE LA SESION
# =============================================================================

if "paso_actual" not in st.session_state:
    st.session_state.paso_actual = 1
if "destino_seleccionado" not in st.session_state:
    st.session_state.destino_seleccionado = None
if "complejo_seleccionado" not in st.session_state:
    st.session_state.complejo_seleccionado = None
if "hotel_seleccionado" not in st.session_state:
    st.session_state.hotel_seleccionado = None
if "reserva_datos" not in st.session_state:
    st.session_state.reserva_datos = {}
if "reservas" not in st.session_state:
    st.session_state.reservas = {}
if "area" not in st.session_state:
    st.session_state.area = "reservas"
if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = []
if "chat_abierto" not in st.session_state:
    st.session_state.chat_abierto = False
if "reserva_confirmada" not in st.session_state:
    st.session_state.reserva_confirmada = None
if "chat_imagenes" not in st.session_state:
    st.session_state.chat_imagenes = []

# =============================================================================
# FUNCIONES
# =============================================================================

# Códigos de complejo para ID de reserva (últimos 5 dígitos)
CODIGOS_COMPLEJO = {
    "Costa Mujeres": "09601",
    "Riviera Maya": "10601", 
    "Punta Cana": "10701"
}

def generar_numero_reserva(complejo):
    """
    Genera un número de reserva con el formato real del dataset:
    - 7 dígitos secuenciales (aleatorios en rango 6100000-6999999)
    - 5 dígitos código de complejo
    Ejemplo: 610012309601 (Costa Mujeres)
    """
    secuencial = random.randint(6100000, 6999999)
    codigo_complejo = CODIGOS_COMPLEJO.get(complejo, "10601")
    return f"{secuencial}{codigo_complejo}"

def calcular_probabilidad_cancelacion(reserva):
    return random.uniform(0.15, 0.55)

def cambiar_paso(nuevo_paso):
    st.session_state.paso_actual = nuevo_paso

def seleccionar_destino(destino):
    st.session_state.destino_seleccionado = destino
    st.session_state.paso_actual = 2

def seleccionar_hotel(hotel):
    st.session_state.hotel_seleccionado = hotel

def cambiar_area(nueva_area):
    st.session_state.area = nueva_area

# -------------------------------------------------------------------------
# EJECUTOR DE ACCIONES DEL AGENTE
# -------------------------------------------------------------------------
def ejecutar_acciones(acciones):
    """Ejecuta las acciones devueltas por el agente."""
    for accion in acciones:
        funcion = accion.get("funcion", "")
        params = accion.get("parametros", {})
        
        try:
            if funcion == "seleccionar_destino":
                pais = params.get("pais", "Mexico")
                if "dominicana" in pais.lower() or "punta" in pais.lower():
                    st.session_state.destino_seleccionado = "Republica Dominicana"
                else:
                    st.session_state.destino_seleccionado = "Mexico"
                st.session_state.paso_actual = 2
            
            elif funcion == "seleccionar_complejo":
                complejo = params.get("complejo", "")
                # Mapear nombres
                if "costa" in complejo.lower() or "mujeres" in complejo.lower():
                    st.session_state.complejo_seleccionado = "Costa Mujeres"
                    st.session_state.destino_seleccionado = "Mexico"
                elif "riviera" in complejo.lower() or "maya" in complejo.lower():
                    st.session_state.complejo_seleccionado = "Riviera Maya"
                    st.session_state.destino_seleccionado = "Mexico"
                elif "punta" in complejo.lower() or "cana" in complejo.lower():
                    st.session_state.complejo_seleccionado = "Punta Cana"
                    st.session_state.destino_seleccionado = "Republica Dominicana"
                st.session_state.paso_actual = 2
            
            elif funcion == "seleccionar_hotel":
                hotel = params.get("hotel", "")
                st.session_state.hotel_seleccionado = hotel
                st.session_state.paso_actual = 3
            
            elif funcion == "configurar_fechas":
                llegada_str = params.get("llegada", "")
                try:
                    noches = int(params.get("noches", 7))
                except:
                    noches = 7
                    
                if llegada_str:
                    from datetime import datetime
                    try:
                        llegada = datetime.strptime(llegada_str, "%Y-%m-%d").date()
                        st.session_state.reserva_datos["fecha_entrada"] = llegada
                        st.session_state.reserva_datos["noches"] = noches
                        
                        # Actualizar widgets UI
                        st.session_state.w_llegada = llegada
                        st.session_state.w_salida = llegada + timedelta(days=noches)
                    except:
                        pass
            
            elif funcion == "configurar_huespedes":
                try:
                    adultos = int(params.get("adultos", 2))
                except:
                    adultos = 2
                
                try:
                    ninos = int(params.get("ninos", 0))
                except:
                    ninos = 0
                    
                st.session_state.reserva_datos["adultos"] = adultos
                st.session_state.reserva_datos["ninos"] = ninos
                
                # Actualizar widgets UI
                st.session_state.w_adultos = adultos
                st.session_state.w_ninos = ninos
            
            elif funcion == "seleccionar_habitacion":
                hab = params.get("habitacion", "")
                if hab:
                    # Intentar asignar directamente. Si no coincide con las opciones del widget, 
                    # Streamlit lanzará warning o lo ignorará en el render si no validamos,
                    # pero como w_habitacion se usa de value en st.radio, debería funcionar si es exacto.
                    # Idealmente haríamos fuzzy matching, pero confiamos en el agente.
                    st.session_state.w_habitacion = hab
            
            elif funcion == "seleccionar_regimen":
                reg = params.get("regimen", "")
                if reg:
                    # Normalizar valores comunes a los válidos
                    reg_normalizado = "All Inclusive"  # Solo hay una opción
                    if any(x in reg.lower() for x in ["todo", "all", "incluido", "inclusive"]):
                        reg_normalizado = "All Inclusive"
                    st.session_state.w_regimen = reg_normalizado
            
            elif funcion == "seleccionar_tarifa":
                tarifa = params.get("tarifa", "")
                if tarifa:
                    st.session_state.tarifa_seleccionada = tarifa
            
            elif funcion == "marcar_fidelidad":
                # Manejar varios formatos posibles del valor
                es_fid = params.get("es_fidelizado", False)
                if isinstance(es_fid, str):
                    es_fid = es_fid.lower() in ["true", "si", "sí", "yes", "1"]
                st.session_state.es_fidelizado = bool(es_fid)
                if st.session_state.es_fidelizado:
                    st.session_state.chat_historial.append({"role": "assistant", "content": "✨ Marcado como cliente Palladium Rewards. ¡Tendrás acceso a beneficios exclusivos!"})
            
            elif funcion == "confirmar_reserva":
                # Lógica de confirmación REAL para el agente
                # Intentamos reconstruir los datos desde session_state
                try:
                    c_compl = st.session_state.get("complejo_seleccionado", "Riviera Maya")
                    c_hotel = st.session_state.get("hotel_seleccionado", "Grand Palladium Colonial")
                    c_hab = "Junior Suite" # Default si no hay
                    
                    # Generar reserva
                    numero = generar_numero_reserva(c_compl)
                    
                    # Guardar básica (si faltan datos, usamos defaults seguros para no romper flujo)
                    reserva_agente = {
                        "numero": numero,
                        "fecha_creacion": datetime.now(),
                        "destino": st.session_state.get("destino_seleccionado", "Mexico"),
                        "complejo": c_compl,
                        "hotel": c_hotel,
                        "habitacion": c_hab,
                        "fecha_entrada": st.session_state.get("reserva_datos", {}).get("fecha_entrada", datetime.now().date()),
                        "fecha_salida": st.session_state.get("reserva_datos", {}).get("fecha_entrada", datetime.now().date()) + timedelta(days=7),
                        "noches": st.session_state.get("reserva_datos", {}).get("noches", 7),
                        "adultos": st.session_state.get("reserva_datos", {}).get("adultos", 2),
                        "ninos": st.session_state.get("reserva_datos", {}).get("ninos", 0),
                        "total_pax": 2,
                        "regimen": "All Inclusive",
                        "tarifa": "Flexible",
                        "precio_total": 0.0, # Pendiente de calculo real
                        "tiene_rewards": False
                    }
                    
                    st.session_state.reservas[numero] = reserva_agente
                    st.session_state.reserva_confirmada = numero
                    
                    # Persistir CSV simplificado
                    try:
                        nueva_row = {
                            "ID_RESERVA": numero,
                            "NOMBRE_HOTEL": c_hotel,
                            "LLEGADA": reserva_agente["fecha_entrada"].strftime("%Y-%m-%d"),
                            "SALIDA": reserva_agente["fecha_salida"].strftime("%Y-%m-%d"),
                            "FECHA_TOMA": datetime.now().strftime("%Y-%m-%d"),
                            "VALOR_RESERVA": 0,
                            "PROB_CANCELACION": 0.1,
                            "CANCELADO": 0,
                            "CANAL_CONSOLIDADO": "AGENTE_WEB",
                            "PAIS_TOP": "España"
                        }
                        try:
                            df_ex = pd.read_csv(CSV_RESERVAS)
                        except Exception as read_err:
                            print(f"[DEBUG] No se pudo leer CSV existente: {read_err}")
                            df_ex = pd.DataFrame()
                        
                        df_new = pd.DataFrame([nueva_row])
                        df_updated = pd.concat([df_ex, df_new], ignore_index=True)
                        df_updated.to_csv(CSV_RESERVAS, index=False)
                        print(f"[DEBUG] CSV guardado: {CSV_RESERVAS} - Total filas: {len(df_updated)}")
                        
                        st.cache_data.clear()
                        # Recargar DataFrame completo desde CSV para tener todas las columnas
                        st.session_state.df_reservas = pd.read_csv(CSV_RESERVAS)
                        for col in ['LLEGADA', 'SALIDA', 'FECHA_TOMA']:
                            if col in st.session_state.df_reservas.columns:
                                st.session_state.df_reservas[col] = pd.to_datetime(st.session_state.df_reservas[col], errors='coerce')

                    except Exception as e:
                        print(f"[ERROR] Persistencia fallida: {e}")
                        st.error(f"Error guardando reserva: {e}")
                        
                    st.session_state.paso_actual = 4
                    st.session_state.chat_historial.append({"role": "assistant", "content": f"✅ Reserva {numero} confirmada correctamente."})
                except Exception as e:
                    st.error(f"Error confirmando: {e}")

            # --- FUNCIONES INTRANET ---
            elif funcion == "consultar_ocupacion":
                mes = params.get("mes", "febrero")
                anio = params.get("anio", 2026)
                
                # Mapeo de nombres de mes a números
                meses_map = {
                    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                }
                
                if "df_reservas" in st.session_state and not st.session_state.df_reservas.empty:
                    df = st.session_state.df_reservas.copy()
                    
                    # Filtrar por mes si tenemos la columna LLEGADA
                    mes_num = meses_map.get(mes.lower(), 2)
                    if 'LLEGADA' in df.columns:
                        df_mes = df[df['LLEGADA'].dt.month == mes_num]
                    else:
                        df_mes = df
                    
                    ventas = df_mes['VALOR_RESERVA'].sum() if 'VALOR_RESERVA' in df_mes.columns else 0
                    reservas = len(df_mes)
                    
                    msg_sys = f"📊 **Datos de {mes.capitalize()} {anio}:**\n"
                    msg_sys += f"- Reservas para el mes: {reservas}\n"
                    msg_sys += f"- Ingresos estimados: ${ventas:,.0f}\n"
                    msg_sys += f"- ADR medio: ${ventas/reservas:,.0f}" if reservas > 0 else ""
                    st.session_state.chat_historial.append({"role": "assistant", "content": msg_sys})
                else:
                    st.session_state.chat_historial.append({"role": "assistant", "content": "⚠️ No hay datos cargados en el sistema."})

            elif funcion == "analizar_cancelaciones":
                mes = params.get("mes", None)
                top_n = int(params.get("top", 3))  # Por defecto top 3
                
                meses_map = {
                    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                }
                
                if "df_reservas" in st.session_state and not st.session_state.df_reservas.empty:
                    df = st.session_state.df_reservas.copy()
                    
                    # Filtrar por mes si se especifica
                    if mes and 'LLEGADA' in df.columns:
                        mes_num = meses_map.get(mes.lower(), None)
                        if mes_num:
                            df = df[df['LLEGADA'].dt.month == mes_num]
                    
                    # Calcular estadísticas
                    tasa = df['PROB_CANCELACION'].mean() * 100 if 'PROB_CANCELACION' in df.columns else 0
                    riesgo_alto = len(df[df['PROB_CANCELACION'] > 0.4]) if 'PROB_CANCELACION' in df.columns else 0
                    
                    # Top N con mayor riesgo
                    df_sorted = df.sort_values('PROB_CANCELACION', ascending=False).head(top_n)
                    
                    titulo_mes = f" de {mes.capitalize()}" if mes else ""
                    msg_sys = f"📉 **Análisis de Riesgo{titulo_mes}:**\n"
                    msg_sys += f"- Total reservas analizadas: {len(df)}\n"
                    msg_sys += f"- Tasa promedio cancelación: {tasa:.1f}%\n"
                    msg_sys += f"- Reservas en riesgo alto (>40%): {riesgo_alto}\n\n"
                    msg_sys += f"**Top {top_n} reservas con mayor riesgo:**\n"
                    
                    for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
                        id_res = row.get('ID_RESERVA', 'N/A')
                        hotel = row.get('NOMBRE_HOTEL', 'N/A')
                        prob = row.get('PROB_CANCELACION', 0) * 100
                        valor = row.get('VALOR_RESERVA', 0)
                        msg_sys += f"{i}. **{id_res}** - {hotel} - Riesgo: {prob:.1f}% - ${valor:,.0f}\n"
                    
                    st.session_state.chat_historial.append({"role": "assistant", "content": msg_sys})

            elif funcion == "consultar_reserva_especifica":
                id_res = params.get("id_reserva", "")
                if "df_reservas" in st.session_state and id_res:
                    df = st.session_state.df_reservas
                    # Buscar por ID (string match)
                    res = df[df['ID_RESERVA'].astype(str).str.contains(str(id_res))]
                    if not res.empty:
                        r = res.iloc[0]
                        detalles = f"**Reserva {r['ID_RESERVA']}**\n"
                        detalles += f"- Hotel: {r.get('NOMBRE_HOTEL', 'N/A')}\n"
                        detalles += f"- Llegada: {r.get('LLEGADA', 'N/A')}\n"
                        detalles += f"- Valor: ${r.get('VALOR_RESERVA', 0):,.0f}\n"
                        detalles += f"- Prob. Cancelación: {r.get('PROB_CANCELACION', 0):.1%}\n"
                        detalles += f"- Canal: {r.get('CANAL_CONSOLIDADO', 'N/A')}\n"
                        detalles += f"- País: {r.get('PAIS_TOP', 'N/A')}"
                        st.session_state.chat_historial.append({"role": "assistant", "content": detalles})
                    else:
                        st.session_state.chat_historial.append({"role": "assistant", "content": f"❌ Reserva {id_res} no encontrada."})

            elif funcion == "resumen_general":
                if "df_reservas" in st.session_state and not st.session_state.df_reservas.empty:
                    df = st.session_state.df_reservas
                    msg = "📊 **RESUMEN GENERAL DEL SISTEMA:**\n\n"
                    msg += f"- Total reservas: {len(df)}\n"
                    msg += f"- Valor total: ${df['VALOR_RESERVA'].sum():,.0f}\n"
                    msg += f"- Tasa cancelación media: {df['PROB_CANCELACION'].mean()*100:.1f}%\n"
                    msg += f"- Reservas alto riesgo (>40%): {len(df[df['PROB_CANCELACION'] > 0.4])}\n"
                    
                    if 'NOMBRE_HOTEL' in df.columns:
                        top_hotel = df['NOMBRE_HOTEL'].value_counts().head(1)
                        if not top_hotel.empty:
                            msg += f"- Hotel más reservado: {top_hotel.index[0]} ({top_hotel.values[0]} reservas)"
                    
                    st.session_state.chat_historial.append({"role": "assistant", "content": msg})

        except Exception as e:
            pass  # Si falla una acción, continuar con las demás

# -------------------------------------------------------------------------
# INTERFAZ DEL CHAT V2 (Reutilizable en columnas)
# -------------------------------------------------------------------------
def render_chat_v2():
    """Renderiza el chat del agente V2 en el contenedor actual."""
    if not AGENT_AVAILABLE:
        st.warning("Agente no disponible. Verifica agent_v2.py")
        return

    st.markdown("### 💬 Asistente Palladium")
    st.caption("Pregúntame sobre hoteles o dime qué quieres reservar")
    
    # Contenedor de mensajes
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.chat_historial:
            st.info("👋 ¡Hola! Puedo ayudarte a:\n- Encontrar el hotel perfecto\n- Comparar precios\n- Hacer tu reserva paso a paso")
        
        for i, msg in enumerate(st.session_state.chat_historial):
            if msg["role"] == "user":
                st.markdown(f"**Tú:** {msg['content']}")
            else:
                st.markdown(f"**🤖:** {msg['content']}")
                # Mostrar imagen si hay
                if i < len(st.session_state.chat_imagenes) and st.session_state.chat_imagenes[i]:
                    try:
                        st.image(st.session_state.chat_imagenes[i], width=300)
                    except:
                        pass
    
    # Input de mensaje
    user_input = st.text_input(
        "Mensaje",
        key="chat_input_v2",
        placeholder="Ej: Quiero ir a Cancún en junio...",
        label_visibility="collapsed"
    )
    
    col_enviar, col_limpiar = st.columns([2, 1])
    with col_enviar:
        enviar = st.button("Enviar", key="btn_enviar_v2", use_container_width=True)
    with col_limpiar:
        if st.button("🗑️", key="btn_limpiar_v2", use_container_width=True):
            st.session_state.chat_historial = []
            st.session_state.chat_imagenes = []
            st.rerun()
    
    if enviar and user_input:
        # Añadir mensaje del usuario
        st.session_state.chat_historial.append({"role": "user", "content": user_input})
        st.session_state.chat_imagenes.append(None)
        
        # Estado actual para contexto
        estado_reserva = {
            "destino": st.session_state.destino_seleccionado,
            "complejo": st.session_state.complejo_seleccionado,
            "hotel": st.session_state.hotel_seleccionado,
            "paso_actual": st.session_state.paso_actual,
            "modo": st.session_state.get("modo_actual", "Reservas")  # IMPORTANTE: modo actual
        }
        
        # Obtener respuesta del agente
        with st.spinner("Pensando..."):
            resultado = chat_con_acciones(
                user_input, 
                st.session_state.chat_historial[:-1],
                estado_reserva
            )
        
        # Procesar respuesta
        mensaje = resultado.get("mensaje", "No pude procesar tu mensaje.")
        acciones = resultado.get("acciones", [])
        imagen_hotel = resultado.get("imagen", None)
        
        # Ejecutar acciones
        if acciones:
            ejecutar_acciones(acciones)
        
        # Añadir respuesta
        st.session_state.chat_historial.append({"role": "assistant", "content": mensaje})
        
        # Añadir imagen si existe
        if imagen_hotel:
            img_path = obtener_imagen_hotel(imagen_hotel)
            st.session_state.chat_imagenes.append(img_path)
        else:
            st.session_state.chat_imagenes.append(None)
        # Limpiar input antes de rerun
        if "chat_input_v2" in st.session_state:
            del st.session_state["chat_input_v2"]
        
        st.rerun()

# =============================================================================
# ESTILOS CSS PROFESIONALES
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Lato:wght@300;400;500;600&display=swap');
    
    :root {
        --dorado: #C9A227;
        --dorado-oscuro: #A68523;
        --azul: #1B365D;
        --azul-claro: #2A4A7A;
        --blanco: #FFFFFF;
        --gris-claro: #F5F5F5;
        --gris: #E0E0E0;
    }
    
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        color: #333;
    }
    
    /* Fondo igual al del logo */
    .stApp {
        background-color: rgb(254, 254, 254) !important;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: var(--azul);
    }
    
    /* Ocultar menú y footer, pero dejar header visible para el sidebar toggle */
    #MainMenu, footer {visibility: hidden;}
    /* header {visibility: visible !important;} */
    
    /* Sidebar nativo limpio */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Contenedor principal */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
        background-color: rgb(254, 254, 254) !important;
    }
    
    /* Header principal */
    .header-bar {
        background: var(--azul);
        padding: 15px 50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 0 -1rem;
    }
    
    .header-logo img {
        height: 50px;
    }
    
    .header-nav {
        display: flex;
        gap: 20px;
    }
    
    .nav-link {
        color: white;
        text-decoration: none;
        font-size: 14px;
        letter-spacing: 1px;
        padding: 8px 20px;
        border-radius: 3px;
        cursor: pointer;
        transition: background 0.3s;
    }
    
    .nav-link:hover {
        background: rgba(255,255,255,0.1);
    }
    
    .nav-link.active {
        background: var(--dorado);
        color: var(--azul);
    }
    
    /* Indicador de pasos */
    .pasos-container {
        display: flex;
        justify-content: center;
        padding: 30px 0;
        background: var(--gris-claro);
        margin: 0 -1rem 30px -1rem;
    }
    
    .paso {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 30px;
    }
    
    .paso-numero {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--gris);
        color: #666;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 14px;
    }
    
    .paso-activo .paso-numero {
        background: var(--dorado);
        color: var(--azul);
    }
    
    .paso-completado .paso-numero {
        background: var(--azul);
        color: white;
    }
    
    .paso-texto {
        font-size: 13px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .paso-activo .paso-texto {
        color: var(--azul);
        font-weight: 600;
    }
    
    .paso-linea {
        width: 60px;
        height: 2px;
        background: var(--gris);
    }
    
    /* Titulo de seccion */
    .seccion-titulo {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .seccion-titulo h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        font-weight: 400;
    }
    
    .seccion-titulo p {
        color: #666;
        font-size: 1.1em;
    }
    
    /* Cards de pais */
    .pais-card {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        border: 2px solid transparent;
    }
    
    .pais-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: var(--dorado);
    }
    
    .pais-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    
    .pais-card-info {
        padding: 20px;
        text-align: center;
    }
    
    .pais-card-info h3 {
        margin: 0;
        font-size: 1.3em;
    }
    
    .pais-card-info p {
        color: #888;
        margin: 5px 0 0;
        font-size: 0.9em;
    }
    
    /* Hotel card */
    .hotel-card {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        display: flex;
        margin-bottom: 20px;
    }
    
    .hotel-card img {
        width: 400px;
        height: 250px;
        object-fit: cover;
    }
    
    .hotel-card-info {
        padding: 30px;
        flex: 1;
    }
    
    .hotel-card-info h3 {
        margin: 0 0 10px;
        font-size: 1.5em;
    }
    
    .hotel-ubicacion {
        color: var(--dorado);
        font-size: 0.95em;
        margin-bottom: 15px;
    }
    
    /* Habitacion card */
    .habitacion-card {
        background: white;
        border: 1px solid var(--gris);
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 20px;
        transition: border-color 0.3s;
    }
    
    .habitacion-card:hover {
        border-color: var(--dorado);
    }
    
    .habitacion-card-content {
        display: flex;
    }
    
    .habitacion-card img {
        width: 280px;
        height: 180px;
        object-fit: cover;
    }
    
    .habitacion-info {
        padding: 20px;
        flex: 1;
    }
    
    .habitacion-info h4 {
        margin: 0 0 8px;
        color: var(--azul);
        font-size: 1.2em;
    }
    
    .habitacion-precio {
        font-size: 1.5em;
        color: var(--dorado);
        font-weight: 600;
    }
    
    .habitacion-amenities {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    
    .amenity-tag {
        background: var(--gris-claro);
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        color: #666;
    }
    
    /* Tarifa card */
    .tarifa-card {
        border: 2px solid var(--gris);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .tarifa-card:hover {
        border-color: var(--dorado);
    }
    
    .tarifa-card.seleccionada {
        border-color: var(--dorado);
        background: rgba(201,162,39,0.08);
    }
    
    .tarifa-nombre {
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    
    .tarifa-descripcion {
        color: #666;
        font-size: 0.9em;
    }
    
    /* Botones */
    .btn-primario {
        background: var(--dorado);
        color: var(--azul);
        border: none;
        padding: 15px 40px;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.3s;
    }
    
    .btn-primario:hover {
        background: var(--dorado-oscuro);
    }
    
    .btn-secundario {
        background: transparent;
        color: var(--azul);
        border: 2px solid var(--azul);
        padding: 13px 38px;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-secundario:hover {
        background: var(--azul);
        color: white;
    }
    
    .stButton > button {
        background: var(--dorado) !important;
        color: var(--azul) !important;
        border: none !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    
    /* Resultado final */
    .reserva-confirmada {
        background: linear-gradient(135deg, var(--azul) 0%, var(--azul-claro) 100%);
        color: white;
        padding: 60px;
        border-radius: 12px;
        text-align: center;
        margin: 40px auto;
        max-width: 700px;
    }
    
    .reserva-confirmada h2 {
        color: var(--dorado);
        font-size: 2em;
        margin-bottom: 20px;
    }
    
    .codigo-reserva {
        font-size: 2.5em;
        color: var(--dorado);
        font-weight: 600;
        letter-spacing: 5px;
        margin: 25px 0;
        font-family: 'Lato', sans-serif;
    }
    
    .precio-final {
        font-size: 3em;
        color: var(--dorado);
        font-weight: 600;
        margin: 30px 0 10px;
    }
    
    /* Mapa placeholder */
    .mapa-container {
        background: #eee;
        border-radius: 8px;
        height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
        font-size: 1.2em;
        margin: 20px 0;
        background-image: url('https://www.palladiumhotelgroup.com/content/dam/phg/hotels/jamaica/grandpalladiumjamaica/desktop/MAPA/mapa-jamaica.jpg');
        background-size: cover;
        background-position: center;
    }
    
    /* Footer */
    .footer {
        background: var(--azul);
        color: white;
        text-align: center;
        padding: 30px;
        margin: 50px -1rem -1rem;
    }
    
    .footer p {
        margin: 5px 0;
        font-size: 0.9em;
        opacity: 0.8;
    }
    
    /* Reducir espacio entre marcas y footer */
    hr {
        margin: 20px 0 10px 0 !important;
    }
    
    /* Chat flotante emergente */
    .chat-container {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 400px;
        max-height: 500px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        z-index: 9998;
        overflow: hidden;
        display: none;
    }
    
    .chat-container.visible {
        display: flex;
        flex-direction: column;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #1B365D 0%, #2A4A7A 100%);
        color: white;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-header h4 {
        margin: 0;
        color: #C9A227;
    }
    
    .chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
    }
    
    .chat-messages {
        flex: 1;
        padding: 15px;
        overflow-y: auto;
        max-height: 300px;
        background: #f9f9f9;
    }
    
    .chat-msg {
        margin-bottom: 12px;
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 85%;
    }
    
    .chat-msg.user {
        background: #1B365D;
        color: white;
        margin-left: auto;
    }
    
    .chat-msg.assistant {
        background: white;
        border: 1px solid #e0e0e0;
    }
    
    .chat-msg img {
        max-width: 100%;
        border-radius: 8px;
        margin-top: 8px;
    }
    
    .chat-input-area {
        padding: 15px;
        border-top: 1px solid #e0e0e0;
        display: flex;
        gap: 10px;
    }
    
    .chat-input-area input {
        flex: 1;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 25px;
        outline: none;
    }
    
    .chat-input-area button {
        background: #C9A227;
        color: #1B365D;
        border: none;
        padding: 12px 20px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
    }
    
    /* Botón flotante para abrir chat */
    .agent-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #C69C5D 0%, #8B6914 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    
    .agent-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.4);
    }
    
    .agent-button .icon {
        width: 35px;
        height: 35px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    
    .agent-button .text {
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Form sections */
    .form-section {
        background: white;
        border: 1px solid var(--gris);
        border-radius: 8px;
        padding: 30px;
        margin-bottom: 25px;
    }
    
    .form-section h3 {
        margin: 0 0 20px;
        font-size: 1.3em;
        padding-bottom: 15px;
        border-bottom: 1px solid var(--gris);
    }
    /* Estilos Chat Flotante */
    .chat-window {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 380px;
        height: 600px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 5px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #e0e0e0;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #1B365D 0%, #2A4A7A 100%);
        color: white;
        padding: 15px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .fixed-chat-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10001;
    }
    
    /* Ajustes para contenedor de mensajes */
    .stChatMessage {
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================

# Logo centrado (20% mas pequeño)
col_vacio1, col_logo, col_vacio2 = st.columns([1.5, 1.5, 1.5])
with col_logo:
    st.image("3.jpg", use_container_width=True)

# Navegacion Reservas / Intranet
st.markdown("<br>", unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
with col_nav2:
    area = st.radio("", ["Reservas", "Intranet"], horizontal=True, label_visibility="collapsed")
    st.session_state.modo_actual = area  # Guardar modo para el agente

st.markdown("---")

# =============================================================================
# LAYOUT PRINCIPAL (Contenido + Chat)
# =============================================================================

# =============================================================================
# LAYOUT PRINCIPAL (Contenido + Sidebar)
# =============================================================================

# Cargar datos globales para Intranet (si no existen)
if "df_reservas" not in st.session_state:
    try:
        st.session_state.df_reservas = pd.read_csv(CSV_RESERVAS)
        # Parsear fechas si existen las columnas
        for col in ['LLEGADA', 'SALIDA', 'FECHA_TOMA']:
            if col in st.session_state.df_reservas.columns:
                st.session_state.df_reservas[col] = pd.to_datetime(st.session_state.df_reservas[col], errors='coerce')
    except:
        st.session_state.df_reservas = pd.DataFrame()

# Configuración Sidebar Nativo
with st.sidebar:
    st.image("3.jpg", use_container_width=True)
    st.markdown("### Asistente Virtual")
    st.caption("Palladium Hotel Group")
    st.markdown("---")
    render_chat_v2()

# Contenedor principal
col_contenido = st.container()

# Renderizar contenido principal
with col_contenido:
    # =============================================================================
    # PANTALLA 1: SELECCIÓN DE DESTINO
    # =============================================================================
    if st.session_state.paso_actual == 1:
        st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Seleccione su destino</h1>", unsafe_allow_html=True)






# Renderizar contenido principal en columna izquierda
with col_contenido:
    # =============================================================================
    # AREA: RESERVAS
    # =============================================================================
    
    if area == "Reservas":
    
        # Indicador de pasos
        paso = st.session_state.paso_actual
    
        st.markdown(f"""
        <div class="pasos-container">
            <div class="paso {'paso-activo' if paso == 1 else 'paso-completado' if paso > 1 else ''}">
                <div class="paso-numero">1</div>
                <span class="paso-texto">Destino</span>
            </div>
            <div class="paso-linea"></div>
            <div class="paso {'paso-activo' if paso == 2 else 'paso-completado' if paso > 2 else ''}">
                <div class="paso-numero">2</div>
                <span class="paso-texto">Hotel</span>
            </div>
            <div class="paso-linea"></div>
            <div class="paso {'paso-activo' if paso == 3 else 'paso-completado' if paso > 3 else ''}">
                <div class="paso-numero">3</div>
                <span class="paso-texto">Habitacion</span>
            </div>
            <div class="paso-linea"></div>
            <div class="paso {'paso-activo' if paso == 4 else ''}">
                <div class="paso-numero">4</div>
                <span class="paso-texto">Confirmacion</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        # -------------------------------------------------------------------------
        # PASO 1: SELECCIONAR DESTINO
        # -------------------------------------------------------------------------
        if paso == 1:
            st.markdown("""
            <div class="seccion-titulo">
                <h1>Seleccione su destino</h1>
                <p>Descubra nuestros resorts de lujo en el Caribe</p>
            </div>
            """, unsafe_allow_html=True)
        
            # Botones de destinos centrados (2 destinos)
            col_vacio1, col_dest1, col_dest2, col_vacio2 = st.columns([1, 1.5, 1.5, 1])
            destinos_lista = list(DESTINOS.keys())
        
            with col_dest1:
                if st.button(destinos_lista[0], key=f"dest_{destinos_lista[0]}", use_container_width=True):
                    st.session_state.destino_seleccionado = destinos_lista[0]
                    st.session_state.paso_actual = 2
                    st.rerun()
        
            with col_dest2:
                if st.button(destinos_lista[1], key=f"dest_{destinos_lista[1]}", use_container_width=True):
                    st.session_state.destino_seleccionado = destinos_lista[1]
                    st.session_state.paso_actual = 2
                    st.rerun()
    
        # -------------------------------------------------------------------------
        # PASO 2: SELECCIONAR COMPLEJO Y HOTEL
        # -------------------------------------------------------------------------
        elif paso == 2:
            destino = st.session_state.destino_seleccionado
            complejos = DESTINOS[destino]["complejos"]
        
            st.markdown(f"""
            <div class="seccion-titulo">
                <h1>Hoteles en {destino}</h1>
                <p>Seleccione el complejo y hotel que mejor se adapte a sus necesidades</p>
            </div>
            """, unsafe_allow_html=True)
        
            # Mostrar complejos y sus hoteles
            for nombre_complejo, datos_complejo in complejos.items():
                st.markdown(f"## {nombre_complejo}")
                st.caption(f"📍 {datos_complejo['ubicacion']}")
            
                # Grid de hoteles del complejo
                hoteles_list = list(datos_complejo["hoteles"].items())
            
                for nombre_hotel, datos_hotel in hoteles_list:
                    col_img, col_info = st.columns([1, 2])
                
                    with col_img:
                        try:
                            st.image(datos_hotel["imagen"], use_container_width=True)
                        except:
                            st.info(f"📷 {nombre_hotel}")
                
                    with col_info:
                        st.markdown(f"### {nombre_hotel}")
                        st.write(datos_hotel["descripcion"])
                        st.caption(f"Habitaciones disponibles: {len(datos_hotel['habitaciones'])}")
                    
                        if st.button("SELECCIONAR HOTEL", key=f"hotel_{nombre_hotel}"):
                            st.session_state.hotel_seleccionado = nombre_hotel
                            st.session_state.complejo_seleccionado = nombre_complejo
                            st.session_state.paso_actual = 3
                            st.rerun()
                
                    st.markdown("---")
        
            # Navegacion del paso
            col_atras, col_espacio, col_adelante = st.columns([1, 2, 1])
            with col_atras:
                if st.button("ATRAS", key="paso2_atras", use_container_width=True):
                    st.session_state.paso_actual = 1
                    st.rerun()
    
        # -------------------------------------------------------------------------
        # PASO 3: SELECCIONAR HABITACION Y OPCIONES
        # -------------------------------------------------------------------------
        # Cálculo de precio: suma de ADR por cada noche según el mes
        # PRECIOS_ADR[hotel_code][habitacion][pax][mes] = adr por persona
        # -------------------------------------------------------------------------
        elif paso == 3:
            destino = st.session_state.destino_seleccionado
            complejo = st.session_state.complejo_seleccionado
            hotel = st.session_state.hotel_seleccionado
        
            # Obtener datos del hotel seleccionado
            datos_hotel = DESTINOS[destino]["complejos"][complejo]["hoteles"][hotel]
            hotel_code = datos_hotel["hotel_code"]
            habitaciones_hotel = datos_hotel["habitaciones"]  # Ahora es un diccionario
        
            st.markdown(f"""
            <div class="seccion-titulo">
                <h1>Configure su estancia</h1>
                <p>{hotel}</p>
            </div>
            """, unsafe_allow_html=True)
        
            # Columna izquierda: Fechas y huespedes
            col1, col2 = st.columns([1, 1])
        
            with col1:
                st.markdown('<div class="form-section"><h3>Fechas y huéspedes</h3>', unsafe_allow_html=True)
            
                # Inicializar keys si no existen para evitar errores
                if "w_llegada" not in st.session_state: st.session_state.w_llegada = datetime.now().date() + timedelta(days=30)
                if "w_salida" not in st.session_state: st.session_state.w_salida = datetime.now().date() + timedelta(days=37)
                if "w_adultos" not in st.session_state: st.session_state.w_adultos = 2
                if "w_ninos" not in st.session_state: st.session_state.w_ninos = 0

                fecha_entrada = st.date_input("Llegada", value=st.session_state.w_llegada, key="w_llegada")
                fecha_salida = st.date_input("Salida", value=st.session_state.w_salida, key="w_salida")
                noches = max((fecha_salida - fecha_entrada).days, 1)
                st.caption(f"Estancia: {noches} noches")
            
                col_a, col_n = st.columns(2)
                with col_a:
                    adultos = st.number_input("Adultos", min_value=1, max_value=6, value=st.session_state.w_adultos, key="w_adultos")
                with col_n:
                    # Si es solo adultos, no mostrar ninos
                    if datos_hotel.get("solo_adultos", False):
                        ninos = 0
                        st.caption("Hotel solo adultos")
                    else:
                        ninos = st.number_input("Niños", min_value=0, max_value=4, value=st.session_state.w_ninos, key="w_ninos")
            
                total_pax = adultos + ninos
                st.markdown('</div>', unsafe_allow_html=True)
            
                # Regimen
                st.markdown('<div class="form-section"><h3>Régimen</h3>', unsafe_allow_html=True)
                # Inicializar si no existe
                if "w_regimen" not in st.session_state: st.session_state.w_regimen = "All Inclusive"
                regimen = st.radio("", list(REGIMENES.keys()), label_visibility="collapsed", key="w_regimen")
                st.caption(REGIMENES[regimen]["descripcion"])
                st.markdown('</div>', unsafe_allow_html=True)
        
            with col2:
                # Tipo de habitacion - usando las del hotel seleccionado (diccionario)
                st.markdown('<div class="form-section"><h3>Tipo de habitación</h3>', unsafe_allow_html=True)
            
                # Filtrar habitaciones que permitan el total de huespedes
                habitaciones_disponibles = {
                    nombre: datos for nombre, datos in habitaciones_hotel.items()
                    if datos["max_pax"] >= total_pax
                }
            
                if not habitaciones_disponibles:
                    st.warning(f"No hay habitaciones para {total_pax} personas. Reduzca el número de huéspedes.")
                    habitaciones_disponibles = habitaciones_hotel  # Mostrar todas como fallback
            
                # Inicializar w_habitacion si hace falta
                if "w_habitacion" not in st.session_state: 
                    st.session_state.w_habitacion = list(habitaciones_disponibles.keys())[0]
                elif st.session_state.w_habitacion not in habitaciones_disponibles:
                     st.session_state.w_habitacion = list(habitaciones_disponibles.keys())[0]

                habitacion_sel = st.radio(
                    "", 
                    list(habitaciones_disponibles.keys()), 
                    label_visibility="collapsed",
                    format_func=lambda x: f"{x} (máx. {habitaciones_disponibles[x]['max_pax']} personas)",
                    key="w_habitacion"
                )
            
                # Mostrar descripcion de la habitacion seleccionada
                if habitacion_sel in habitaciones_disponibles:
                    st.caption(habitaciones_disponibles[habitacion_sel]["descripcion"])
            
                st.markdown('</div>', unsafe_allow_html=True)
        
            # Tipo de tarifa
            st.markdown('<div class="form-section"><h3>Tipo de tarifa</h3>', unsafe_allow_html=True)
        
            tarifa_cols = st.columns(3)
            tarifa_sel = None
        
            for i, (nombre_tarifa, datos_tarifa) in enumerate(TARIFAS.items()):
                with tarifa_cols[i]:
                    if st.button(nombre_tarifa, key=f"tarifa_{nombre_tarifa}", use_container_width=True):
                        tarifa_sel = nombre_tarifa
                    st.caption(datos_tarifa["descripcion"])
                    if datos_tarifa["descuento"] > 0:
                        st.success(f"{int(datos_tarifa['descuento']*100)}% descuento")
        
            if "tarifa_seleccionada" not in st.session_state:
                st.session_state.tarifa_seleccionada = "Flexible - Paga Ahora"
        
            if tarifa_sel:
                st.session_state.tarifa_seleccionada = tarifa_sel
        
            tarifa = st.session_state.tarifa_seleccionada
            st.markdown('</div>', unsafe_allow_html=True)
        
            # Palladium Rewards
            tiene_rewards = st.checkbox("Soy miembro de Palladium Rewards (5% descuento adicional)")
        
            # =====================================================================
            # CALCULO DE PRECIO - SUMA DE ADR POR CADA NOCHE
            # =====================================================================
            precio_total = 0
            precio_por_noche = []
        
            # Obtener precios del diccionario PRECIOS_ADR
            precios_hotel = PRECIOS_ADR.get(hotel_code, {})
            precios_habitacion = precios_hotel.get(habitacion_sel, {})
        
            # Buscar el PAX mas cercano disponible
            pax_disponibles = list(precios_habitacion.keys())
            if pax_disponibles:
                pax_a_usar = min(pax_disponibles, key=lambda x: abs(int(x) - total_pax))
                precios_pax = precios_habitacion.get(pax_a_usar, {})
            else:
                precios_pax = {}
        
            # Calcular precio para cada noche de la estancia
            # El CSV tiene columnas por SEMANA: 2026-01 = semana 1 de 2026
            from datetime import date
            fecha_actual = fecha_entrada
            while fecha_actual < fecha_salida:
                # Obtener año y semana ISO de la fecha
                iso_calendar = fecha_actual.isocalendar()
                año = iso_calendar[0]
                semana = iso_calendar[1]
                semana_columna = f"{año}-{semana:02d}"  # Formato: 2026-05
            
                # Obtener ADR de la semana, si no existe usar valor promedio
                adr_noche = precios_pax.get(semana_columna, 200.0)  # Default 200 si no hay datos
                precio_por_noche.append(adr_noche)
                precio_total += adr_noche * total_pax
            
                fecha_actual = fecha_actual + timedelta(days=1)
        
            # Aplicar suplemento de regimen
            suplemento_regimen = REGIMENES[regimen]["suplemento"] * noches * total_pax
            precio_total += suplemento_regimen
        
            # Aplicar descuento de tarifa
            descuento_tarifa = TARIFAS[tarifa]["descuento"]
            precio_total = precio_total * (1 - descuento_tarifa)
        
            # Aplicar descuento Rewards
            if tiene_rewards:
                precio_total = precio_total * 0.95
        
            precio_noche_promedio = precio_total / noches if noches > 0 else 0
        
            # Navegacion del paso
            st.markdown("---")
            col_atras, col_resumen, col_confirmar = st.columns([1, 2, 1])
        
            with col_atras:
                if st.button("ATRAS", key="paso3_atras", use_container_width=True):
                    st.session_state.paso_actual = 2
                    st.rerun()
        
            with col_resumen:
                st.markdown(f"**Resumen:** {noches} noches | {habitacion_sel} | {regimen}")
                st.markdown(f"### Total: ${precio_total:,.0f} USD")
                st.caption(f"~${precio_noche_promedio:.0f}/noche | {total_pax} personas | Tarifa: {tarifa}")
        
            with col_confirmar:
                # Preparar datos para el callback (evitar problemas de scope)
                datos_reserva_final = {
                    "destino": destino,
                    "complejo": complejo,
                    "hotel": hotel,
                    "hotel_code": hotel_code,
                    "fecha_entrada": fecha_entrada,
                    "fecha_salida": fecha_salida,
                    "noches": noches,
                    "adultos": adultos,
                    "ninos": ninos,
                    "total_pax": total_pax,
                    "habitacion": habitacion_sel,
                    "regimen": regimen,
                    "tarifa": tarifa,
                    "tiene_rewards": tiene_rewards,
                    "precio_total": precio_total
                }

                def procesar_confirmacion(datos):
                    # 1. Generar numero y timestamp
                    numero = generar_numero_reserva(datos["complejo"])
                    datos["numero"] = numero
                    datos["fecha_creacion"] = datetime.now()
                    
                    # 2. Guardar en Session State
                    st.session_state.reservas[numero] = datos
                    st.session_state.reserva_confirmada = numero
                    
                    # 3. Persistir en CSV (Lógica encapsulada)
                    try:
                        complejo_map = {"Costa Mujeres": "MUJE", "Riviera Maya": "MAYA", "Punta Cana": "CANA"}
                        
                        # Probabilidad simulada
                        prob_base = 0.25
                        days_diff = (datos["fecha_entrada"] - datetime.now().date()).days
                        if days_diff > 90: prob_base += 0.10
                        if datos["tiene_rewards"]: prob_base -= 0.10
                        if datos["noches"] >= 7: prob_base -= 0.05
                        prob_cancelacion = max(0.05, min(0.70, prob_base))

                        nueva_reserva_csv = {
                            "ID_RESERVA": numero,
                            "LLEGADA": datos["fecha_entrada"].strftime("%Y-%m-%d"),
                            "SALIDA": datos["fecha_salida"].strftime("%Y-%m-%d"),
                            "NOCHES": datos["noches"],
                            "REGIMEN": datos["regimen"],
                            "PAX": datos["total_pax"],
                            "ADULTOS": datos["adultos"],
                            "NENES": datos["ninos"],
                            "FECHA_TOMA": datetime.now().strftime("%Y-%m-%d"),
                            "NOMBRE_COMPLEJO": complejo_map.get(datos["complejo"], "MAYA"),
                            "NOMBRE_HOTEL": datos["hotel"],
                            "NOMBRE_HABITACION": datos["habitacion"],
                            "VALOR_RESERVA": round(datos["precio_total"], 2),
                            "ADR": round(datos["precio_total"] / datos["noches"], 2) if datos["noches"] > 0 else 0,
                            "LEAD_TIME": days_diff,
                            "CANAL_CONSOLIDADO": "VENTA DIRECTA",
                            "PAIS_TOP": "ESPAÑA",
                            "TIENE_FIDELIDAD": 1 if datos["tiene_rewards"] else 0,
                            "CANCELADO": 0,
                            "PROB_CANCELACION": round(prob_cancelacion, 4),
                            "TARIFA": datos["tarifa"],
                            "ORIGEN": "WEB"
                        }
                        
                        try:
                            df_existente = pd.read_csv(CSV_RESERVAS)
                        except:
                            df_existente = pd.DataFrame()
                        
                        df_nueva = pd.DataFrame([nueva_reserva_csv])
                        df_actualizado = pd.concat([df_existente, df_nueva], ignore_index=True)
                        df_actualizado.to_csv(CSV_RESERVAS, index=False)
                        st.cache_data.clear()
                    except Exception as e:
                        print(f"Error persistiendo CSV: {e}")

                    # 4. Cambiar paso al final (trigger para la UI)
                    st.session_state.paso_actual = 4

                st.button("CONFIRMAR", key="paso3_confirmar", on_click=procesar_confirmacion, args=(datos_reserva_final,), use_container_width=True)
    
        # -------------------------------------------------------------------------
        # PASO 4: CONFIRMACION
        # -------------------------------------------------------------------------
        elif paso == 4:
            numero = st.session_state.reserva_confirmada
        
            # Validación: si no hay reserva confirmada, volver al paso 1
            if numero is None or numero not in st.session_state.reservas:
                st.warning("No hay reserva confirmada. Iniciando nueva reserva.")
                st.session_state.paso_actual = 1
                st.rerun()
        
            reserva = st.session_state.reservas[numero]
        
            st.markdown(f"""
            <div class="reserva-confirmada">
                <h2>Reserva Confirmada</h2>
                <p>Su numero de reserva:</p>
                <div class="codigo-reserva">{numero}</div>
                <p>{reserva['hotel']}</p>
                <p>{reserva['fecha_entrada'].strftime('%d/%m/%Y')} - {reserva['fecha_salida'].strftime('%d/%m/%Y')} | {reserva['noches']} noches</p>
                <p>{reserva['habitacion']} | {reserva['regimen']}</p>
                <p>{reserva['adultos']} adultos{f", {reserva['ninos']} ninos" if reserva['ninos'] > 0 else ""}</p>
                <div class="precio-final">${reserva['precio_total']:,.0f} USD</div>
                <p style="opacity:0.7">Tarifa: {reserva['tarifa']}</p>
            </div>
            """, unsafe_allow_html=True)
        
            if st.button("NUEVA RESERVA"):
                st.session_state.paso_actual = 1
                st.session_state.destino_seleccionado = None
                st.session_state.complejo_seleccionado = None
                st.session_state.hotel_seleccionado = None
                st.rerun()

    # =============================================================================
    # AREA: INTRANET
    # =============================================================================

    elif area == "Intranet":
        st.markdown("""
        <div class="seccion-titulo">
            <h1>Panel de Gestion</h1>
            <p>Consulta de reservas y prediccion de cancelaciones</p>
        </div>
        """, unsafe_allow_html=True)
    
        tab1, tab2 = st.tabs(["Consultar Reserva", "Vista Mensual"])
    
        with tab1:
            numero_busqueda = st.text_input("Numero de reserva", placeholder="610012309601").strip()
        
            if st.button("BUSCAR"):
                if numero_busqueda in st.session_state.reservas:
                    r = st.session_state.reservas[numero_busqueda]
                    prob = calcular_probabilidad_cancelacion(r)
                
                    # Determinar nivel de riesgo
                    if prob < 0.25:
                        nivel = "BAJO"
                        color = "#28a745"
                    elif prob < 0.40:
                        nivel = "MEDIO"
                        color = "#ffc107"
                    else:
                        nivel = "ALTO"
                        color = "#dc3545"
                
                    col1, col2 = st.columns([2, 1])
                
                    with col1:
                        st.markdown("### Datos de la reserva")
                        st.write(f"**ID:** {r['numero']}")
                        st.write(f"**Hotel:** {r['hotel']}")
                        st.write(f"**Fechas:** {r['fecha_entrada'].strftime('%d/%m/%Y')} - {r['fecha_salida'].strftime('%d/%m/%Y')}")
                        st.write(f"**Habitacion:** {r['habitacion']} | {r['regimen']}")
                        st.write(f"**Huéspedes:** {r.get('total_pax', r['adultos'] + r['ninos'])} personas")
                        st.write(f"**Tarifa:** {r['tarifa']}")
                        st.write(f"**Total:** ${r['precio_total']:,.0f} USD")
                
                    with col2:
                        st.markdown("### Predicción ML")
                        st.metric("Prob. Cancelación", f"{prob*100:.1f}%")
                        st.markdown(f"<span style='color:{color};font-weight:600;font-size:1.5em'>{nivel}</span>", unsafe_allow_html=True)
                
                    # =========================================================
                    # OFERTAS PERSONALIZADAS SEGÚN NIVEL DE RIESGO
                    # =========================================================
                    st.markdown("---")
                    st.markdown(f"### Ofertas recomendadas para riesgo {nivel}")
                
                    if nivel == "BAJO":
                        # Riesgo bajo: ofertas de upselling y fidelización
                        st.success("Cliente con alta probabilidad de mantener la reserva. Oportunidad de upselling.")
                    
                        col_o1, col_o2, col_o3 = st.columns(3)
                        with col_o1:
                            st.markdown("""
                            **Upgrade de habitación**
                            - Suite Premium por +$50/noche
                            - Vistas al mar garantizadas
                            - Late checkout incluido
                            """)
                            st.button("Aplicar Upgrade", key="offer_upgrade", disabled=True)
                    
                        with col_o2:
                            st.markdown("""
                            **Pack VIP Experience**
                            - Cena romántica privada
                            - Spa para 2 personas (60 min)
                            - Champagne de bienvenida
                            - **+$180 total**
                            """)
                            st.button("Añadir Pack VIP", key="offer_vip", disabled=True)
                    
                        with col_o3:
                            st.markdown("""
                            **Palladium Rewards**
                            - 3x puntos en esta reserva
                            - Inscripción gratuita
                            - 5% dto próxima reserva
                            """)
                            st.button("Inscribir Rewards", key="offer_rewards", disabled=True)
                
                    elif nivel == "MEDIO":
                        # Riesgo medio: ofertas de retención moderada
                        st.warning("Cliente con riesgo moderado. Recomendamos incentivos de retención.")
                    
                        col_o1, col_o2, col_o3 = st.columns(3)
                        with col_o1:
                            st.markdown("""
                            **Garantía de precio**
                            - Congelamos el precio actual
                            - Cancelación flexible hasta 7 días
                            - Sin penalización
                            """)
                            st.button("Activar Garantía", key="offer_garantia", disabled=True)
                    
                        with col_o2:
                            st.markdown("""
                            **All Inclusive Premium**
                            - Upgrade a AI Premium gratis
                            - Restaurantes a la carta ilimitados
                            - Bebidas top shelf
                            - **Ahorro: $70/noche**
                            """)
                            st.button("Upgrade AI Gratis", key="offer_ai", disabled=True)
                    
                        with col_o3:
                            st.markdown("""
                            **Flexibilidad total**
                            - Cambio de fechas sin coste
                            - Válido hasta 12 meses
                            - Mismas condiciones
                            """)
                            st.button("Activar Flexibilidad", key="offer_flex", disabled=True)
                
                    else:  # ALTO
                        # Riesgo alto: ofertas agresivas de retención
                        st.error("Cliente con alto riesgo de cancelación. Aplicar medidas de retención urgentes.")
                    
                        col_o1, col_o2, col_o3 = st.columns(3)
                        with col_o1:
                            st.markdown("""
                            **Descuento de retención**
                            - 15% descuento inmediato
                            - Aplicado automáticamente
                            - Sin condiciones adicionales
                            - **Ahorro: ${:,.0f}**
                            """.format(r['precio_total'] * 0.15))
                            st.button("Aplicar -15%", key="offer_dto15", disabled=True)
                    
                        with col_o2:
                            st.markdown("""
                            **Pack Experiencias GRATIS**
                            - Excursión valorada en $150
                            - Cena temática para 2
                            - Traslados incluidos
                            - **Valor: $300**
                            """)
                            st.button("Regalar Pack", key="offer_exp", disabled=True)
                    
                        with col_o3:
                            st.markdown("""
                            **Reprogramar sin coste**
                            - Cambio fechas gratis
                            - + 10% crédito adicional
                            - Válido 18 meses
                            - Priority booking
                            """)
                            st.button("Ofrecer Cambio", key="offer_cambio", disabled=True)
                
                    st.caption("Los botones estarán activos cuando se integre con el sistema de gestión de reservas.")
                
                else:
                    st.warning("Reserva no encontrada. Busca por el número completo (12 dígitos).")
    
        with tab2:
            # -----------------------------------------------------------------
            # VISTA MENSUAL - Gestión de reservas por riesgo de cancelación
            # -----------------------------------------------------------------
        
            # Cargar dataset de reservas 2026
            @st.cache_data
            def cargar_reservas_2026():
                try:
                    df = pd.read_csv(CSV_RESERVAS)
                    df['LLEGADA'] = pd.to_datetime(df['LLEGADA'])
                    df['SALIDA'] = pd.to_datetime(df['SALIDA'])
                    df['FECHA_TOMA'] = pd.to_datetime(df['FECHA_TOMA'])
                    return df
                except:
                    return pd.DataFrame()
        
            df_reservas = cargar_reservas_2026()
        
            if df_reservas.empty:
                st.warning(f"No se encontró el archivo {CSV_RESERVAS}")
            else:
                st.markdown("#### Filtros")
            
                col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 1])
            
                with col_f1:
                    # Selector de mes
                    meses = {
                        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                    }
                    mes_actual = datetime.now().month
                    mes_seleccionado = st.selectbox(
                        "Mes de llegada",
                        options=list(meses.keys()),
                        format_func=lambda x: f"{meses[x]} 2026",
                        index=mes_actual - 1
                    )
            
                with col_f2:
                    # Filtro de riesgo
                    riesgo_filtro = st.selectbox(
                        "Nivel de riesgo",
                        ["Todos", "ALTO (>40%)", "MEDIO (25-40%)", "BAJO (<25%)"]
                    )
            
                with col_f3:
                    # Filtro de complejo
                    complejo_filtro = st.selectbox(
                        "Complejo",
                        ["Todos"] + df_reservas['NOMBRE_COMPLEJO'].unique().tolist()
                    )
            
                with col_f4:
                    # Solo no canceladas
                    solo_activas = st.checkbox("Solo reservas activas", value=True)
            
                # Aplicar filtros
                df_filtrado = df_reservas[df_reservas['LLEGADA'].dt.month == mes_seleccionado].copy()
            
                if riesgo_filtro == "ALTO (>40%)":
                    df_filtrado = df_filtrado[df_filtrado['PROB_CANCELACION'] >= 0.40]
                elif riesgo_filtro == "MEDIO (25-40%)":
                    df_filtrado = df_filtrado[(df_filtrado['PROB_CANCELACION'] >= 0.25) & (df_filtrado['PROB_CANCELACION'] < 0.40)]
                elif riesgo_filtro == "BAJO (<25%)":
                    df_filtrado = df_filtrado[df_filtrado['PROB_CANCELACION'] < 0.25]
            
                if complejo_filtro != "Todos":
                    df_filtrado = df_filtrado[df_filtrado['NOMBRE_COMPLEJO'] == complejo_filtro]
            
                if solo_activas:
                    df_filtrado = df_filtrado[df_filtrado['CANCELADO'] == 0]
            
                # Ordenar por probabilidad de cancelación (mayor primero)
                df_filtrado = df_filtrado.sort_values('PROB_CANCELACION', ascending=False)
            
                # Estadísticas
                st.markdown("---")
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                with col_s1:
                    st.metric("Total reservas", len(df_filtrado))
                with col_s2:
                    valor_total = df_filtrado['VALOR_RESERVA'].sum()
                    st.metric("Valor total", f"${valor_total:,.0f}")
                with col_s3:
                    alto_riesgo = len(df_filtrado[df_filtrado['PROB_CANCELACION'] >= 0.40])
                    st.metric("Alto riesgo", alto_riesgo)
                with col_s4:
                    if len(df_filtrado) > 0:
                        prob_media = df_filtrado['PROB_CANCELACION'].mean() * 100
                        st.metric("Prob. media", f"{prob_media:.1f}%")
                    else:
                        st.metric("Prob. media", "N/A")
            
                st.markdown("---")
            
                # Tabla de reservas
                if len(df_filtrado) == 0:
                    st.info(f"No hay reservas para {meses[mes_seleccionado]} 2026 con los filtros seleccionados.")
                else:
                    # Preparar datos para mostrar
                    df_mostrar = df_filtrado[[
                        'ID_RESERVA', 'NOMBRE_COMPLEJO', 'LLEGADA', 'NOCHES', 
                        'PAX', 'VALOR_RESERVA', 'CANAL_CONSOLIDADO', 'PROB_CANCELACION'
                    ]].copy()
                
                    # Añadir columna de nivel de riesgo
                    def calcular_nivel(prob):
                        if prob >= 0.40:
                            return "ALTO"
                        elif prob >= 0.25:
                            return "MEDIO"
                        else:
                            return "BAJO"
                
                    df_mostrar['RIESGO'] = df_mostrar['PROB_CANCELACION'].apply(calcular_nivel)
                    df_mostrar['LLEGADA'] = df_mostrar['LLEGADA'].dt.strftime('%d/%m/%Y')
                    df_mostrar['PROB_CANCELACION'] = (df_mostrar['PROB_CANCELACION'] * 100).round(1).astype(str) + '%'
                    df_mostrar['VALOR_RESERVA'] = df_mostrar['VALOR_RESERVA'].apply(lambda x: f"${x:,.0f}")
                
                    # Renombrar columnas
                    df_mostrar.columns = ['ID', 'Complejo', 'Llegada', 'Noches', 'PAX', 'Valor', 'Canal', 'Prob.', 'Riesgo']
                
                    # Mostrar tabla
                    st.dataframe(
                        df_mostrar.head(50),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "ID": st.column_config.TextColumn("ID Reserva", width="small"),
                            "Complejo": st.column_config.TextColumn("Complejo", width="small"),
                            "Llegada": st.column_config.TextColumn("Llegada", width="small"),
                            "Noches": st.column_config.NumberColumn("Noches", width="small"),
                            "PAX": st.column_config.NumberColumn("PAX", width="small"),
                            "Valor": st.column_config.TextColumn("Valor", width="small"),
                            "Canal": st.column_config.TextColumn("Canal", width="medium"),
                            "Prob.": st.column_config.TextColumn("Prob. Cancel.", width="small"),
                            "Riesgo": st.column_config.TextColumn("Riesgo", width="small")
                        }
                    )
                
                    st.caption(f"Mostrando {min(50, len(df_filtrado))} de {len(df_filtrado)} reservas (ordenadas por probabilidad de cancelación)")
                
                    # Sección para gestionar reserva seleccionada
                    st.markdown("---")
                    st.markdown("#### Gestionar reserva")
                
                    id_seleccionado = st.text_input(
                        "Introduce ID de reserva para ver detalles",
                        placeholder="Ej: 610000009601"
                    )
                
                    if id_seleccionado:
                        reserva_sel = df_filtrado[df_filtrado['ID_RESERVA'].astype(str) == id_seleccionado]
                        if not reserva_sel.empty:
                            r = reserva_sel.iloc[0]
                            prob = r['PROB_CANCELACION']
                        
                            col_d1, col_d2 = st.columns([2, 1])
                            with col_d1:
                                st.write(f"**Hotel:** {r['NOMBRE_HOTEL']}")
                                st.write(f"**Habitación:** {r['NOMBRE_HABITACION']}")
                                st.write(f"**Fechas:** {r['LLEGADA'].strftime('%d/%m/%Y')} - {r['SALIDA'].strftime('%d/%m/%Y')} ({r['NOCHES']} noches)")
                                st.write(f"**Huéspedes:** {r['PAX']} ({r['ADULTOS']} adultos, {r['NENES']} niños)")
                                st.write(f"**Canal:** {r['CANAL_CONSOLIDADO']} | País: {r['PAIS_TOP']}")
                                st.write(f"**Valor:** ${r['VALOR_RESERVA']:,.0f}")
                        
                            with col_d2:
                                st.metric("Prob. Cancelación", f"{prob*100:.1f}%")
                                nivel = calcular_nivel(prob)
                                color = "#28a745" if nivel == "BAJO" else "#ffc107" if nivel == "MEDIO" else "#dc3545"
                                st.markdown(f"<span style='color:{color};font-weight:600;font-size:1.3em'>{nivel}</span>", unsafe_allow_html=True)
                        
                            # Botones de acción
                            col_a1, col_a2, col_a3 = st.columns(3)
                            with col_a1:
                                st.button("Enviar oferta retención", key="btn_oferta", disabled=True)
                            with col_a2:
                                st.button("Upgrade habitación", key="btn_upgrade", disabled=True)
                            with col_a3:
                                st.button("Contactar cliente", key="btn_contactar", disabled=True)
                        else:
                            st.warning("Reserva no encontrada en el mes seleccionado")

    # =============================================================================
# FOOTER - Marcas y creditos
# =============================================================================

# Imagen de marcas de Palladium (copiar marcas_palladium.png a la carpeta 03_app)
st.markdown("---")
col_f1, col_marcas, col_f2 = st.columns([0.5, 3, 0.5])
with col_marcas:
    try:
        st.image("marcas_palladium.png", use_container_width=True)
    except:
        pass  # Si no existe la imagen, no mostrar error

st.markdown("""
<div class="footer">
    <p><strong>Palladium Hotel Group</strong></p>
    <p>TFM Grupo 4 - Master en Data Science | Sistema de Prediccion de Cancelaciones</p>
</div>
""", unsafe_allow_html=True)



