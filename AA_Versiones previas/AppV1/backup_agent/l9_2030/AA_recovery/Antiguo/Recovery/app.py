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
                        "descripcion": "Resort de lujo familiar con sistema de canales navegables, 'Family Selection', Rafa Nadal Tennis Centre, y Zentropia Spa de clase mundial.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "CMU JUNIOR SUITE GV": {
                                "descripcion": "Junior Suite con vistas al jardín tropical y la laguna",
                                "max_pax": 8,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/MUJE_CMU/Grand-Palladium-Costa-Mujeres-junior-suite-garden-lagoon-suite1.webp",
                                    "media/habitaciones/MUJE_CMU/Grand-Palladium-Costa-Mujeres-junior-suite-garden-lagoon-suite-21.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-Garden-Lagoon-view-vista-jardin.webp",
                                    "media/habitaciones/MUJE_CMU/GP-JUNIOR-SUITE-01-MG-1399.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_CMU/GP-COSTA_MUJERES_JUNIOR-SUITE.webp",
                                "servicios": ["Cama King o 2 dobles", "Terraza amueblada", "Cafetera Nespresso", "Minibar diaria", "Altavoz Bluetooth", "TV 50\"", "Caja fuerte"]
                            },
                            "CMU JUNIOR SUITE PS": {
                                "descripcion": "Junior Suite junto a la piscina con acceso directo",
                                "max_pax": 8,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-poolside-vista2.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-poolside-vista3.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-poolside2.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-poolside4.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_CMU/GP-COSTA_MUJERES_JUNIOR-SUITE (1).webp",
                                "servicios": ["Cama King o 2 dobles", "Menú de almohadas", "Cafetera Nespresso", "Sofá cama", "Bañera hidromasaje", "Albornoz y zapatillas", "Servicio de mayordomo"]
                            },
                            "CMU JUNIOR SUITE PS OV": {
                                "descripcion": "Junior Suite piscina con vistas panorámicas al océano",
                                "max_pax": 7,
                                "m2": 50,
                                "imagenes": [
                                    "media/habitaciones/MUJE_CMU/Grand-Palladium-Costa-Mujeres-junior-suite-poolside-ocean-view-3.webp",
                                    "media/habitaciones/MUJE_CMU/Grand-Palladium-Costa-Mujeres-junior-suite-poolside-ocean-view.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-poolside-ocean-view3.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Junior-Suite-poolside-ocean-view6.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_CMU/GP-COSTA_MUJERES_JUNIOR-SUITE (2).webp",
                                "servicios": ["Vista al mar", "Acceso piscina", "Terraza privada", "Minibar", "Aire acondicionado", "WiFi gratis", "Cafetera Nespresso"]
                            },
                            "CMU LOFT SUITE JT": {
                                "descripcion": "Loft Suite de dos plantas con jacuzzi privado en terraza",
                                "max_pax": 5,
                                "m2": 75,
                                "imagenes": [
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Loft-Suite-Jacuzzi-Terrace-vista.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Loft-Suite-Jacuzzi-Terrace-vista2.webp",
                                    "media/habitaciones/MUJE_CMU/GP-Costa-Mujeres-Loft-Suite-Jacuzzi-Terrace-vista4.webp",
                                    "media/habitaciones/MUJE_CMU/LOFT-SUITE-GP-COSTA-MUJERES18.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_CMU/GP-COSTA_MUJERES_LOFT-SUITE.webp",
                                "servicios": ["Jacuzzi privado", "Dos plantas", "Sala de estar", "Terraza", "Minibar premium", "Servicio VIP"]
                            },
                        }
                    },
                    # .........................................................
                    # Family Selection at Grand Palladium Costa Mujeres
                    # .........................................................
                    "Family Selection Costa Mujeres": {
                        "hotel_code": "MUJE_CMU_FS",
                        "imagen": "media/hoteles/costa_mujeres/family_selection_costa_mujeres.jpg",
                        "descripcion": "Zona VIP exclusiva para familias dentro del resort, con servicios premium, mayordomía, accesos preferentes y áreas reservadas.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "CMU FS JUNIOR SUITE BS": {
                                "descripcion": "Junior Suite familiar junto a la playa con acceso directo al mar",
                                "max_pax": 8,
                                "m2": 50,
                                "imagenes": [
                                    "media/habitaciones/MUJE_CMU_FS/family-selection-junior-suite-beachside.webp",
                                    "media/habitaciones/MUJE_CMU_FS/family-selection-junior-suite-beachside-1.webp",
                                    "media/habitaciones/MUJE_CMU_FS/Family-Selection-Grand-Palladium-Costa-Mujeres-Junior-Suite-Beachfront3.webp",
                                    "media/habitaciones/MUJE_CMU_FS/Family-Selection-Grand-Palladium-Costa-Mujeres-Junior-Suite-Beachfront5.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_CMU_FS/Family-Selection-Costa-Mujeres-Junior-Suite.webp",
                                "servicios": ["Acceso playa", "Terraza privada", "Minibar", "Aire acondicionado", "WiFi gratis", "Servicio Family Selection", "Kit de bienvenida para niños"]
                            },
                            "CMU FS JUNIOR SUI BS POV": {
                                "descripcion": "Junior Suite familiar con vista panorámica al océano Caribe",
                                "max_pax": 6,
                                "m2": 55,
                                "imagenes": [
                                    "media/habitaciones/MUJE_CMU_FS/Family-Selection-Grand-Palladium-Costa-Mujeres-Junior-Suite-beachside-panoramic-ocean-view-vista-exterior-3.webp",
                                    "media/habitaciones/MUJE_CMU_FS/Family-Selection-Grand-Palladium-Costa-Mujeres-Junior-Suite-beachside-panoramic-ocean-view-vista-exterior.webp",
                                    "media/habitaciones/MUJE_CMU_FS/Family-Selection-Grand-Palladium-Costa-Mujeres-Junior-Suite-Beachfront-Panoramic-Ocean-View7.webp",
                                    "media/habitaciones/MUJE_CMU_FS/Family-Selection-Grand-Palladium-Costa-Mujeres-Junior-Suite-Beachfront-Panoramic-Ocean-View5.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_CMU_FS/Family-Selection-Costa-Mujeres-Junior-Suite (1).webp",
                                "servicios": ["Vista panorámica océano", "Acceso playa", "Terraza privada", "Minibar", "Aire acondicionado", "Servicio Family Selection"]
                            },
                        }
                    },
                    # .........................................................
                    # TRS Coral Hotel (Solo Adultos)
                    # .........................................................
                    "TRS Coral Hotel": {
                        "hotel_code": "MUJE_TRS",
                        "imagen": "media/hoteles/costa_mujeres/trs_coral.jpg",
                        "descripcion": "Solo adultos de lujo en Costa Mujeres. Miembro de 'The Leading Hotels of the World'. Servicio de mayordomo y 'Infinite Indulgence'.",
                        "solo_adultos": True,
                        "habitaciones": {
                            "TRS JUNIOR SUITE BS OV": {
                                "descripcion": "Junior Suite frente a la playa con vistas panorámicas al océano",
                                "max_pax": 3,
                                "m2": 50,
                                "imagenes": [
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-junior-suite-beachside-ocean-view-vista-exterior.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Junior-Suite-beachfront-ocean-view2.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Junior-Suite-beachfront-ocean-view3.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Junior-Suite-beachfront-ocean-view5.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_TRSC/TRS-CORAL_HOTEL_JUNIOR-SUITE.webp",
                                "servicios": ["Cama King size", "Bañera hidromasaje", "Cafetera Nespresso", "Vaporera", "Menú de almohadas", "Mayordomo", "Room Service 24h"]
                            },
                            "TRS JUNIOR SUITE GV": {
                                "descripcion": "Junior Suite con vistas al exuberante jardín tropical",
                                "max_pax": 3,
                                "m2": 48,
                                "imagenes": [
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Junior-Suite-garden-view-vista.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-JUNIOR-SUITE-02-MG-16401.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-JUNIOR-SUITE-05-MG-15711.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-junior-suite-beachside-vista-exterior.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_TRSC/TRS-CORAL_HOTEL_JUNIOR-SUITE (1).webp",
                                "servicios": ["Cama King o 2 dobles", "Terraza privada", "Servicio de mayordomo", "Minibar premium", "WiFi gratis", "Solo adultos", "Cafetera Nespresso"]
                            },
                            "TRS JUNIOR SUITE OV": {
                                "descripcion": "Junior Suite con impresionantes vistas al océano Caribe",
                                "max_pax": 3,
                                "m2": 50,
                                "imagenes": [
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-junior-suite-ocean-view-vista-exterior-2.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-junior-suite-ocean-view-vista-exterior.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Junior-Suite-ocean-view2.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Junior-Suite-ocean-view5.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_TRSC/TRS-CORAL_HOTEL_JUNIOR-SUITE (2).webp",
                                "servicios": ["Vista al océano", "Terraza privada", "Servicio de mayordomo", "Minibar premium", "WiFi gratis", "Solo adultos", "Cafetera Nespresso"]
                            },
                            "TRS JUNIOR SUITE SW": {
                                "descripcion": "Junior Suite Swim Up con acceso directo a piscina privada",
                                "max_pax": 3,
                                "m2": 52,
                                "imagenes": [
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-JUNIOR-SUITE-SWIM-UP10.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-JUNIOR-SUITE-SWIM-UP7.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-JUNIOR-SUITE-SWIM-UP5.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-JUNIOR-SUITE-SWIM-UP3.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_TRSC/TRS-CORAL_HOTEL_JUNIOR-SUITE-SWIM-UP.webp",
                                "servicios": ["Acceso piscina semi-privada", "Swim Up", "Servicio de mayordomo", "Minibar premium", "WiFi gratis", "Solo adultos", "Carta de aromaterapia"]
                            },
                            "TRS LOFT SUITE JT": {
                                "descripcion": "Loft Suite de dos plantas con jacuzzi privado en terraza",
                                "max_pax": 3,
                                "m2": 80,
                                "imagenes": [
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-LOFT-SUITE-01-MG-1082.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-LOFT-SUITE-05-MG-1210.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-CORAL-LOFT-SUITE-07-MG-1276.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-loft-suite-jacuzzi-terrace-vista-exterior-2.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_TRSC/TRS-CORAL_HOTEL_LOFT-SUITE.webp",
                                "servicios": ["Jacuzzi privado", "Dos plantas", "Sala de estar", "Servicio VIP", "Minibar premium", "Solo adultos"]
                            },
                            "TRS LOFT SUITE JT OV": {
                                "descripcion": "Loft Suite con jacuzzi en terraza y vistas panorámicas al océano",
                                "max_pax": 3,
                                "m2": 85,
                                "imagenes": [
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Loft-Suite-Jacuzzi-Terrace-Ocean-View-vista.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Loft-Suite-Jacuzzi-Terrace-Ocean-View4.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Loft-Suite-Jacuzzi-Terrace-Ocean-View6.webp",
                                    "media/habitaciones/MUJE_TRSC/TRS-Coral-Hotel-Loft-Suite-Jacuzzi-Terrace-Ocean-View.webp"
                                ],
                                "plano": "media/habitaciones/MUJE_TRSC/TRS-CORAL_HOTEL_LOFT-SUITE (1).webp",
                                "servicios": ["Jacuzzi privado", "Vista al océano", "Dos plantas", "Servicio VIP", "Minibar premium", "Solo adultos"]
                            },
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
                        "descripcion": "Resort con arquitectura colonial española. Ideal para familias, rodeado de naturaleza y cenotes. Acceso a Kantenah y White Sand.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "COL DELUXE GARDEN VIEW": {
                                "descripcion": "Habitación Deluxe con vistas al jardín tropical y arquitectura colonial",
                                "max_pax": 6,
                                "m2": 40,
                                "imagenes": [
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View2.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View3.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View4.webp"
                                ],
                                "servicios": ["Cama King o 2 dobles", "Terraza amueblada", "Cafetera", "Minibar", "Plancha y tabla", "Caja fuerte", "Amenidades baño"]
                            },
                            "COL JUNIOR SUITE GV": {
                                "descripcion": "Amplia Junior Suite con vistas al exuberante jardín tropical",
                                "max_pax": 8,
                                "m2": 48,
                                "imagenes": [
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View2.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View3.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View4.webp"
                                ],
                                "servicios": ["Vista al jardín", "Sala de estar", "Terraza privada", "Minibar", "Aire acondicionado", "WiFi gratis"]
                            },
                            "COL JUNIOR SUITE PS": {
                                "descripcion": "Junior Suite junto a la piscina con acceso directo al área acuática",
                                "max_pax": 8,
                                "m2": 48,
                                "imagenes": [
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View2.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View3.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View4.webp"
                                ],
                                "servicios": ["Acceso piscina", "Terraza privada", "Sala de estar", "Minibar", "Aire acondicionado", "WiFi gratis", "Albornoz y zapatillas"]
                            },
                            "COL ROMANCE VILLA SUI PS": {
                                "descripcion": "Villa Suite romántica junto a la piscina, ideal para parejas",
                                "max_pax": 3,
                                "m2": 55,
                                "imagenes": [
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View2.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View3.webp",
                                    "media/habitaciones/MAYA_COL/Grand-Palladium-Colonial-Resort-Spa-Deluxe-Garden-View4.webp"
                                ],
                                "servicios": ["Ambiente romántico", "Acceso piscina", "Terraza privada", "Minibar premium", "Servicio especial parejas", "WiFi gratis"]
                            },
                        }
                    },
                    # .........................................................
                    # Grand Palladium Kantenah Resort & Spa
                    # .........................................................
                    "Grand Palladium Kantenah Resort & Spa": {
                        "hotel_code": "MAYA_KAN",
                        "imagen": "media/hoteles/riviera_maya/gp_kantenah.jpg",
                        "descripcion": "Resort familiar renovado estilo maya. Acceso directo a playa Kantenah, amplias zonas deportivas y de entretenimiento.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "KAN DELUXE GARDEN VIEW": {
                                "descripcion": "Habitación Deluxe con vistas al jardín tropical y acceso al cenote",
                                "max_pax": 4,
                                "m2": 40,
                                "imagenes": [
                                    "media/habitaciones/MAYA_KAN/Grand_Palladium_Kantenah_Deluxe_garden_view.webp",
                                    "media/habitaciones/MAYA_KAN/family-selection-at-grand-palladium-kantenah-resort-spa-junior-suite-garden-view-01.webp",
                                    "media/habitaciones/MAYA_KAN/family-selection-at-grand-palladium-kantenah-resort-spa-junior-suite-garden-view-02.webp",
                                    "media/habitaciones/MAYA_KAN/family-selection-at-grand-palladium-kantenah-resort-spa-junior-suite-garden-view-03.webp"
                                ],
                                "servicios": ["Cama King o 2 dobles", "Terraza amueblada", "Cafetera", "Minibar diaria", "Plancha y tabla", "TV 42\"", "Amenidades baño"]
                            },
                            "KAN JUNIOR SUITE GV": {
                                "descripcion": "Amplia Junior Suite con vistas al exuberante jardín tropical",
                                "max_pax": 8,
                                "m2": 48,
                                "imagenes": [
                                    "media/habitaciones/MAYA_KAN/grand-palladium-kantenah-resort-spa-habitacion-junior-suite.webp",
                                    "media/habitaciones/MAYA_KAN/grand-palladium-kantenah-resort-spa-habitacion-junior-suite_02.webp",
                                    "media/habitaciones/MAYA_KAN/grand-palladium-kantenah-resort-spa-habitacion-junior-suite_03.webp",
                                    "media/habitaciones/MAYA_KAN/family-selection-at-grand-palladium-kantenah-resort-spa-junior-suite-garden-view-04.webp"
                                ],
                                "servicios": ["Vista al jardín", "Sala de estar", "Terraza privada", "Minibar", "Aire acondicionado", "WiFi gratis"]
                            },
                            "KAN ROMANCE VILLA SUI BS": {
                                "descripcion": "Villa Suite romántica junto a la playa con vistas al mar Caribe",
                                "max_pax": 2,
                                "m2": 60,
                                "imagenes": [
                                    "media/habitaciones/MAYA_KAN/Grand_Palladium_Kantenah_Residence_Suite_Beachfront.webp",
                                    "media/habitaciones/MAYA_KAN/gp-kantenah-signature-residence-1.webp",
                                    "media/habitaciones/MAYA_KAN/gp-kantenah-signature-residence-3.webp",
                                    "media/habitaciones/MAYA_KAN/gp-kantenah-signature-residence-4.webp"
                                ],
                                "servicios": ["Vista al mar", "Acceso directo playa", "Ambiente romántico", "Minibar premium", "Servicio especial parejas", "WiFi gratis"]
                            },
                        }
                    },
                    # .........................................................
                    # TRS Yucatan Hotel (Solo Adultos)
                    # .........................................................
                    "TRS Yucatan Hotel": {
                        "hotel_code": "MAYA_TRS",
                        "imagen": "media/hoteles/riviera_maya/trs_yucatan.jpg",
                        "descripcion": "Hotel de lujo solo adultos. Suites privadas con piscina/jacuzzi, mayordomo 24h, piscina infinita exclusiva y acceso preferente.",
                        "solo_adultos": True,
                        "habitaciones": {
                            "TRS JUNIOR SUITE GV": {
                                "descripcion": "Lujosa Junior Suite con vistas a los jardines tropicales y diseño contemporáneo",
                                "max_pax": 5,
                                "m2": 60,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-JS-6726_MG_8817.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-JS-6726_MG_9008.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-JS-6726_MG_9050.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-JS-6726_MG_9068.webp"
                                ],
                                "servicios": ["Cama King size", "Bañera hidromasaje", "Cafetera Nespresso", "Menú de almohadas", "Mayordomo", "Room Service 24h", "Albornoz y zapatillas"]
                            },
                            "TRS JUNIOR SUITE PS": {
                                "descripcion": "Junior Suite ubicada junto a la piscina con acceso preferente",
                                "max_pax": 4,
                                "m2": 60,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside2.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside3.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside4.webp"
                                ],
                                "servicios": ["Junto a la piscina", "Mayordomo", "Bañera de hidromasaje", "Minibar premium", "Terraza", "WiFi"]
                            },
                            "TRS JUNIOR SUITE PS OV": {
                                "descripcion": "Junior Suite con vistas frontales al Mar Caribe desde el área de piscina",
                                "max_pax": 3,
                                "m2": 65,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside-Ocean-View.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside-Ocean-View3.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside-Ocean-View4.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside-Ocean-View5.webp"
                                ],
                                "servicios": ["Vista al océano", "Junto a la piscina", "Mayordomo", "Minibar premium", "Bañera hidromasaje", "WiFi"]
                            },
                            "TRS JUNIOR SUITE PP GV": {
                                "descripcion": "Suite exclusiva con piscina privada y vistas al jardín",
                                "max_pax": 4,
                                "m2": 70,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Junior-Suite-Private-Pool-Garden-View.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Junior-Suite-Private-Pool-Garden-View2.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Junior-Suite-Private-Pool-Garden-View3.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Junior-Suite-Private-Pool-Garden-View4.webp"
                                ],
                                "servicios": ["Piscina privada", "Vista al jardín", "Mayordomo", "Minibar premium", "Bañera hidromasaje", "WiFi"]
                            },
                            "TRS JUNIOR SUITE PP PS": {
                                "descripcion": "Suite con piscina privada ubicada cerca del área general de piscinas",
                                "max_pax": 3,
                                "m2": 70,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Junior-Suite-Private-Pool-Garden-View.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Junior-Suite-Private-Pool-Garden-View2.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Poolside2.webp"
                                ],
                                "servicios": ["Piscina privada", "Mayordomo", "Minibar premium", "Bañera hidromasaje", "WiFi", "Amenities VIP"]
                            },
                            "TRS JS JACUZZI TERR PS": {
                                "descripcion": "Junior Suite con Jacuzzi privado en la terraza junto a la piscina",
                                "max_pax": 3,
                                "m2": 65,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Jacuzzi-Terrace-Poolside.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Jacuzzi-Terrace-Poolside2.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Jacuzzi-Terrace-Poolside3.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-Hotel-Junior-Suite-Jacuzzi-Terrace-Poolside4.webp"
                                ],
                                "servicios": ["Jacuzzi en terraza", "Mayordomo", "Minibar premium", "WiFi", "Cama King Size", "Room service"]
                            },
                            "TRS ST JACUZZI TERR PS": {
                                "descripcion": "Lujosa Suite con Jacuzzi exterior en terraza privada",
                                "max_pax": 3,
                                "m2": 80,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Suite-Jacuzzi-Terrace-Poolside.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Suite-Jacuzzi-Terrace-Poolside3.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Suite-Jacuzzi-Terrace-Poolside4.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-HOTEL-Suite-Jacuzzi-Terrace-Poolside5.webp"
                                ],
                                "servicios": ["Jacuzzi premium", "Sala independiente", "Mayordomo", "Minibar VIP", "WiFi", "Terraza amueblada"]
                            },
                            "TRS ROMANCE BW BYTHE LAKE": {
                                "descripcion": "Villa de lujo tipo Bungalow sobre el lago para una experiencia inolvidable",
                                "max_pax": 2,
                                "m2": 70,
                                "imagenes": [
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-AMBASSADOR-SUITE-6731_MG_8842.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-YUCATAN-AMBASSADOR-SUITE-6731_MG_8956.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-Yucatan-Ambassador-Suite-10-.webp",
                                    "media/habitaciones/MAYA_TRS/TRS-Yucatan-Ambassador-Suite-2-.webp"
                                ],
                                "servicios": ["Ubicación sobre lago", "Ducha exterior", "Privacidad total", "Mayordomo", "Minibar premium", "WiFi"]
                            },
                        }
                    },
                    # .........................................................
                    # Grand Palladium Select White Sand
                    # .........................................................
                    "Grand Palladium Select White Sand": {
                        "hotel_code": "MAYA_WS",
                        "imagen": "media/hoteles/riviera_maya/gp_white_sand.jpg",
                        "descripcion": "En el corazón de Riviera Maya. Suites amplias y románticas, algunas con vistas al lago. Acceso a instalaciones de Colonial y Kantenah.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "WS JUNIOR SUITE BS": {
                                "descripcion": "Junior Suite Select con vistas privilegiadas frente al mar",
                                "max_pax": 8,
                                "m2": 52,
                                "imagenes": [
                                    "media/habitaciones/MAYA_WS/gp-white-sand-junior-suite-beachfront.webp",
                                    "media/habitaciones/MAYA_WS/gp-white-sand-junior-suite-beachfront-1.webp",
                                    "media/habitaciones/MAYA_WS/gp-white-sand-junior-suite-beachfront-2.webp",
                                    "media/habitaciones/MAYA_WS/gp-white-sand-junior-suite-beachfront-3.webp"
                                ],
                                "servicios": ["Cama King o 2 dobles", "Bañera hidromasaje", "Cafetera Nespresso", "Menú almohadas", "Sofá cama", "Room service", "Albornoz y zapatillas"]
                            },
                            "WS JUNIOR SUITE GV": {
                                "descripcion": "Amplia Junior Suite con vistas a los exuberantes jardines tropicales",
                                "max_pax": 8,
                                "m2": 52,
                                "imagenes": [
                                    "media/habitaciones/MAYA_WS/gp-select-white-sand-junior-suite-garden-view-4.webp",
                                    "media/habitaciones/MAYA_WS/gp-select-white-sand-junior-suite-garden-view-5.webp",
                                    "media/habitaciones/MAYA_WS/gp-select-white-sand-junior-suite-garden-view-6.webp",
                                    "media/habitaciones/MAYA_WS/gp-select-white-sand-junior-suite-garden-view-7.webp"
                                ],
                                "servicios": ["Vista al jardín", "Terraza", "Minibar", "WiFi", "Aire acondicionado", "Servicios Select"]
                            },
                            "WS SUITE GARDEN VIEW": {
                                "descripcion": "Lujosa Suite con sala de estar independiente y vistas al jardín",
                                "max_pax": 7,
                                "m2": 68,
                                "imagenes": [
                                    "media/habitaciones/MAYA_WS/gp-white-sand-suite-garden-view-4.webp",
                                    "media/habitaciones/MAYA_WS/gp-white-sand-suite-garden-view.webp",
                                    "media/habitaciones/MAYA_WS/gp-white-sand-suite-garden-view-2.webp",
                                    "media/habitaciones/MAYA_WS/gp-white-sand-suite-garden-view-3.webp"
                                ],
                                "servicios": ["Sala independiente", "Vista al jardín", "Minibar premium", "WiFi", "Servicio room service", "Servicios Select"]
                            },
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
                        "descripcion": "Resort 5 estrellas en Playa Bávaro. Experiencia 'Select' con servicios exclusivos, ideal para quien busca un plus de confort.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "BAV JUNIOR SUITE GV": {
                                "descripcion": "Junior Suite espaciosa con vistas a los jardines tropicales de Bávaro",
                                "max_pax": 8,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/CANA_BAV/grand-palladium-bavaro-suites-resort-spa-junior-suite-garden-view.webp",
                                    "media/habitaciones/CANA_BAV/grand-palladium-bavaro-suites-resort-spa-junior-suite-garden-view-2.webp",
                                    "media/habitaciones/CANA_BAV/grand-palladium-bavaro-suites-resort-spa-junior-suite-garden-view-4.webp",
                                    "media/habitaciones/CANA_BAV/grand-palladium-bavaro-suites-resort-spa-junior-suite-garden-view-5.webp"
                                ],
                                "servicios": ["Vista al jardín", "Bañera hidromasaje", "Minibar", "WiFi", "Aire acondicionado", "Cama King"]
                            },
                            "BAV PREMIUM JS GV": {
                                "descripcion": "Junior Suite Premium con decoración refinada y servicios superiores",
                                "max_pax": 7,
                                "m2": 48,
                                "imagenes": [
                                    "media/habitaciones/CANA_BAV/Grand-Palladium-Bvaro-Suites-Resort-Spa-Luxury-Junior-Suite-6.webp",
                                    "media/habitaciones/CANA_BAV/grand-palladium-bavaro-suites-resort-spa-junior-suite-garden-view.webp",
                                    "media/habitaciones/CANA_BAV/grand-palladium-bavaro-suites-resort-spa-junior-suite-garden-view-2.webp"
                                ],
                                "servicios": ["Servicios VIP", "Vista al jardín", "Bañera hidromasaje", "Minibar", "WiFi"]
                            },
                            "BAV SUPERIOR JS GV": {
                                "descripcion": "Junior Suite Superior con piscina privada o acceso directo",
                                "max_pax": 6,
                                "m2": 50,
                                "imagenes": [
                                    "media/habitaciones/CANA_BAV/superior-junior-suite-private-pool.webp",
                                    "media/habitaciones/CANA_BAV/superior-junior-suite-private-pool-1.webp",
                                    "media/habitaciones/CANA_BAV/superior-junior-suite-private-pool-2.webp",
                                    "media/habitaciones/CANA_BAV/superior-junior-suite-private-pool-3.webp",
                                    "media/habitaciones/CANA_BAV/superior-junior-suite-private-pool-4.webp"
                                ],
                                "servicios": ["Piscina privada", "Terraza amueblada", "Minibar", "WiFi", "Bañera hidromasaje"]
                            },
                            "BAV ROMANCE SUITE GV": {
                                "descripcion": "Suite diseñada para parejas con detalles románticos y máxima privacidad",
                                "max_pax": 4,
                                "m2": 65,
                                "imagenes": [
                                    "media/habitaciones/CANA_BAV/romance-suite-garden-view-1.webp",
                                    "media/habitaciones/CANA_BAV/romance-suite-garden-view-3.webp",
                                    "media/habitaciones/CANA_BAV/romance-suite-garden-view-4.webp",
                                    "media/habitaciones/CANA_BAV/romance-suite-garden-view-5.webp"
                                ],
                                "servicios": ["Detalles románticos", "Ducha exterior", "Cama King", "Minibar premium", "Late checkout (sujeto disponibilidad)"]
                            },
                            "BAV ROOFTOP JT JS": {
                                "descripcion": "Junior Suite exclusiva con jacuzzi privado en la terraza superior",
                                "max_pax": 4,
                                "m2": 55,
                                "imagenes": [
                                    "media/habitaciones/CANA_BAV/grand_palladium_bavaro_suites_resort_rooftop-jacuzzi-terrace-junior-suite.webp",
                                    "media/habitaciones/CANA_BAV/grand_palladium_bavaro_suites_resort_rooftop-jacuzzi-terrace-junior-suite-1.webp",
                                    "media/habitaciones/CANA_BAV/grand_palladium_bavaro_suites_resort_rooftop-jacuzzi-terrace-junior-suite-3.webp"
                                ],
                                "servicios": ["Jacuzzi en azotea", "Vistas panorámicas", "Terraza privada", "Minibar", "WiFi"]
                            },
                        }
                    },
                    # .........................................................
                    # Grand Palladium Palace Resort & Spa
                    # .........................................................
                    "Grand Palladium Palace Resort & Spa": {
                        "hotel_code": "CANA_PAL",
                        "imagen": "media/hoteles/punta_cana/gp_palace.jpg",
                        "descripcion": "En Playa Bávaro. Resort todo incluido con amplias habitaciones, casino, spa, y acceso a instalaciones de Punta Cana y Bavaro.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "PAL DELUXE BEACHSIDE": {
                                "descripcion": "Habitación Deluxe con ubicación privilegiada junto a la playa",
                                "max_pax": 5,
                                "m2": 33,
                                "imagenes": ["media/habitaciones/CANA_PAL/deluxe-beachside.webp"],
                                "servicios": ["Vista parcial mar", "Cerca de la playa", "Minibar", "WiFi", "Aire acondicionado"]
                            },
                            "PAL DELUXE GARDEN VIEW": {
                                "descripcion": "Confortable habitación con relajantes vistas a los jardines",
                                "max_pax": 5,
                                "m2": 33,
                                "imagenes": [
                                    "media/habitaciones/CANA_PAL/deluxe-garden-view.webp",
                                    "media/habitaciones/CANA_PAL/deluxe-garden-view-1.webp"
                                ],
                                "servicios": ["Vista al jardín", "Minibar", "WiFi", "Aire acondicionado", "TV pantalla plana", "Caja fuerte"]
                            },
                            "PAL JUNIOR SUITE BS": {
                                "descripcion": "Junior Suite espaciosa ubicada a pocos pasos de la arena blanca",
                                "max_pax": 4,
                                "m2": 45,
                                "imagenes": ["media/habitaciones/CANA_PAL/grand_palladium_palace_resort_spa_casino-junior-suite-beachside.webp"],
                                "servicios": ["Proximidad playa", "Bañera hidromasaje", "Área de estar", "Minibar", "WiFi"]
                            },
                            "PAL JUNIOR SUITE BS OV": {
                                "descripcion": "Junior Suite con impresionantes vistas frontales al Mar Caribe",
                                "max_pax": 7,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/CANA_PAL/junior-suite-beachside-ocean-view.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-beachside-ocean-view-1.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-beachside-ocean-view-2.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-beachside-ocean-view-3.webp"
                                ],
                                "servicios": ["Vista al mar", "Bañera hidromasaje", "Minibar", "WiFi", "Amenities premium"]
                            },
                            "PAL JUNIOR SUITE GV": {
                                "descripcion": "Junior Suite rodeada de vegetación tropical y todas las comodidades",
                                "max_pax": 5,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/CANA_PAL/junior-suite-garden-view.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-garden-view-1.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-garden-view-2.webp"
                                ],
                                "servicios": ["Vista al jardín", "Bañera hidromasaje", "Minibar", "WiFi"]
                            },
                            "PAL JUNIOR SUITE SW BS": {
                                "descripcion": "Junior Suite con acceso directo a la piscina y ubicación frente a playa",
                                "max_pax": 4,
                                "m2": 48,
                                "imagenes": [
                                    "media/habitaciones/CANA_PAL/junior-suite-swim-up-beachside.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-swim-up-beachside-1.webp",
                                    "media/habitaciones/CANA_PAL/junior-suite-swim-up-beachside-3.webp"
                                ],
                                "servicios": ["Acceso Swim Up", "Frente a playa", "Terraza privada", "Minibar", "WiFi"]
                            },
                            "PAL LOFT SUITE GV": {
                                "descripcion": "Suite de dos niveles con dormitorio superior y salón en planta baja",
                                "max_pax": 8,
                                "m2": 62,
                                "imagenes": [
                                    "media/habitaciones/CANA_PAL/loft-suite-garden-view.webp",
                                    "media/habitaciones/CANA_PAL/loft-suite-garden-view-1.webp",
                                    "media/habitaciones/CANA_PAL/loft-suite-garden-view-2.webp"
                                ],
                                "servicios": ["Dos niveles", "Sofá cama", "Vista al jardín", "Minibar", "2 TVs"]
                            },
                            "PAL LOFT SUITE BS POV": {
                                "descripcion": "Loft Suite de lujo con vistas panorámicas al océano desde el área de playa",
                                "max_pax": 4,
                                "m2": 62,
                                "imagenes": [
                                    "media/habitaciones/CANA_PAL/loft-suite-beachside.webp",
                                    "media/habitaciones/CANA_PAL/loft-suite-beachside-1.webp",
                                    "media/habitaciones/CANA_PAL/loft-suite-beachside-2.webp"
                                ],
                                "servicios": ["Dos niveles", "Vista panorámica mar", "Ubicación playa", "Minibar premium", "WiFi"]
                            },
                        }
                    },
                    # .........................................................
                    # Grand Palladium Punta Cana Resort & Spa
                    # .........................................................
                    "Grand Palladium Punta Cana Resort & Spa": {
                        "hotel_code": "CANA_PC",
                        "imagen": "media/hoteles/punta_cana/gp_punta_cana.jpg",
                        "descripcion": "Resort familiar activo en Playa Bávaro. Amplia oferta de deportes acuáticos, piscinas, clubes infantiles y entretenimiento completo.",
                        "solo_adultos": False,
                        "habitaciones": {
                            "PC DELUXE GARDEN VIEW": {
                                "descripcion": "Habitación clásica y confortable con vistas a los jardines",
                                "max_pax": 6,
                                "m2": 34,
                                "imagenes": [
                                    "media/habitaciones/CANA_PC/grand-palladium-punta-cana-deluxe-garden-view-1.webp",
                                    "media/habitaciones/CANA_PC/grand-palladium-punta-cana-deluxe-garden-view-2.webp",
                                    "media/habitaciones/CANA_PC/grand-palladium-punta-cana-deluxe-garden-view-3.webp"
                                ],
                                "servicios": ["Vista al jardín", "WiFi", "Minibar", "Caja fuerte", "TV cable", "Plancha y tabla"]
                            },
                            "PC DELUXE POOLSIDE": {
                                "descripcion": "Habitación ubicada cerca de la zona de ocio y piscinas principales",
                                "max_pax": 4,
                                "m2": 34,
                                "imagenes": [
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Deluxe-Poolside-1.webp",
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Deluxe-Poolside-2.webp"
                                ],
                                "servicios": ["Junto a piscina", "Terraza/Balcón", "WiFi", "Minibar"]
                            },
                            "PC JUNIOR SUITE GV": {
                                "descripcion": "Junior Suite con mayor amplitud y elegantes vistas tropicales",
                                "max_pax": 6,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Junior-Suite-Garden-View1.webp",
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Junior-Suite-Garden-View2.webp"
                                ],
                                "servicios": ["Vista al jardín", "Sofá cama", "Bañera hidromasaje", "WiFi"]
                            },
                            "PC JUNIOR SUITE POOLSIDE": {
                                "descripcion": "Junior Suite con diseño moderno situada cerca de las piscinas",
                                "max_pax": 4,
                                "m2": 45,
                                "imagenes": [
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Junior-Suite-poolside.webp",
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Junior-Suite-poolside3.webp"
                                ],
                                "servicios": ["Vista piscina", "Sofá cama", "Bañera hidromasaje", "WiFi"]
                            },
                            "PC LOFT SUITE GV": {
                                "descripcion": "Suite de dos niveles ideal para familias que buscan espacio y confort",
                                "max_pax": 7,
                                "m2": 63,
                                "imagenes": [
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Loft-Suite-Garden-View1.webp",
                                    "media/habitaciones/CANA_PC/Grand-Palladium-Punta-Cana-Loft-Suite-Garden-View2.webp"
                                ],
                                "servicios": ["Dos niveles", "Vista al jardín", "Minibar", "2 Baños", "WiFi"]
                            },
                        }
                    },
                    # .........................................................
                    # TRS Turquesa Hotel (Solo Adultos)
                    # .........................................................
                    "TRS Turquesa Hotel": {
                        "hotel_code": "CANA_TRS",
                        "imagen": "media/hoteles/punta_cana/trs_turquesa.jpg",
                        "descripcion": "Solo adultos exclusivo en Punta Cana. Acceso privado a playa, servicio de mayordomo, piscinas privadas y acceso a todas las instalaciones del Grand Palladium vecino.",
                        "solo_adultos": True,
                        "habitaciones": {
                            "TRS JUNIOR SUITE GV/PV": {
                                "descripcion": "Junior Suite elegante con vistas a los jardines o la piscina principal",
                                "max_pax": 4,
                                "m2": 52,
                                "imagenes": [
                                    "media/habitaciones/CANA_TRS/TRS_TURQUESA_HOTEL_TRS_JUNIOR-SUITE.webp",
                                    "media/habitaciones/CANA_TRS/TRS-TURQUESA-JUNIOR-SUITE-GARDEN-POOL-VIEW-5535_MG_1969.webp",
                                    "media/habitaciones/CANA_TRS/TRS-TURQUESA-JUNIOR-SUITE-GARDEN-POOL-VIEW-5535_MG_1989.webp"
                                ],
                                "servicios": ["Mayordomo", "Vista jardín/piscina", "Bañera hidromasaje", "Minibar premium", "WiFi"]
                            },
                            "TRS JUNIOR SUITE PS": {
                                "descripcion": "Junior Suite Premium ubicada en primera línea de piscina",
                                "max_pax": 3,
                                "m2": 52,
                                "imagenes": [
                                    "media/habitaciones/CANA_TRS/TRS-TURQUESA-JUNIOR-SUITE-POOLSIDE-5225_MG_2181.webp",
                                    "media/habitaciones/CANA_TRS/TRS-TURQUESA-JUNIOR-SUITE-POOLSIDE-5225_MG_2205.webp"
                                ],
                                "servicios": ["Junto a piscina", "Mayordomo", "Amenities VIP", "Minibar premium", "WiFi"]
                            },
                            "TRS JUNIOR SUITE SWIM UP": {
                                "descripcion": "Junior Suite con acceso privado y directo a la piscina desde su terraza",
                                "max_pax": 3,
                                "m2": 55,
                                "imagenes": [
                                    "media/habitaciones/CANA_TRS/TRS_TURQUESA_HOTEL_JUNIOR-SUITE-SWIM-UP.webp",
                                    "media/habitaciones/CANA_TRS/Royal-Deluxe-Junior-Suite-swim-up-2-.webp"
                                ],
                                "servicios": ["Acceso Swim Up", "Mayordomo", "Terraza privada", "Minibar premium", "WiFi"]
                            },
                            "TRS ROMANCE SUITE PS": {
                                "descripcion": "Suite de lujo diseñada exclusivamente para parejas con jacuzzi y vistas piscina",
                                "max_pax": 3,
                                "m2": 68,
                                "imagenes": [
                                    "media/habitaciones/CANA_TRS/TRS_TURQUESA_HOTEL_ROMANCE-SUITE.webp",
                                    "media/habitaciones/CANA_TRS/TRS-TURQUESA-ROMANCE-SUITE-POOLSIDE-5519_MG_1962.webp"
                                ],
                                "servicios": ["Detalles románticos", "Mayordomo", "Jacuzzi", "Vista piscina", "Room service 24h"]
                            },
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
        "descuento": 0.0,
        "color": "#dc3545"
    },
    "Flexible - Paga Ahora": {
        "descripcion": "Cancelacion gratuita hasta 7 dias antes. Pago completo en el momento de la reserva.",
        "descuento": 0.0,
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
        --dorado: #BB9719;
        --dorado-oscuro: #6E550C;
        --azul: #292929;
        --azul-claro: #50685C;
        --blanco: #FFFFFF;
        --gris-claro: #F0EDE6;
        --gris: #AEA780;
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
    
    /* Estilo para opción de tarifa seleccionada */
    div[data-testid="stMetricValue"] {
        color: var(--dorado-oscuro) !important;
    }
    
    .tarifa-selected {
        border: 2px solid var(--dorado);
        background-color: #FFF9E6;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Palladium Rewards Card */
    .rewards-card {
        background-color: #536458;
        border-radius: 8px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: 'Gill Sans', 'Century Gothic', sans-serif;
        width: 100%; /* El ancho se controla con las columnas de Streamlit */
    }
    .rewards-logo {
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 1.4em;
        margin-bottom: 0px;
        font-weight: 400;
    }
    .rewards-subtitle {
        font-size: 0.6em;
        letter-spacing: 5px;
        margin-bottom: 10px;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Nuevas cabeceras compactas y coloridas */
    .palladium-header {
        background: linear-gradient(90deg, var(--dorado-oscuro) 0%, var(--dorado) 100%);
        color: white;
        padding: 6px 15px;
        border-radius: 4px;
        font-family: 'Century Gothic', sans-serif;
        font-weight: 500;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        margin-bottom: 15px;
        margin-top: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
    }
    
    .palladium-header i, .palladium-header span {
        margin-right: 10px;
    }

    .form-section {
        border: 1px solid #eee;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 15px;
        background: white;
    }
    
    .form-section h3 {
        display: none; /* Ocultar h3 viejos si quedan */
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
    
    /* Expander plano habitación - estilo dorado */
    [data-testid="stExpander"] {
        border: 2px solid var(--dorado) !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, rgba(201, 162, 39, 0.1) 0%, rgba(166, 133, 35, 0.05) 100%) !important;
    }
    
    [data-testid="stExpander"] summary {
        color: var(--dorado) !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stExpander"] summary:hover {
        background: rgba(201, 162, 39, 0.15) !important;
    }
    
    /* Galería de imágenes habitación - miniaturas uniformes */
    [data-testid="stImage"] img {
        border-radius: 8px;
    }
    
    /* Miniaturas - altura uniforme forzada */
    .gallery-thumbs + div [data-testid="column"] [data-testid="stImage"] img,
    [data-testid="column"] [data-testid="stImage"] img {
        height: 120px !important;
        max-height: 120px !important;
        min-height: 120px !important;
        object-fit: cover !important;
        width: 100% !important;
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
    
    /* RELOJ DIGITAL PALLADIUM */
    .digital-clock-container {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 10000;
        background: rgba(255, 255, 255, 0.95);
        padding: 5px 15px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #bfa05a; /* Gold border */
        text-align: center;
        min-width: 120px;
        font-family: 'Century Gothic', 'Roboto', sans-serif;
    }
    
    .digital-time {
        font-size: 24px;
        font-weight: bold;
        color: #1B365D; /* Palladium Blue */
        letter-spacing: 1px;
        line-height: 1.2;
    }
    
    .digital-date {
        font-size: 11px;
        color: #8B6914; /* Darker Gold */
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 2px;
        border-top: 1px solid #eee;
        padding-top: 2px;
    }

""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================

# Logo centrado (20% mas pequeño)
col_vacio1, col_logo, col_vacio2 = st.columns([1.5, 1.5, 1.5])
with col_logo:
    st.image("media/general/3.jpg", use_container_width=True)

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
    st.image("media/general/3.jpg", use_container_width=True)
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
            # PROTECCIÓN CONTRA ERRORES: Si el hotel no existe, volver al paso 2
            try:
                datos_hotel = DESTINOS[destino]["complejos"][complejo]["hoteles"][hotel]
            except KeyError:
                st.error(f"Error: No se encontraron datos para el hotel '{hotel}'. Volviendo al menú anterior.")
                st.session_state.paso_actual = 2
                st.rerun()
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
                st.markdown('<div class="palladium-header"><i class="fas fa-calendar-alt"></i><span>Fechas y huéspedes</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
            
                # Inicializar keys si no existen para evitar errores
                if "w_llegada" not in st.session_state: st.session_state.w_llegada = datetime.now().date() + timedelta(days=30)
                if "w_salida" not in st.session_state: st.session_state.w_salida = datetime.now().date() + timedelta(days=37)
                if "w_adultos" not in st.session_state: st.session_state.w_adultos = 2
                if "w_ninos" not in st.session_state: st.session_state.w_ninos = 0
                if "w_cunas" not in st.session_state: st.session_state.w_cunas = 0

                fecha_entrada = st.date_input("Llegada", key="w_llegada")
                fecha_salida = st.date_input("Salida", key="w_salida")
                noches = max((fecha_salida - fecha_entrada).days, 1)
                st.caption(f"Estancia: {noches} noches")
            
                col_a, col_n, col_c = st.columns(3)
                with col_a:
                    adultos = st.number_input("Adultos", min_value=1, max_value=6, key="w_adultos")
                with col_n:
                    # Si es solo adultos, no mostrar ninos
                    if datos_hotel.get("solo_adultos", False):
                        ninos = 0
                        st.caption("Hotel solo adultos")
                    else:
                        ninos = st.number_input("Niños", min_value=0, max_value=4, key="w_ninos")
                with col_c:
                    if datos_hotel.get("solo_adultos", False):
                        cunas = 0
                    else:
                         cunas = st.number_input("Cunas (0-2)", min_value=0, max_value=2, key="w_cunas")
            
                total_pax = adultos + ninos
                if "w_pais" not in st.session_state: st.session_state.w_pais = "ESPAÑA"

                # Cargar lista de paises si no existe en session_state
                if "lista_paises" not in st.session_state:
                    try:
                        df_res = pd.read_csv("reservas_2026.csv")
                        paises = sorted(df_res["PAIS_TOP"].unique().tolist())
                        # Asegurar que ESPAÑA esté si es necesario, o usar el dataset tal cual
                        if "ESPAÑA" not in paises: paises.append("ESPAÑA")
                        st.session_state.lista_paises = sorted(paises)
                    except:
                        st.session_state.lista_paises = ["ALEMANIA", "ARGENTINA", "BRASIL", "CANADA", "ESPAÑA", "ESTADOS UNIDOS", "FRANCIA", "ITALIA", "MEXICO", "OTROS", "REINO UNIDO"]

                # Selector de País
                st.selectbox(
                    "País de residencia",
                    st.session_state.lista_paises,
                    index=st.session_state.lista_paises.index(st.session_state.w_pais) if st.session_state.w_pais in st.session_state.lista_paises else 0,
                    key="w_pais"
                )

                st.markdown('</div>', unsafe_allow_html=True)
            
                # Regimen
                st.markdown('<div class="palladium-header" style="margin-top:20px;"><i class="fas fa-utensils"></i><span>Régimen</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                # Inicializar si no existe
                if "w_regimen" not in st.session_state: st.session_state.w_regimen = "All Inclusive"
                regimen = st.radio("", list(REGIMENES.keys()), label_visibility="collapsed", key="w_regimen")
                st.caption(REGIMENES[regimen]["descripcion"])
                st.markdown('</div>', unsafe_allow_html=True)
            
                # Mostrar plano de habitación colapsado (Movido aquí)
                habitaciones_posibles = {n: d for n, d in habitaciones_hotel.items() if d["max_pax"] >= total_pax}
                if not habitaciones_posibles: habitaciones_posibles = habitaciones_hotel
                hab_actual_key_plano = st.session_state.get("w_habitacion", list(habitaciones_posibles.keys())[0])
                
                if hab_actual_key_plano in habitaciones_posibles:
                    datos_plano = habitaciones_posibles[hab_actual_key_plano]
                    if "plano" in datos_plano:
                         with st.expander("Ver plano de la habitación"):
                            try:
                                st.image(datos_plano["plano"], use_container_width=True)
                            except:
                                st.info("Plano no disponible")
            
                st.markdown('</div>', unsafe_allow_html=True)
            
            # --- MOSTRAR DETALLES DE LA HABITACIÓN SELECCIONADA AQUÍ (IZQUIERDA) ---
            
            habitaciones_posibles = {n: d for n, d in habitaciones_hotel.items() if d["max_pax"] >= total_pax}
            if not habitaciones_posibles: habitaciones_posibles = habitaciones_hotel
            
            hab_actual_key = st.session_state.get("w_habitacion", list(habitaciones_posibles.keys())[0])
            
            if hab_actual_key in habitaciones_posibles:
                datos_hab_actual = habitaciones_posibles[hab_actual_key]
                
                # Usar un contenedor con menos padding/margen via markdown
                # Usar un contenedor con menos padding/margen via markdown
                st.markdown(f"""
                <div class="palladium-header"><i class="fas fa-info-circle"></i><span>Detalles de la habitación</span></div>
                <div class="form-section">
                    <p style="font-size: 0.95em; margin-bottom: 5px;"><strong>{datos_hab_actual['descripcion']}</strong></p>
                """, unsafe_allow_html=True)
                
                # Metros cuadrados
                if "m2" in datos_hab_actual:
                    st.markdown(f"<p style='font-size: 0.9em; margin: 0;'>📐 Tamaño: <strong>{datos_hab_actual['m2']} m²</strong></p>", unsafe_allow_html=True)
                
                # Servicios en lista compacta
                if "servicios" in datos_hab_actual:
                    st.markdown("<h5 style='margin-top:10px; margin-bottom:5px; font-size:1em;'>Servicios incluidos:</h5>", unsafe_allow_html=True)
                    # Crear HTML de lista compacta
                    servicios_html = "<ul style='margin: 0; padding-left: 20px; font-size: 0.9em;'>"
                    for servicio in datos_hab_actual["servicios"]:
                         servicios_html += f"<li style='margin-bottom: 2px;'>{servicio}</li>"
                    servicios_html += "</ul>"
                    st.markdown(servicios_html, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
        
            with col2:
                # Tipo de habitacion - usando las del hotel seleccionado (diccionario)
                st.markdown('<div class="palladium-header"><i class="fas fa-bed"></i><span>Tipo de habitación</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
            
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
            
                # Mostrar detalles de la habitacion seleccionada
                if habitacion_sel in habitaciones_disponibles:
                    datos_hab = habitaciones_disponibles[habitacion_sel]
                    
                    # Mostrar galería de imágenes si existe
                    if "imagenes" in datos_hab and datos_hab["imagenes"]:
                        # Mostrar imagen principal grande
                        # Mostrar imagen principal grande (Limitada a 400px para que no ocupe todo)
                        try:
                            st.image(datos_hab["imagenes"][0], width=400)
                        except:
                            pass
                        
                        # Mostrar resto de fotos en fila pequeña
                        if len(datos_hab["imagenes"]) > 1:
                            st.markdown('<div class="gallery-thumbs">', unsafe_allow_html=True)
                            img_cols = st.columns(len(datos_hab["imagenes"]) - 1)
                            for i, img_path in enumerate(datos_hab["imagenes"][1:]):
                                with img_cols[i]:
                                    try:
                                        st.image(img_path, use_container_width=True)
                                    except:
                                        pass
                            st.markdown('</div>', unsafe_allow_html=True)
                    # Compatibilidad con habitaciones que solo tienen una imagen
                    elif "imagen" in datos_hab:
                        try:
                            st.image(datos_hab["imagen"], width=400)
                        except:
                            pass
                    
                    # Mostrar plano si existe
                    
                    # Plano movido a la izquierda

                    
                    
                    # Descripción y detalles movidos a la columna izquierda
                    
                    # Mostrar metros cuadrados (opcional mantener aquí o quitar)
                    if "m2" in datos_hab:
                        # st.markdown(f"📐 **{datos_hab['m2']} m²**")
                        pass
                    
                    # Servicios (movidos a izquierda)
            
                st.markdown('</div>', unsafe_allow_html=True)
        
            # Tipo de tarifa
            st.markdown('<div class="palladium-header"><i class="fas fa-tags"></i><span>Elige tu tarifa</span></div>', unsafe_allow_html=True)
            # Palladium Rewards Banner
            # Palladium Rewards Banner - Centrado y con Checkbox debajo
            col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
            with col_r2:
                st.markdown("""
                <div class="rewards-card">
                    <div class="rewards-logo">PALLADIUM</div>
                    <div class="rewards-subtitle">R E W A R D S</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón HAZTE MIEMBRO justo debajo de la tarjeta
                if "w_fidelizado" not in st.session_state: st.session_state.w_fidelizado = False

                if not st.session_state.w_fidelizado:
                    if st.button("HAZTE MIEMBRO", key="btn_hazte_miembro", use_container_width=True):
                        st.session_state.w_fidelizado = True
                        st.session_state.chk_rewards = True
                        st.rerun()
                else:
                    st.button("MIEMBRO ACTIVO ✓", key="btn_miembro_activo", disabled=True, use_container_width=True)

                # Checkbox para activar membresía (Validation)
                is_member = st.checkbox("Soy miembro de Palladium Rewards (5% descuento adicional)", value=st.session_state.w_fidelizado, key="chk_rewards")
                
                # Sincronizar estado
                if is_member != st.session_state.w_fidelizado:
                    st.session_state.w_fidelizado = is_member
                    st.rerun()

                if st.session_state.w_fidelizado:
                    st.success("¡Descuento de Palladium Rewards aplicado! (5% extra)")

            st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
            # Selector de tarifa con Radio Button para feedback visual claro
            # =====================================================================
            # CALCULO DE PRECIO BASE (ANTES DE TARIFA)
            # =====================================================================
            precio_base = 0
            
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
            from datetime import date
            fecha_actual = fecha_entrada
            while fecha_actual < fecha_salida:
                iso_calendar = fecha_actual.isocalendar()
                año = iso_calendar[0]
                semana = iso_calendar[1]
                semana_columna = f"{año}-{semana:02d}"
            
                adr_noche = precios_pax.get(semana_columna, 200.0)
                precio_base += adr_noche * total_pax
                fecha_actual = fecha_actual + timedelta(days=1)
        
            # Aplicar suplemento de regimen
            suplemento_regimen = REGIMENES[regimen]["suplemento"] * noches * total_pax
            precio_base += suplemento_regimen

            # ---------------------------------------------------------------------
            # SELECTOR DE TARIFA VISUAL (TARJETAS)
            # ---------------------------------------------------------------------
            if "tarifa_seleccionada" not in st.session_state:
                st.session_state.tarifa_seleccionada = "Flexible - Paga Ahora"

            # CSS para las tarjetas de tarifa
            st.markdown("""
            <style>
            .tarifa-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
                height: 100%;
                transition: all 0.3s ease;
                background-color: white;
            }
            .tarifa-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .tarifa-selected-card {
                border: 2px solid #bfa05a;
                background-color: #fffdf5;
                box-shadow: 0 0 10px rgba(191,160,90,0.2);
            }
            .tarifa-title {
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 5px;
                color: #333;
            }
            .tarifa-price {
                font-size: 1.5em;
                font-weight: bold;
                color: #bfa05a;
                margin: 10px 0;
            }
            .tarifa-desc {
                font-size: 0.85em;
                color: #666;
                margin-bottom: 15px;
                min-height: 40px;
            }
            .tarifa-tag {
                display: inline-block;
                padding: 3px 8px;
                background-color: #f0f0f0;
                border-radius: 12px;
                font-size: 0.75em;
                color: #555;
                margin-bottom: 10px;
            }
            </style>
            """, unsafe_allow_html=True)

            columnas_tarifas = st.columns(3)
            tarifas_options = list(TARIFAS.keys())

            for i, nombre_tarifa in enumerate(tarifas_options):
                datos_t = TARIFAS[nombre_tarifa]
                
                # Calcular precio específico para esta tarifa
                desc = datos_t["descuento"]
                precio_calc = precio_base * (1 - desc)
                # Aplicar Rewards si corresponde para mostrar precio final real
                if st.session_state.w_fidelizado:
                    precio_calc *= 0.95
                
                es_seleccionada = (st.session_state.tarifa_seleccionada == nombre_tarifa)
                clase_extra = "tarifa-selected-card" if es_seleccionada else ""
                icono_check = "✅" if es_seleccionada else ""
                
                with columnas_tarifas[i]:
                    div_tag = f'<div class="tarifa-tag">{int(desc*100)}% Dto</div>' if desc > 0 else ""
                    html_card = f'<div class="tarifa-card {clase_extra}"><div class="tarifa-title">{nombre_tarifa} {icono_check}</div>{div_tag}<div class="tarifa-desc">{datos_t["descripcion"]}</div><div class="tarifa-price">${precio_calc:,.0f}</div></div>'
                    st.markdown(html_card, unsafe_allow_html=True)
                    
                    label_btn = "Seleccionar" if not es_seleccionada else "Seleccionado"
                    btn_type = "primary" if es_seleccionada else "secondary"
                    
                    if st.button(label_btn, key=f"btn_tarifa_{i}", use_container_width=True, type=btn_type):
                        st.session_state.tarifa_seleccionada = nombre_tarifa
                        st.rerun()
            
            tarifa = st.session_state.tarifa_seleccionada
            
            # Actualizar estado
            st.session_state.tarifa_seleccionada = tarifa
            
            # Mostrar detalle visual de la selección
            st.info(f"Has seleccionado: **{tarifa}**")
        
            tarifa = st.session_state.tarifa_seleccionada
            st.markdown('</div>', unsafe_allow_html=True)
        
            # Palladium Rewards (DUPLICADO ELIMINADO)
            # tiene_rewards = st.checkbox("Soy miembro de Palladium Rewards (5% descuento adicional)")
            tiene_rewards = st.session_state.w_fidelizado
        
            # =====================================================================
            # CALCULO DE PRECIO FINAL
            # =====================================================================
            # Recalcular precio total final basado en la selección actual
            descuento_tarifa = TARIFAS[tarifa]["descuento"]
            precio_total = precio_base * (1 - descuento_tarifa)
        
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
                    # Calcular Lead Time para el modelo de predicción
                    datos["lead_time"] = (datos["fecha_entrada"] - datos["fecha_creacion"].date()).days
                    
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
        st.image("media/general/marcas_palladium.png", use_container_width=True)
    except:
        pass  # Si no existe la imagen, no mostrar error

st.markdown("""
<div class="footer">
    <p><strong>Palladium Hotel Group</strong></p>
    <p>TFM Grupo 4 - Master en Data Science | Sistema de Prediccion de Cancelaciones</p>
</div>
""", unsafe_allow_html=True)



