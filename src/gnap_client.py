"""
Módulo para gestionar concesiones (grants) y autorización con GNAP.

Basado en las notas de la Clase-11:
- GNAP: Grant Negotiation and Authorization Protocol
- Solicitudes de concesión al Authorization Server
- Tokens de acceso para recursos protegidos
- Flujos interactivos y no interactivos
"""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from datetime import datetime, timedelta
import httpx
import json


@dataclass
class AccessRight:
    """Derecho de acceso a un recurso específico"""
    type: Literal["incoming-payment", "quote", "outgoing-payment"]
    actions: List[Literal["create", "read", "update", "list"]]
    identifier: Optional[str] = None  # URL del recurso específico
    limits: Optional[Dict[str, Any]] = None  # Límites opcionales


@dataclass
class GrantRequest:
    """Solicitud de concesión al Authorization Server"""
    access_token: List[AccessRight]
    client: str  # Identificador del cliente
    interact: Optional[Dict[str, Any]] = None  # Para flujos interactivos


@dataclass
class AccessToken:
    """Token de acceso otorgado por el AS"""
    value: str
    manage: str  # URL para gestionar el token
    expires_in: Optional[int] = None  # Segundos hasta expiración
    access: List[AccessRight] = None


class GNAPClient:
    """Cliente para flujos de autorización GNAP"""
    
    def __init__(
        self,
        auth_server_url: str,
        client_key_id: str,
        private_key_path: str
    ):
        """
        Inicializa el cliente GNAP.
        
        Args:
            auth_server_url: URL del Authorization Server
            client_key_id: ID de la llave del cliente
            private_key_path: Ruta a la llave privada para firmar
        """
        self.auth_server_url = auth_server_url
        self.client_key_id = client_key_id
        
        # Cargar llave privada
        with open(private_key_path, "rb") as f:
            from cryptography.hazmat.primitives import serialization
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
        
        self.client = httpx.Client(timeout=30.0)
    
    def request_grant_non_interactive(
        self,
        access_rights: List[AccessRight],
        client_id: str
    ) -> Dict[str, Any]:
        """
        Solicita una concesión NO interactiva.
        
        Según las notas: Para acceso automatizado entre servicios,
        sin participación del usuario final.
        
        Args:
            access_rights: Lista de derechos de acceso solicitados
            client_id: Identificador del cliente
            
        Returns:
            Respuesta del Authorization Server con tokens
        """
        grant_request = {
            "access_token": [
                {
                    "type": right.type,
                    "actions": right.actions,
                    **({"identifier": right.identifier} if right.identifier else {}),
                    **({"limits": right.limits} if right.limits else {})
                }
                for right in access_rights
            ],
            "client": client_id
        }
        
        print(f"📤 Solicitando concesión no interactiva al AS...")
        print(f"   Recursos: {[r.type for r in access_rights]}")
        
        # Firmar la solicitud
        body = json.dumps(grant_request)
        headers = self._sign_request("POST", f"{self.auth_server_url}/", body)
        
        response = self.client.post(
            f"{self.auth_server_url}/",
            content=body,
            headers=headers
        )
        response.raise_for_status()
        
        grant_response = response.json()
        
        if "access_token" in grant_response:
            print(f"✅ Concesión otorgada!")
            print(f"   Token: {grant_response['access_token']['value'][:20]}...")
            if "expires_in" in grant_response["access_token"]:
                print(f"   Expira en: {grant_response['access_token']['expires_in']}s")
        
        return grant_response
    
    def request_grant_interactive(
        self,
        access_rights: List[AccessRight],
        client_id: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Solicita una concesión INTERACTIVA.
        
        Según las notas clase-11: Requiere participación del usuario.
        El AS devuelve una URL de redirección para autenticación.
        
        Args:
            access_rights: Lista de derechos de acceso solicitados
            client_id: Identificador del cliente
            redirect_uri: URL a donde redirigir después de la autorización
            
        Returns:
            Respuesta con URL de interacción y detalles de la concesión
        """
        grant_request = {
            "access_token": [
                {
                    "type": right.type,
                    "actions": right.actions,
                    **({"identifier": right.identifier} if right.identifier else {}),
                    **({"limits": right.limits} if right.limits else {})
                }
                for right in access_rights
            ],
            "client": client_id,
            "interact": {
                "start": ["redirect"],
                "finish": {
                    "method": "redirect",
                    "uri": redirect_uri,
                    "nonce": self._generate_nonce()
                }
            }
        }
        
        print(f"📤 Solicitando concesión INTERACTIVA al AS...")
        print(f"   Recursos: {[r.type for r in access_rights]}")
        print(f"   Requiere consentimiento del usuario")
        
        # Firmar la solicitud
        body = json.dumps(grant_request)
        headers = self._sign_request("POST", f"{self.auth_server_url}/", body)
        
        response = self.client.post(
            f"{self.auth_server_url}/",
            content=body,
            headers=headers
        )
        response.raise_for_status()
        
        grant_response = response.json()
        
        if "interact" in grant_response:
            print(f"✅ Concesión pendiente de autorización")
            print(f"   🔗 URL de interacción: {grant_response['interact']['redirect']}")
            print(f"   ⏳ Usuario debe aprobar en el IdP")
        
        return grant_response
    
    def continue_grant(
        self,
        continue_uri: str,
        continue_token: str
    ) -> Dict[str, Any]:
        """
        Continúa una concesión interactiva después del consentimiento.
        
        Según las notas: Después de que el usuario aprueba en el IdP,
        se usa el punto final de continuación para finalizar.
        
        Args:
            continue_uri: URL de continuación del AS
            continue_token: Token de continuación
            
        Returns:
            Respuesta con el access token final
        """
        print(f"📤 Continuando concesión...")
        
        headers = {
            "Authorization": f"GNAP {continue_token}",
            "Content-Type": "application/json"
        }
        
        response = self.client.post(
            continue_uri,
            headers=headers
        )
        response.raise_for_status()
        
        grant_response = response.json()
        
        if "access_token" in grant_response:
            print(f"✅ Autorización completada!")
            print(f"   Token: {grant_response['access_token']['value'][:20]}...")
        
        return grant_response
    
    def _sign_request(
        self,
        method: str,
        url: str,
        body: Optional[str] = None
    ) -> Dict[str, str]:
        """Firma una solicitud HTTP (implementación simplificada)"""
        import hashlib
        import base64
        from datetime import timezone
        
        headers = {"Content-Type": "application/json"}
        
        # Timestamp para evitar replay attacks
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Crear contenido a firmar
        content_to_sign = f"{method}\n{url}\n{timestamp}"
        if body:
            content_digest = hashlib.sha256(body.encode()).digest()
            content_to_sign += f"\n{base64.b64encode(content_digest).decode()}"
        
        # Firmar
        signature_bytes = self.private_key.sign(content_to_sign.encode())
        signature_b64 = base64.b64encode(signature_bytes).decode()
        
        # Headers de firma
        headers["Signature"] = f'keyId="{self.client_key_id}",algorithm="ed25519",signature="{signature_b64}"'
        headers["Signature-Input"] = f'sig1=();created={timestamp}'
        
        return headers
    
    def _generate_nonce(self) -> str:
        """Genera un nonce para la solicitud interactiva"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def close(self):
        """Cierra el cliente HTTP"""
        self.client.close()


if __name__ == "__main__":
    print("⚠️  Este es un módulo de biblioteca.")
    print("    Mira los ejemplos en la carpeta 'examples/' para uso práctico.")
