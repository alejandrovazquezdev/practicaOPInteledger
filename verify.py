"""
Script de verificación del entorno.

Verifica que todo esté correctamente configurado para trabajar
con OpenPayments e Interledger.
"""

import sys
from pathlib import Path
import os


def check_item(name, condition, success_msg, fail_msg):
    """Verifica un item y muestra el resultado"""
    if condition:
        print(f"  ✅ {name}: {success_msg}")
        return True
    else:
        print(f"  ❌ {name}: {fail_msg}")
        return False


def main():
    print("=" * 70)
    print("🔍 VERIFICACIÓN DEL ENTORNO - OpenPayments & Interledger")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # 1. Verificar Python
    print("1️⃣  Python:")
    python_version = sys.version_info
    all_ok &= check_item(
        "Versión",
        python_version >= (3, 12),
        f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
        f"Necesitas Python 3.12+ (tienes {python_version.major}.{python_version.minor})"
    )
    print()
    
    # 2. Verificar dependencias
    print("2️⃣  Dependencias:")
    try:
        import httpx
        all_ok &= check_item("httpx", True, f"v{httpx.__version__}", "No instalado")
    except ImportError:
        all_ok &= check_item("httpx", False, "", "No instalado - ejecuta: mise exec -- pip install -r requirements.txt")
    
    try:
        import cryptography
        all_ok &= check_item("cryptography", True, f"v{cryptography.__version__}", "No instalado")
    except ImportError:
        all_ok &= check_item("cryptography", False, "", "No instalado")
    
    try:
        from dotenv import load_dotenv
        all_ok &= check_item("python-dotenv", True, "Instalado", "No instalado")
    except ImportError:
        all_ok &= check_item("python-dotenv", False, "", "No instalado")
    
    print()
    
    # 3. Verificar estructura de archivos
    print("3️⃣  Estructura de archivos:")
    
    files_to_check = {
        "src/key_manager.py": "Gestor de llaves",
        "src/openpayments_client.py": "Cliente OpenPayments",
        "examples/01_generate_keys.py": "Ejemplo 1",
        "examples/02_get_wallet_info.py": "Ejemplo 2",
        "examples/03_create_quote.py": "Ejemplo 3",
        ".env": "Variables de entorno",
        "requirements.txt": "Dependencias"
    }
    
    for file_path, description in files_to_check.items():
        exists = Path(file_path).exists()
        all_ok &= check_item(
            description,
            exists,
            file_path,
            f"{file_path} no encontrado"
        )
    
    print()
    
    # 4. Verificar llaves
    print("4️⃣  Llaves criptográficas:")
    
    keys_dir = Path("keys")
    private_key = keys_dir / "key-1_private.pem"
    public_key = keys_dir / "key-1_public.pem"
    jwk_file = keys_dir / "public_keys.json"
    
    has_private = private_key.exists()
    has_public = public_key.exists()
    has_jwk = jwk_file.exists()
    
    check_item(
        "Llave privada",
        has_private,
        str(private_key),
        "No generada - ejecuta: examples/01_generate_keys.py"
    )
    check_item(
        "Llave pública",
        has_public,
        str(public_key),
        "No generada - ejecuta: examples/01_generate_keys.py"
    )
    check_item(
        "JWK público",
        has_jwk,
        str(jwk_file),
        "No generado - ejecuta: examples/01_generate_keys.py"
    )
    
    print()
    
    # 5. Verificar configuración
    print("5️⃣  Configuración (.env):")
    
    if Path(".env").exists():
        from dotenv import dotenv_values
        config = dotenv_values(".env")
        
        wallet_configured = bool(config.get("WALLET_ADDRESS") and 
                                not config.get("WALLET_ADDRESS").startswith("https://ilp.rafiki.money/your"))
        
        check_item(
            "WALLET_ADDRESS",
            wallet_configured,
            config.get("WALLET_ADDRESS", ""),
            "No configurada - edita .env con tu wallet address"
        )
        
        check_item(
            "KEY_ID",
            bool(config.get("KEY_ID")),
            config.get("KEY_ID", ""),
            "No configurado"
        )
    else:
        all_ok = False
        print("  ❌ Archivo .env no existe")
    
    print()
    print("=" * 70)
    
    if all_ok and has_private and has_public:
        print("✅ ¡ENTORNO COMPLETAMENTE CONFIGURADO!")
        print()
        print("🚀 Estás listo para:")
        print("   - Consultar wallets: mise exec -- python examples/02_get_wallet_info.py")
        print("   - Crear cotizaciones: mise exec -- python examples/03_create_quote.py")
        print("   - Flujo completo: mise exec -- python examples/04_complete_flow.py")
    else:
        print("⚠️  CONFIGURACIÓN INCOMPLETA")
        print()
        print("📝 Pasos pendientes:")
        if not (has_private and has_public):
            print("   1. Generar llaves: mise exec -- python examples/01_generate_keys.py")
        if not Path(".env").exists():
            print("   2. Copiar .env: cp .env.example .env")
        print("   3. Obtener wallet address: https://wallet.interledger-test.dev")
        print("   4. Configurar .env con tu wallet address")
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
