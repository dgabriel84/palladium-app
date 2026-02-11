# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# Lista fija de habitaciones TOP basada en datos de entrenamiento (>0.3% frecuencia)
# Esta lista es necesaria para la lógica de negocio de 'HABITACION_TOP'
TOP_HABITACIONES_LIST = [
    'CMU JUNIOR SUITE GV', 'CMU JUNIOR SUITE PS', 'BAV SUPERIOR JS GV', 'COL DELUXE GARDEN VIEW', 
    'TRS JUNIOR SUITE GV', 'PC DELUXE GARDEN VIEW', 'TRS JUNIOR SUITE PS', 'WS JUNIOR SUITE GV', 
    'TRSC JUNIOR SUITE GV', 'PC DELUXE POOLSIDE', 'KAN DELUXE GARDEN VIEW', 'TRS JUNIOR SUITE GV/PV', 
    'PC JUNIOR SUITE GV', 'BAV JUNIOR SUITE GV', 'TRS JS JACUZZI TERR PS', 'CMU FS JUNIOR SUITE BS', 
    'PC JUNIOR SUITE POOLSIDE', 'PAL JUNIOR SUITE GV', 'COL JUNIOR SUITE GV', 'BAV PREMIUM JS GV', 
    'WS JUNIOR SUITE BS', 'KAN JUNIOR SUITE GV', 'PAL DELUXE GARDEN VIEW', 'PAL DELUXE BEACHSIDE', 
    'TRSC JUNIOR SUITE SW', 'TRS JUNIOR SUITE PP GV', 'TRS JUNIOR SUITE SW', 'BAV ROOFTOP JT JS', 
    'TRS JUNIOR SUITE SWIM UP', 'COL JUNIOR SUITE PS', 'TRS JUNIOR SUITE PP PS', 'TRS JUNIOR SUITE PS OV', 
    'PAL LOFT SUITE GV', 'PAL JUNIOR SUITE SW BS', 'TRSC JUNIOR SUITE OV', 'BAV ROMANCE SUITE GV', 
    'CMU LOFT SUITE JT', 'TRSC LOFT SUITE JT', 'TRSC JUNIOR SUITE BS OV', 'TRS JUNIOR SUITE OV', 
    'TRS LOFT SUITE JT', 'CMU JUNIOR SUITE PS OV', 'TRS ROMANCE BW BYTHE LAKE', 'PC LOFT SUITE GV', 
    'TRS JUNIOR SUITE BS OV', 'WS SUITE GARDEN VIEW', 'COL ROMANCE VILLA SUI PS', 'TRSC LOFT SUITE JT OV', 
    'PAL JUNIOR SUITE BS', 'TRS ROMANCE SUITE PS', 'TRS LOFT SUITE JT OV', 'KAN ROMANCE VILLA SUI BS', 
    'PAL JUNIOR SUITE BS OV', 'PAL LOFT SUITE BS POV', 'TRS ST JACUZZI TERR PS', 'CMU FS JUNIOR SUI BS POV', 
    'TRSC JUNIOR SUITE BS'
]

