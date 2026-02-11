
import datetime
import sys
import os

# Mock streamlit before import if needed, or just import data
from precios_data import PRECIOS_ADR

# Copied from app.py
MAPEO_HOTELES_PRECIOS = {
    "Grand Palladium Select Costa Mujeres": "MUJE_CMU",
    "Family Selection Costa Mujeres": "MUJE_CMU_FS",
    "TRS Coral Hotel": "MUJE_TRS",
    "Grand Palladium Colonial Resort & Spa": "MAYA_COL",
    "Grand Palladium Kantenah Resort & Spa": "MAYA_KAN",
    "TRS Yucatan Hotel": "MAYA_TRS",
    "Grand Palladium Select White Sand": "MAYA_WS",
    "Grand Palladium Select Bavaro": "CANA_BAV",
    "Grand Palladium Palace Resort & Spa": "CANA_PAL",
    "Grand Palladium Punta Cana Resort & Spa": "CANA_PC",
    "TRS Turquesa Hotel": "CANA_TRS"
}

def get_iso_week_key(date_obj):
    year, week, _ = date_obj.isocalendar()
    return f"{year}-{week:02d}"

def calcular_coste_estancia(hotel_nombre, habitacion, llegada, noches, pax):
    codigo_hotel = MAPEO_HOTELES_PRECIOS.get(hotel_nombre)
    if not codigo_hotel: 
        print(f"Hotel no encontrado: {hotel_nombre}")
        return 200 * noches 
    
    datos_hotel = PRECIOS_ADR.get(codigo_hotel, {})
    datos_hab = datos_hotel.get(habitacion, {})
    
    pax_str = str(pax)
    if pax_str not in datos_hab:
        found = False
        for p in range(pax, 0, -1):
             if str(p) in datos_hab:
                 pax_str = str(p)
                 found = True
                 break
        if not found and "2" in datos_hab: pax_str = "2"
        
    print(f"Using PAX key: {pax_str}")
    datos_precios = datos_hab.get(pax_str, {})
    if not datos_precios: return 200 * noches
    
    total = 0.0
    print(f"Calculating for {noches} nights starting {llegada}")
    for i in range(noches):
        dia = llegada + datetime.timedelta(days=i)
        key_semana = get_iso_week_key(dia)
        precio = datos_precios.get(key_semana, 200.0)
        print(f"  Date: {dia}, Week: {key_semana}, Price: {precio}")
        total += precio
        
    return total

# Test
llegada = datetime.date(2026, 3, 11)
noches = 7
pax = 2
hotel = "Grand Palladium Select Costa Mujeres"
habitacion = "CMU JUNIOR SUITE GV"

coste = calcular_coste_estancia(hotel, habitacion, llegada, noches, pax)
print(f"Total Cost: {coste}€")
print(f"Average Night: {coste/noches}€")
