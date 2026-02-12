#!/usr/bin/env python3
"""
Test de verificación: comparar predicción de la web con predicción directa del modelo
"""
import sys
import os

# Añadir paths
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(current_dir), "04_models")
sys.path.insert(0, models_dir)
sys.path.insert(0, current_dir)

from datetime import date, datetime
from predictor import predecir_cancelacion

# Datos exactos de la reserva web - ID: 646582709601
resultado = predecir_cancelacion(
    fecha_llegada=date(2026, 6, 1),          # 01/06/2026
    noches=15,                                 # 16 - 1 = 15 noches
    adultos=2,
    ninos=0,
    pais="ESPAÑA",                            # Asumiendo España
    es_rewards=False,                         # Sin Rewards
    nombre_hotel="Grand Palladium Select Costa Mujeres",
    nombre_habitacion="CMU JUNIOR SUITE GV",  # Diferente de PS!
    valor_reserva=11088.0                     # $11,088 USD
)

print("=" * 60)
print("VERIFICACIÓN DE PREDICCIÓN - RESERVA 646582709601")
print("=" * 60)
print(f"Hotel: Grand Palladium Select Costa Mujeres")
print(f"Habitación: CMU JUNIOR SUITE GV")
print(f"Fechas: 01/06/2026 - 16/06/2026 (15 noches)")
print(f"Huéspedes: 2 adultos")
print(f"Precio: $11,088 USD")
print("=" * 60)
print(f"\n📊 RESULTADO DEL MODELO:")
print(f"   Probabilidad: {resultado['probabilidad']:.4f} ({resultado['probabilidad']*100:.1f}%)")
print(f"   Riesgo: {resultado['riesgo'].upper()}")
print(f"   Success: {resultado['success']}")
if resultado.get('error'):
    print(f"   Error: {resultado['error']}")
print("=" * 60)
print("\n🌐 Valor en la web: 28.6% (MEDIO)")
print(f"🔬 Valor del test:  {resultado['probabilidad']*100:.1f}% ({resultado['riesgo'].upper()})")

if abs(resultado['probabilidad'] - 0.286) < 0.01:
    print("\n✅ ¡COINCIDEN! El modelo está funcionando correctamente.")
else:
    print(f"\n⚠️ Diferencia: {abs(resultado['probabilidad']*100 - 28.6):.2f}%")
