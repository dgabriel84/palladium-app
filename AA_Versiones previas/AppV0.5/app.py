"""
Palladium Hotel Group - Sistema de Prediccion de Cancelaciones
Aplicacion unificada con navegacion superior y wizard de reserva.

Estructura Cliente (Wizard 4 pasos):
1. Destino (Cancun / Punta Cana)
2. Datos del cliente
3. Hotel, habitacion y condiciones
4. Confirmacion

Estructura Intranet:
- Busqueda por codigo de reserva
- Panel de prediccion manual

Autor: Grupo 4 - TFM Palladium
Fecha: Febrero 2026
"""

import streamlit as st
import pandas as pd
import datetime
import sys
import os
import numpy as np
import random

# -----------------------------------------------------------------------------
# CONFIGURACION DE RUTAS
# -----------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_model, get_features

# -----------------------------------------------------------------------------
# CONFIGURACION DE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Palladium Hotels",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# PALETA DE COLORES CORPORATIVOS
# -----------------------------------------------------------------------------
COLOR_DORADO_OSCURO = "#6E550C"
COLOR_DORADO = "#BB9719"
COLOR_BEIGE = "#CCC3A5"
COLOR_VERDE_OSCURO = "#50685C"
COLOR_NEGRO = "#292929"
COLOR_GRIS = "#757171"
COLOR_OLIVA = "#AEA780"
COLOR_CREMA = "#FCF4E4"
COLOR_CREMA_CLARO = "#F0EDE6"
COLOR_BEIGE_CLARO = "#E3D7C1"
COLOR_BLANCO = "#FFFFFF"
COLOR_RIESGO_ALTO = "#C0392B"
COLOR_RIESGO_MEDIO = "#D68910"
COLOR_RIESGO_BAJO = "#1E8449"

# -----------------------------------------------------------------------------
# ESTILOS CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
    [data-testid="stSidebarNav"] {{ display: none; }}
    .main {{ background-color: {COLOR_CREMA_CLARO}; }}
    
    /* Wizard steps */
    .wizard-container {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1.5rem 0 2rem 0;
        padding: 1rem;
        background: {COLOR_BLANCO};
        border-radius: 4px;
    }}
    .wizard-step {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: {COLOR_GRIS};
    }}
    .wizard-step.active {{
        color: {COLOR_DORADO_OSCURO};
        font-weight: 500;
    }}
    .wizard-step.completed {{
        color: {COLOR_VERDE_OSCURO};
    }}
    .step-number {{
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: {COLOR_BEIGE};
        font-size: 0.85rem;
    }}
    .wizard-step.active .step-number {{
        background: {COLOR_DORADO_OSCURO};
        color: {COLOR_BLANCO};
    }}
    .wizard-step.completed .step-number {{
        background: {COLOR_VERDE_OSCURO};
        color: {COLOR_BLANCO};
    }}
    
    /* Destino cards */
    .destino-card {{
        background: {COLOR_BLANCO};
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
    }}
    .destino-card:hover {{
        border-color: {COLOR_DORADO};
        transform: translateY(-5px);
    }}
    .destino-card h3 {{
        color: {COLOR_NEGRO};
        margin-bottom: 0.5rem;
    }}
    .destino-card p {{
        color: {COLOR_GRIS};
        font-size: 0.9rem;
    }}
    
    /* Content card */
    .content-card {{
        background: {COLOR_BLANCO};
        border-radius: 4px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 3px solid {COLOR_DORADO};
    }}
    
    /* Form section */
    .form-section {{
        background: {COLOR_BLANCO};
        padding: 1.5rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        border-left: 3px solid {COLOR_OLIVA};
    }}
    
    /* Precio */
    .price-display {{
        font-size: 2.5rem;
        font-weight: 300;
        color: {COLOR_DORADO_OSCURO};
    }}
    .price-label {{
        color: {COLOR_GRIS};
        font-size: 0.9rem;
    }}
    
    /* Success box */
    .success-box {{
        background: {COLOR_VERDE_OSCURO};
        color: {COLOR_BLANCO};
        padding: 2.5rem;
        text-align: center;
        border-radius: 8px;
    }}
    .success-box h2 {{ font-weight: 300; letter-spacing: 1px; }}
    .reservation-code {{
        font-size: 2rem;
        font-weight: 500;
        letter-spacing: 2px;
        margin: 1rem 0;
        padding: 0.5rem 1.5rem;
        background: rgba(255,255,255,0.2);
        border-radius: 4px;
        display: inline-block;
    }}
    
    /* Result card */
    .result-card {{
        background: {COLOR_BLANCO};
        border-radius: 8px; /* Redondeado 8px */
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid {COLOR_BEIGE};
    }}
    .result-value {{ font-size: 3rem; font-weight: 300; }}
    .result-label {{
        color: {COLOR_GRIS};
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .risk-high {{ color: {COLOR_RIESGO_ALTO}; border-left: 5px solid {COLOR_RIESGO_ALTO}; border-radius: 4px; }}
    .risk-medium {{ color: {COLOR_RIESGO_MEDIO}; border-left: 5px solid {COLOR_RIESGO_MEDIO}; border-radius: 4px; }}
    .risk-low {{ color: {COLOR_RIESGO_BAJO}; border-left: 5px solid {COLOR_RIESGO_BAJO}; border-radius: 4px; }}
    
    /* Buttons (Dorado -> Marrón) */
    .stButton > button {{
        background: {COLOR_DORADO};
        color: {COLOR_BLANCO};
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px; /* Redondeado 8px */
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .stButton > button:hover {{ background: {COLOR_DORADO_OSCURO}; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
    
    section[data-testid="stSidebar"] {{ background-color: {COLOR_BLANCO}; }}
    
    /* Fotos de hotel - más altas */
    .hotel-card div[data-testid="stImage"] img {{
        height: 180px !important;
    }}
    
    /* Galería de habitaciones - tamaño uniforme */
    div[data-testid="stImage"] {{
        overflow: hidden;
        border-radius: 8px;
    }}
    div[data-testid="stImage"] img {{
        width: 100%;
        height: 160px !important;
        object-fit: cover;
        border-radius: 8px;
        transition: transform 0.3s ease;
    }}
    div[data-testid="stImage"]:hover img {{
        transform: scale(1.02);
    }}
    
    /* Planos de planta más altos */
    .stExpander div[data-testid="stImage"] img {{
        height: 280px !important;
    }}
    
    /* Scroll suave */
    html {{
        scroll-behavior: smooth;
    }}
    
    /* Ancla para scroll */
    #habitaciones-section {{
        scroll-margin-top: 20px;
    }}
    
    /* ===============================
       ESTILOS INPUTS ELEGANTES PALLADIUM
       =============================== */
    
    /* Inputs de texto, número y fecha */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
        color: {COLOR_NEGRO} !important;
        padding: 0.5rem !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {{
        border-color: {COLOR_DORADO_OSCURO} !important;
        box-shadow: 0 0 0 2px rgba(110, 85, 12, 0.2) !important;
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: {COLOR_DORADO_OSCURO} !important;
    }}
    
    /* Dropdown del selectbox */
    div[data-baseweb="select"] > div {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
    }}
    
    div[data-baseweb="select"] > div:focus-within {{
        border-color: {COLOR_DORADO_OSCURO} !important;
        box-shadow: 0 0 0 2px rgba(110, 85, 12, 0.2) !important;
    }}
    
    /* Multiselect */
    .stMultiSelect > div > div {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
    }}
    
    /* Date input container */
    .stDateInput > div > div {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
    }}
    
    /* Ajuste simple para inputs numéricos */
    .stNumberInput > div > div {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
        color: {COLOR_NEGRO} !important;
    }}
    
    /* Asegurar que el texto sea visible */
    .stNumberInput input {{
        color: {COLOR_NEGRO} !important;
    }}
    
    /* Labels de los campos */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label,
    .stMultiSelect label {{
        color: {COLOR_DORADO_OSCURO} !important;
        font-weight: 500 !important;
    }}
    
    /* Expander headers */
    .streamlit-expanderHeader {{
        background-color: {COLOR_CREMA} !important;
        border: 1px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
        color: {COLOR_DORADO_OSCURO} !important;
        font-weight: 500 !important;
    }}
    
</style>"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATOS MAESTROS
# Estructura jerarquica: Destino > Complejo > Hotel > Habitaciones
# El modelo recibe NOMBRE_HOTEL = Complejo, pero el usuario selecciona Hotel
# -----------------------------------------------------------------------------

CODIGO_HOTEL = {
    "Complejo Costa Mujeres": "09601",
    "Complejo Riviera Maya": "10601",
    "Complejo Punta Cana": "10701"
}

