# -*- coding: utf-8 -*-
"""
Módulo de Predicción de Cancelaciones
Integra el modelo LightGBM entrenado para predecir probabilidad de cancelación.
"""

# IMPORTANTE: Configurar DYLD_LIBRARY_PATH ANTES de cualquier import
# para que LightGBM encuentre libomp.dylib
import os
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/lib:/opt/homebrew/opt/libomp/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')

import sys
import pandas as pd
import numpy as np
from datetime import datetime, date
import joblib

# Añadir path al módulo de funciones de producción
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(current_dir), "04_models")
sys.path.insert(0, models_dir)

# Importar funciones de feature engineering
# Usar nuestra versión local con corrección de categorías en inferencia
# from funcion_producion import get_features 
from feature_eng import get_features

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

MODEL_PATH = os.path.join(models_dir, "lightgbm_FINAL20260206_142533", "lightgbm.joblib")

# Variables que usa el modelo (sin CANCELADO que es el target)
VARIABLES_MODELO = [
    "FUENTE_NEGOCIO_SEGMENTO_CLIENTE",
    "PAIS_TOP_200",
    "LEAD_TIME",
    "PALLADIUM_REWARDS",
    "COMPLEJO_RESERVA",
    "ADR",
    "HORA_TOMA_COS",
    "MES_LLEGADA_SIN",
    "TIPO_VIAJERO",
    "REV_PAX",
    "ES_GRUPO",
    "TIENE_FIDELIDAD",
    "MES_LLEGADA_COS",
    "HOTEL_HABITACION_TOP",
    "NOCHES",
    "ADULTOS",
    "HORA_TOMA_SIN"
]

# Mapeo de NOMBRE_HOTEL de la app al formato del modelo
MAPEO_HOTEL = {
    # Costa Mujeres -> Complejo Costa Mujeres
    "Grand Palladium Select Costa Mujeres": "Complejo Costa Mujeres",
    "Family Selection Costa Mujeres": "Complejo Costa Mujeres",
    "TRS Coral Hotel": "Complejo Costa Mujeres",
    
    # Riviera Maya -> Complejo Riviera Maya
    "Grand Palladium Colonial Resort & Spa": "Complejo Riviera Maya",
    "Grand Palladium Kantenah Resort & Spa": "Complejo Riviera Maya",
    "Grand Palladium Select White Sand": "Complejo Riviera Maya",
    "TRS Yucatan Hotel": "Complejo Riviera Maya",
    
    # Punta Cana -> Complejo Punta Cana
    "Grand Palladium Select Bavaro": "Complejo Punta Cana",
    "Grand Palladium Palace Resort & Spa": "Complejo Punta Cana",
    "Grand Palladium Punta Cana Resort & Spa": "Complejo Punta Cana",
    "TRS Turquesa Hotel": "Complejo Punta Cana",
}

# Valores por defecto para campos que no tenemos en la web
# IMPORTANTE: Usar los valores EXACTOS con los que fue entrenado el modelo
DEFAULTS = {
    "CLIENTE": "ROIBACK (GLOBAL OBI S.L.)",  # Reservas web siempre son ROIBACK
    "CLIENTE_DE": "ROIBACK (GLOBAL OBI S.L.) - DE",  # Si el país es Alemania
    "SEGMENTO": "Loyalty",  # Programa de fidelización web
    "FUENTE_NEGOCIO": "DIRECT SALES",  # Venta directa desde web
    "ID_MULTIPLE": 0,  # Nunca es grupo desde la web
}

# =============================================================================
# CARGA DEL MODELO
# =============================================================================

_modelo = None

def cargar_modelo():
    """Carga el modelo de LightGBM desde disco (lazy loading)."""
    global _modelo
    if _modelo is None:
        try:
            _modelo = joblib.load(MODEL_PATH)
            print(f"[PREDICTOR] Modelo cargado desde: {MODEL_PATH}")
        except Exception as e:
            print(f"[PREDICTOR] Error cargando modelo: {e}")
            _modelo = None
    return _modelo


# =============================================================================
# FUNCIÓN PRINCIPAL DE PREDICCIÓN
# =============================================================================