def get_features(LLEGADA, NOCHES, PAX, ADULTOS, CLIENTE, FECHA_TOMA, FIDELIDAD, PAIS, SEGMENTO, FUENTE_NEGOCIO, NOMBRE_HOTEL, NOMBRE_HABITACION, VALOR_RESERVA):
    
    # 1. Crear DataFrame inicial con datos crudos
    data = {
        'LLEGADA': [LLEGADA],
        'NOCHES': [NOCHES],
        'PAX': [PAX],
        'ADULTOS': [ADULTOS],
        'CLIENTE': [CLIENTE],
        'ID_MULTIPLE': 0, # Asumimos reserva individual por defecto para la web
        'FECHA_TOMA': [FECHA_TOMA],
        'FIDELIDAD': [FIDELIDAD],
        'PAIS': [PAIS],
        'SEGMENTO': [SEGMENTO],
        'FUENTE_NEGOCIO': [FUENTE_NEGOCIO],
        'NOMBRE_HOTEL': [NOMBRE_HOTEL],
        'NOMBRE_HABITACION': [NOMBRE_HABITACION],
        'VALOR_RESERVA': [VALOR_RESERVA]
    }
    df = pd.DataFrame(data)

    # 2. Conversión de Tipos
    # Aseguramos datetime
    df['LLEGADA'] = pd.to_datetime(df['LLEGADA'])
    df['FECHA_TOMA'] = pd.to_datetime(df['FECHA_TOMA'])
    # Manejo de None/NaN en Fidelidad explícito como en el dossier
    df['FIDELIDAD'] = df['FIDELIDAD'].replace({None: np.nan})

    # 3. Generación de Variables (Feature Engineering)
    
    # Ratios Económicos
    df['ADR'] = df['VALOR_RESERVA'] / df['NOCHES']
    df['REV_PAX'] = df['VALOR_RESERVA'] / df['PAX']
    
    # Tiempos (Lead Time)
    # Días entre reserva y llegada (normalizando a medianoche para evitar decimales por horas)
    df['LEAD_TIME'] = (df['LLEGADA'].dt.normalize() - df['FECHA_TOMA'].dt.normalize()).dt.days
    
    # Variables Cíclicas (Hora de Toma)
    df['HORA_TOMA'] = df['FECHA_TOMA'].dt.hour
    df['HORA_TOMA_SIN'] = np.sin(2 * np.pi * df['HORA_TOMA'] / 24)
    df['HORA_TOMA_COS'] = np.cos(2 * np.pi * df['HORA_TOMA'] / 24)
    
    # Variables Cíclicas (Mes de Llegada)
    df['MES_LLEGADA'] = df['LLEGADA'].dt.month
    df['MES_LLEGADA_SIN'] = np.sin(2 * np.pi * df['MES_LLEGADA'] / 12)
    df['MES_LLEGADA_COS'] = np.cos(2 * np.pi * df['MES_LLEGADA'] / 12)
    
    # Lógica de Negocio Específica
    
    # PAIS_TOP_200 (Copia directa, el modelo maneja la cardinalidad internamente o espera paises raw)
    df['PAIS_TOP_200'] = df['PAIS'] 
    
    # TIPO_VIAJERO
    condiciones_pax = [
        (df['PAX'] == 1),
        (df['PAX'] == 2),
        (df['PAX'] >= 3)
    ]
    etiquetas_pax = ['Single', 'Parejas', 'Familias']
    df['TIPO_VIAJERO'] = np.select(condiciones_pax, etiquetas_pax, default='Otro')
    
    # Fidelidad
    df['TIENE_FIDELIDAD'] = np.where(df['FIDELIDAD'].isna(), 0, 1)
    df['PALLADIUM_REWARDS'] = np.where(df['FIDELIDAD'] == 'Palladium Rewards', 1, 0)
    
    # Grupos (ID_MULTIPLE 0 -> No es grupo)
    df['ES_GRUPO'] = np.where(df['ID_MULTIPLE'] != 0, 1, 0)
    
    # Cadenas Compuestas (Manejo de strings complejos para Hotel/Habitación)
    
    # NOMBRE_COMPLEJO
    condiciones_hotel = [
        df['NOMBRE_HOTEL'] == 'Complejo Riviera Maya',
        df['NOMBRE_HOTEL'] == 'Complejo Punta Cana',
        df['NOMBRE_HOTEL'] == 'Complejo Costa Mujeres'
    ]
    df['NOMBRE_COMPLEJO'] = np.select(condiciones_hotel, ['MAYA', 'CANA', 'MUJE'], default='OTRO')
    
    # PREFIJO_HAB: Extraer primera palabra, con excepción de 'CMU FS'
    df['PREFIJO_HAB'] = [x.split(' ')[0] for x in df['NOMBRE_HABITACION']]
    filtro_cmu_fs = df['NOMBRE_HABITACION'].str.startswith('CMU FS')
    df.loc[filtro_cmu_fs, 'PREFIJO_HAB'] = 'CMU FS'
    
    # HOTEL_COMPLEJO
    condiciones_complejo = [
      (df['NOMBRE_HOTEL'] == 'Complejo Riviera Maya') & (df['PREFIJO_HAB'].str.startswith('COL')),
      (df['NOMBRE_HOTEL'] == 'Complejo Riviera Maya') & (df['PREFIJO_HAB'].str.startswith('KAN')),
      (df['NOMBRE_HOTEL'] == 'Complejo Riviera Maya') & (df['PREFIJO_HAB'].str.startswith('TRS')),
      (df['NOMBRE_HOTEL'] == 'Complejo Riviera Maya') & (df['PREFIJO_HAB'].str.startswith('WS')),
      (df['NOMBRE_HOTEL'] == 'Complejo Punta Cana') & (df['PREFIJO_HAB'].str.startswith('BAV')),
      (df['NOMBRE_HOTEL'] == 'Complejo Punta Cana') & (df['PREFIJO_HAB'].str.startswith('PAL')),
      (df['NOMBRE_HOTEL'] == 'Complejo Punta Cana') & (df['PREFIJO_HAB'].str.startswith('PC')),
      (df['NOMBRE_HOTEL'] == 'Complejo Punta Cana') & (df['PREFIJO_HAB'].str.startswith('TRS')),
      (df['NOMBRE_HOTEL'] == 'Complejo Costa Mujeres') & (df['PREFIJO_HAB'].str.startswith('CMU FS')),
      (df['NOMBRE_HOTEL'] == 'Complejo Costa Mujeres') & (df['PREFIJO_HAB'].str.startswith('CMU')),
      (df['NOMBRE_HOTEL'] == 'Complejo Costa Mujeres') & (df['PREFIJO_HAB'].str.startswith('TRSC')),
      (df['NOMBRE_HOTEL'] == 'Complejo Costa Mujeres') & (df['PREFIJO_HAB'].str.startswith('TRS'))
    ]
    opciones_complejo = [
      'MAYA_COL', 'MAYA_KAN', 'MAYA_TRS', 'MAYA_WS',
      'CANA_BAV', 'CANA_PAL', 'CANA_PC', 'CANA_TRS',
      'MUJE_CMU_FS', 'MUJE_CMU', 'MUJE_TRSC', 'MUJE_TRS'
    ]
    df['HOTEL_COMPLEJO'] = np.select(condiciones_complejo, opciones_complejo, default='OTRO')
    
    # Lógica de Frecuencia para HABITACION_TOP (Vital para inferencia de 1 fila)
    # Si la habitación no está en la lista TOP, se marca como 'OTROS'
    df['HABITACION_TOP'] = df['NOMBRE_HABITACION'].apply(lambda x: x if x in TOP_HABITACIONES_LIST else 'OTROS')

    # Variables Concatenadas (Interacciones)
    # Estas son críticas porque el modelo aprendió comportamientos específicos de estas combinaciones
    df['COMPLEJO_RESERVA'] = df['HOTEL_COMPLEJO'] + ' - ' + df['NOMBRE_HABITACION']
    
    # HOTEL_HABITACION_TOP: Usa la versión filtrada (HABITACION_TOP) + HOTEL_COMPLEJO
    df['HOTEL_HABITACION_TOP'] = df['HOTEL_COMPLEJO'] + ' - ' + df['HABITACION_TOP']
    
    df['FUENTE_NEGOCIO_SEGMENTO_CLIENTE'] = df['FUENTE_NEGOCIO'] + '_' + df['SEGMENTO'] + '_' + df['CLIENTE']

    return df
