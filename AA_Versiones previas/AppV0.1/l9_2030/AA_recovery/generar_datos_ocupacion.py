import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import os

# Definición de Hoteles y Capacidades
HOTELES_DATA = [
    {"Complejo": "COSTA MUJERES", "Hotel": "Grand Palladium Costa Mujeres Resort & Spa", "Capacidad": 670},
    {"Complejo": "COSTA MUJERES", "Hotel": "TRS Coral Hotel", "Capacidad": 469},
    {"Complejo": "RIVIERA MAYA", "Hotel": "Grand Palladium Kantenah", "Capacidad": 422},
    {"Complejo": "RIVIERA MAYA", "Hotel": "Grand Palladium Colonial", "Capacidad": 413},
    {"Complejo": "RIVIERA MAYA", "Hotel": "Grand Palladium White Sand", "Capacidad": 264},
    {"Complejo": "RIVIERA MAYA", "Hotel": "TRS Yucatan Hotel", "Capacidad": 454},
    {"Complejo": "PUNTA CANA", "Hotel": "Grand Palladium Bávaro", "Capacidad": 672},
    {"Complejo": "PUNTA CANA", "Hotel": "Grand Palladium Punta Cana", "Capacidad": 535},
    {"Complejo": "PUNTA CANA", "Hotel": "Grand Palladium Palace", "Capacidad": 366},
    {"Complejo": "PUNTA CANA", "Hotel": "TRS Turquesa Hotel", "Capacidad": 372},
    {"Complejo": "PUNTA CANA", "Hotel": "TRS Cap Cana Waterfront*", "Capacidad": 115}
]

def generar_datos_ocupacion_2026():
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    delta = end_date - start_date
    dias_totales = delta.days + 1
    
    registros = []
    
    for i in range(dias_totales):
        fecha_actual = start_date + timedelta(days=i)
        mes = fecha_actual.month
        dia_semana = fecha_actual.weekday() # 0=Lunes, 6=Domingo
        
        # Factor Estacionalidad (Simplificado)
        # Alta: Enero, Febrero, Semana Santa (Aprox Abril), Julio, Agosto, Diciembre
        factor_estacionalidad = 0.6  # Base baja temporada
        
        if mes in [1, 2, 3, 12]: # Invierno alto
            factor_estacionalidad = 0.85
        elif mes in [7, 8]: # Verano alto
            factor_estacionalidad = 0.95
        elif mes == 4: # Abril (Semana Santa aprox)
            factor_estacionalidad = 0.80
        
        # Picos aleatorios (Eventos, Grupos)
        if random.random() < 0.1: 
            factor_estacionalidad += 0.15
            
        for hotel in HOTELES_DATA:
            capacidad = hotel["Capacidad"]
            
            # Ocupacion Base
            ocupacion_pct = factor_estacionalidad + random.uniform(-0.05, 0.05)
            
            # Fin de semana sube un poco
            if dia_semana >= 5:
                ocupacion_pct += 0.05
                
            # Forzar Overbooking en temporada muy alta
            if mes in [8, 12] and random.random() > 0.3:
                ocupacion_pct = random.uniform(1.01, 1.10) # Overbooking 1-10%
            
            # Calcular habitaciones ocupadas (Bruto)
            habitaciones_ocupadas = int(capacidad * ocupacion_pct)
            
            # Prediccion de Cancelación Promedio para ese día/hotel
            # En temporada alta cancelan menos (gente comprometida), en baja más.
            # Rango 10% - 30%
            pct_cancelacion_predicha = random.uniform(0.10, 0.30)
            if ocupacion_pct > 0.9: # Si hay mucha demanda, cancelan menos
                pct_cancelacion_predicha = random.uniform(0.05, 0.15)
                
            registros.append({
                "fecha": fecha_actual,
                "complejo": hotel["Complejo"],
                "hotel": hotel["Hotel"],
                "capacidad_total": capacidad,
                "habitaciones_ocupadas": habitaciones_ocupadas,
                "ocupacion_pct_bruta": round(ocupacion_pct, 2),
                "tasa_cancelacion_predicha": round(pct_cancelacion_predicha, 2)
            })
            
    df = pd.DataFrame(registros)
    
    # Guardar en local
    output_path = "ocupacion_2026.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset generado: {output_path} con {len(df)} registros.")
    return df

if __name__ == "__main__":
    generar_datos_ocupacion_2026()
