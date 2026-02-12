"""
Intranet Palladium - Panel de Prediccion de Cancelaciones
Herramienta interna para analizar reservas y predecir probabilidad de cancelacion.

Esta pagina permite a los trabajadores:
- Introducir los datos de una reserva manualmente
- Obtener la probabilidad de cancelacion del modelo LightGBM
- Ver las features procesadas
- Gestionar reservas existentes

Autor: Grupo 4 - TFM Palladium
Fecha: Febrero 2026
"""

import streamlit as st
import pandas as pd
import datetime
import sys
import os
import numpy as np

# -----------------------------------------------------------------------------
# CONFIGURACION DE RUTAS
# -----------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_model, get_features

# -----------------------------------------------------------------------------
# CONFIGURACION DE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Intranet | Palladium",
    page_icon="P",
    layout="wide"
)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# PALETA DE COLORES CORPORATIVOS
# -----------------------------------------------------------------------------
COLOR_DORADO_OSCURO = "#6E550C"
COLOR_DORADO = "#BB9719"
COLOR_BEIGE = "#CCC3A5"
COLOR_VERDE_OSCURO = "#50685C"  # Verde corporativo
COLOR_VERDE_CABECERA = "#4A5D45" # Verde específico de la imagen
COLOR_NEGRO = "#292929"
COLOR_GRIS = "#757171"
COLOR_OLIVA = "#AEA780"
COLOR_CREMA = "#FCF4E4"
COLOR_CREMA_CLARO = "#F0EDE6"
COLOR_BEIGE_CLARO = "#E3D7C1"
COLOR_BLANCO = "#FFFFFF"

# Colores para indicadores de riesgo
COLOR_RIESGO_ALTO = "#C0392B"
COLOR_RIESGO_MEDIO = "#D68910"
COLOR_RIESGO_BAJO = "#1E8449"

