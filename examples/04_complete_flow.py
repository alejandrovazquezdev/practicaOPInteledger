"""
Ejemplo completo: Flujo de pago de extremo a extremo

Este ejemplo demuestra el flujo completo de un pago según
las notas de las Clases 06-08:

1. Consultar wallet del receptor
2. Crear una cotización (Quote)
3. Revisar detalles (monto, comisiones, expiración)
4. Crear el pago (simulado - requiere autorización GNAP real)

NOTA: Este es un ejemplo educativo. En producción necesitarías
implementar el flujo completo de autorización GNAP.
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.openpayments_client import OpenPaymentsClient


def print_section(title):
    """Imprime una sección del flujo"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def main():
    print_section("💸 FLUJO COMPLETO DE PAGO - OpenPayments")
    
    load_dotenv()
    
    # Configuración
    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key_path = os.getenv("PRIVATE_KEY_PATH", "keys/key-1_private.pem")
    key_id = os.getenv("KEY_ID", "key-1")
    
    if not wallet_address:
        print("❌ Error: Configura WALLET_ADDRESS en .env")
        print()
        print("Ejecuta primero:")
        print("  mise exec -- python setup.py")
        return
    
    print("📋 Configuración:")
    print(f"   Tu wallet: {wallet_address}")
    print(f"   Llave privada: {private_key_path}")
    print(f"   Key ID: {key_id}")
    
    # === PASO 1: Wallet del receptor ===
    print_section("PASO 1: Obtener wallet del receptor")
    
    receiver_wallet = input("Ingresa la wallet address del receptor: ").strip()
    if not receiver_wallet:
        print("❌ Necesitas una wallet de destino para continuar")
        print()
        print("💡 Puedes usar otra cuenta de prueba de:")
        print("   https://wallet.interledger-test.dev")
        return
    
    try:
        client = OpenPaymentsClient(
            wallet_address=wallet_address,
            private_key_path=private_key_path,
            key_id=key_id
        )
        
        print(f"🔍 Verificando wallet: {receiver_wallet}")
        receiver_info = client.get_wallet_info(receiver_wallet)
        print(f"✅ Wallet válida: {receiver_info.get('id')}")
        
        # === PASO 2: Crear cotización ===
        print_section("PASO 2: Crear cotización (Quote)")
        
        amount = input("Monto a enviar (ejemplo: 10.50): ").strip() or "5.00"
        currency = input("Moneda (ejemplo: USD): ").strip() or "USD"
        
        # Convertir a formato OpenPayments
        amount_parts = amount.split(".")
        if len(amount_parts) == 2:
            asset_scale = len(amount_parts[1])
            value_in_smallest = amount_parts[0] + amount_parts[1]
        else:
            asset_scale = 0
            value_in_smallest = amount
        
        send_amount = {
            "value": value_in_smallest,
            "assetCode": currency,
            "assetScale": asset_scale
        }
        
        print(f"💰 Solicitando cotización para {amount} {currency}...")
        quote = client.create_quote(
            receiver_wallet=receiver_wallet,
            send_amount=send_amount
        )
        
        # === PASO 3: Revisar detalles ===
        print_section("PASO 3: Revisar detalles de la cotización")
        
        print(f"🆔 Quote ID: {quote.get('id')}")
        print(f"💸 Enviarás: {quote.get('sendAmount')}")
        print(f"💵 Recibirá: {quote.get('receiveAmount')}")
        print(f"⏰ Válido hasta: {quote.get('expiresAt')}")
        
        # === PASO 4: Confirmar pago (simulado) ===
        print_section("PASO 4: Confirmar pago")
        
        print("⚠️  NOTA IMPORTANTE:")
        print("   Para ejecutar el pago real necesitas:")
        print("   1. Implementar autorización GNAP completa")
        print("   2. Obtener tokens de acceso del AS (Authorization Server)")
        print("   3. Usar el token para crear el outgoing payment")
        print()
        print("   Este ejemplo muestra el flujo hasta la cotización.")
        print("   La implementación completa de GNAP está fuera del alcance")
        print("   de este ejemplo educativo.")
        print()
        
        confirm = input("¿Deseas intentar crear el pago? (s/N): ").strip().lower()
        
        if confirm == 's':
            print()
            print("📤 Intentando crear pago...")
            try:
                payment = client.create_outgoing_payment(
                    quote_id=quote.get('id'),
                    wallet_address=receiver_wallet,
                    metadata={"note": "Pago de prueba desde Python"}
                )
                
                print()
                print("✅ ¡Pago creado!")
                print(f"   ID: {payment.get('id')}")
                
            except Exception as e:
                print()
                print(f"⚠️  Error esperado: {e}")
                print()
                print("   Esto es normal. Para completar el pago necesitas:")
                print("   - Token de acceso de GNAP")
                print("   - Autorización del usuario")
                print("   - Grant válido del Authorization Server")
        else:
            print("✅ Flujo completado hasta la cotización")
        
        client.close()
        
        # === Resumen ===
        print_section("📊 RESUMEN DEL FLUJO")
        
        print("✅ Pasos completados:")
        print("   1. ✅ Verificación de wallet del receptor")
        print("   2. ✅ Creación de cotización (Quote)")
        print("   3. ✅ Revisión de detalles y transparencia")
        print()
        print("📚 Conceptos aplicados de tus notas:")
        print("   - Wallet Address como identificador público")
        print("   - Quote ID para transparencia antes de pagar")
        print("   - Firma de solicitudes con llaves Ed25519")
        print("   - API RESTful con recursos y métodos")
        print("   - Metadatos opcionales en pagos")
        print()
        print("🎓 Siguiente nivel:")
        print("   - Implementar flujo GNAP completo")
        print("   - Manejar estados de pago (pending, completed, failed)")
        print("   - Implementar webhooks para notificaciones")
        print("   - Rotación de llaves con múltiples Key IDs")
        print()
        
    except FileNotFoundError:
        print("❌ No se encontraron las llaves")
        print("   Ejecuta: mise exec -- python examples/01_generate_keys.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