def predecir_cancelacion(
    fecha_llegada: date,
    noches: int,
    adultos: int,
    ninos: int,
    pais: str,
    es_rewards: bool,
    nombre_hotel: str,
    nombre_habitacion: str,
    valor_reserva: float,
    fecha_toma: datetime = None,
    incluir_explicacion: bool = False
) -> dict:
    """
    Predice la probabilidad de cancelación para una reserva.
    
    Args:
        fecha_llegada: Fecha de check-in
        noches: Número de noches
        adultos: Número de adultos
        ninos: Número de niños
        pais: País del cliente (ej: 'ESPAÑA', 'ALEMANIA')
        es_rewards: Si es cliente Palladium Rewards
        nombre_hotel: Nombre del hotel (de la app)
        nombre_habitacion: Nombre de la habitación (de la app)
        valor_reserva: Precio total de la reserva
        fecha_toma: Fecha/hora de la reserva (default: ahora)
        incluir_explicacion: Si True, incluye contribución de cada variable
        
    Returns:
        dict con:
            - probabilidad: float (0-1)
            - riesgo: str ('bajo', 'medio', 'alto')
            - success: bool
            - error: str (si hubo error)
            - explicacion: dict (si incluir_explicacion=True)
    """
    try:
        # 1. Cargar modelo
        modelo = cargar_modelo()
        if modelo is None:
            return {
                "probabilidad": None,
                "riesgo": "desconocido",
                "success": False,
                "error": "Modelo no disponible"
            }
        
        # 2. Preparar datos de entrada
        if fecha_toma is None:
            fecha_toma = datetime.now()
        
        # Convertir fecha_llegada a string si es date
        if isinstance(fecha_llegada, date) and not isinstance(fecha_llegada, datetime):
            llegada_str = fecha_llegada.strftime("%Y-%m-%d")
        else:
            llegada_str = str(fecha_llegada)
        
        # Convertir fecha_toma a string
        if isinstance(fecha_toma, datetime):
            fecha_toma_str = fecha_toma.strftime("%Y-%m-%d %H:%M:%S")
        else:
            fecha_toma_str = str(fecha_toma)
        
        # PAX total
        pax = adultos + ninos
        
        # Cliente según país
        cliente = DEFAULTS["CLIENTE_DE"] if pais.upper() in ["ALEMANIA", "GERMANY"] else DEFAULTS["CLIENTE"]
        
        # Fidelidad
        fidelidad = "Palladium Rewards" if es_rewards else None
        
        # Mapear nombre del hotel al formato del modelo
        hotel_modelo = MAPEO_HOTEL.get(nombre_hotel, "Complejo Riviera Maya")
        
        # df_features = get_features(...) se encarga de imprimir los inputs si hace falta, o podemos comentarlo
        # Dejamos estos prints comentados para produccion
        # print(f"\n[DEBUG PREDICTOR] Valores de entrada: ...")
        
        df_features = get_features(
            LLEGADA=llegada_str,
            NOCHES=noches,
            PAX=pax,
            ADULTOS=adultos,
            CLIENTE=cliente,
            FECHA_TOMA=fecha_toma_str,
            FIDELIDAD=fidelidad,
            PAIS=pais.upper(),
            SEGMENTO=DEFAULTS["SEGMENTO"],
            FUENTE_NEGOCIO=DEFAULTS["FUENTE_NEGOCIO"],
            NOMBRE_HOTEL=hotel_modelo,
            NOMBRE_HABITACION=nombre_habitacion,
            VALOR_RESERVA=valor_reserva
        )
        
        # 4. Seleccionar solo las variables que usa el modelo
        X = df_features[VARIABLES_MODELO].copy()
        
        # Guardar valores originales ANTES de convertir para explicación
        valores_originales = {}
        for col in VARIABLES_MODELO:
            val = df_features[col].iloc[0]
            valores_originales[col] = val
        
        # -------------------------------------------------------------------------
        # Conversión de Tipos (Según Dossier)
        # -------------------------------------------------------------------------
        
        # 1. Asegurar numéricos (float/int)
        cols_numericas = ["LEAD_TIME", "ADR", "HORA_TOMA_COS", "MES_LLEGADA_SIN", 
                          "REV_PAX", "ES_GRUPO", "TIENE_FIDELIDAD", "MES_LLEGADA_COS", 
                          "NOCHES", "ADULTOS", "HORA_TOMA_SIN"]
        for col in cols_numericas:
            if col in X.columns:
                X[col] = pd.to_numeric(X[col], errors='coerce')

        # 2. Conversión EXPLÍCITA de Categóricas (Punto Crítico del Dossier)
        categorical_cols = [
            'FUENTE_NEGOCIO_SEGMENTO_CLIENTE',
            'PAIS_TOP_200',
            'COMPLEJO_RESERVA',
            'TIPO_VIAJERO',
            'HOTEL_HABITACION_TOP'
        ]

        for col in categorical_cols:
            if col in X.columns:
                # Convertir a 'category' explícitamente
                X[col] = X[col].astype('category')
        
        # Limpieza adicional: asegurar que no quedan objects sueltos que el modelo no espere
        # (Aunque según el dossier, solo esas 5 son críticas)
            
        print("\n[DEBUG PREDICTOR] Dtypes finales antes de predict:")
        print(X.dtypes)
        print("\n[DEBUG PREDICTOR] Muestra de datos (primera fila):")
        print(X.iloc[0])
        print(f"[DEBUG] HABITACION_TOP: {X['HOTEL_HABITACION_TOP'].iloc[0]}")
        print(f"[DEBUG] PAIS_TOP: {X['PAIS_TOP_200'].iloc[0]}")

        # 5. Predecir
        prob = modelo.predict_proba(X)[0][1]  # Probabilidad de clase 1 (cancelación)
        
        # 6. Clasificar riesgo
        if prob < 0.3:
            riesgo = "bajo"
        elif prob < 0.6:
            riesgo = "medio"
        else:
            riesgo = "alto"
        
        resultado = {
            "probabilidad": round(prob, 4),
            "riesgo": riesgo,
            "success": True,
            "error": None
        }
        
        # 7. Incluir explicación si se solicita
        if incluir_explicacion:
            # Obtener importancia de features del modelo
            try:
                importancias = modelo.feature_importances_
                feature_names = modelo.feature_name_ if hasattr(modelo, 'feature_name_') else VARIABLES_MODELO
                
                # Crear diccionario de importancia
                imp_dict = {}
                for i, var in enumerate(VARIABLES_MODELO):
                    if i < len(importancias):
                        imp_dict[var] = {
                            "importancia": float(importancias[i]),
                            "valor": valores_originales.get(var, "N/A")
                        }
                
                # Ordenar por importancia
                imp_ordenado = dict(sorted(imp_dict.items(), key=lambda x: x[1]["importancia"], reverse=True))
                
                resultado["explicacion"] = imp_ordenado
                resultado["feature_values"] = valores_originales
                
            except Exception as e:
                resultado["explicacion"] = {}
                resultado["explicacion_error"] = str(e)
        
        return resultado
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "probabilidad": None,
            "riesgo": "desconocido",
            "success": False,
            "error": str(e)
        }


