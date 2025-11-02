"""
Script de configuración inicial del proyecto.

Este script te guía paso a paso para configurar tu entorno
de desarrollo para OpenPayments e Interledger.
"""

import os
from pathlib import Path


def main():
    print("=" * 70)
    print("⚙️  CONFIGURACIÓN INICIAL - OpenPayments & Interledger")
    print("=" * 70)
    print()
    
    # Verificar que exista .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No se encontró el archivo .env")
        print("   Creándolo desde .env.example...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Archivo .env creado")
        else:
            print("❌ Tampoco se encontró .env.example")
            return
    
    print("📝 Configuración de variables de entorno:")
    print()
    
    # Leer .env actual
    env_lines = []
    with open(".env", "r") as f:
        env_lines = f.readlines()
    
    # Preguntar por wallet address
    print("🌐 WALLET ADDRESS")
    print("   Para obtener tu wallet address:")
    print("   1. Visita: https://wallet.interledger-test.dev")
    print("   2. Crea una cuenta de prueba")
    print("   3. Copia tu wallet address (ejemplo: https://ilp.rafiki.money/alice)")
    print()
    
    wallet_address = input("   Ingresa tu wallet address (o presiona Enter para configurar después): ").strip()
    
    if wallet_address:
        # Actualizar .env
        new_env_lines = []
        for line in env_lines:
            if line.startswith("WALLET_ADDRESS="):
                new_env_lines.append(f"WALLET_ADDRESS={wallet_address}\n")
            else:
                new_env_lines.append(line)
        
        with open(".env", "w") as f:
            f.writelines(new_env_lines)
        
        print(f"   ✅ Wallet address configurada: {wallet_address}")
    else:
        print("   ⚠️  Recuerda configurar WALLET_ADDRESS en .env antes de usar los ejemplos")
    
    print()
    print("=" * 70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("📚 PRÓXIMOS PASOS:")
    print()
    print("1. ✅ Llaves generadas en: keys/")
    print("2. ✅ Archivo .env configurado")
    print()
    print("3. 🧪 Probar los ejemplos:")
    print("   mise exec -- python examples/02_get_wallet_info.py")
    print("   mise exec -- python examples/03_create_quote.py")
    print()
    print("4. 📖 Lee el README.md para más información")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
