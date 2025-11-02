"""
Módulo para gestionar recursos de OpenPayments.

Basado en las notas de las Clases 10 y 12:
- Incoming Payments (pagos entrantes)
- Outgoing Payments (pagos salientes)  
- Quotes (cotizaciones)

Estos recursos están protegidos y requieren concesiones (grants) del AS.
"""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from datetime import datetime
import httpx
import json


@dataclass
class IncomingPayment:
    """
    Pago entrante en la cuenta del receptor.
    
    Según clase-10: Los fondos que llegan a un receptor.
    Se crea del lado del receptor.
    """
    wallet_address: str
    incoming_amount: Dict[str, Any]  # {"value": "1000", "assetCode": "USD", "assetScale": 2}
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    completed: Optional[bool] = None
    received_amount: Optional[Dict[str, Any]] = None


@dataclass
class OutgoingPayment:
    """
    Pago saliente desde la cuenta del remitente.
    
    Según clase-10: El dinero que sale de la cuenta.
    Requiere concesión interactiva (consentimiento del usuario).
    """
    wallet_address: str
    quote_id: str
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    sent_amount: Optional[Dict[str, Any]] = None
    failed: Optional[bool] = None


class ResourceClient:
    """Cliente para interactuar con recursos de OpenPayments"""
    
    def __init__(
        self,
        resource_server_url: str,
        access_token: str
    ):
        """
        Inicializa el cliente de recursos.
        
        Args:
            resource_server_url: URL del Resource Server
            access_token: Token de acceso obtenido del AS
        """
        self.resource_server_url = resource_server_url
        self.access_token = access_token
        self.client = httpx.Client(timeout=30.0)
    
    def create_incoming_payment(
        self,
        wallet_address: str,
        incoming_amount: Dict[str, Any],
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IncomingPayment:
        """
        Crea un pago entrante en la cuenta del receptor.
        
        Según clase-10: El pago entrante se crea del lado del receptor.
        Modalidades: FixReceive (monto exacto) o FixSend (lo que llegue).
        
        Args:
            wallet_address: URL de la billetera del receptor
            incoming_amount: {"value": "1000", "assetCode": "USD", "assetScale": 2}
            expires_at: Fecha de expiración (ISO 8601)
            metadata: Información adicional (ej: {"description": "invoice #76"})
            
        Returns:
            IncomingPayment creado
        """
        payload = {
            "walletAddress": wallet_address,
            "incomingAmount": incoming_amount
        }
        
        if expires_at:
            payload["expiresAt"] = expires_at
        if metadata:
            payload["metadata"] = metadata
        
        print(f"📥 Creando pago entrante...")
        print(f"   Receptor: {wallet_address}")
        print(f"   Monto: {incoming_amount}")
        
        headers = {
            "Authorization": f"GNAP {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = self.client.post(
            f"{self.resource_server_url}/incoming-payments",
            content=json.dumps(payload),
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ Pago entrante creado: {data.get('id')}")
        
        return IncomingPayment(
            wallet_address=wallet_address,
            incoming_amount=incoming_amount,
            expires_at=expires_at,
            metadata=metadata,
            id=data.get("id"),
            completed=data.get("completed", False),
            received_amount=data.get("receivedAmount")
        )
    
    def get_incoming_payment(self, payment_id: str) -> Dict[str, Any]:
        """Consulta el estado de un pago entrante"""
        print(f"🔍 Consultando pago entrante: {payment_id}")
        
        headers = {
            "Authorization": f"GNAP {self.access_token}",
            "Accept": "application/json"
        }
        
        response = self.client.get(
            payment_id,  # El ID es una URL completa
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Estado: {'Completado' if data.get('completed') else 'Pendiente'}")
        
        return data
    
    def create_outgoing_payment(
        self,
        wallet_address: str,
        quote_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OutgoingPayment:
        """
        Crea un pago saliente desde la cuenta del remitente.
        
        Según clase-10 y clase-12: Requiere concesión interactiva.
        El usuario debe dar consentimiento explícito.
        
        Args:
            wallet_address: URL de la billetera del remitente
            quote_id: ID de la cotización previamente creada
            metadata: Información adicional
            
        Returns:
            OutgoingPayment creado
        """
        payload = {
            "walletAddress": wallet_address,
            "quoteId": quote_id
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        print(f"📤 Creando pago saliente...")
        print(f"   Remitente: {wallet_address}")
        print(f"   Quote ID: {quote_id}")
        
        headers = {
            "Authorization": f"GNAP {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = self.client.post(
            f"{self.resource_server_url}/outgoing-payments",
            content=json.dumps(payload),
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ Pago saliente creado: {data.get('id')}")
        print(f"   💸 Monto enviado: {data.get('sentAmount')}")
        
        return OutgoingPayment(
            wallet_address=wallet_address,
            quote_id=quote_id,
            metadata=metadata,
            id=data.get("id"),
            sent_amount=data.get("sentAmount"),
            failed=data.get("failed", False)
        )
    
    def get_outgoing_payment(self, payment_id: str) -> Dict[str, Any]:
        """Consulta el estado de un pago saliente"""
        print(f"🔍 Consultando pago saliente: {payment_id}")
        
        headers = {
            "Authorization": f"GNAP {self.access_token}",
            "Accept": "application/json"
        }
        
        response = self.client.get(
            payment_id,  # El ID es una URL completa
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("failed"):
            print(f"❌ Pago falló")
        else:
            print(f"✅ Pago procesado exitosamente")
        
        return data
    
    def close(self):
        """Cierra el cliente HTTP"""
        self.client.close()


if __name__ == "__main__":
    print("⚠️  Este es un módulo de biblioteca.")
    print("    Mira los ejemplos en la carpeta 'examples/' para uso práctico.")