# =============================================================================
# FUNCIÓN PARA EXPLICAR UNA RESERVA EXISTENTE
# =============================================================================

def explicar_reserva(reserva_dict: dict) -> dict:
    """
    Genera explicación detallada para una reserva ya existente.
    
    Args:
        reserva_dict: Diccionario con datos de la reserva del CSV
        
    Returns:
        dict con predicción y explicación
    """
    from datetime import datetime, timedelta
    
    # print(f"[DEBUG EXPLICAR] Analizando reserva. Keys: {list(reserva_dict.keys())}")
    
    try:
        # Normalizar claves a mayúsculas para evitar problemas
        r = {k.upper(): v for k, v in reserva_dict.items()}
        
        # Extraer datos del diccionario
        fecha_llegada = r.get("LLEGADA", datetime.now().date())
        if isinstance(fecha_llegada, str):
            try:
                fecha_llegada = datetime.strptime(fecha_llegada, "%Y-%m-%d").date()
            except:
                fecha_llegada = datetime.strptime(fecha_llegada, "%Y-%m-%d %H:%M:%S").date()
        
        # Calcular fecha toma de forma robusta
        fecha_toma = None
        fecha_toma_val = r.get("FECHA_TOMA") or r.get("FECHA_CREACION")
        
        if fecha_toma_val:
            if isinstance(fecha_toma_val, (datetime, date)):
                fecha_toma = fecha_toma_val
            else:
                try:
                     fecha_toma = datetime.strptime(str(fecha_toma_val), "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        fecha_toma = datetime.strptime(str(fecha_toma_val), "%Y-%m-%d")
                    except:
                        pass
                        
        # Si sigue siendo None, intentar con LEAD_TIME
        if fecha_toma is None:
             lead_val = r.get("LEAD_TIME")
             if lead_val is not None:
                 try:
                     lead_days = int(lead_val)
                     # Reconstruir fecha toma
                     # Asumimos hora 12:00 por defecto si reconstruimos
                     base_date = datetime.combine(fecha_llegada, datetime.min.time()) + timedelta(hours=12)
                     fecha_toma = base_date - timedelta(days=lead_days)
                 except:
                     pass
        
        # Fallback final: 30 días antes
        if fecha_toma is None:
            dt_llegada = datetime.combine(fecha_llegada, datetime.min.time())
            fecha_toma = dt_llegada - timedelta(days=30)
            
        # Asegurar que sea datetime
        if isinstance(fecha_toma, date) and not isinstance(fecha_toma, datetime):
            fecha_toma = datetime.combine(fecha_toma, datetime.min.time())
            
        # IMPORTANTE: Truncar minutos y segundos como pide el usuario
        fecha_toma = fecha_toma.replace(minute=0, second=0, microsecond=0)
        
        # Calcular noches
        fecha_salida = r.get("SALIDA", fecha_llegada)
        if isinstance(fecha_salida, str):
            fecha_salida = datetime.strptime(fecha_salida, "%Y-%m-%d").date()
        noches = (fecha_salida - fecha_llegada).days if fecha_salida and fecha_llegada else 7
        
        return predecir_cancelacion(
            fecha_llegada=fecha_llegada,
            noches=noches,
            adultos=int(reserva_dict.get("ADULTOS", 2)),
            ninos=int(reserva_dict.get("PAX", 2)) - int(reserva_dict.get("ADULTOS", 2)),
            pais=reserva_dict.get("PAIS_TOP", "ESPAÑA"),
            es_rewards=bool(reserva_dict.get("TIENE_REWARDS", 0)),
            nombre_hotel=reserva_dict.get("NOMBRE_HOTEL", "Grand Palladium Colonial Resort & Spa"),
            nombre_habitacion=reserva_dict.get("NOMBRE_HABITACION", "COL JUNIOR SUITE GV"),
            valor_reserva=float(reserva_dict.get("VALOR_RESERVA", 1000)),
            fecha_toma=fecha_toma,
            incluir_explicacion=True
        )
    except Exception as e:
        return {
            "probabilidad": None,
            "riesgo": "desconocido",
            "success": False,
            "error": str(e)
        }


# =============================================================================
# FUNCIÓN PARA PREDICCIÓN EN LOTE (INTRANET)
# =============================================================================

def predecir_lote(df_reservas: pd.DataFrame) -> pd.DataFrame:
    """
    Predice probabilidad de cancelación para un DataFrame de reservas.
    
    Args:
        df_reservas: DataFrame con columnas: LLEGADA, NOCHES, PAX, ADULTOS, etc.
        
    Returns:
        DataFrame original con columna PROB_CANCELACION añadida
    """
    modelo = cargar_modelo()
    if modelo is None:
        df_reservas["PROB_CANCELACION"] = 0.5  # Default si no hay modelo
        return df_reservas
    
    # TODO: Implementar predicción en lote
    # Por ahora, usar el valor existente o 0.5
    if "PROB_CANCELACION" not in df_reservas.columns:
        df_reservas["PROB_CANCELACION"] = 0.5
    
    return df_reservas


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test de la función
    resultado = predecir_cancelacion(
        fecha_llegada=date(2026, 6, 15),
        noches=7,
        adultos=2,
        ninos=0,
        pais="ESPAÑA",
        es_rewards=False,
        nombre_hotel="Grand Palladium Colonial Resort & Spa",
        nombre_habitacion="COL JUNIOR SUITE GV",
        valor_reserva=4500.0
    )
    
    print("\n=== TEST DE PREDICCIÓN ===")
    print(f"Probabilidad de cancelación: {resultado['probabilidad']}")
    print(f"Nivel de riesgo: {resultado['riesgo']}")
    print(f"Success: {resultado['success']}")
    if resultado['error']:
        print(f"Error: {resultado['error']}")
