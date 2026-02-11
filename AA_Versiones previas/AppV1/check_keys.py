import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from precios_data import PRECIOS_ADR
    print("--- HOTEL KEYS ---")
    print(list(PRECIOS_ADR.keys()))
    
    hotel_code = "MUJE_CMU"
    if hotel_code in PRECIOS_ADR:
        print(f"\n--- ROOMS FOR {hotel_code} ---")
        print(list(PRECIOS_ADR[hotel_code].keys()))
    else:
        print(f"\nXXX {hotel_code} NOT FOUND XXX")

except ImportError:
    print("Could not import precios_data")
except Exception as e:
    print(f"Error: {e}")