# Estructura completa de hoteles por complejo
HOTELES_POR_COMPLEJO = {
    "Complejo Costa Mujeres": {
        "Grand Palladium Select Costa Mujeres": {
            "descripcion": "Resort de lujo frente al mar Caribe con playa privada y servicios premium",
            "prefijo": "CMU",
            "habitaciones": [
                "CMU JUNIOR SUITE GV",
                "CMU JUNIOR SUITE PS", 
                "CMU JUNIOR SUITE PS OV",
                "CMU FAMILY SUITE"
            ]
        },
        "Family Selection Costa Mujeres": {
            "descripcion": "Experiencia familiar exclusiva con servicios especiales para familias con niños",
            "prefijo": "CMU FS",
            "habitaciones": [
                "CMU FS JUNIOR SUITE BS",
                "CMU FS JUNIOR SUITE BS OV"
            ]
        },
        "TRS Coral Hotel": {
            "descripcion": "Hotel solo adultos con experiencia premium y servicios exclusivos",
            "prefijo": "TRSC",
            "habitaciones": [
                "TRSC JUNIOR SUITE GV",
                "TRSC JUNIOR SUITE SW",
                "TRSC JUNIOR SUITE BS OV",
                "TRS JUNIOR SUITE GV",
                "TRS JUNIOR SUITE OV",
                "TRS JUNIOR SUITE SW"
            ]
        }
    },
    "Complejo Riviera Maya": {
        "Grand Palladium Colonial Resort & Spa": {
            "descripcion": "Resort con arquitectura colonial junto a la playa y cenotes naturales",
            "prefijo": "COL",
            "habitaciones": [
                "COL JUNIOR SUITE GV",
                "COL JUNIOR SUITE PS",
                "COL DELUXE GARDEN VIEW",
                "COL ROMANCE VILLA SUI PS"
            ]
        },
        "Grand Palladium Kantenah Resort & Spa": {
            "descripcion": "Resort frente al mar con acceso a cenote privado y actividades acuáticas",
            "prefijo": "KAN",
            "habitaciones": [
                "KAN JUNIOR SUITE GV",
                "KAN JUNIOR SUITE OV",
                "KAN DELUXE GARDEN VIEW"
            ]
        },
        "TRS Yucatan Hotel": {
            "descripcion": "Hotel solo adultos con experiencia gourmet y spa de lujo",
            "prefijo": "TRS",
            "habitaciones": [
                "TRS JUNIOR SUITE GV",
                "TRS JUNIOR SUITE PS",
                "TRS JUNIOR SUITE PS OV",
                "TRS JS JACUZZI TERR PS",
                "TRS SUITE GARDEN VIEW",
                "TRS SUITE PP PS",
                "TRS AMBASSADOR SUITE POV",
                "TRS ROMANCE BW BYTHE LAKE"
            ]
        },
        "Grand Palladium Select White Sand": {
            "descripcion": "Resort premium con playa de arena blanca y servicios exclusivos",
            "prefijo": "WS",
            "habitaciones": [
                "WS JUNIOR SUITE GV",
                "WS JUNIOR SUITE BS",
                "WS SUITE GARDEN VIEW"
            ]
        }
    },
    "Complejo Punta Cana": {
        "Grand Palladium Select Bavaro": {
            "descripcion": "Resort premium en playa Bávaro con servicios Select exclusivos",
            "prefijo": "BAV",
            "habitaciones": [
                "BAV JUNIOR SUITE GV",
                "BAV SUPERIOR JS GV",
                "BAV SUPERIOR JS BS",
                "BAV PREMIUM JS GV",
                "BAV ROOFTOP JT ST"
            ]
        },
        "Grand Palladium Palace Resort & Spa": {
            "descripcion": "Resort emblemático con arquitectura elegante y spa de clase mundial",
            "prefijo": "PAL",
            "habitaciones": [
                "PAL JUNIOR SUITE GV",
                "PAL JUNIOR SUITE BS",
                "PAL JUNIOR SUITE SW BS",
                "PAL JUNIOR SUITE BS OV",
                "PAL DELUXE BEACHSIDE",
                "PAL DELUXE GARDEN VIEW",
                "PAL DELUXE BS POV",
                "PAL LOFT SUITE GV"
            ]
        },
        "Grand Palladium Punta Cana Resort & Spa": {
            "descripcion": "Resort familiar con amplia oferta de actividades y entretenimiento",
            "prefijo": "PC",
            "habitaciones": [
                "PC JUNIOR SUITE GV",
                "PC JUNIOR SUITE POOLSIDE",
                "PC DELUXE GARDEN VIEW",
                "PC DELUXE POOLSIDE",
                "PC FAMILY SUITE"
            ]
        },
        "TRS Turquesa Hotel": {
            "descripcion": "Hotel solo adultos con playa privada y experiencia gastronómica exclusiva",
            "prefijo": "TRS",
            "habitaciones": [
                "TRS JUNIOR SUITE GV/PV",
                "TRS JUNIOR SUITE PS",
                "TRS JUNIOR SUITE SWIM UP",
                "TRS ROMANCE SUITE PS"
            ]
        }
    }
}

# Mapeo de destinos a complejos
DESTINOS = {
    "MEXICO": {
        "nombre": "Cancun - Riviera Maya",
        "descripcion": "Costa Mujeres y Riviera Maya",
        "complejos": ["Complejo Costa Mujeres", "Complejo Riviera Maya"]
    },
    "REPUBLICA DOMINICANA": {
        "nombre": "Punta Cana",
        "descripcion": "Playa Bávaro y Palladium Resort",
        "complejos": ["Complejo Punta Cana"]
    }
}

PAISES = [
    "ESPAÑA", "ESTADOS UNIDOS", "CANADA", "MEXICO", "ALEMANIA", "REINO UNIDO",
    "FRANCIA", "ITALIA", "ARGENTINA", "BRASIL", "COLOMBIA", "CHILE", "PERU",
    "URUGUAY", "REPUBLICA DOMINICANA", "SUECIA", "POLONIA", "SIN PAIS"
]

SEGMENTOS = ["BAR", "Fixed Rates", "Loyalty", "Package", "Group Leisure", "Weddings"]
FUENTES_NEGOCIO = ["DIRECT SALES", "T.O. / T.A.", "E-COMMERCE", "CORPORATE"]
CLIENTES = [
    "ROIBACK (GLOBAL OBI S.L.)", "CALL CENTER", "PALLADIUM TRAVEL CLUB_SOCIOS",
    "EXPEDIA", "BOOKING EUROPE BV", "AGODA COMPANY PTE LTD", "HOTELBEDS USA INC.",
    "DESPEGAR.COM MEXICO S.A. DE C.V.", "FUNJET VACATIONS ALG", "CVC BRASIL", "OTROS"
]
PROGRAMAS_FIDELIDAD = ["Sin programa", "Palladium Rewards", "WyndHam Rewards", "Palladium Connect"]

# Mapeo de imagenes de hoteles
IMAGENES_HOTELES = {
    "Grand Palladium Select Costa Mujeres": "hoteles/costa_mujeres/gp_select_costa_mujeres.jpg",
    "Family Selection Costa Mujeres": "hoteles/costa_mujeres/family_selection_costa_mujeres.jpg",
    "TRS Coral Hotel": "hoteles/costa_mujeres/trs_coral.jpg",
    "Grand Palladium Colonial Resort & Spa": "hoteles/riviera_maya/gp_colonial.jpg",
    "Grand Palladium Kantenah Resort & Spa": "hoteles/riviera_maya/gp_kantenah.jpg",
    "TRS Yucatan Hotel": "hoteles/riviera_maya/trs_yucatan.jpg",
    "Grand Palladium Select White Sand": "hoteles/riviera_maya/gp_white_sand.jpg",
    "Grand Palladium Select Bavaro": "hoteles/punta_cana/gp_select_bavaro.jpg",
    "Grand Palladium Palace Resort & Spa": "hoteles/punta_cana/gp_palace.jpg",
    "Grand Palladium Punta Cana Resort & Spa": "hoteles/punta_cana/gp_punta_cana.jpg",
    "TRS Turquesa Hotel": "hoteles/punta_cana/trs_turquesa.jpg"
}

# Mapeo de prefijos de habitacion a carpetas de imagenes
CARPETAS_HABITACIONES = {
    "CMU": "habitaciones/MUJE_CMU",
    "CMU FS": "habitaciones/MUJE_CMU_FS",
    "TRSC": "habitaciones/MUJE_TRSC",
    "TRS": "habitaciones/MUJE_TRS",  # Default TRS para Costa Mujeres
    "COL": "habitaciones/MAYA_COL",
    "KAN": "habitaciones/MAYA_KAN",
    "WS": "habitaciones/MAYA_WS",
    "BAV": "habitaciones/CANA_BAV",
    "PAL": "habitaciones/CANA_PAL",
    "PC": "habitaciones/CANA_PC"
}

