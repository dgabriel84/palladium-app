import pandas as pd
import numpy as np
import sys
import os
import random
from datetime import timedelta, date

# Añadir ruta local para importar precios_data
sys.path.append(os.getcwd())
try:
    from precios_data import PRECIOS_ADR
except ImportError:
    print("Error importando precios_data.py. Asegurate de estar en 03_app")
    PRECIOS_ADR = {}

def generar_reservas_2026():
    print("Cargando dataset histórico...")
    # Ruta relativa desde 03_app
    csv_path = "../01_data/processed/df_unificado_completo_v8.csv"
    
    if not os.path.exists(csv_path):
        # Intento ruta absoluta fallback si falla relativa
        csv_path = "/Users/gabi/Library/CloudStorage/GoogleDrive-dgabriel84@gmail.com/.shortcut-targets-by-id/1MHQ8E-8B1PFz3EgbmBRY7WLo5AhTV1mF/TFM_Palladium_Team/01_data/processed/df_unificado_completo_v8.csv"
        if not os.path.exists(csv_path):
            print(f"Error: No se encuentra {csv_path}")
            return

    # Leer solo columnas necesarias para acelerar o todo
    df = pd.read_csv(csv_path)
    
    # Convertir fechas
    for col in ['LLEGADA', 'SALIDA', 'FECHA_TOMA', 'FECHA_MOD', 'FECHA_CANCELACION']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Filtrar año base 2023
    df_base = df[df['LLEGADA'].dt.year == 2023].copy()
    print(f"Registros base 2023: {len(df_base)}")
    
    if len(df_base) == 0:
        df_base = df[df['LLEGADA'].dt.year == 2022].copy()
        print(f"Usando fallback 2022. Registros: {len(df_base)}")

    # Desplazamiento a 2026
    start_base = date(df_base['LLEGADA'].dt.year.iloc[0], 1, 1)
    target_date = date(2026, 1, 1)
    days_shift = (target_date - start_base).days
    
    print(f"Desplazando fechas {days_shift} días...")
    
    time_cols = ['LLEGADA', 'SALIDA', 'FECHA_TOMA', 'FECHA_MOD']
    for col in time_cols:
        if col in df_base.columns:
            df_base[col] = df_base[col] + pd.to_timedelta(days_shift, unit='D')
            
    if 'FECHA_CANCELACION' in df_base.columns:
        mask = df_base['FECHA_CANCELACION'].notna()
        df_base.loc[mask, 'FECHA_CANCELACION'] = df_base.loc[mask, 'FECHA_CANCELACION'] + pd.to_timedelta(days_shift, unit='D')

    # Generar Overbooking (Duplicar 15% en picos)
    print("Generando overbooking...")
    mask_peaks = (
        (df_base['LLEGADA'].dt.month.isin([7, 8])) |  # Verano
        (df_base['LLEGADA'].dt.month == 12) |         # Navidad
        (df_base['LLEGADA'].dt.month == 4)            # Semana Santa
    )
    
    if mask_peaks.any():
        df_over = df_base[mask_peaks].sample(frac=0.15, random_state=42).copy()
        # Modificar ID para uniqueness
        # Si ID es numerico
        try:
            df_over['ID_RESERVA'] = df_over['ID_RESERVA'].astype(int) + 900000000
        except:
            df_over['ID_RESERVA'] = df_over['ID_RESERVA'].astype(str) + "_OV"
            
        df_final = pd.concat([df_base, df_over], ignore_index=True)
    else:
        df_final = df_base

    print(f"Total registros finales: {len(df_final)}")

    # Actualizar Precios
    print("Actualizando precios 2026...")
    
    # Cachear precios para agilizar
    # Dict: (Hotel, Hab, Pax, Mes) -> Precio
    price_cache = {}
    
    def get_price(hotel, hab, pax, mes_str):
        key = (hotel, hab, pax, mes_str)
        if key in price_cache: return price_cache[key]
        
        try:
            val = PRECIOS_ADR[hotel][hab][pax][mes_str]
            price_cache[key] = val
            return val
        except:
            price_cache[key] = None
            return None

    # Vectorizar o loop optimizado?
    # Loop es lento para 100k+ registros. 
    # Pero las logicas son complejas. Haremos un apply simple
    
    # Pre-calcular mapeo de columnas para velocidad
    # Necesitamos HOTEL_COMPLEJO, NOMBRE_HABITACION, PAX, NOCHES, LLEGADA
    
    vals_reserva = []
    
    # Iterar tuplas es mas rapido que apply
    for row in df_final.itertuples():
        hotel = getattr(row, 'HOTEL_COMPLEJO', None)
        hab = getattr(row, 'NOMBRE_HABITACION', None)
        pax = str(int(getattr(row, 'PAX', 2)))
        noches = int(getattr(row, 'NOCHES', 1))
        llegada = getattr(row, 'LLEGADA')
        valor_original = getattr(row, 'VALOR_RESERVA', 0)
        
        nuevo_valor = 0
        encontrado = False
        
        if hotel and hab:
            # Intentar calcular
            temp_valor = 0
            dias_encontrados = 0
            
            for i in range(noches):
                dia = llegada + timedelta(days=i)
                mes = dia.strftime("%Y-%m")
                p = get_price(hotel, hab, pax, mes)
                if p is None:
                    # Fallback PAX=2
                    p = get_price(hotel, hab, "2", mes)
                
                if p is not None:
                    temp_valor += p
                    dias_encontrados += 1
            
            if dias_encontrados > 0:
                # Extrapolar si faltaron dias
                nuevo_valor = (temp_valor / dias_encontrados) * noches
                encontrado = True
        
        if not encontrado:
            nuevo_valor = valor_original * 1.15 # Inflacion simple 15%
            
        vals_reserva.append(nuevo_valor)
        
    df_final['VALOR_RESERVA'] = vals_reserva
    df_final['ADR'] = df_final['VALOR_RESERVA'] / df_final['NOCHES'].replace(0, 1)
    
    # Guardar
    out_path = "reservas_sinteticas_2026.csv"
    df_final.to_csv(out_path, index=False)
    print(f"Generado {out_path}")

if __name__ == "__main__":
    generar_reservas_2026()
