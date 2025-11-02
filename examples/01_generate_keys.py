"""
Ejemplo 1: Generación de llaves para OpenPayments

Este script demuestra cómo generar el par de llaves Ed25519
necesarias para firmar solicitudes HTTP en OpenPayments.

Según las notas de la Clase-08:
- Necesitas un par de llaves para firmar solicitudes
- La llave privada se mantiene segura en tu backend
- La llave pública se publica en un endpoint JSON
- OpenPayments descarga, cachea y usa tu llave pública para verificar
"""

import sys
from pathlib import Path

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.key_manager import KeyManager


def main():
    print("=" * 60)
    print("🔐 Generación de Llaves para OpenPayments")
    print("=" * 60)
    print()
    
    # Crear gestor de llaves
    manager = KeyManager(keys_dir="keys")
    
    # Generar par de llaves
    print("📝 Generando par de llaves Ed25519...")
    print()
    private_path, public_path = manager.generate_keypair(key_id="key-1")
    
    print()
    print("-" * 60)
    
    # Exportar llave pública en formato JWK
    print()
    print("📤 Exportando llave pública en formato JWK...")
    print()
    jwk_path = manager.save_public_jwk_file(
        public_key_path=public_path,
        key_id="key-1",
        output_path="keys/public_keys.json"
    )
    
    print()
    print("=" * 60)
    print("✅ ¡Llaves generadas exitosamente!")
    print("=" * 60)
    print()
    print("📋 PASOS SIGUIENTES:")
    print()
    print("1. 🌐 Obtén tu Wallet Address:")
    print("   Visita: https://wallet.interledger-test.dev")
    print("   Crea una cuenta y obtén tu dirección de billetera")
    print()
    print("2. 📤 Publica tu llave pública:")
    print(f"   Sube el archivo '{jwk_path}' a tu servidor")
    print("   OpenPayments lo usará para verificar tus firmas")
    print()
    print("3. 🔒 Protege tu llave privada:")
    print(f"   NUNCA compartas: {private_path}")
    print("   Mantenla segura en tu backend")
    print()
    print("4. ⚙️  Configura tu entorno:")
    print("   Copia .env.example a .env")
    print("   Agrega tu wallet address y rutas de llaves")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
