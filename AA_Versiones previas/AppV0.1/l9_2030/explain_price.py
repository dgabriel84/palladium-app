
import datetime
from precios_data import PRECIOS_ADR

# Configuration
hotel_name = "Grand Palladium Select Costa Mujeres"
hotel_code = "MUJE_CMU" # Mapped manually for this script based on app.py
room_name = "CMU JUNIOR SUITE GV"
pax = "2"
start_date = datetime.date(2026, 3, 11)
nights = 7

print(f"--- Desglose de Precio ---")
print(f"Hotel: {hotel_name} ({hotel_code})")
print(f"Habitación: {room_name}")
print(f"Pax: {pax}")
print(f"Fecha Llegada: {start_date}")
print(f"Noches: {nights}")
print(f"-"*30)

total = 0.0
prices_data = PRECIOS_ADR[hotel_code][room_name][pax]

for i in range(nights):
    current_date = start_date + datetime.timedelta(days=i)
    year, week, _ = current_date.isocalendar()
    week_key = f"{year}-{week:02d}"
    
    price = prices_data.get(week_key, 0.0)
    total += price
    
    print(f"Noche {i+1}: {current_date} (Semana {week_key}) -> {price}€")

print(f"-"*30)
print(f"TOTAL: {total:,.2f}€")
print(f"Promedio: {total/nights:,.2f}€/noche")