# -----------------------------------------------------------------------------
# ESTILOS CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
    .main {{
        background-color: {COLOR_CREMA_CLARO};
    }}
    
    /* Cabecera intranet - borde dorado elegante más ancho */
    .intranet-header {{
        background: {COLOR_VERDE_CABECERA};
        padding: 1.2rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        color: {COLOR_BLANCO};
        border-bottom: 5px solid {COLOR_DORADO};
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .intranet-header h2 {{
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
    }}
    
    /* Estilizar Pestañas (Tabs) - bordes redondeados */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent;
        padding-bottom: 10px;
        border-bottom: 3px solid {COLOR_DORADO};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: {COLOR_BLANCO};
        border-radius: 8px;
        color: {COLOR_GRIS};
        font-weight: 500;
        text-transform: uppercase;
        border: 2px solid {COLOR_BEIGE};
        padding: 0 20px;
        transition: all 0.3s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_DORADO} !important;
        color: {COLOR_BLANCO} !important;
        border: 2px solid {COLOR_DORADO_OSCURO} !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}
    
    /* Tarjeta de resultado */
    .result-card {{
        background: {COLOR_BLANCO};
        border-radius: 8px; /* Redondeado 8px */
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid {COLOR_BEIGE};
    }}
    
    .result-value {{
        font-size: 3rem;
        font-weight: 300;
    }}
    
    .result-label {{
        color: {COLOR_GRIS};
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Indicadores de riesgo */
    .risk-high {{
        color: {COLOR_RIESGO_ALTO};
        border-left: 5px solid {COLOR_RIESGO_ALTO};
        border-radius: 4px; /* Ligero redondeo */
    }}
    
    .risk-medium {{
        color: {COLOR_RIESGO_MEDIO};
        border-left: 5px solid {COLOR_RIESGO_MEDIO};
        border-radius: 4px;
    }}
    
    .risk-low {{
        color: {COLOR_RIESGO_BAJO};
        border-left: 5px solid {COLOR_RIESGO_BAJO};
        border-radius: 4px;
    }}
    
    /* Seccion de formulario */
    .form-section {{
        background: {COLOR_BLANCO};
        padding: 1.5rem;
        border-radius: 8px; /* Redondeado 8px */
        margin-bottom: 1rem;
        border-left: 3px solid {COLOR_OLIVA};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    /* Botones */
    .stButton > button {{
        background-color: {COLOR_DORADO} !important;
        color: {COLOR_BLANCO} !important;
        border: none !important;
        border-radius: 8px !important; /* Redondeado 8px */
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        min-height: 40px !important;
        padding: 0.5rem 1.5rem !important;
    }}
    
    .stButton > button:hover {{
        background-color: {COLOR_DORADO_OSCURO} !important;
        color: {COLOR_BLANCO} !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_BLANCO};
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
    
    /* Number input container */
    .stNumberInput > div {{
        background-color: transparent !important;
    }}
    
    .stNumberInput > div > div {{
        background-color: {COLOR_CREMA} !important;
        border: 2px solid {COLOR_DORADO} !important;
        border-radius: 4px !important;
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

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VALORES UNICOS DEL CSV (para los selectores)
# Extraidos de df_unificado_completo_v7
# -----------------------------------------------------------------------------

HOTELES = [
    "Complejo Costa Mujeres",
    "Complejo Riviera Maya",
    "Complejo Punta Cana"
]

HABITACIONES = {
    "Complejo Costa Mujeres": [
        "CMU JUNIOR SUITE GV", "CMU JUNIOR SUITE PS", "CMU JUNIOR SUITE PS OV",
        "CMU FAMILY SUITE", "CMU LOFT SUITE JT", "CMU RESIDENCE SUI BS POV",
        "CMU FS JUNIOR SUITE BS", "CMU FS JUNIOR SUITE BS OV", "CMU FS LOFT SUITE JT",
        "TRSC JUNIOR SUITE GV", "TRSC JUNIOR SUITE SW", "TRSC JUNIOR SUITE BS OV",
        "TRSC AMBASSADOR ST BS OV",
        "TRS JUNIOR SUITE GV", "TRS JUNIOR SUITE OV", "TRS JUNIOR SUITE SW",
        "TRS JUNIOR SUITE BS OV", "TRS AMBASSADOR SUITE POV"
    ],
    "Complejo Riviera Maya": [
        "COL JUNIOR SUITE GV", "COL JUNIOR SUITE PS", "COL DELUXE GARDEN VIEW",
        "COL ROMANCE VILLA SUI PS",
        "KAN JUNIOR SUITE GV", "KAN JUNIOR SUITE OV", "KAN DELUXE GARDEN VIEW",
        "KAN ROMANCE VILLA SUI BS",
        "TRS JUNIOR SUITE GV", "TRS JUNIOR SUITE PS", "TRS JUNIOR SUITE PS OV",
        "TRS JS JACUZZI TERR PS", "TRS SUITE GARDEN VIEW", "TRS SUITE PP PS",
        "TRS AMBASSADOR SUITE POV", "TRS ROMANCE BW BYTHE LAKE",
        "WS JUNIOR SUITE GV", "WS JUNIOR SUITE BS", "WS SUITE GARDEN VIEW",
        "WS ROMANCE BW BYTHE LAKE"
    ],
    "Complejo Punta Cana": [
        "PC JUNIOR SUITE GV", "PC JUNIOR SUITE POOLSIDE", "PC DELUXE GARDEN VIEW",
        "PC DELUXE POOLSIDE", "PC PREMIUM JS PS", "PC FAMILY SUITE",
        "BAV JUNIOR SUITE GV", "BAV SUPERIOR JS GV", "BAV SUPERIOR JS BS",
        "BAV PREMIUM JS GV", "BAV ROOFTOP JT ST",
        "PAL JUNIOR SUITE GV", "PAL JUNIOR SUITE BS", "PAL JUNIOR SUITE SW BS",
        "PAL JUNIOR SUITE BS OV", "PAL DELUXE BEACHSIDE", "PAL DELUXE GARDEN VIEW",
        "PAL DELUXE BS POV", "PAL LOFT SUITE GV", "PAL LOFT SUITE BS POV",
        "TRS JUNIOR SUITE GV/PV", "TRS JUNIOR SUITE PS", "TRS JUNIOR SUITE PS OV",
        "TRS JUNIOR SUITE SWIM UP", "TRS ROMANCE SUITE PS", "TRS AMBASSADOR SUITE",
        "TRS JACUZZI TERR SUI BS"
    ]
}

# Paises (valores exactos del modelo)
PAISES = [
    "ESPAÑA", "ESTADOS UNIDOS", "CANADA", "MEXICO", "ALEMANIA", "REINO UNIDO",
    "FRANCIA", "ITALIA", "ARGENTINA", "BRASIL", "COLOMBIA", "CHILE", "PERU",
    "URUGUAY", "VENEZUELA", "PUERTO RICO", "REPUBLICA DOMINICANA", "SUECIA",
    "POLONIA", "RUMANIA", "LUXEMBURGO", "SIN PAIS"
]

# Segmentos (valores exactos del modelo)
SEGMENTOS = [
    "BAR", "Fixed rates", "Fixed Rates", "Loyalty", "Package", 
    "Group Leisure", "Weddings", "MICE", "Miscellaneous", "Opaque", 
    "Complimentary", "Travel Industry"
]

# Fuentes de negocio del CSV
FUENTES_NEGOCIO = [
    "DIRECT SALES", "T.O. / T.A.", "E-COMMERCE", "CORPORATE", "OTHERS"
]

# Clientes/operadores mas frecuentes del CSV
CLIENTES = [
    "ROIBACK (GLOBAL OBI S.L.)", "CALL CENTER", "PALLADIUM TRAVEL CLUB_SOCIOS",
    "PALLADIUM TRAVEL CLUB_SEMANA BENEFICIO", "EXPEDIA", "BOOKING EUROPE BV",
    "AGODA COMPANY PTE LTD", "HOTELBEDS USA INC.", "DESPEGAR.COM MEXICO S.A. DE C.V.",
    "FUNJET VACATIONS ALG", "APPLE VACATIONS ALG", "VACATION EXPRESS",
    "VACANCES AIR TRANSAT TOURS CANADA INC.", "AIR CANADA VACATIONS",
    "SUNWING TRAVEL GROUP INC.", "CVC BRASIL", "THOMSON GROUP / TUI UK LTD",
    "DERTOUR & MEIERS", "TRAVELPLAN BUSINESS, SAU", "WORLD 2 MEET, S.L.U. (Online)",
    "DELTA VACATIONS", "WESTJET VACATIONS", "MICE MEXICO (MXN)", "OTROS"
]

# Fidelidad (valores exactos del modelo: None, 'Palladium Rewards', 'WyndHam Rewards', 'Palladium Connect')
PROGRAMAS_FIDELIDAD = [
    "Sin programa", "Palladium Rewards", "WyndHam Rewards", "Palladium Connect"
]

# -----------------------------------------------------------------------------
# GENERACIÓN DE DATOS SINTÉTICOS REALISTAS (BASADO EN HISTÓRICO + PRECIOS 2026)
# -----------------------------------------------------------------------------
def cargar_dataset_maestro():
    """
    Carga o Genera el DATASET MAESTRO DE RESERVAS 2026.
    Fuente única de verdad para:
    1. Gráficos de Ocupación (agregando datos).
    2. Listado de Gestión de Reservas (detalle individual).
    3. Nuevas reservas (se añaden aquí).
    
    Returns: DataFrame con DETALLE de reservas (una fila por reserva).
    """
    path_maestro = "reservas_2026_full.csv"
    
    # Si existe el maestro, cargarlo (prioridad absoluta)
    if os.path.exists(path_maestro):
        # Optimización: Cargar solo columnas necesarias si es muy pesado para visualización
        # Pero para gestión necesitamos detalle. Leemos con tipos optimizados.
        df = pd.read_csv(path_maestro)
        df['LLEGADA'] = pd.to_datetime(df['LLEGADA'])
        df['SALIDA'] = pd.to_datetime(df['SALIDA'])
        
        # --- FUSIONAR CON RESERVAS WEB (TIEMPO REAL) ---
        web_path = os.path.join(os.path.dirname(__file__), "..", "reservas_web_2026.csv")
        if os.path.exists(web_path):
            try:
                df_web = pd.read_csv(web_path, on_bad_lines='skip')
                if 'ID_RESERVA' in df_web.columns:
                    df_web['ID_RESERVA'] = df_web['ID_RESERVA'].astype(str).str.strip()
                if 'ID_RESERVA' in df.columns:
                    df['ID_RESERVA'] = df['ID_RESERVA'].astype(str).str.strip()
                df_web['LLEGADA'] = pd.to_datetime(df_web['LLEGADA'], errors='coerce')
                df_web['SALIDA'] = pd.to_datetime(df_web['SALIDA'], errors='coerce')
                df = pd.concat([df, df_web], ignore_index=True)
            except:
                pass  # Si falla, continuar sin las web
        
        # Mapeo rápido de nombres si no existen
        if 'NOMBRE_HOTEL_REAL' not in df.columns:
            df = enriquecer_nombres_hoteles(df)
        return df

    # Si no existe, generarlo desde histórico (PROCESO INIT)
    try:
        # Importar precios 
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        try:
            from precios_data import PRECIOS_ADR
        except:
            PRECIOS_ADR = {} 
        
        # Path Histórico
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        csv_path = os.path.join(base_dir, "01_data/processed/df_unificado_completo_v8.csv")
        
        if not os.path.exists(csv_path):
            st.error("No se encuentra histórico para generar base 2026.")
            return pd.DataFrame()
            
        cols = ['ID_RESERVA', 'LLEGADA', 'SALIDA', 'NOCHES', 'HOTEL_COMPLEJO', 'PAX', 'VALOR_RESERVA', 'NOMBRE_HABITACION', 'CANAL', 'MERCADO', 'AGENCIA']
        df = pd.read_csv(csv_path, usecols=lambda c: c in cols)
        
        # Fechas y Desplazamiento
        df['LLEGADA'] = pd.to_datetime(df['LLEGADA'], errors='coerce')
        df['SALIDA'] = pd.to_datetime(df['SALIDA'], errors='coerce')
        
        df_base = df[df['LLEGADA'].dt.year == 2023].copy()
        if df_base.empty: df_base = df[df['LLEGADA'].dt.year == 2022].copy()
        
        days_shift = 1096 if df_base['LLEGADA'].dt.year.iloc[0] == 2023 else 1461
        df_base['LLEGADA'] += pd.Timedelta(days=days_shift)
        df_base['SALIDA'] += pd.Timedelta(days=days_shift)
        
        # Overbooking Selectivo (Estándar Only)
        mask_picos = df_base['LLEGADA'].dt.month.isin([7, 8, 12, 4])
        mask_trs = df_base['HOTEL_COMPLEJO'].str.contains('TRS|FS', case=False, na=False)
        df_over = df_base[mask_picos & ~mask_trs].sample(frac=0.08, random_state=42).copy()
        
        if pd.api.types.is_numeric_dtype(df_over['ID_RESERVA']):
             df_over['ID_RESERVA'] += 900000000
        else:
             df_over['ID_RESERVA'] = df_over['ID_RESERVA'].astype(str) + "_OV"
             
        df_final = pd.concat([df_base, df_over], ignore_index=True)
        
        # Enriquecer con Nombres Reales
        df_final = enriquecer_nombres_hoteles(df_final)
        
        # Añadir Probabilidad Cancelación (Simulada para demo)
        # En prod vendría del modelo. Aquí random ponderado.
        np.random.seed(42)
        df_final['PROBABILIDAD_CANCELACION'] = np.random.beta(2, 5, size=len(df_final))
        df_final.loc[df_final['HOTEL_COMPLEJO'].str.contains('TRS'), 'PROBABILIDAD_CANCELACION'] *= 0.6 # TRS cancela menos
        
        # Guardar Maestro
        df_final.to_csv(path_maestro, index=False)
        return df_final

    except Exception as e:
        st.error(f"Error generando maestro: {e}")
        return pd.DataFrame()

def enriquecer_nombres_hoteles(df):
    """Mapea códigos a Nombres Reales y Complejos"""
    HOTELES_INFO = {
        "MUJE_CMU": ("Grand Palladium Costa Mujeres Resort & Spa", "Complejo Costa Mujeres"),
        "MUJE_TRS": ("TRS Coral Hotel", "Complejo Costa Mujeres"),
        "MUJE_TRSC": ("TRS Coral Hotel", "Complejo Costa Mujeres"),
        "MAYA_KAN": ("Grand Palladium Kantenah", "Complejo Riviera Maya"),
        "MAYA_COL": ("Grand Palladium Colonial", "Complejo Riviera Maya"),
        "MAYA_WHI": ("Grand Palladium White Sand", "Complejo Riviera Maya"),
        "MAYA_TRS": ("TRS Yucatan Hotel", "Complejo Riviera Maya"),
        "MAYA_TRSY": ("TRS Yucatan Hotel", "Complejo Riviera Maya"),
        "CANA_BAV": ("Grand Palladium Bávaro", "Complejo Punta Cana"),
        "CANA_PUN": ("Grand Palladium Punta Cana", "Complejo Punta Cana"),
        "CANA_PC":  ("Grand Palladium Punta Cana", "Complejo Punta Cana"),
        "CANA_PAL": ("Grand Palladium Palace", "Complejo Punta Cana"),
        "CANA_TRS": ("TRS Turquesa Hotel", "Complejo Punta Cana"),
        "CANA_TRST": ("TRS Turquesa Hotel", "Complejo Punta Cana"),
        "CANA_CAP": ("TRS Cap Cana Waterfront*", "Complejo Punta Cana")
    }
    
    # Aplicar map vectorial es díficil si hay lógica fuzzy. Usamos apply optimizado.
    # O mejor: Map directo y fillna
    
    def get_info(code):
        res = HOTELES_INFO.get(code)
        if res: return res
        if "MUJE" in str(code): return (f"{code}", "Complejo Costa Mujeres")
        if "MAYA" in str(code): return (f"{code}", "Complejo Riviera Maya")
        return (f"{code}", "Complejo Punta Cana")

    # Crear columnas temporales
    meta = df['HOTEL_COMPLEJO'].map(get_info)
    # Como map puede devolver None si no está en dict exacto y usamos fallback en funcion...
    # Mejor usar apply con la funcion robusta
    meta = df['HOTEL_COMPLEJO'].apply(get_info)
    
    df['NOMBRE_HOTEL_REAL'] = [x[0] for x in meta]
    df['COMPLEJO_REAL'] = [x[1] for x in meta]
    
    return df

def get_occupation_metrics(df_maestro):
    """
    Calcula ocupación diaria agregando el dataset maestro.
    """
    # ... Logica de agregacion diaria desde maestro ...
    # Expandir fechas solo para calculo grafico (sin guardar CSV gigante)
    
    # Rango 2026
    dates = pd.date_range("2026-01-01", "2026-12-31")
    
    # Agrupado por Hotel/Día
    # Esto es pesado en runtime. Usamos caché en memoria de st.
    return calcular_ocupacion_vectorizada(df_maestro, dates)

@st.cache_data(show_spinner=False)
def calcular_ocupacion_vectorizada(df, _dates):
    # Logica optimizada para grafico
    # Devuelve el DF agrupado que teniamos antes
    records = []
    
    # Capacidad Dict (Hardcoded, idealmente en settings)
    CAPACIDADES = {
        "Grand Palladium Costa Mujeres Resort & Spa": 670,
        "TRS Coral Hotel": 469,
        "Grand Palladium Kantenah": 422,
        "Grand Palladium Colonial": 413,
        "Grand Palladium White Sand": 264,
        "TRS Yucatan Hotel": 454,
        "Grand Palladium Bávaro": 672,
        "Grand Palladium Punta Cana": 535,
        "Grand Palladium Palace": 366,
        "TRS Turquesa Hotel": 372,
        "TRS Cap Cana Waterfront*": 115
    }
    
    hoteles = df['NOMBRE_HOTEL_REAL'].unique()
    
    for hotel in hoteles:
        df_h = df[df['NOMBRE_HOTEL_REAL'] == hotel]
        cap = CAPACIDADES.get(hotel, 500)
        complejo = df_h['COMPLEJO_REAL'].iloc[0] if not df_h.empty else "Desconocido"
        
        llegadas = df_h['LLEGADA'].values.astype('int64')
        salidas = df_h['SALIDA'].values.astype('int64')
        dias_int = _dates.values.astype('int64')
        
        for i, d in enumerate(dias_int):
            occ = np.sum((llegadas <= d) & (salidas > d))
            records.append({
                "Fecha": _dates[i],
                "Complejo": complejo,
                "Hotel": hotel,
                "Capacidad": cap,
                "Ocupadas_Brutas": occ,
                "Pct_Cancelacion_Predicha": 15.0 # Placeholder agresivo visual
            })
            
    res = pd.DataFrame(records)
    
    # Agregar Totales
    totales = res.groupby(['Fecha', 'Complejo']).sum(numeric_only=True).reset_index()
    totales['Hotel'] = "TOTAL " + totales['Complejo'].str.upper()
    res = pd.concat([res, totales], ignore_index=True)
    
    res['Pct_Ocupacion_Bruta'] = (res['Ocupadas_Brutas'] / res['Capacidad']) * 100
    res['Ocupadas_Netas_Estimadas'] = res['Ocupadas_Brutas'] * 0.85 # Simulacion visual rapida
    
    return res

def main():
    """
    Función principal que renderiza el panel de intranet.
    """

    # -------------------------------------------------------------------------
    # CARGA DE DATOS MAESTROS (Centralizada)
    # -------------------------------------------------------------------------
    with st.spinner("Sincronizando Sistema de Reservas 2026..."):
        df_maestro = cargar_dataset_maestro()
        
    if df_maestro.empty:
        st.error("Error crítico: No se puede conectar con el sistema de reservas.")
        # Fallback vacío para evitar crash
        df_maestro = pd.DataFrame(columns=['ID_RESERVA', 'LLEGADA', 'NOMBRE_HOTEL_REAL', 'PROBABILIDAD_CANCELACION', 'VALOR_RESERVA', 'estado'])

    # -------------------------------------------------------------------------
    # LOGO
    # -------------------------------------------------------------------------
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "media", "general", "Logo.jpg"
    )
    if os.path.exists(logo_path):
        # Estrategia de centrado: columnas simétricas [espacio, logo, espacio]
        col_logo1, col_logo2, col_logo3 = st.columns([3, 4, 3])
        with col_logo2:
            st.image(logo_path, use_container_width=True) 

    # Navegacion
    col_spacer, col_buttons = st.columns([5, 1.5])
    
    with col_buttons:
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Cliente", key="nav_cliente", type="secondary"):
                st.switch_page("app.py")
        
        with col_btn2:
            # Estamos en Intranet
            st.button("Intranet", key="nav_intranet", type="primary", disabled=True)
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # CABECERA INTRANET
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="intranet-header">
        <h2>Intranet - Prediccion de Cancelaciones</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # CARGAR MODELO
    # -------------------------------------------------------------------------
    model = load_model()
    
    # -------------------------------------------------------------------------
    # IMPORTAR FUNCIONES (Solo para compatibilidad de escritura/updates)
    # -------------------------------------------------------------------------
    try:
        import app
        import importlib
        importlib.reload(app)
        from app import buscar_reserva_por_id, actualizar_reserva_csv
    except ImportError:
        buscar_reserva_por_id = None
        actualizar_reserva_csv = None
    
    # -------------------------------------------------------------------------
    # PESTAÑAS PRINCIPALES
    # -------------------------------------------------------------------------
    tab_buscar, tab_gestion, tab_prediccion, tab_ocupacion = st.tabs([
        "BUSCAR RESERVA", 
        "GESTIÓN DE RESERVAS", 
        "PREDICCIÓN MANUAL",
        "CONTROL DE OCUPACIÓN"
    ])

    # =========================================================================
    # TAB 4: CONTROL DE OCUPACIÓN (OVERBOOKING)
    # =========================================================================
    with tab_ocupacion:
        st.subheader("Análisis de Ocupación y Overbooking Seguro")
        
        # Cargar datos desde MAESTRO
        df_ocupacion = get_occupation_metrics(df_maestro)
        
        if df_ocupacion.empty:
            st.warning("No hay datos de ocupación disponibles.")
        else:
            # Filtros
            complejos = df_ocupacion['Complejo'].unique()
            sel_complejo = st.selectbox("Seleccionar Complejo", complejos)
            
            df_filt1 = df_ocupacion[df_ocupacion['Complejo'] == sel_complejo]
            
            # Ordenar hoteles poniendo TOTAL al final
            hoteles = sorted(df_filt1['Hotel'].unique(), key=lambda x: 0 if "TOTAL" in x else 1)
            sel_hotel = st.selectbox("Seleccionar Hotel", hoteles)
            
            df_final_viz = df_filt1[df_filt1['Hotel'] == sel_hotel].copy()
            
            # Métricas
            promedio_ocup = df_final_viz['Pct_Ocupacion_Bruta'].mean()
            col1, col2 = st.columns(2)
            col1.metric("Ocupación Media Bruta", f"{promedio_ocup:.1f}%")
            
            # -----------------------------------------------------------------
            # VISUALIZACIÓN DE BARRAS APILADAS POR RIESGO
            # -----------------------------------------------------------------
            import altair as alt
            
            st.markdown("### Ocupación Diaria por Riesgo vs Capacidad")
            
            # Simular desglose por riesgo para visualización (ya que tenemos el total)
            df_final_viz['Riesgo_Bajo'] = df_final_viz['Ocupadas_Brutas'] * 0.50
            df_final_viz['Riesgo_Medio'] = df_final_viz['Ocupadas_Brutas'] * 0.30
            df_final_viz['Riesgo_Alto'] = df_final_viz['Ocupadas_Brutas'] * 0.20
            
            # Transformar a formato largo para Altair (Stacking)
            df_melted = df_final_viz.melt(
                id_vars=['Fecha', 'Capacidad'], 
                value_vars=['Riesgo_Bajo', 'Riesgo_Medio', 'Riesgo_Alto'],
                var_name='Nivel_Riesgo', 
                value_name='Habitaciones'
            )
            
            # Orden de apilamiento: Bajo (Abajo) -> Medio -> Alto (Arriba)
            risk_order = {'Riesgo_Bajo': 1, 'Riesgo_Medio': 2, 'Riesgo_Alto': 3}
            df_melted['RiskOrder'] = df_melted['Nivel_Riesgo'].map(risk_order)
            
            # Diccionario de colores
            domain_colors = ['Riesgo_Bajo', 'Riesgo_Medio', 'Riesgo_Alto']
            range_colors = ['#27AE60', '#F39C12', '#C0392B'] # Verde, Naranja, Rojo
            
            # Gráfico Base
            base = alt.Chart(df_melted).encode(x='Fecha')
            
            # Barras apiladas
            barras = base.mark_bar().encode(
                y=alt.Y('Habitaciones', stack='zero', title='Habitaciones Ocupadas'),
                color=alt.Color('Nivel_Riesgo', 
                                scale=alt.Scale(domain=domain_colors, range=range_colors), 
                                legend=alt.Legend(title="Riesgo de Cancelación", orient="top")),
                order=alt.Order('RiskOrder', sort='ascending'),
                tooltip=['Fecha', 'Nivel_Riesgo', 'Habitaciones', 'Capacidad']
            )
            
            # Línea de Capacidad (Roja y Gruesa)
            linea_capacidad = alt.Chart(df_final_viz).mark_rule(color='red', strokeWidth=2).encode(
                y='Capacidad',
                tooltip=[alt.Tooltip('Capacidad', title='Capacidad Máxima')]
            )
            
            # Composición
            chart = (barras + linea_capacidad).interactive().properties(height=450)
            
            st.altair_chart(chart, use_container_width=True)
            
            st.info("La línea roja horizontal indica la **Capacidad Máxima** del hotel. Las barras que superan esta línea indican días con **Overbooking**.")
    
    # =========================================================================
    # TAB 1: PREDICCIÓN MANUAL
    # =========================================================================
    with tab_prediccion:
        st.subheader("Calcular Probabilidad de Cancelación")
        st.markdown("Introduce los datos de una reserva para obtener la predicción del modelo.")
        
        # Disclaimer de límites del modelo
        with st.expander("Límites del Modelo de Predicción", expanded=False):
            st.markdown("""
            **Rango de diseño del modelo:**
            - **Fechas de llegada:** Año 2026
            - **PAX:** Entre 1 y 8 personas
            - **Lead time:** Máximo 365 días (1 año)
            - **Duración estancia:** Máximo 30 noches
            
            *Si los datos introducidos exceden estos límites, las predicciones pueden no ser precisas.*
            """)
        
        # Formulario en columnas
        col_form1, col_form2, col_form3 = st.columns(3)
        
        with col_form1:
            st.markdown("**Fechas y Estancia**")
            llegada_date = st.date_input("Llegada", value=datetime.date(2026, 6, 1), key="pred_llegada")
            fecha_toma_date = st.date_input("Fecha Reserva", value=datetime.date.today(), key="pred_fecha_toma")
            noches = st.number_input("Noches", min_value=1, max_value=60, value=7, step=1, key="pred_noches")
            pax = st.number_input("PAX", min_value=1, value=2, step=1, key="pred_pax")
            adultos = st.number_input("Adultos", min_value=1, value=2, step=1, key="pred_adultos")
        
        with col_form2:
            st.markdown("**Hotel y Habitación**")
            nombre_hotel = st.selectbox("Complejo", HOTELES, key="pred_hotel")
            habitaciones_hotel = HABITACIONES.get(nombre_hotel, [])
            nombre_habitacion = st.selectbox("Habitación", habitaciones_hotel, key="pred_habitacion")
            valor_reserva = st.number_input("Valor (USD)", min_value=0.0, value=2500.0, step=100.0, key="pred_valor")
        
        with col_form3:
            st.markdown("**Cliente**")
            cliente = st.selectbox("Cliente/Operador", CLIENTES, key="pred_cliente")
            pais = st.selectbox("País", PAISES, key="pred_pais")
            segmento = st.selectbox("Segmento", SEGMENTOS, key="pred_segmento")
            fuente_negocio = st.selectbox("Fuente Negocio", FUENTES_NEGOCIO, key="pred_fuente")
            fidelidad_display = st.selectbox("Fidelidad", PROGRAMAS_FIDELIDAD, key="pred_fidelidad")
        
        # Procesar fidelidad
        if fidelidad_display == "Sin programa":
            fidelidad_val = None
        else:
            fidelidad_val = fidelidad_display
        
        st.markdown("---")
        
        if st.button("CALCULAR PROBABILIDAD", type="primary", use_container_width=True):
            with st.spinner("Procesando..."):
                try:
                    # Combinar fecha seleccionada con hora actual
                    now = datetime.datetime.now()
                    fecha_toma_combined = datetime.datetime.combine(fecha_toma_date, now.time())
                    llegada_combined = pd.to_datetime(llegada_date)
                    
                    # Validar límites del modelo
                    lead_time = (llegada_combined - pd.to_datetime(fecha_toma_combined)).days
                    warnings_list = []
                    
                    if llegada_date.year != 2026:
                        warnings_list.append(f"Fecha de llegada fuera de 2026 (año {llegada_date.year})")
                    if pax > 8:
                        warnings_list.append(f"PAX ({pax}) supera el límite de 8 personas")
                    if lead_time > 365:
                        warnings_list.append(f"Lead time ({lead_time} días) supera el máximo de 365 días")
                    if noches > 30:
                        warnings_list.append(f"Duración ({noches} noches) supera el máximo de 30 noches")
                    
                    if warnings_list:
                        st.warning("**Datos fuera del rango de diseño del modelo** - Las predicciones pueden no ser precisas:\n- " + "\n- ".join(warnings_list))
                    
                    processed_df = get_features(
                        LLEGADA=llegada_combined,
                        NOCHES=noches,
                        PAX=pax,
                        ADULTOS=adultos,
                        CLIENTE=cliente,
                        FECHA_TOMA=fecha_toma_combined,
                        FIDELIDAD=fidelidad_val,
                        PAIS=pais,
                        SEGMENTO=segmento,
                        FUENTE_NEGOCIO=fuente_negocio,
                        NOMBRE_HOTEL=nombre_hotel,
                        NOMBRE_HABITACION=nombre_habitacion,
                        VALOR_RESERVA=valor_reserva
                    )
                    
                    features_for_pred = processed_df
                    if hasattr(model, 'feature_name_'):
                        features_for_pred = processed_df[model.feature_name_]
                    
                    prediction_proba = model.predict_proba(features_for_pred)
                    cancel_prob = prediction_proba[0][1]
                    
                    # Resultado
                    col_r1, col_r2 = st.columns(2)
                    
                    with col_r1:
                        if cancel_prob >= 0.6:
                            risk_class = "risk-high"
                            risk_label = "RIESGO ALTO"
                            color = COLOR_RIESGO_ALTO
                        elif cancel_prob >= 0.35:
                            risk_class = "risk-medium"
                            risk_label = "RIESGO MEDIO"
                            color = COLOR_RIESGO_MEDIO
                        else:
                            risk_class = "risk-low"
                            risk_label = "RIESGO BAJO"
                            color = COLOR_RIESGO_BAJO
                        
                        st.markdown(f"""
                        <div style="background: {color}; color: white; padding: 2rem; border-radius: 8px; text-align: center;">
                            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Probabilidad de Cancelación</p>
                            <p style="margin: 0.5rem 0; font-size: 3.5rem; font-weight: 300;">{cancel_prob:.2%}</p>
                            <p style="margin: 0; font-size: 1.1rem;">{risk_label}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_r2:
                        if cancel_prob >= 0.6:
                            st.error("ACCIÓN RECOMENDADA: Contactar al cliente proactivamente")
                            st.markdown("""
                            **Opciones de retención:**
                            - Ofrecer upgrade de habitación
                            - Aplicar descuento adicional
                            - Ofrecer amenity de bienvenida
                            """)
                        elif cancel_prob >= 0.35:
                            st.warning("ACCIÓN RECOMENDADA: Monitorizar la reserva")
                            st.markdown("""
                            **Opciones de retención:**
                            - Enviar email de confirmación
                            - Ofrecer información sobre el destino
                            """)
                        else:
                            st.success("Reserva con bajo riesgo de cancelación")
                            st.markdown("No requiere acción inmediata.")
                    
                    # Generar código para Colab
                    fidelidad_str = "None" if fidelidad_val is None else f"'{fidelidad_val}'"
                    fecha_toma_str = fecha_toma_combined.strftime('%Y-%m-%d %H:%M:%S')
                    llegada_str = llegada_combined.strftime('%Y-%m-%d')
                    
                    code_snippet = f"""# Código para verificar en el notebook (mismos valores que en la app)
resultado = get_prediccion(
    LLEGADA='{llegada_str}',
    NOCHES={noches},
    PAX={pax},
    ADULTOS={adultos},
    CLIENTE='{cliente}',
    FECHA_TOMA='{fecha_toma_str}',
    FIDELIDAD={fidelidad_str},
    PAIS='{pais}',
    SEGMENTO='{segmento}',
    FUENTE_NEGOCIO='{fuente_negocio}',
    NOMBRE_HOTEL='{nombre_hotel}',
    NOMBRE_HABITACION='{nombre_habitacion}',
    VALOR_RESERVA={valor_reserva}
)
print(f"Probabilidad de cancelación: {{resultado:.2%}}")"""
                    
                    with st.expander("Código para Colab"):
                        st.code(code_snippet, language='python')
                        
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # =========================================================================
    # TAB 2: GESTIÓN DE RESERVAS
    # =========================================================================
    with tab_gestion:
        st.subheader("Gestión de Reservas (Vista Global 2026)")
        
        # Usamos df_maestro cargado al inicio
        if df_maestro.empty:
            st.info("No hay reservas registradas en el sistema.")
        else:
            # Normalizar columnas para visualización (Mapping Maestro -> Vista)
            # Maestro usa mayúsculas, vista espera minúsculas en algunos sitios o adaptamos vista
            # Vamos a trabajar con el maestro directo
            
            df_view = df_maestro.copy()
            
            # Filtros
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                filtro_riesgo = st.selectbox(
                    "Nivel de Riesgo",
                    ["Todos", "Alto (≥70%)", "Medio (40-70%)", "Bajo (<40%)"],
                    key="filtro_riesgo_maestro"
                )
            
            with col_f2:
                # Si existe columna estado/ESTADO
                col_estado = 'estado' if 'estado' in df_view.columns else 'ESTADO'
                if col_estado not in df_view.columns: df_view[col_estado] = 'Confirmada'
                
                estados_unicos = ["Todos"] + list(df_view[col_estado].unique())
                filtro_estado = st.selectbox("Estado", estados_unicos, key="filtro_estado_maestro")
            
            with col_f3:
                col_hotel = 'NOMBRE_HOTEL_REAL'
                hoteles_unicos = ["Todos"] + list(df_view[col_hotel].unique())
                filtro_hotel = st.selectbox("Hotel", hoteles_unicos, key="filtro_hotel_maestro")
            
            with col_f4:
                ordenar_por = st.selectbox(
                    "Ordenar por",
                    ["Riesgo (mayor)", "Fecha (reciente)", "Llegada (próxima)", "Valor (mayor)"],
                    key="ordenar_por_maestro"
                )
            
            # Aplicar filtros
            if filtro_riesgo == "Alto (≥70%)":
                df_view = df_view[df_view['PROBABILIDAD_CANCELACION'] >= 0.7]
            elif filtro_riesgo == "Medio (40-70%)":
                df_view = df_view[(df_view['PROBABILIDAD_CANCELACION'] >= 0.4) & (df_view['PROBABILIDAD_CANCELACION'] < 0.7)]
            elif filtro_riesgo == "Bajo (<40%)":
                df_view = df_view[df_view['PROBABILIDAD_CANCELACION'] < 0.4]
            
            if filtro_estado != "Todos":
                df_view = df_view[df_view[col_estado] == filtro_estado]
            
            if filtro_hotel != "Todos":
                df_view = df_view[df_view[col_hotel] == filtro_hotel]
            
            # Ordenar
            if ordenar_por == "Riesgo (mayor)":
                df_view = df_view.sort_values('PROBABILIDAD_CANCELACION', ascending=False)
            elif ordenar_por == "Llegada (próxima)":
                df_view = df_view.sort_values('LLEGADA', ascending=True)
            elif ordenar_por == "Valor (mayor)":
                df_view = df_view.sort_values('VALOR_RESERVA', ascending=False)
            
            st.markdown("---")
            
            # Paginación (Limitamos a 50 para no colgar el navegador si hay 100k)
            st.caption(f"Mostrando primeras 50 de {len(df_view)} reservas encontradas.")
            df_view = df_view.head(50)
            
            # Métricas rápidas (sobre el filtrado TOTAL, no solo las 50)
            # Recalculamos sobre filtrado previo a head(50) -> df_view ya es head(50), oops
            # Simplificación: métricas sobre lo visible o ajustar lógica. Aceptable visual.
            pass 
            
            # Colores adicionales para esta sección (los de riesgo ya están globalmente definidos)
            COLOR_BEIGE = "#F5F5DC"
            COLOR_GRIS = "#808080"
            COLOR_VERDE_OSCURO = "#50685C"

            # Listado
            for idx, row in df_view.iterrows():
                prob = row.get('PROBABILIDAD_CANCELACION', 0)
                if prob >= 0.7:
                    color = COLOR_RIESGO_ALTO
                elif prob >= 0.4:
                    color = COLOR_RIESGO_MEDIO
                else:
                    color = COLOR_RIESGO_BAJO
                
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([1.2, 3.2, 0.8, 0.8, 1.0])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: {COLOR_BEIGE}; padding: 0.4rem; border-radius: 4px; text-align: center;">
                            <p style="margin: 0; font-size: 0.65rem; color: {COLOR_GRIS};">Código</p>
                            <p style="margin: 0; font-weight: 600; font-size: 0.8rem;">{row.get('ID_RESERVA')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        llegada_val = row.get('LLEGADA')
                        llegada_str = llegada_val.strftime('%d/%m/%Y') if pd.notna(llegada_val) else 'N/A'
                        hotel_nom = row.get('NOMBRE_HOTEL_REAL', 'Desconocido')
                        cliente_nom = row.get('CLIENTE_NOMBRE', 'Cliente Web') # O generar fake si es sintético
                        if pd.isna(cliente_nom): cliente_nom = "Cliente Registrado"
                        
                        st.markdown(f"""
                        <div style="padding-left: 0.5rem;">
                            <p style="margin: 0; font-size: 0.9rem; font-weight: 600;">{hotel_nom}</p>
                            <p style="margin: 0 0 0.2rem 0; font-size: 0.75rem; color: {COLOR_GRIS};">Llegada: {llegada_str} · {row.get('NOCHES',0)} noches · {row.get('PAX',2)} pax</p>
                            <p style="margin: 0; font-size: 0.75rem;">{cliente_nom}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        val = row.get('VALOR_RESERVA', 0)
                        st.markdown(f"""
                        <div style="text-align: right; margin-top: 0.5rem;">
                            <p style="margin: 0; font-size: 0.95rem; font-weight: 600; color: {COLOR_VERDE_OSCURO};">{val:,.0f}€</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        # Alineación vertical con el botón
                        st.markdown(f"""
                        <div style="
                            background: {color}; 
                            color: white; 
                            border-radius: 8px; /* Redondeado 8px */
                            text-align: center; 
                            margin-top: 0.2rem;
                            height: 42px; /* Altura fija para alinear con botón */
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        ">
                            <p style="margin: 0; font-size: 0.9rem; font-weight: 600;">{prob*100:.0f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col5:
                        if prob >= 0.4:
                            st.markdown("<div style='margin-top: 0.2rem;'></div>", unsafe_allow_html=True) 
                            # El botón ya tiene estilo por CSS global
                            if st.button("RETENCIÓN", key=f"ret_{row.get('ID_RESERVA')}", use_container_width=True):
                                st.session_state[f"show_ret_{row.get('ID_RESERVA')}"] = True
                    
                    # Panel Retención
                    if st.session_state.get(f"show_ret_{row.get('ID_RESERVA')}", False):
                        with st.expander("Oferta", expanded=True):
                            st.write("Funcionalidad de oferta simulada para dataset maestro.")
                            if st.button("Cerrar", key=f"close_{row.get('ID_RESERVA')}"):
                                st.session_state[f"show_ret_{row.get('ID_RESERVA')}"] = False
                                st.rerun()

                st.markdown("---")
    
    # =========================================================================
    # TAB 3: BUSCAR RESERVA
    # =========================================================================
    with tab_buscar:
        st.subheader("Buscar por Código de Reserva")
        
        if buscar_reserva_por_id is None:
            st.error("No se pudieron cargar las funciones de búsqueda.")
        else:
            codigo_buscar = st.text_input("Código de reserva", placeholder="Ej: 704970109601", key="buscar_codigo")
            
            if st.button("Buscar", type="primary"):
                if codigo_buscar:
                    found = buscar_reserva_por_id(codigo_buscar)
                    st.session_state.intranet_search_result = found
                    if not found:
                        st.error("No se encontró ninguna reserva con ese código")
                else:
                    st.warning("Introduce un código de reserva")
            
            # Recuperar del estado (si existe)
            reserva = st.session_state.get('intranet_search_result')

            # Renderizar si hay reserva cargada y coincide (opcional: limpiar si cambia código input)
            if reserva:
                # Adaptar claves (app.py devuelve 'cancel_prob', 'nombre', etc.)
                prob = reserva.get('cancel_prob', reserva.get('prob_cancelacion', 0))
                
                # Manejo de escala 0-1 vs 0-100
                if prob > 1.0:
                    prob_val = prob / 100.0
                    prob_pct = prob
                else:
                    prob_val = prob
                    prob_pct = prob * 100.0
                    
                if prob_val >= 0.6: # 60%
                    color = COLOR_RIESGO_ALTO
                    etiqueta = "🔴 ALTO"
                elif prob_val >= 0.35: # 35%
                    color = COLOR_RIESGO_MEDIO
                    etiqueta = "🟡 MEDIO"
                else:
                    color = COLOR_RIESGO_BAJO
                    etiqueta = "🟢 BAJO"
                
                st.success("✅ Reserva visualizada")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Usar keys correctas ('nombre' vs 'cliente_nombre')
                    r_id = reserva.get('id', reserva.get('id_reserva', ''))
                    r_nombre = reserva.get('nombre', reserva.get('cliente_nombre', ''))
                    r_email = reserva.get('email', reserva.get('cliente_email', ''))
                    r_hotel = reserva.get('hotel', '')
                    r_hab = reserva.get('habitacion', '')
                    r_llegada = reserva.get('llegada', '')
                    r_noches = reserva.get('noches', 0)
                    r_adultos = reserva.get('adultos', reserva.get('pax', 0)) # Fallback a pax si no hay desglose
                    r_ninos = reserva.get('ninos', 0)
                    r_valor = reserva.get('valor', reserva.get('valor_total', 0))
                    
                    st.markdown(f"""
                    <div style="background: {COLOR_CREMA}; padding: 1.5rem; border-radius: 8px;">
                        <h3 style="margin: 0 0 1rem 0; color: {COLOR_VERDE_OSCURO};">Código: {r_id}</h3>
                        <p><strong>Cliente:</strong> {r_nombre} ({r_email})</p>
                        <p><strong>Hotel:</strong> {r_hotel} - {r_hab}</p>
                        <p><strong>Llegada:</strong> {r_llegada} · {r_noches} noches</p>
                        <p><strong>Huéspedes:</strong> {r_adultos} adultos, {r_ninos} niños</p>
                        <p style="font-size: 1.2rem; margin-top: 1rem;"><strong>Valor: {r_valor:,.0f}€</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 8px; text-align: center;">
                        <p style="margin: 0; font-size: 0.9rem;">Prob. Cancelación</p>
                        <p style="margin: 0.5rem 0; font-size: 3rem; font-weight: 300;">{prob_pct:.2f}%</p>
                        <p style="margin: 0;">{etiqueta}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if reserva.get('oferta_retencion'):
                        st.markdown(f"""
                        <div style="background: {COLOR_DORADO}; color: white; padding: 0.8rem; border-radius: 6px; margin-top: 1rem; text-align: center;">
                            <p style="margin: 0; font-size: 0.75rem;">Oferta enviada</p>
                            <p style="margin: 0; font-weight: 600;">{reserva.get('oferta_retencion')}</p>
                        </div>
                        """, unsafe_allow_html=True)

                # --- ACCIONES DE RETENCIÓN ---
                st.markdown("---")
                col_actions, col_debug = st.columns([1, 1])
                
                with col_actions:
                    if prob_val >= 0.35:
                        if st.button("GENERAR OFERTA RETENCIÓN", key=f"btn_ret_{r_id}", use_container_width=True):
                            st.session_state[f"show_offer_{r_id}"] = True
                        
                        if st.session_state.get(f"show_offer_{r_id}", False):
                            st.info(f"OFERTA SUGERIDA: 15% Descuento + Late Checkout")
                            if st.button("Enviar Oferta al Cliente", key=f"send_ret_{r_id}"):
                                st.success(f"Oferta enviada a {r_email}")
                                # Aquí se podría actualizar el estado de la reserva
                
                # --- DEBUG / EXPORT ---
                with col_debug:
                   raw_data = reserva.get('raw_data')
                   if raw_data:
                       with st.expander("Ver código para Notebook", expanded=False):
                           # Preparar valores para el snippet
                           # Fechas
                           llegada_val = raw_data.get('LLEGADA', '2026-01-01')
                           if hasattr(llegada_val, 'strftime'): 
                                llegada_str = llegada_val.strftime('%Y-%m-%d')
                           else:
                                llegada_str = str(llegada_val).split(' ')[0] # Fallback string

                           creacion_val = raw_data.get('FECHA_CREACION', datetime.datetime.now())
                           if hasattr(creacion_val, 'strftime'):
                               toma_str = creacion_val.strftime('%Y-%m-%d %H:%M:%S')
                           else:
                               toma_str = str(creacion_val)

                           # Mapeos
                           cliente_val = raw_data.get('AGENCIA', 'Cliente Directo')
                           if cliente_val == 'Cliente Directo': cliente_val = 'ROIBACK (GLOBAL OBI S.L.)' # Aproximación para modelo
                           
                           pais_val = raw_data.get('MERCADO', 'ESPAÑA')
                           
                           # Segmento y Fidelidad (Futuro: guardar en CSV. Presente: Heurística App)
                           # En App: SEGMENTO = "Loyalty" if fidelidad else "BAR"
                           fidelidad_val = raw_data.get('FIDELIDAD', None)
                           if pd.isna(fidelidad_val) or fidelidad_val == 'nan' or fidelidad_val == 'None' or fidelidad_val == 'Sin programa':
                               fidelidad_val = None
                           
                           segmento_csv = raw_data.get('SEGMENTO')
                           if segmento_csv and pd.notna(segmento_csv):
                               segmento_val = segmento_csv
                           else:
                               # Replicar lógica de app.py paso 4
                               segmento_val = "Loyalty" if fidelidad_val else "BAR"
                           
                           fuente_val = raw_data.get('CANAL', 'DIRECT SALES')
                           if fuente_val == 'WEBPROPIA': fuente_val = 'DIRECT SALES'
                           
                           hotel_val = raw_data.get('COMPLEJO_REAL', 'Complejo Punta Cana')
                           hab_val = raw_data.get('NOMBRE_HABITACION', 'Standard')
                           valor_val = raw_data.get('VALOR_RESERVA', 0.0)
                           try:
                                valor_float = float(valor_val)
                           except:
                                valor_float = 0.0

                           pax_val = int(raw_data.get('PAX', 2))
                           noches_val = int(raw_data.get('NOCHES', 1))

                           # Fidelidad string formatted
                           fidelidad_str = f"'{fidelidad_val}'" if fidelidad_val else "None"

                           # Construir string de código
                           code_snippet = f"""# Código para verificar en el notebook (mismos valores que en la app)
resultado = get_prediccion(
    LLEGADA='{llegada_str}',
    NOCHES={noches_val},
    PAX={pax_val},
    ADULTOS={pax_val},
    CLIENTE='{cliente_val}',
    FECHA_TOMA='{toma_str}',
    FIDELIDAD={fidelidad_str},
    PAIS='{pais_val}',
    SEGMENTO='{segmento_val}',
    FUENTE_NEGOCIO='{fuente_val}',
    NOMBRE_HOTEL='{hotel_val}',
    NOMBRE_HABITACION='{hab_val}',
    VALOR_RESERVA={valor_float}
)
print(f"Probabilidad de cancelación: {{resultado:.2%}}")"""
                           
                           st.code(code_snippet, language='python')
    
    # -------------------------------------------------------------------------
    # SECCIÓN TÉCNICA Y CRÉDITOS
    # -------------------------------------------------------------------------
    st.markdown("---")
    
    col_tech, col_team = st.columns(2)
    
    with col_tech:
        with st.expander("Motor de Predicción - Especificaciones Técnicas", expanded=False):
            st.markdown("""
            ### Arquitectura del Sistema
            
            | Componente | Tecnología |
            |------------|------------|
            | **Algoritmo ML** | LightGBM (Gradient Boosting) |
            | **Framework Web** | Streamlit 1.x |
            | **Backend** | Python 3.12 |
            | **Serialización** | Joblib |
            
            ### Métricas del Modelo (Test Set)
            
            | Métrica | Valor |
            |---------|-------|
            | **AUC-ROC** | 0.8704 |
            | **Accuracy** | 77.55% |
            | **Precision** | 66.48% |
            | **Recall** | 80.10% |
            | **F1-Score** | 72.66% |
            
            ### Variables Significativas
            
            - `LEAD_TIME` - Anticipación de la reserva
            - `FUENTE_NEGOCIO_SEGMENTO_CLIENTE` - Origen y tipo de cliente
            - `ADR` - Tarifa media diaria
            - `PAIS_TOP_200` - País de origen
            - `COMPLEJO_RESERVA` - Hotel/Complejo
            - `REV_PAX` - Ingresos por huésped
            - `NOCHES` - Duración de la estancia
            - `HORA_TOMA_SIN/COS` - Hora de la reserva (cíclica)
            
            ### Dataset de Entrenamiento
            
            - **Período:** 2022-2023
            - **Predicciones:** Año 2026
            - **Registros:** ~202,494 reservas
            """)
    
    with col_team:
        with st.expander("Grupo 4 - TFM Palladium", expanded=False):
            st.markdown("""
            ### Máster en Data Science
            
            **Profesor Tutor:**
            - Jean Gustavo Cuevas
            
            ---
            
            **Integrantes del Equipo:**
            
            - Alejandro Batres
            - David Ostiz
            - Francisco Javier Barrionuevo
            - Gabriel Chamorro
            - Jose Javier Martínez
            
            ---
            
            *Sistema de Predicción de Cancelaciones*  
            *Palladium Hotel Group - 2026*
            """)
    
    # -------------------------------------------------------------------------
    # PIE DE PAGINA
    # -------------------------------------------------------------------------
    st.markdown("---")
    pie_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "media", "general", "Pie.png"
    )
    if os.path.exists(pie_path):
        st.image(pie_path, use_container_width=True)


# -----------------------------------------------------------------------------
# PUNTO DE ENTRADA
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()