# Mapeo especifico para TRS segun complejo
CARPETAS_TRS = {
    "Complejo Costa Mujeres": "habitaciones/MUJE_TRS",
    "Complejo Riviera Maya": "habitaciones/MAYA_TRS",
    "Complejo Punta Cana": "habitaciones/CANA_TRS"
}
# Descripciones de tipos de habitacion con servicios y precios
DESCRIPCIONES_HABITACIONES = {
    # Costa Mujeres
    "CMU JUNIOR SUITE GV": {
        "nombre": "Junior Suite Garden View",
        "descripcion": "Espaciosa suite con vistas al jardín tropical",
        "servicios": ["45 m²", "Cama King o 2 dobles", "Balcón privado", "Minibar", "WiFi gratis", "Aire acondicionado"],
        "patron_busqueda": ["junior-suite-garden", "JUNIOR-SUITE", "garden-lagoon"],
        "precio_noche": 180
    },
    "CMU JUNIOR SUITE PS": {
        "nombre": "Junior Suite Poolside",
        "descripcion": "Suite con acceso directo a la piscina",
        "servicios": ["50 m²", "Cama King", "Terraza con acceso piscina", "Minibar premium", "WiFi gratis", "Servicio 24h"],
        "patron_busqueda": ["poolside", "pool-side"],
        "precio_noche": 220
    },
    "CMU JUNIOR SUITE PS OV": {
        "nombre": "Junior Suite Poolside Ocean View",
        "descripcion": "Suite junto a piscina con vistas al mar",
        "servicios": ["50 m²", "Cama King", "Vistas al océano", "Acceso piscina", "Minibar premium", "Servicio 24h"],
        "patron_busqueda": ["poolside-ocean", "ocean-view"],
        "precio_noche": 260
    },
    "CMU LOFT SUITE JT": {
        "nombre": "Loft Suite Jacuzzi Terrace",
        "descripcion": "Suite dúplex con jacuzzi privado en terraza",
        "servicios": ["70 m²", "Jacuzzi privado", "2 niveles", "Sala de estar", "Minibar premium", "Vistas panorámicas"],
        "patron_busqueda": ["LOFT-SUITE", "Loft-Suite-Jacuzzi"],
        "precio_noche": 350
    },
    "CMU FAMILY SUITE": {
        "nombre": "Family Suite",
        "descripcion": "Suite familiar con espacio extra para niños",
        "servicios": ["65 m²", "2 habitaciones", "Sala de estar", "Minibar", "WiFi gratis", "Kids amenities"],
        "patron_busqueda": ["family", "FAMILY"],
        "precio_noche": 280
    },
    # TRS (Solo adultos)
    "TRS JUNIOR SUITE GV": {
        "nombre": "TRS Junior Suite Garden View",
        "descripcion": "Suite premium solo adultos con jardín privado",
        "servicios": ["55 m²", "Cama King", "Solo adultos", "Servicio butler", "Minibar premium", "Acceso exclusivo"],
        "patron_busqueda": ["Junior-Suite-Private-Pool-Garden", "JS-6726"],
        "precio_noche": 320
    },
    "TRS JUNIOR SUITE PS": {
        "nombre": "TRS Junior Suite Poolside",
        "descripcion": "Suite premium junto a la piscina infinita",
        "servicios": ["55 m²", "Jacuzzi privado", "Solo adultos", "Butler 24h", "Terraza privada", "Acceso spa"],
        "patron_busqueda": ["Poolside", "Jacuzzi-Terrace"],
        "precio_noche": 380
    },
    # Riviera Maya
    "COL JUNIOR SUITE GV": {
        "nombre": "Colonial Junior Suite Garden View",
        "descripcion": "Suite de estilo colonial con vistas al jardín",
        "servicios": ["48 m²", "Estilo colonial", "Balcón", "Minibar", "WiFi gratis", "Aire acondicionado"],
        "patron_busqueda": ["junior-suite", "garden"],
        "precio_noche": 170
    },
    "KAN JUNIOR SUITE GV": {
        "nombre": "Kantenah Junior Suite Garden View",
        "descripcion": "Suite frente a los cenotes naturales",
        "servicios": ["48 m²", "Vista cenote", "Balcón privado", "Minibar", "WiFi gratis", "Acceso cenote"],
        "patron_busqueda": ["junior-suite", "garden"],
        "precio_noche": 175
    },
    # Punta Cana
    "PAL JUNIOR SUITE GV": {
        "nombre": "Palace Junior Suite Garden View",
        "descripcion": "Suite elegante con vistas a jardines tropicales",
        "servicios": ["52 m²", "Cama King", "Balcón", "Minibar", "WiFi gratis", "Room service 24h"],
        "patron_busqueda": ["junior-suite-garden"],
        "precio_noche": 190
    },
    "PAL JUNIOR SUITE BS": {
        "nombre": "Palace Junior Suite Beachside",
        "descripcion": "Suite junto a la playa con vistas al océano",
        "servicios": ["52 m²", "Vista al mar", "Acceso playa", "Minibar premium", "WiFi gratis", "Servicio playa"],
        "patron_busqueda": ["junior-suite-beachside", "beachside"],
        "precio_noche": 240
    },
    "PAL DELUXE GV": {
        "nombre": "Palace Deluxe Garden View",
        "descripcion": "Habitación deluxe con vistas al jardín",
        "servicios": ["40 m²", "Cama King", "Terraza", "Minibar", "WiFi gratis", "Aire acondicionado"],
        "patron_busqueda": ["deluxe-garden", "DELUXE"],
        "precio_noche": 150
    },
    "PAL DELUXE BS": {
        "nombre": "Palace Deluxe Beachside",
        "descripcion": "Habitación deluxe con acceso directo a playa",
        "servicios": ["40 m²", "Frente al mar", "Terraza", "Minibar", "WiFi gratis", "Sombrilla incluida"],
        "patron_busqueda": ["deluxe-beachside", "DELUXE"],
        "precio_noche": 200
    },
    "BAV JUNIOR SUITE GV": {
        "nombre": "Bavaro Junior Suite Garden View",
        "descripcion": "Suite premium en playa Bávaro",
        "servicios": ["50 m²", "Vistas jardín", "Balcón", "Minibar premium", "WiFi gratis", "Servicio Select"],
        "patron_busqueda": ["junior-suite-garden"],
        "precio_noche": 210
    },
    "TRS JUNIOR SUITE GV/PV": {
        "nombre": "TRS Junior Suite Garden/Pool View",
        "descripcion": "Suite solo adultos con vistas a jardín o piscina",
        "servicios": ["55 m²", "Solo adultos", "Butler 24h", "Piscina infinita", "Premium all-inclusive", "Spa access"],
        "patron_busqueda": ["Junior-Suite", "Pool"],
        "precio_noche": 340
    }
}


def obtener_complejo_de_hotel(nombre_hotel: str) -> str:
    """
    Dado un nombre de hotel individual, devuelve el Complejo al que pertenece.
    Esto es necesario porque el modelo usa NOMBRE_HOTEL = Complejo.
    """
    for complejo, hoteles in HOTELES_POR_COMPLEJO.items():
        if nombre_hotel in hoteles:
            return complejo
    return "Complejo Riviera Maya"  # Default


def generar_id_reserva(hotel: str) -> str:
    """
    Genera un ID de reserva con la misma estructura del dataset.
    Formato: XXXXXXXXXYYYYY donde YYYYY es el codigo de hotel.
    """
    codigo_hotel = CODIGO_HOTEL.get(hotel, "10601")
    # Generamos un numero secuencial basado en timestamp + random
    timestamp_part = int(datetime.datetime.now().timestamp()) % 100000000
    random_part = random.randint(0, 9)
    id_base = str(timestamp_part) + str(random_part)
    return id_base[:7] + codigo_hotel


# Ruta del archivo de historial de reservas (Dataset Maestro Unificado)
# Rutas de archivos
HISTORIAL_RESERVAS_PATH = os.path.join(os.path.dirname(__file__), "reservas_2026_full.csv")
RESERVAS_WEB_PATH = os.path.join(os.path.dirname(__file__), "reservas_web_2026.csv")


# Definición de columnas fijas para evitar corrupción de CSV
COLUMNAS_WEB_FIJAS = [
    'ID_RESERVA', 'LLEGADA', 'SALIDA', 'NOCHES', 'PAX', 'VALOR_RESERVA',
    'NOMBRE_HABITACION', 'CANAL', 'MERCADO', 'AGENCIA', 'NOMBRE_HOTEL_REAL',
    'COMPLEJO_REAL', 'PROBABILIDAD_CANCELACION', 'HOTEL_COMPLEJO',
    'CLIENTE_NOMBRE', 'CLIENTE_EMAIL', 'SEGMENTO', 'FIDELIDAD', 'FUENTE_NEGOCIO',
    'FECHA_CREACION', 'ESTADO'
]

