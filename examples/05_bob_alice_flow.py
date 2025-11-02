"""
Ejemplo 5: Flujo completo Bob y Alicia (de la Clase-12)

Este ejemplo recrea el escenario de las notas:
- Bob: Músico que vende una canción
- Alicia: Compra la canción de Bob
- Sitio de música: Actúa como intermediario usando OpenPayments

Flujo completo:
1. Autorizar pago entrante para Bob (receptor)
2. Crear pago entrante en cuenta de Bob
3. Crear cotización desde cuenta de Alicia
4. Autorización interactiva (Alicia da consentimiento)
5. Crear pago saliente desde cuenta de Alicia
6. Liquidación entre bancos/billeteras
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gnap_client import GNAPClient, AccessRight
from src.resources_client import ResourceClient
from src.openpayments_client import OpenPaymentsClient


def print_step(number: int, title: str):
    """Imprime un paso del flujo"""
    print()
    print("=" * 70)
    print(f"PASO {number}: {title}")
    print("=" * 70)
    print()


def main():
    print("=" * 70)
    print("🎵 FLUJO COMPLETO: Bob vende canción a Alicia")
    print("=" * 70)
    print()
    print("Escenario:")
    print("  👨‍🎤 Bob: Músico con banco que usa OpenPayments")
    print("  👩‍💼 Alicia: Compradora con billetera digital OpenPayments")
    print("  🎼 Sitio de música: Intermediario que usa la API")
    print()
    
    load_dotenv()
    
    # Configuración
    # En un caso real, estos serían diferentes wallets
    bob_wallet = os.getenv("BOB_WALLET_ADDRESS", "https://ilp.rafiki.money/bob")
    alicia_wallet = os.getenv("ALICIA_WALLET_ADDRESS", "https://ilp.rafiki.money/alicia")
    
    private_key_path = os.getenv("PRIVATE_KEY_PATH", "keys/key-1_private.pem")
    key_id = os.getenv("KEY_ID", "key-1")
    
    # URLs de servidores (en producción serían diferentes)
    auth_server_url = "https://auth.rafiki.money"
    resource_server_url = "https://backend.rafiki.money"
    
    print(f"📋 Configuración:")
    print(f"   Bob (receptor): {bob_wallet}")
    print(f"   Alicia (remitente): {alicia_wallet}")
    print()
    
    try:
        # ====================================================================
        # PASO 1: Solicitar autorización para crear pago entrante (Bob)
        # ====================================================================
        print_step(1, "Autorizar creación de pago entrante para Bob")
        
        print("El sitio de música solicita permiso al banco de Bob")
        print("para crear un pago entrante en su cuenta.")
        print()
        
        # Crear cliente GNAP
        gnap_client = GNAPClient(
            auth_server_url=auth_server_url,
            client_key_id=key_id,
            private_key_path=private_key_path
        )
        
        # Solicitar concesión no interactiva para pago entrante
        incoming_grant = gnap_client.request_grant_non_interactive(
            access_rights=[
                AccessRight(
                    type="incoming-payment",
                    actions=["create", "read"]
                )
            ],
            client_id="music-site-client"
        )
        
        # Obtener token de acceso
        incoming_token = incoming_grant.get("access_token", {}).get("value")
        
        if not incoming_token:
            print("❌ No se pudo obtener token para pago entrante")
            print("💡 En este ejemplo educativo, simularemos el token")
            incoming_token = "simulated-incoming-token"
        
        # ====================================================================
        # PASO 2: Crear pago entrante en cuenta de Bob
        # ====================================================================
        print_step(2, "Crear pago entrante en cuenta bancaria de Bob")
        
        print("El sitio de música crea el pago entrante para recibir $5 USD")
        print("por la canción de Bob.")
        print()
        
        # Crear cliente de recursos
        resource_client = ResourceClient(
            resource_server_url=resource_server_url,
            access_token=incoming_token
        )
        
        # Crear pago entrante
        incoming_payment = resource_client.create_incoming_payment(
            wallet_address=bob_wallet,
            incoming_amount={
                "value": "500",  # $5.00 USD (escala 2 = centavos)
                "assetCode": "USD",
                "assetScale": 2
            },
            metadata={
                "description": "Canción: Melodía del Atardecer"
            }
        )
        
        print(f"✅ Pago entrante ID: {incoming_payment.id or 'simulated-id'}")
        
        # ====================================================================
        # PASO 3: Crear cotización desde cuenta de Alicia
        # ====================================================================
        print_step(3, "Crear cotización desde cuenta de Alicia")
        
        print("Alicia necesita saber cuánto le costará exactamente")
        print("enviar dinero a Bob (comisiones incluidas).")
        print()
        
        # Solicitar concesión para cotización
        quote_grant = gnap_client.request_grant_non_interactive(
            access_rights=[
                AccessRight(
                    type="quote",
                    actions=["create", "read"]
                )
            ],
            client_id="music-site-client"
        )
        
        quote_token = quote_grant.get("access_token", {}).get("value", "simulated-quote-token")
        
        # Crear cliente OpenPayments para cotización
        op_client = OpenPaymentsClient(
            wallet_address=alicia_wallet,
            private_key_path=private_key_path,
            key_id=key_id
        )
        
        # Crear cotización
        quote = op_client.create_quote(
            receiver_wallet=bob_wallet,
            send_amount={
                "value": "500",
                "assetCode": "USD",
                "assetScale": 2
            }
        )
        
        quote_id = quote.get("id", "simulated-quote-id")
        
        print(f"💰 Cotización válida por tiempo limitado")
        print(f"   (Para mantener tasas exactas)")
        
        # ====================================================================
        # PASO 4: Autorización interactiva - Consentimiento de Alicia
        # ====================================================================
        print_step(4, "Autorización interactiva - Alicia da consentimiento")
        
        print("⚠️  IMPORTANTE: Concesión INTERACTIVA requerida")
        print()
        print("Alicia debe dar su consentimiento explícito antes de")
        print("que el dinero salga de su cuenta.")
        print()
        
        # Solicitar concesión interactiva
        outgoing_grant = gnap_client.request_grant_interactive(
            access_rights=[
                AccessRight(
                    type="outgoing-payment",
                    actions=["create", "read"]
                )
            ],
            client_id="music-site-client",
            redirect_uri="https://music-site.com/payment/callback"
        )
        
        if "interact" in outgoing_grant:
            interact_url = outgoing_grant["interact"].get("redirect")
            print(f"🔗 URL de interacción: {interact_url or '[simulada]'}")
            print()
            print("En una implementación real:")
            print("  1. Redirigir a Alicia a esta URL")
            print("  2. Alicia se autentica con su banco/billetera (IdP)")
            print("  3. Alicia ve pantalla de confirmación:")
            print("     - Monto: $5.00 USD")
            print("     - Receptor: Bob")
            print("     - Concepto: Canción")
            print("  4. Alicia aprueba el pago")
            print("  5. El IdP redirige de vuelta al sitio de música")
            print()
            
            # Simular que Alicia aprobó
            print("✅ [SIMULADO] Alicia aprobó el pago")
            print()
            
            # En producción, aquí se llamaría a continue_grant
            # con el token de continuación
            # outgoing_token = gnap_client.continue_grant(...)
            outgoing_token = "simulated-outgoing-token"
        else:
            outgoing_token = "simulated-outgoing-token"
        
        # ====================================================================
        # PASO 5: Crear pago saliente desde cuenta de Alicia
        # ====================================================================
        print_step(5, "Crear pago saliente desde cuenta de Alicia")
        
        print("Con el consentimiento de Alicia, el sitio de música")
        print("crea el pago saliente usando la cotización.")
        print()
        
        resource_client_out = ResourceClient(
            resource_server_url=resource_server_url,
            access_token=outgoing_token
        )
        
        outgoing_payment = resource_client_out.create_outgoing_payment(
            wallet_address=alicia_wallet,
            quote_id=quote_id,
            metadata={
                "note": "Pago por canción de Bob"
            }
        )
        
        # ====================================================================
        # PASO 6: Liquidación
        # ====================================================================
        print_step(6, "Liquidación entre bancos/billeteras")
        
        print("🔄 Liquidación en proceso...")
        print()
        print("Gracias a la capa de interoperabilidad OpenPayments:")
        print("  - El banco de Bob recibe $5.00 USD")
        print("  - La billetera de Alicia debita $5.00 USD")
        print("  - Los sistemas se comunican directamente")
        print("  - Sin exponer datos bancarios privados")
        print()
        print("✅ ¡Transacción completada!")
        
        # Resumen final
        print()
        print("=" * 70)
        print("📊 RESUMEN DE LA TRANSACCIÓN")
        print("=" * 70)
        print()
        print(f"Flujo completado:")
        print(f"  ✅ 1. Pago entrante autorizado y creado (Bob)")
        print(f"  ✅ 2. Cotización generada (Alicia)")
        print(f"  ✅ 3. Consentimiento interactivo obtenido (Alicia)")
        print(f"  ✅ 4. Pago saliente creado (Alicia)")
        print(f"  ✅ 5. Liquidación completada")
        print()
        print(f"Conceptos aplicados de las notas:")
        print(f"  📝 Clase-10: Incoming payments, quotes, outgoing payments")
        print(f"  📝 Clase-11: Concesiones GNAP, tokens, flujo interactivo")
        print(f"  📝 Clase-12: Flujo Bob-Alicia, wallet addresses")
        print()
        print(f"Arquitectura:")
        print(f"  🏦 ACE (Account Servicing Entity): Bancos/billeteras")
        print(f"  🔐 AS (Authorization Server): Otorga permisos")
        print(f"  📦 Resource Server: Almacena recursos de API")
        print(f"  👤 IdP (Identity Provider): Autentica usuario")
        print()
        
        # Limpiar
        gnap_client.close()
        resource_client.close()
        resource_client_out.close()
        op_client.close()
        
    except FileNotFoundError:
        print("❌ No se encontraron las llaves")
        print("   Ejecuta: mise exec -- python examples/01_generate_keys.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
