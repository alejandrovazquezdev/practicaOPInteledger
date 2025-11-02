"""
Ejemplo 2: Obtener información de una Wallet Address

Este script demuestra cómo consultar información pública
de una wallet address usando la API de OpenPayments.

Según las notas:
- La wallet address es pública, como un email pero para dinero
- No requiere autenticación para consultar información básica
- Es el primer paso antes de crear cotizaciones o pagos
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.openpayments_client import OpenPaymentsClient


def main():
    print("=" * 60)
    print("🔍 Consultar Información de Wallet Address")
    print("=" * 60)
    print()
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar configuración
    wallet_address = os.getenv("WALLET_ADDRESS")
    if not wallet_address:
        print("❌ Error: No se encontró WALLET_ADDRESS en .env")
        print()
        print("Pasos para configurar:")
        print("1. Copia .env.example a .env")
        print("2. Obtén tu wallet address en https://wallet.interledger-test.dev")
        print("3. Actualiza WALLET_ADDRESS en .env")
        return
    
    private_key_path = os.getenv("PRIVATE_KEY_PATH", "keys/key-1_private.pem")
    key_id = os.getenv("KEY_ID", "key-1")
    
    # Crear cliente
    print(f"🔗 Conectando a: {wallet_address}")
    print()
    
    try:
        client = OpenPaymentsClient(
            wallet_address=wallet_address,
            private_key_path=private_key_path,
            key_id=key_id
        )
        
        # Obtener información de la wallet
        wallet_info = client.get_wallet_info()
        
        print()
        print("-" * 60)
        print("📊 Información de la Wallet:")
        print("-" * 60)
        
        import json
        print(json.dumps(wallet_info, indent=2))
        
        print()
        print("✅ Consulta exitosa!")
        
        client.close()
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se encontró el archivo de llave privada")
        print(f"   Ejecuta primero: python examples/01_generate_keys.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Asegúrate de:")
        print("   1. Tener una wallet address válida")
        print("   2. Haber generado tus llaves (ejemplo 01)")
        print("   3. Tener conexión a internet")


if __name__ == "__main__":
    main()
