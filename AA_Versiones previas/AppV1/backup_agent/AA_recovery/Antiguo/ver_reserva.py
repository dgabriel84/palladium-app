#!/usr/bin/env python3
"""Script para ver los datos de una reserva."""
import pandas as pd
import os

# Cargar CSV local
csv_path = os.path.join(os.path.dirname(__file__), 'reservas_2026.csv')
df = pd.read_csv(csv_path)

# Buscar reserva
id_reserva = '6419831096601'
reserva = df[df['ID_RESERVA'].astype(str) == id_reserva]

if not reserva.empty:
    print(f"\n=== DATOS DE LA RESERVA {id_reserva} ===\n")
    
    # Columnas relevantes para el modelo
    cols_importantes = [
        'ID_RESERVA', 'LLEGADA', 'NOCHES', 'PAX', 'ADULTOS',
        'CANAL_CONSOLIDADO', 'FECHA_TOMA', 'TIENE_FIDELIDAD', 'PAIS_TOP',
        'TARIFA', 'NOMBRE_HOTEL', 
        'NOMBRE_HABITACION', 'VALOR_RESERVA', 'LEAD_TIME', 'ADR'
    ]
    
    for col in cols_importantes:
        if col in reserva.columns:
            valor = reserva[col].values[0]
            print(f"{col:25s}: {valor}")
    
    print("\n" + "="*50)
else:
    print(f"Reserva {id_reserva} no encontrada")