def guardar_reserva_csv(reserva: dict) -> bool:
    """
    Guarda una reserva nueva en el archivo dedicado de reservas web (reservas_web_2026.csv).
    Preserva todos los datos del cliente y estructura enriquecida.
    """
    try:
        # Calcular fechas
        llegada_dt = pd.to_datetime(reserva.get('llegada'))
        # Asegurar noches int
        try:
            noches = int(reserva.get('noches', 0))
        except:
            noches = 1
        salida_dt = llegada_dt + datetime.timedelta(days=noches)
        
        # Mapear a columnas Estándar (Compatible con Maestro + Campos Nuevos)
        row_data = {
            'ID_RESERVA': str(reserva.get('id', '')), # ID como string para evitar líos
            'LLEGADA': llegada_dt.strftime('%Y-%m-%d'),
            'SALIDA': salida_dt.strftime('%Y-%m-%d'),
            'NOCHES': noches,
            'PAX': reserva.get('pax', 0),
            'VALOR_RESERVA': reserva.get('valor', 0),
            'NOMBRE_HABITACION': reserva.get('habitacion', ''),
            'CANAL': 'WEBPROPIA',
            'MERCADO': reserva.get('pais', 'Directo'),
            'AGENCIA': 'Cliente Directo',
            'NOMBRE_HOTEL_REAL': reserva.get('hotel', ''),
            'COMPLEJO_REAL': reserva.get('complejo', ''),
            'PROBABILIDAD_CANCELACION': reserva.get('cancel_prob', 0),
            'HOTEL_COMPLEJO': 'WEB_DIRECT', 
            # Campos NUEVOS ricos (Solo en archivo web)
            'CLIENTE_NOMBRE': reserva.get('nombre', ''),
            'CLIENTE_EMAIL': reserva.get('email', ''),
            'SEGMENTO': reserva.get('segmento', 'BAR'),
            'FIDELIDAD': reserva.get('fidelidad', 'None'),
            'FUENTE_NEGOCIO': reserva.get('fuente_negocio', 'DIRECT SALES'),
            'FECHA_CREACION': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ESTADO': 'Confirmada'
        }
        
        df_new = pd.DataFrame([row_data])
        
        # Asegurar columnas exactas
        for col in COLUMNAS_WEB_FIJAS:
            if col not in df_new.columns:
                 df_new[col] = ''
        df_new = df_new[COLUMNAS_WEB_FIJAS]
        
        # Guardar en archivo Web (Append o Create)
        if os.path.exists(RESERVAS_WEB_PATH):
            # Append sin header
            df_new.to_csv(RESERVAS_WEB_PATH, mode='a', header=False, index=False)
        else:
            # Create con header
            df_new.to_csv(RESERVAS_WEB_PATH, mode='w', header=True, index=False)
            
        return True
    except Exception as e:
        st.error(f"Error guardando reserva web: {e}")
        return False


def cargar_reservas_csv() -> pd.DataFrame:
    """
    Carga y fusiona reservas del Histórico (Solo lectura) y Web (Lectura/Escritura).
    Devuelve DataFrame unificado.
    """
    dfs = []
    
    # 1. Cargar Reservas Web (Prioridad Alta, Datos Ricos)
    if os.path.exists(RESERVAS_WEB_PATH):
        try:
            # Tolerancia a fallos: Saltamos líneas corruptas automáticamente
            df_web = pd.read_csv(RESERVAS_WEB_PATH, on_bad_lines='skip')
            # Limpieza básica web
            df_web.columns = df_web.columns.astype(str).str.strip()
            df_web['ID_RESERVA'] = df_web['ID_RESERVA'].astype(str).str.strip()
            # Convertir fechas web
            for col in ['LLEGADA', 'SALIDA']:
                if col in df_web.columns:
                    df_web[col] = pd.to_datetime(df_web[col], errors='coerce')
            dfs.append(df_web)
        except Exception as e:
            st.error(f"Error leyendo reservas web (Archivo corrupto, se ignorará): {e}")

    # 2. Cargar Histórico (Prioridad Baja, Datos Anónimos)
    if os.path.exists(HISTORIAL_RESERVAS_PATH):
        try:
            # Optimización: Leer tipos específicos si es posible, pero fallan los floats en ID.
            # Leemos todo y convertimos después.
            df_hist = pd.read_csv(HISTORIAL_RESERVAS_PATH)
            df_hist.columns = df_hist.columns.astype(str).str.strip()
            
            # Limpieza ID Histórico
            if 'ID_RESERVA' in df_hist.columns:
                df_hist.dropna(subset=['ID_RESERVA'], inplace=True)
                # Convertir float IDs (123.0) a string "123"
                df_hist['ID_RESERVA'] = df_hist['ID_RESERVA'].apply(
                    lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)
                ).str.strip()
            
            # Fechas Histórico
            for col in ['LLEGADA', 'SALIDA']:
                if col in df_hist.columns:
                    df_hist[col] = pd.to_datetime(df_hist[col], errors='coerce')
            
            dfs.append(df_hist)
        except Exception as e:
            st.error(f"Error cargando histórico: {e}")

    if not dfs:
        return pd.DataFrame()
        
    # Fusionar (Web va primero -> Prioridad en drop_duplicates si hiciera falta)
    # concat alinea columnas automáticamente. Las columnas de Web (Cliente) serán NaN en Histórico.
    df_full = pd.concat(dfs, ignore_index=True)
    
    return df_full


def buscar_reserva_por_id(id_reserva: str) -> dict:
    """
    Busca una reserva por su código.
    Devuelve un diccionario con formato estandarizado para la UI.
    """
    try:
        df = cargar_reservas_csv()
        if df.empty:
            return {}
            
        # Detectar columnas
        cols = df.columns.tolist()
        
        # Mapping de columnas (CSV Real -> UI Esperada)
        # CSV Real visto: ID_RESERVA, LLEGADA, SALIDA, NOCHES, PAX, NOMBRE_HABITACION, 
        # VALOR_RESERVA, HOTEL_COMPLEJO, NOMBRE_HOTEL_REAL, COMPLEJO_REAL, PROBABILIDAD_CANCELACION
        
        col_id = 'ID_RESERVA' if 'ID_RESERVA' in cols else 'id_reserva'
        
        # Buscar
        if col_id in cols:
            id_buscado = str(id_reserva).strip()
            if id_buscado.endswith(".0"): id_buscado = id_buscado[:-2]
            
            # Filtrado seguro
            df[col_id] = df[col_id].astype(str).str.strip()
            match = df[df[col_id] == id_buscado]
            
            if not match.empty:
                row = match.iloc[0]
                
                # Extracción directa usando nombres confirmados del CSV
                # Nota: Usamos .get() con valores default por seguridad
                
                # Cliente (No existe en CSV, simulamos)
                cliente_nombre = row.get('CLIENTE_NOMBRE', f"Huésped {id_buscado[-4:]}")
                if pd.isna(cliente_nombre) or str(cliente_nombre) == 'nan':
                    cliente_nombre = f"Huésped {id_buscado[-4:]}" # Ej: Huésped 0601
                
                # Probabilidad (Ajuste escala 0-1 -> 0-100)
                prob_raw = row.get('PROBABILIDAD_CANCELACION', 0.0)
                if pd.isna(prob_raw): prob_raw = 0.0
                if 0.0 < prob_raw <= 1.0:
                    prob_pct = prob_raw * 100.0  # Convertir 0.21 -> 21.0
                else:
                    prob_pct = prob_raw # Asumimos ya es % o es 0
                    
                # Valor
                valor = row.get('VALOR_RESERVA', 0.0)
                if pd.isna(valor): valor = 0.0
                
                return {
                    'id': str(row.get(col_id)),
                    'llegada': row.get('LLEGADA', row.get('llegada')),
                    'salida': row.get('SALIDA', row.get('salida')),
                    'noches': row.get('NOCHES', 1),
                    'pax': row.get('PAX', 2),
                    'valor': float(valor),
                    'habitacion': row.get('NOMBRE_HABITACION', 'Estándar'),
                    'hotel': row.get('NOMBRE_HOTEL_REAL', row.get('hotel', 'Hotel Desconocido')),
                    'complejo': row.get('COMPLEJO_REAL', 'Palladium Complex'),
                    'cancel_prob': float(prob_pct),
                    'nombre': cliente_nombre,
                    'email': row.get('CLIENTE_EMAIL', 'cliente@example.com'),
                    'estado': row.get('ESTADO', 'Confirmada'),
                    'raw_data': row.to_dict() # Debug info for UI
                }
    except Exception as e:
        st.error(f"Error buscando reserva: {e}")
        return {}
        
    return {}


def actualizar_reserva_csv(id_reserva: str, campo: str, valor) -> bool:
    """
    Actualiza un campo específico de una reserva.
    """
    if os.path.exists(HISTORIAL_RESERVAS_PATH):
        try:
            df = pd.read_csv(HISTORIAL_RESERVAS_PATH)
            
            # Detectar columna ID
            col_id = 'ID_RESERVA' if 'ID_RESERVA' in df.columns else 'id_reserva'
            
            if col_id in df.columns:
                mask = df[col_id].astype(str).str.strip() == str(id_reserva).strip()
                if mask.any():
                    # Mapear campos UI -> Maestro si es necesario
                    # (Por ahora asumimos que 'campo' viene correcto o lo dejamos dinámico)
                    # Si el campo es 'estado' y el CSV usa 'ESTADO', adaptar
                    if campo == 'estado' and 'ESTADO' in df.columns:
                        campo_real = 'ESTADO'
                    else:
                        campo_real = campo
                        
                    df.loc[mask, campo_real] = valor
                    df.to_csv(HISTORIAL_RESERVAS_PATH, index=False)
                    return True
        except Exception as e:
            st.error(f"Error actualizando reserva: {e}")
    return False


