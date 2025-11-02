"""
Ejemplo 3: Crear una cotización (Quote)

Este script demuestra cómo crear una cotización para un pago.

Según las notas de la Clase-06:
- El Quote ID asegura transparencia antes de aprobar un pago
- Define monto, comisiones y tipo de conversión
- Todo queda claro antes de confirmar: sin cargos ocultos
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.openpayments_client import OpenPaymentsClient


def main():
    print("=" * 60)
    print("💰 Crear Cotización (Quote) para Pago")
    print("=" * 60)
    print()
    
    load_dotenv()
    
    # Configuración
    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key_path = os.getenv("PRIVATE_KEY_PATH", "keys/key-1_private.pem")
    key_id = os.getenv("KEY_ID", "key-1")
    
    if not wallet_address:
        print("❌ Error: Configura tu .env primero")
        return
    
    # Wallet del receptor (ejemplo - cambiar por una real)
    receiver_wallet = input("Ingresa la wallet address del receptor: ").strip()
    if not receiver_wallet:
        print("❌ Necesitas una wallet address de destino")
        return
    
    # Monto a enviar
    print()
    print("💵 Configurar monto:")
    amount_value = input("Monto a enviar (ejemplo: 10.50): ").strip() or "10.00"
    currency = input("Moneda (ejemplo: USD): ").strip() or "USD"
    
    # Convertir a formato OpenPayments
    # Si el monto es "10.00" USD, assetScale=2 (centavos)
    amount_parts = amount_value.split(".")
    if len(amount_parts) == 2:
        asset_scale = len(amount_parts[1])
        value_in_smallest = amount_parts[0] + amount_parts[1]
    else:
        asset_scale = 0
        value_in_smallest = amount_value
    
    send_amount = {
        "value": value_in_smallest,
        "assetCode": currency,
        "assetScale": asset_scale
    }
    
    print()
    print(f"📤 Enviando cotización para {amount_value} {currency}")
    print()
    
    try:
        client = OpenPaymentsClient(
            wallet_address=wallet_address,
            private_key_path=private_key_path,
            key_id=key_id
        )
        
        # Crear cotización
        quote = client.create_quote(
            receiver_wallet=receiver_wallet,
            send_amount=send_amount
        )
        
        print()
        print("=" * 60)
        print("✅ Cotización creada exitosamente!")
        print("=" * 60)
        print()
        print(f"🆔 Quote ID: {quote.get('id')}")
        print(f"💸 Enviarás: {quote.get('sendAmount')}")
        print(f"💵 Recibirá: {quote.get('receiveAmount')}")
        print(f"⏰ Expira: {quote.get('expiresAt')}")
        print()
        print("📝 Guarda el Quote ID para crear el pago")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Verifica:")
        print("   - Wallet address del receptor es válida")
        print("   - Tus llaves están configuradas correctamente")
        print("   - Tienes permisos para crear cotizaciones")


if __name__ == "__main__":
    main()
