"""
Cliente HTTP para interactuar con la API de OpenPayments.

Basado en tus notas de las Clases 06, 07 y 08:
- API RESTful con recursos (quotes, payments, accounts)
- Métodos HTTP (GET, POST, PUT, DELETE)
- Autenticación con GNAP (tokens de acceso)
- Firma de mensajes HTTP con llaves Ed25519
"""

import httpx
import json
import hashlib
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519
from pathlib import Path


class OpenPaymentsClient:
    """Cliente para la API de OpenPayments"""
    
    def __init__(
        self,
        wallet_address: str,
        private_key_path: str,
        key_id: str,
        base_url: str = None
    ):
        """
        Inicializa el cliente de OpenPayments.
        
        Args:
            wallet_address: URL de tu wallet (ej: https://ilp.rafiki.money/alice)
            private_key_path: Ruta a tu llave privada para firmar
            key_id: ID de tu llave pública
            base_url: URL base del servidor OpenPayments (opcional)
        """
        self.wallet_address = wallet_address
        self.key_id = key_id
        
        # Cargar llave privada
        with open(private_key_path, "rb") as f:
            from cryptography.hazmat.primitives import serialization
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
        
        # Cliente HTTP
        self.client = httpx.Client(timeout=30.0)
        
        # Si no se proporciona base_url, extraer del wallet_address
        if base_url is None:
            from urllib.parse import urlparse
            parsed = urlparse(wallet_address)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            self.base_url = base_url
    
    def _sign_request(
        self,
        method: str,
        url: str,
        body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Firma una solicitud HTTP según el estándar de OpenPayments.
        
        Según tus notas: cada solicitud debe estar firmada con la llave
        privada. El servidor de OpenPayments usa tu llave pública para
        verificar autenticidad e integridad.
        """
        if headers is None:
            headers = {}
        
        # Timestamp para evitar replay attacks
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Crear el contenido a firmar
        # En una implementación completa, seguirías el estándar HTTP Message Signatures
        # Por ahora, una versión simplificada para desarrollo
        content_to_sign = f"{method}\n{url}\n{timestamp}"
        if body:
            content_digest = hashlib.sha256(body.encode()).digest()
            content_to_sign += f"\n{base64.b64encode(content_digest).decode()}"
        
        # Firmar con llave privada Ed25519
        signature_bytes = self.private_key.sign(content_to_sign.encode())
        signature_b64 = base64.b64encode(signature_bytes).decode()
        
        # Agregar headers de autenticación
        headers["Signature"] = f'keyId="{self.key_id}",algorithm="ed25519",signature="{signature_b64}"'
        headers["Signature-Input"] = f'sig1=();created={timestamp}'
        headers["Content-Type"] = "application/json"
        
        return headers
    
    def create_quote(
        self,
        receiver_wallet: str,
        send_amount: Optional[Dict[str, Any]] = None,
        receive_amount: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea una cotización (quote) para un pago.
        
        Según tus notas: el Quote ID define el monto, comisiones y tipo
        de conversión. Todo queda claro antes de confirmar.
        
        Args:
            receiver_wallet: Wallet address del receptor
            send_amount: {"value": "100", "assetCode": "USD", "assetScale": 2}
            receive_amount: {"value": "100", "assetCode": "EUR", "assetScale": 2}
        """
        url = f"{self.base_url}/quotes"
        
        payload = {
            "walletAddress": receiver_wallet,
            "method": "ilp"
        }
        
        # Debe especificar send_amount O receive_amount, no ambos
        if send_amount:
            payload["sendAmount"] = send_amount
        elif receive_amount:
            payload["receiveAmount"] = receive_amount
        else:
            raise ValueError("Debes especificar send_amount o receive_amount")
        
        body = json.dumps(payload)
        headers = self._sign_request("POST", url, body)
        
        print(f"📊 Creando cotización para: {receiver_wallet}")
        response = self.client.post(url, content=body, headers=headers)
        response.raise_for_status()
        
        quote_data = response.json()
        print(f"✅ Quote creado: {quote_data.get('id')}")
        print(f"   💰 Monto a enviar: {quote_data.get('sendAmount')}")
        print(f"   💵 Monto a recibir: {quote_data.get('receiveAmount')}")
        
        return quote_data
    
    def create_outgoing_payment(
        self,
        quote_id: str,
        wallet_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un pago saliente usando un quote.
        
        Según tus notas (Clase-06): los campos clave son
        - walletAddress: URL de la cuenta destino
        - quoteId: ID único de la cotización
        - metadata: información adicional (opcional)
        """
        url = f"{self.base_url}/outgoing-payments"
        
        payload = {
            "walletAddress": wallet_address,
            "quoteId": quote_id
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        body = json.dumps(payload)
        headers = self._sign_request("POST", url, body)
        
        print(f"💸 Creando pago saliente...")
        response = self.client.post(url, content=body, headers=headers)
        response.raise_for_status()
        
        payment_data = response.json()
        print(f"✅ Pago creado: {payment_data.get('id')}")
        
        return payment_data
    
    def get_wallet_info(self, wallet_address: str = None) -> Dict[str, Any]:
        """
        Obtiene información de una wallet address.
        
        GET request para obtener información pública de una billetera.
        """
        if wallet_address is None:
            wallet_address = self.wallet_address
        
        print(f"🔍 Obteniendo información de: {wallet_address}")
        
        # Las wallet addresses son públicas, no requieren firma
        response = self.client.get(
            wallet_address,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        
        wallet_info = response.json()
        print(f"✅ Wallet encontrada: {wallet_info.get('id')}")
        
        return wallet_info
    
    def close(self):
        """Cierra el cliente HTTP"""
        self.client.close()


if __name__ == "__main__":
    # Ejemplo de uso (necesitas configurar tus credenciales primero)
    print("⚠️  Este es un módulo de biblioteca.")
    print("    Mira los ejemplos en la carpeta 'examples/' para uso práctico.")