def obtener_imagen_hotel(nombre_hotel: str) -> str:
    """
    Devuelve la ruta completa de la imagen del hotel.
    """
    ruta_relativa = IMAGENES_HOTELES.get(nombre_hotel, "")
    if ruta_relativa:
        return os.path.join(os.path.dirname(__file__), "media", ruta_relativa)
    return ""


def obtener_imagenes_habitacion(codigo_habitacion: str, complejo: str, max_imagenes: int = 4) -> list:
    """
    Devuelve una lista de rutas de imágenes de la habitación.
    Usa patrones de búsqueda inteligentes basados en el tipo de habitación.
    """
    imagenes = []
    
    # Determinar prefijo
    prefijo = codigo_habitacion.split()[0] if codigo_habitacion else ""
    
    # Caso especial para TRS (depende del complejo)
    if prefijo == "TRS":
        carpeta = CARPETAS_TRS.get(complejo, "habitaciones/MAYA_TRS")
    else:
        carpeta = CARPETAS_HABITACIONES.get(prefijo, "")
    
    if carpeta:
        carpeta_completa = os.path.join(os.path.dirname(__file__), "media", carpeta)
        if os.path.exists(carpeta_completa):
            # Obtener patrones de búsqueda
            info_hab = DESCRIPCIONES_HABITACIONES.get(codigo_habitacion, {})
            patrones = info_hab.get("patron_busqueda", [])
            
            # Buscar imágenes que coincidan con patrones (excluyendo planos)
            archivos_encontrados = []
            for archivo in os.listdir(carpeta_completa):
                if archivo.endswith(('.jpg', '.webp', '.png')):
                    # Excluir planos (formato GP-HOTEL_TIPO con guiones bajos)
                    if archivo.startswith('GP-') and '_' in archivo and archivo.split('_')[0].isupper():
                        continue  # Es un plano, lo saltamos aquí
                    
                    # Priorizar por patrón
                    prioridad = 100
                    for i, patron in enumerate(patrones):
                        if patron.lower() in archivo.lower():
                            prioridad = i
                            break
                    archivos_encontrados.append((prioridad, archivo))
            
            # Ordenar por prioridad y tomar las primeras max_imagenes
            archivos_encontrados.sort(key=lambda x: x[0])
            for _, archivo in archivos_encontrados[:max_imagenes]:
                imagenes.append(os.path.join(carpeta_completa, archivo))
    
    return imagenes


def obtener_plano_habitacion(codigo_habitacion: str, complejo: str) -> str:
    """
    Devuelve la ruta del plano de planta de la habitación si existe.
    Los planos tienen formato: GP-HOTEL_TIPO.webp
    """
    # Determinar prefijo
    prefijo = codigo_habitacion.split()[0] if codigo_habitacion else ""
    
    # Caso especial para TRS (depende del complejo)
    if prefijo == "TRS":
        carpeta = CARPETAS_TRS.get(complejo, "habitaciones/MAYA_TRS")
    else:
        carpeta = CARPETAS_HABITACIONES.get(prefijo, "")
    
    if carpeta:
        carpeta_completa = os.path.join(os.path.dirname(__file__), "media", carpeta)
        if os.path.exists(carpeta_completa):
            # Obtener patrones de búsqueda para el plano
            info_hab = DESCRIPCIONES_HABITACIONES.get(codigo_habitacion, {})
            patrones = info_hab.get("patron_busqueda", [])
            
            # Buscar archivos que parezcan planos
            for archivo in os.listdir(carpeta_completa):
                if archivo.endswith(('.jpg', '.webp', '.png')):
                    # Identificar planos: formato GP-HOTEL_TIPO (mayúsculas con guiones bajos)
                    if archivo.startswith('GP-') and '_' in archivo:
                        # Verificar que coincide con algún patrón de la habitación
                        for patron in patrones:
                            if patron.upper().replace('-', '_').replace(' ', '_') in archivo.upper():
                                return os.path.join(carpeta_completa, archivo)
                        # Si no hay patrón específico, buscar por nombre de habitación
                        nombre_hab_upper = codigo_habitacion.upper().replace(' ', '-')
                        if nombre_hab_upper in archivo.upper() or any(p in archivo.upper() for p in nombre_hab_upper.split('-') if len(p) > 3):
                            return os.path.join(carpeta_completa, archivo)
    
    return ""


def obtener_imagen_habitacion(codigo_habitacion: str, complejo: str) -> str:
    """
    Devuelve la ruta de una imagen representativa de la habitación (backwards compatibility).
    """
    imagenes = obtener_imagenes_habitacion(codigo_habitacion, complejo, max_imagenes=1)
    return imagenes[0] if imagenes else ""


def obtener_info_habitacion(codigo_habitacion: str) -> dict:
    """
    Devuelve la información descriptiva de una habitación.
    """
    info = DESCRIPCIONES_HABITACIONES.get(codigo_habitacion, {})
    if not info:
        # Generar información por defecto
        return {
            "nombre": codigo_habitacion,
            "descripcion": "Habitación confortable con todas las comodidades",
            "servicios": ["Aire acondicionado", "WiFi gratis", "Minibar", "Caja fuerte", "TV pantalla plana"],
            "precio_noche": 160
        }
    return info


