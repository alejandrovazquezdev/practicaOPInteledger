"""
Módulo para generar y gestionar llaves Ed25519 para firmar solicitudes HTTP
en OpenPayments según tus notas de la Clase-08.

Las llaves privadas se usan para firmar cada solicitud.
Las llaves públicas se publican en un endpoint JSON para verificación.
"""

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import json
from typing import Tuple


class KeyManager:
    """Gestor de llaves Ed25519 para OpenPayments"""
    
    def __init__(self, keys_dir: str = "keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True)
        
    def generate_keypair(self, key_id: str = "key-1") -> Tuple[str, str]:
        """
        Genera un par de llaves Ed25519 (privada y pública).
        
        Según las notas: necesitas un par de llaves para firmar solicitudes.
        Cada solicitud debe estar firmada con la privada y la pública
        se expone en un endpoint JSON.
        
        Args:
            key_id: Identificador único para este par de llaves
            
        Returns:
            Tupla con (ruta_privada, ruta_publica)
        """
        # Generar llave privada
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Obtener llave pública correspondiente
        public_key = private_key.public_key()
        
        # Guardar llave privada (PEM format)
        private_path = self.keys_dir / f"{key_id}_private.pem"
        with open(private_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        
        # Guardar llave pública (PEM format)
        public_path = self.keys_dir / f"{key_id}_public.pem"
        with open(public_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )
        
        print(f"✅ Par de llaves generado exitosamente:")
        print(f"   🔒 Privada: {private_path}")
        print(f"   🔓 Pública: {public_path}")
        
        return str(private_path), str(public_path)
    
    def load_private_key(self, private_key_path: str) -> ed25519.Ed25519PrivateKey:
        """Carga una llave privada desde archivo"""
        with open(private_key_path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None
            )
    
    def load_public_key(self, public_key_path: str) -> ed25519.Ed25519PublicKey:
        """Carga una llave pública desde archivo"""
        with open(public_key_path, "rb") as f:
            return serialization.load_pem_public_key(f.read())
    
    def export_public_key_jwk(self, public_key_path: str, key_id: str) -> dict:
        """
        Exporta la llave pública en formato JWK (JSON Web Key).
        
        Este es el formato que OpenPayments espera para publicar
        en tu endpoint JSON y que otros puedan verificar tus firmas.
        
        Args:
            public_key_path: Ruta al archivo de llave pública
            key_id: Identificador de la llave
            
        Returns:
            Diccionario con el formato JWK
        """
        public_key = self.load_public_key(public_key_path)
        
        # Obtener los bytes crudos de la llave pública
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Convertir a base64url (sin padding)
        import base64
        x = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
        
        jwk = {
            "kid": key_id,  # Key ID para identificar cuál llave se usó
            "kty": "OKP",   # Key Type: Octet string Key Pairs
            "alg": "EdDSA", # Algorithm: Edwards-curve Digital Signature Algorithm
            "crv": "Ed25519", # Curve
            "x": x,         # Public key value
            "use": "sig"    # Uso: signature
        }
        
        return jwk
    
    def save_public_jwk_file(self, public_key_path: str, key_id: str, 
                            output_path: str = None) -> str:
        """
        Guarda la llave pública JWK en un archivo JSON.
        Este archivo debe ser publicado en tu servidor para que
        OpenPayments pueda verificar tus firmas.
        """
        if output_path is None:
            output_path = self.keys_dir / "public_keys.json"
        
        jwk = self.export_public_key_jwk(public_key_path, key_id)
        
        # Formato que espera OpenPayments
        public_keys_json = {
            "keys": [jwk]
        }
        
        with open(output_path, "w") as f:
            json.dump(public_keys_json, f, indent=2)
        
        print(f"✅ Llave pública JWK guardada en: {output_path}")
        print(f"📤 Publica este archivo en tu servidor para verificación")
        
        return str(output_path)


if __name__ == "__main__":
    # Ejemplo de uso
    manager = KeyManager()
    
    # Generar nuevo par de llaves
    private_path, public_path = manager.generate_keypair("key-1")
    
    # Exportar llave pública en formato JWK
    jwk_path = manager.save_public_jwk_file(public_path, "key-1")
    
    print("\n📝 Siguiente paso:")
    print("   1. Copia tu wallet address de https://wallet.interledger-test.dev")
    print("   2. Publica el archivo public_keys.json en tu servidor")
    print("   3. Usa la llave privada para firmar tus solicitudes HTTP")