def render_wizard_steps(current_step: int):
    """
    Renderiza los pasos del wizard usando componentes nativos de Streamlit.
    """
    steps = ["Destino", "Datos", "Hotel", "Confirmacion"]
    
    # Usamos columnas de Streamlit para mostrar los pasos
    cols = st.columns(len(steps))
    
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current_step:
                # Completado
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: {COLOR_VERDE_OSCURO}; color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 0.85rem; margin-bottom: 0.3rem;">✓</div>
                    <div style="color: {COLOR_VERDE_OSCURO}; font-size: 0.85rem;">{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
            elif i == current_step:
                # Activo
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: {COLOR_DORADO_OSCURO}; color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 0.85rem; margin-bottom: 0.3rem;">{i}</div>
                    <div style="color: {COLOR_DORADO_OSCURO}; font-weight: 500; font-size: 0.85rem;">{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Pendiente
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <div style="width: 30px; height: 30px; border-radius: 50%; background: {COLOR_BEIGE}; color: {COLOR_GRIS}; display: inline-flex; align-items: center; justify-content: center; font-size: 0.85rem; margin-bottom: 0.3rem;">{i}</div>
                    <div style="color: {COLOR_GRIS}; font-size: 0.85rem;">{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")


# =============================================================================
# VISTA CLIENTE - WIZARD
# =============================================================================
def render_vista_cliente():
    """
    Renderiza el wizard de reserva en 4 pasos.
    """
    
    # Inicializamos estados
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 1
    if 'reservations' not in st.session_state:
        st.session_state.reservations = []
    
    # Renderizamos steps
    render_wizard_steps(st.session_state.wizard_step)
    
    # -------------------------------------------------------------------------
    # PASO 1: DESTINO
    # -------------------------------------------------------------------------
    if st.session_state.wizard_step == 1:
        st.markdown("<h2 style='text-align:center;'>Seleccione su destino</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#757171;'>Descubra nuestros resorts de lujo en el Caribe</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("MEXICO\n\nCancun - Riviera Maya", key="dest_mexico", use_container_width=True):
                st.session_state.destino_seleccionado = "MEXICO"
                st.session_state.wizard_step = 2
                st.rerun()
        
        with col2:
            if st.button("REPUBLICA DOMINICANA\n\nPunta Cana", key="dest_rd", use_container_width=True):
                st.session_state.destino_seleccionado = "REPUBLICA DOMINICANA"
                st.session_state.wizard_step = 2
                st.rerun()
    
    # -------------------------------------------------------------------------
    # PASO 2: DATOS DEL CLIENTE
    # -------------------------------------------------------------------------
    elif st.session_state.wizard_step == 2:
        # Sección de fechas y huéspedes PRIMERO
        st.subheader("Fechas y huéspedes")
        
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        
        with col_f1:
            fecha_llegada = st.date_input(
                "Llegada",
                value=datetime.date.today() + datetime.timedelta(days=30),
                min_value=datetime.date.today(),
                key="w_llegada"
            )
        
        with col_f2:
            noches = st.number_input("Noches", min_value=1, max_value=30, value=7, key="w_noches")
        
        with col_f3:
            adultos = st.number_input("Adultos", min_value=1, max_value=6, value=2, key="w_adultos")
        
        with col_f4:
            ninos = st.number_input("Niños", min_value=0, max_value=4, value=0, key="w_ninos")
        
        with col_f5:
            cunas = st.number_input("Cunas", min_value=0, max_value=2, value=0, key="w_cunas")
        
        st.markdown("---")
        
        # Datos del huésped DESPUÉS
        st.subheader("Datos del Huésped")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo *", key="w_nombre")
            email = st.text_input("Email *", key="w_email")
            telefono = st.text_input("Teléfono", key="w_telefono")
        
        with col2:
            pais = st.selectbox("País de residencia", PAISES, key="w_pais")
            
            # Widget Palladium Rewards
            st.markdown(f"""
            <div style="background: {COLOR_VERDE_OSCURO}; border-radius: 8px; padding: 1.2rem; margin-top: 0.5rem; text-align: center;">
                <p style="color: white; font-size: 1.3rem; font-weight: 300; letter-spacing: 3px; margin: 0;">PALLADIUM</p>
                <p style="color: white; font-size: 0.7rem; letter-spacing: 5px; margin: 0.2rem 0 0 0;">R · E · W · A · R · D · S</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Inicializar estado de verificación
            if 'rewards_verificado' not in st.session_state:
                st.session_state.rewards_verificado = False
            
            # Formulario de verificación
            if not st.session_state.rewards_verificado:
                rewards_email = st.text_input("Email de miembro Rewards", placeholder="tu@email.com", key="rewards_email_input")
                if st.button("VERIFICAR MIEMBRO", key="btn_verify_rewards"):
                    if rewards_email and "@" in rewards_email:
                        st.session_state.rewards_verificado = True
                        st.session_state.rewards_email_guardado = rewards_email
                        st.rerun()
                    else:
                        st.warning("Introduce un email válido")
            else:
                email_guardado = st.session_state.get('rewards_email_guardado', '')
                st.markdown(f"""
                <div style="background: {COLOR_CREMA}; border-radius: 4px; padding: 0.8rem; margin-top: 0.5rem; text-align: center; border: 1px solid {COLOR_VERDE_OSCURO};">
                    <span style="color: {COLOR_VERDE_OSCURO};">✓ Miembro verificado</span><br>
                    <span style="color: {COLOR_GRIS}; font-size: 0.8rem;">{email_guardado}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Cambiar cuenta", key="btn_change_rewards"):
                    st.session_state.rewards_verificado = False
                    st.rerun()
        
        st.markdown("---")
        
        col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])
        with col_nav1:
            if st.button("Atrás", key="back_2"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col_nav3:
            if st.button("Continuar", key="next_2", type="primary"):
                if not nombre or not email:
                    st.error("Nombre y email son obligatorios")
                else:
                    st.session_state.cliente_nombre = nombre
                    st.session_state.cliente_email = email
                    st.session_state.cliente_telefono = telefono
                    st.session_state.cliente_pais = pais
                    # Guardar datos de fechas y huéspedes
                    st.session_state.reserva_llegada = fecha_llegada
                    st.session_state.reserva_noches = noches
                    st.session_state.reserva_adultos = adultos
                    st.session_state.reserva_ninos = ninos
                    st.session_state.reserva_cunas = cunas
                    st.session_state.reserva_pax = adultos + ninos
                    # Fidelidad basada en verificación Rewards
                    if st.session_state.rewards_verificado:
                        st.session_state.cliente_fidelidad = "Palladium Rewards"
                    else:
                        st.session_state.cliente_fidelidad = "Sin programa"
                    st.session_state.wizard_step = 3
                    st.rerun()
    
    # -------------------------------------------------------------------------
    # PASO 3: HOTEL Y HABITACION
    # -------------------------------------------------------------------------
    elif st.session_state.wizard_step == 3:
        destino = st.session_state.get('destino_seleccionado', 'MEXICO')
        complejos_disponibles = DESTINOS[destino]['complejos']
        destino_nombre = DESTINOS[destino]['nombre']
        
        # Titulo
        st.markdown(f"""
        <h2 style="text-align: center; font-weight: 300; margin-bottom: 0.5rem;">Hoteles en {destino_nombre}</h2>
        <p style="text-align: center; color: {COLOR_GRIS}; margin-bottom: 2rem;">Seleccione el complejo y hotel que mejor se adapte a sus necesidades</p>
        """, unsafe_allow_html=True)
        
        # Seleccion de complejo (tabs o selector)
        complejo = st.selectbox(
            "Zona",
            complejos_disponibles,
            key="w_complejo",
            format_func=lambda x: x.replace("Complejo ", "")
        )
        
        st.markdown(f"""
        <p style="color: {COLOR_RIESGO_MEDIO}; font-size: 0.85rem;">📍 {destino_nombre.split('-')[0].strip()}</p>
        """, unsafe_allow_html=True)
        
        # Obtenemos hoteles del complejo
        hoteles_del_complejo = HOTELES_POR_COMPLEJO.get(complejo, {})
        
        # Inicializar seleccion de hotel
        if 'hotel_seleccionado_paso3' not in st.session_state:
            st.session_state.hotel_seleccionado_paso3 = None
        
        # Mostrar tarjetas de hoteles
        for nombre_hotel, info_hotel in hoteles_del_complejo.items():
            imagen_hotel = obtener_imagen_hotel(nombre_hotel)
            descripcion = info_hotel.get('descripcion', '')
            num_habitaciones = len(info_hotel.get('habitaciones', []))
            
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                if imagen_hotel and os.path.exists(imagen_hotel):
                    st.image(imagen_hotel, use_container_width=True)
                else:
                    st.markdown(f"""
                    <div style="background: {COLOR_BEIGE}; height: 150px; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                        <span style="color: {COLOR_GRIS};">🏨</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_info:
                st.markdown(f"""
                <h4 style="margin: 0 0 0.5rem 0; color: {COLOR_NEGRO};">{nombre_hotel}</h4>
                <p style="color: {COLOR_GRIS}; font-size: 0.9rem; margin-bottom: 0.5rem;">{descripcion}</p>
                <p style="color: {COLOR_GRIS}; font-size: 0.85rem;">Habitaciones disponibles: {num_habitaciones}</p>
                """, unsafe_allow_html=True)
                
                if st.button("SELECCIONAR HOTEL", key=f"btn_hotel_{nombre_hotel}", type="secondary"):
                    st.session_state.hotel_seleccionado_paso3 = nombre_hotel
                    st.rerun()
            
            st.markdown("---")
        
        # Si hay hotel seleccionado, mostrar habitaciones y fechas
        if st.session_state.hotel_seleccionado_paso3:
            hotel_seleccionado = st.session_state.hotel_seleccionado_paso3
            info_hotel = hoteles_del_complejo.get(hotel_seleccionado, {})
            habitaciones_hotel = info_hotel.get('habitaciones', [])
            
            # Header del hotel seleccionado con scroll automático
            st.markdown(f"""
            <div id="habitaciones-section" style="background: {COLOR_VERDE_OSCURO}; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h3 style="margin: 0; font-weight: 300;">✓ {hotel_seleccionado}</h3>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">{info_hotel.get('descripcion', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Script de scroll automático (usando iframe trick para Streamlit)
            import streamlit.components.v1 as components
            components.html("""
                <script>
                    setTimeout(function() {
                        var target = window.parent.document.getElementById('habitaciones-section');
                        if (target) {
                            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 100);
                </script>
            """, height=0)
            
            # Recuperar fechas del paso 2
            fecha_llegada = st.session_state.get('reserva_llegada', datetime.date.today() + datetime.timedelta(days=30))
            noches = st.session_state.get('reserva_noches', 7)
            adultos = st.session_state.get('reserva_adultos', 2)
            ninos = st.session_state.get('reserva_ninos', 0)
            cunas = st.session_state.get('reserva_cunas', 0)
            pax = st.session_state.get('reserva_pax', adultos + ninos)
            fecha_salida = fecha_llegada + datetime.timedelta(days=noches)
            
            # Resumen de fechas
            st.markdown(f"""
            <div style="background: {COLOR_BEIGE}; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <span style="color: {COLOR_GRIS};">📅 {fecha_llegada.strftime('%d %b')} - {fecha_salida.strftime('%d %b %Y')} · {noches} noches · {adultos} adultos{f' · {ninos} niños' if ninos > 0 else ''}{f' · {cunas} cunas' if cunas > 0 else ''}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Ordenar habitaciones por precio
            habitaciones_ordenadas = sorted(
                habitaciones_hotel,
                key=lambda h: obtener_info_habitacion(h).get('precio_noche', 160)
            )
            
            # Sección de habitaciones con radio buttons
            st.markdown(f"### 🛏️ Seleccione su habitación")
            
            # Crear opciones para el radio con precio
            opciones_habitaciones = []
            for codigo_hab in habitaciones_ordenadas:
                info_hab = obtener_info_habitacion(codigo_hab)
                precio = info_hab.get('precio_noche', 160)
                nombre = info_hab.get('nombre', codigo_hab)
                opciones_habitaciones.append(f"{nombre} (desde {precio}€/noche)")
            
            # Radio buttons para selección de habitación
            habitacion_seleccionada_idx = st.radio(
                "Tipo de habitación",
                range(len(habitaciones_ordenadas)),
                format_func=lambda i: opciones_habitaciones[i],
                key="radio_habitacion",
                label_visibility="collapsed"
            )
            
            # Obtener código de habitación seleccionada
            habitacion = habitaciones_ordenadas[habitacion_seleccionada_idx]
            info_hab = obtener_info_habitacion(habitacion)
            
            # Mostrar descripción de la habitación seleccionada
            st.markdown(f"""
            <p style="color: {COLOR_GRIS}; font-size: 0.9rem; font-style: italic; margin: 0.5rem 0 1rem 0;">
                {info_hab.get('descripcion', '')}
            </p>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Mostrar detalles solo de la habitación seleccionada
            imagenes_hab = obtener_imagenes_habitacion(habitacion, complejo, max_imagenes=4)
            plano_hab = obtener_plano_habitacion(habitacion, complejo)
            precio_noche = info_hab.get('precio_noche', 160)
            precio_total = precio_noche * noches * pax
            servicios = info_hab.get('servicios', [])
            
            # Galería de fotos - ANCHO COMPLETO (4 columnas)
            st.markdown(f"**📷 Galería de fotos**")
            if imagenes_hab:
                cols_img = st.columns(4)
                for idx, img in enumerate(imagenes_hab[:4]):
                    if os.path.exists(img):
                        with cols_img[idx]:
                            st.image(img, use_container_width=True)
            
            # Características y plano en fila
            col_caract, col_plano, col_precio = st.columns([1, 1, 1])
            
            with col_caract:
                st.markdown(f"**✨ Características**")
                for servicio in servicios:
                    st.markdown(f"<span style='color: {COLOR_GRIS}; font-size: 0.85rem;'>• {servicio}</span>", unsafe_allow_html=True)
            
            with col_plano:
                if plano_hab and os.path.exists(plano_hab):
                    with st.expander("📐 Ver plano de planta", expanded=False):
                        st.image(plano_hab, use_container_width=True)
            
            with col_precio:
                st.markdown(f"""
                <div style="background: {COLOR_CREMA}; padding: 1rem; border-radius: 8px; text-align: center;">
                    <p style="color: {COLOR_GRIS}; font-size: 0.8rem; margin: 0;">Precio total</p>
                    <p style="color: {COLOR_DORADO_OSCURO}; font-size: 1.8rem; font-weight: 500; margin: 0;">{precio_total:,.0f}€</p>
                    <p style="color: {COLOR_GRIS}; font-size: 0.75rem; margin: 0;">{noches} noches · {pax} huéspedes</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Resumen dinámico con TODA la información acumulada
            destino_nombre = DESTINOS.get(st.session_state.get('destino_seleccionado', 'MEXICO'), {}).get('nombre', 'México')
            cliente_nombre = st.session_state.get('cliente_nombre', '')
            cliente_email = st.session_state.get('cliente_email', '')
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLOR_VERDE_OSCURO} 0%, #4a6741 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <p style="margin: 0; font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px;">Resumen de su reserva</p>
                        <p style="margin: 0.3rem 0; font-size: 1.1rem;"><strong>{hotel_seleccionado}</strong></p>
                        <p style="margin: 0; font-size: 0.95rem; opacity: 0.95;">{info_hab.get('nombre', habitacion)}</p>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.85;">
                            📍 {destino_nombre} · {complejo}<br>
                            📅 {fecha_llegada.strftime('%d %b %Y')} → {fecha_salida.strftime('%d %b %Y')} ({noches} noches)<br>
                            👥 {adultos} adultos{f', {ninos} niños' if ninos > 0 else ''}{f', {cunas} cunas' if cunas > 0 else ''}
                        </p>
                        {f'<p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;">👤 {cliente_nombre} · {cliente_email}</p>' if cliente_nombre else ''}
                    </div>
                    <div style="text-align: right; min-width: 120px;">
                        <p style="margin: 0; font-size: 0.75rem; opacity: 0.7;">Precio total</p>
                        <p style="margin: 0; font-size: 2.2rem; font-weight: 300;">{precio_total:,.0f}€</p>
                        <p style="margin: 0; font-size: 0.75rem; opacity: 0.7;">{precio_noche}€/noche</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])
            with col_nav1:
                if st.button("Atrás", key="back_3"):
                    st.session_state.hotel_seleccionado_paso3 = None
                    st.session_state.wizard_step = 2
                    st.rerun()
            with col_nav3:
                if st.button("RESERVAR AHORA", key="next_3", type="primary"):
                    st.session_state.reserva_complejo = complejo
                    st.session_state.reserva_hotel = hotel_seleccionado
                    st.session_state.reserva_habitacion = habitacion
                    st.session_state.reserva_valor = precio_total
                    st.session_state.wizard_step = 4
                    st.rerun()
        else:
            # Navegación (solo atrás si no hay hotel seleccionado)
            if st.button("Atrás", key="back_3_no_hotel"):
                st.session_state.wizard_step = 2
                st.rerun()
    
    # -------------------------------------------------------------------------
    # PASO 4: CONFIRMACION
    # -------------------------------------------------------------------------
    elif st.session_state.wizard_step == 4:
        
        # Recuperamos datos
        hotel = st.session_state.get('reserva_hotel', '')  # Hotel individual (para mostrar)
        complejo = st.session_state.get('reserva_complejo', '')  # Complejo (para el modelo)
        habitacion = st.session_state.get('reserva_habitacion', '')
        llegada = st.session_state.get('reserva_llegada', datetime.date.today())
        noches = st.session_state.get('reserva_noches', 7)
        pax = st.session_state.get('reserva_pax', 2)
        adultos = st.session_state.get('reserva_adultos', 2)
        valor = st.session_state.get('reserva_valor', 0)
        nombre = st.session_state.get('cliente_nombre', '')
        email = st.session_state.get('cliente_email', '')
        pais = st.session_state.get('cliente_pais', 'ESPAÑA')
        fidelidad = st.session_state.get('cliente_fidelidad', 'Sin programa')
        
        # Generamos ID de reserva (basado en el complejo)
        id_reserva = generar_id_reserva(complejo)
        
        # Calculamos prediccion (usando el Complejo para el modelo)
        model = load_model()
        fecha_toma = datetime.datetime.now()
        llegada_dt = pd.to_datetime(llegada)
        fidelidad_val = None if fidelidad == "Sin programa" else fidelidad
        
        try:
            processed_df = get_features(
                LLEGADA=llegada_dt, NOCHES=noches, PAX=pax, ADULTOS=adultos,
                CLIENTE="ROIBACK (GLOBAL OBI S.L.)", FECHA_TOMA=fecha_toma,
                FIDELIDAD=fidelidad_val, PAIS=pais,
                SEGMENTO="Loyalty" if fidelidad_val else "BAR",
                FUENTE_NEGOCIO="DIRECT SALES",
                NOMBRE_HOTEL=complejo,  # El modelo espera el Complejo, no el hotel individual
                NOMBRE_HABITACION=habitacion,
                VALOR_RESERVA=valor
            )
            
            features = processed_df
            if hasattr(model, 'feature_name_'):
                features = processed_df[model.feature_name_]
            
            if model is not None:
                cancel_prob = model.predict_proba(features)[0][1]
            else:
                st.error("No se pudo cargar el modelo predictivo (model is None).")
                cancel_prob = 0.0
                
        except Exception as e:
            st.error(f"Error en la predicción: {str(e)}")
            # st.write(f"Debug Features Error: {processed_df}") if 'processed_df' in locals() else None
            cancel_prob = 0.0
        
        # Guardamos reserva con todos los datos
        destino = st.session_state.get('destino_seleccionado', 'MEXICO')
        ninos = st.session_state.get('reserva_ninos', 0)
        cunas = st.session_state.get('reserva_cunas', 0)
        telefono = st.session_state.get('cliente_telefono', '')
        
        reserva = {
            'id': id_reserva,
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'pais': pais,
            'destino': destino,
            'hotel': hotel,
            'complejo': complejo,
            'habitacion': habitacion,
            'llegada': llegada,
            'noches': noches,
            'adultos': adultos,
            'ninos': ninos,
            'cunas': cunas,
            'pax': pax,
            'valor': valor,
            'cancel_prob': cancel_prob,
            'segmento': "Loyalty" if fidelidad_val else "BAR",
            'fidelidad': str(fidelidad_val),
            'fuente_negocio': "DIRECT SALES",
            'fecha_reserva': datetime.datetime.now(),
            'fidelidad': fidelidad,
            'estado': 'Confirmada'
        }
        
        # Guardar en memoria de sesión
        st.session_state.reservations.append(reserva)
        
        # Guardar en archivo CSV persistente
        guardar_reserva_csv(reserva)
        
        # Mostramos confirmacion
        st.markdown(f"""
        <div class="success-box">
            <h2>Reserva Confirmada</h2>
            <p>Gracias, <strong>{nombre}</strong></p>
            <div class="reservation-code">{id_reserva}</div>
            <p>Guarda este codigo para consultar tu reserva</p>
            <br>
            <p><strong>{hotel}</strong></p>
            <p>{habitacion}</p>
            <p>{llegada.strftime('%d/%m/%Y')} - {noches} noches - {pax} huespedes</p>
            <p style="font-size: 1.3rem; margin-top: 1rem;"><strong>{valor:,.2f} EUR</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()
        
        st.markdown("")
        if st.button("Nueva Reserva", key="new_reservation"):
            st.session_state.wizard_step = 1
            st.rerun()


# =============================================================================
# VISTA INTRANET
# =============================================================================
def render_vista_intranet():
    """
    Renderiza el panel de intranet con busqueda y prediccion.
    """
    
    st.markdown("""
    <div style="background: #292929; color: white; padding: 1rem; margin-bottom: 1.5rem;">
        <h3 style="margin: 0; font-weight: 300; letter-spacing: 2px;">INTRANET - GESTION DE RESERVAS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # BUSQUEDA POR CODIGO
    # -------------------------------------------------------------------------
    st.subheader("Buscar Reserva")
    
    col_search, col_btn = st.columns([3, 1])
    
    with col_search:
        codigo_busqueda = st.text_input("Codigo de reserva", placeholder="Ej: 123456710601", key="search_code")
    
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        buscar = st.button("Buscar", key="btn_search", type="primary")
    
    if buscar and codigo_busqueda:
        reservations = st.session_state.get('reservations', [])
        encontrada = None
        
        for r in reservations:
            if str(r['id']) == codigo_busqueda:
                encontrada = r
                break
        
        if encontrada:
            st.success(f"Reserva encontrada: {encontrada['id']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="form-section">
                    <strong>Cliente:</strong> {encontrada['nombre']}<br>
                    <strong>Email:</strong> {encontrada['email']}<br>
                    <strong>Pais:</strong> {encontrada['pais']}<br>
                    <strong>Fidelidad:</strong> {encontrada.get('fidelidad', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="form-section">
                    <strong>Hotel:</strong> {encontrada['hotel']}<br>
                    <strong>Habitacion:</strong> {encontrada['habitacion']}<br>
                    <strong>Llegada:</strong> {encontrada['llegada']}<br>
                    <strong>Noches:</strong> {encontrada['noches']} | <strong>PAX:</strong> {encontrada['pax']}<br>
                    <strong>Valor:</strong> {encontrada['valor']:,.2f} EUR
                </div>
                """, unsafe_allow_html=True)
            
            # Mostramos riesgo
            prob = encontrada['cancel_prob']
            if prob >= 0.6:
                risk_class = "risk-high"
                risk_label = "RIESGO ALTO"
            elif prob >= 0.35:
                risk_class = "risk-medium"
                risk_label = "RIESGO MEDIO"
            else:
                risk_class = "risk-low"
                risk_label = "RIESGO BAJO"
            
            st.markdown(f"""
            <div class="result-card {risk_class}" style="margin-top: 1rem;">
                <p class="result-label">Probabilidad de Cancelacion</p>
                <p class="result-value">{prob:.2%}</p>
                <p class="result-label">{risk_label}</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning(f"No se encontro reserva con codigo {codigo_busqueda}")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # LISTADO DE RESERVAS
    # -------------------------------------------------------------------------
    st.subheader("Reservas Recientes")
    
    reservations = st.session_state.get('reservations', [])
    
    if reservations:
        for r in reversed(reservations[-10:]):  # Ultimas 10
            prob = r['cancel_prob']
            if prob >= 0.6:
                color = COLOR_RIESGO_ALTO
            elif prob >= 0.35:
                color = COLOR_RIESGO_MEDIO
            else:
                color = COLOR_RIESGO_BAJO
            
            st.markdown(f"""
            <div class="content-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{r['id']}</strong> - {r['nombre']}<br>
                    <span style="color: #757171;">{r['hotel']} | {r['llegada']} | {r['valor']:,.2f} EUR</span>
                </div>
                <div style="text-align: right;">
                    <span style="color: {color}; font-weight: 500;">{prob:.1%}</span><br>
                    <span style="color: #757171; font-size: 0.85rem;">{r.get('estado', 'Confirmada')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay reservas registradas")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # PREDICCION MANUAL
    # -------------------------------------------------------------------------
    with st.expander("Prediccion Manual (Avanzado)"):
        model = load_model()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            llegada_date = st.date_input("Llegada", value=datetime.date(2026, 6, 1), key="m_llegada")
            noches = st.number_input("Noches", min_value=1, value=7, key="m_noches")
            pax = st.number_input("PAX", min_value=1, value=2, key="m_pax")
            adultos = st.number_input("Adultos", min_value=1, value=2, key="m_adultos")
            valor = st.number_input("Valor USD", min_value=0.0, value=2500.0, key="m_valor")
        
        with col2:
            cliente = st.selectbox("Cliente", CLIENTES, key="m_cliente")
            fidelidad = st.selectbox("Fidelidad", PROGRAMAS_FIDELIDAD, key="m_fidelidad")
            pais = st.selectbox("Pais", PAISES, key="m_pais")
            segmento = st.selectbox("Segmento", SEGMENTOS, key="m_segmento")
            fuente = st.selectbox("Fuente", FUENTES_NEGOCIO, key="m_fuente")
        
        with col3:
            complejo = st.selectbox("Complejo", list(HOTELES_POR_COMPLEJO.keys()), key="m_complejo")
            # Obtener todas las habitaciones del complejo
            habitaciones_complejo = []
            for hotel_info in HOTELES_POR_COMPLEJO.get(complejo, {}).values():
                habitaciones_complejo.extend(hotel_info.get('habitaciones', []))
            habitacion = st.selectbox("Habitacion", habitaciones_complejo, key="m_habitacion")
        
        if st.button("Calcular Riesgo", type="primary", key="btn_calc"):
            with st.spinner("Calculando..."):
                fecha_toma = datetime.datetime.now()
                fidelidad_val = None if fidelidad == "Sin programa" else fidelidad
                
                try:
                    processed_df = get_features(
                        LLEGADA=pd.to_datetime(llegada_date), NOCHES=noches, PAX=pax, ADULTOS=adultos,
                        CLIENTE=cliente, FECHA_TOMA=fecha_toma, FIDELIDAD=fidelidad_val,
                        PAIS=pais, SEGMENTO=segmento, FUENTE_NEGOCIO=fuente,
                        NOMBRE_HOTEL=complejo, NOMBRE_HABITACION=habitacion,
                        VALOR_RESERVA=valor
                    )
                    
                    features = processed_df
                    if hasattr(model, 'feature_name_'):
                        features = processed_df[model.feature_name_]
                    
                    prob = model.predict_proba(features)[0][1]
                    
                    if prob >= 0.6:
                        st.error(f"Probabilidad: {prob:.2%} - RIESGO ALTO")
                    elif prob >= 0.35:
                        st.warning(f"Probabilidad: {prob:.2%} - RIESGO MEDIO")
                    else:
                        st.success(f"Probabilidad: {prob:.2%} - RIESGO BAJO")
                        
                except Exception as e:
                    st.error(f"Error: {e}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    """
    Funcion principal.
    """
    
    # Sidebar reservado
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem; text-align: center; color: #757171; font-style: italic;">
            <br><br>
            <p>Espacio reservado para</p>
            <p><strong>Asistente IA</strong></p>
            <p>(Proximamente)</p>
            <br><br>
        </div>
        """, unsafe_allow_html=True)
    
    # Cabecera con logo
    logo_path = os.path.join(os.path.dirname(__file__), "media", "general", "Logo.jpg")
    
    # Estrategia de centrado robusta
    col_space1, col_logo, col_space2 = st.columns([3, 4, 3])
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center;'>PALLADIUM HOTELS</h1>", unsafe_allow_html=True)
    
    # Navegacion
    # Navegacion
    col_spacer, col_buttons = st.columns([5, 1.5])
    
    with col_buttons:
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            # Estamos en Cliente (app.py)
            st.button("Cliente", key="nav_cliente", type="primary", disabled=True)
        
        with col_btn2:
            if st.button("Intranet", key="nav_intranet", type="secondary"):
                st.switch_page("pages/1_Intranet.py")
    
    st.markdown("---")
    
    # Contenido - Siempre renderiza Cliente aqui, la Intranet esta en otra pagina
    render_vista_cliente()
    
    # Pie
    st.markdown("---")
    pie_path = os.path.join(os.path.dirname(__file__), "media", "general", "Pie.png")
    if os.path.exists(pie_path):
        st.image(pie_path, use_container_width=True)


if __name__ == "__main__":
    main()
