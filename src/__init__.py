"""
Paquete principal para trabajar con OpenPayments e Interledger.

Basado en las notas de aprendizaje sobre:
- Interoperabilidad en pagos digitales (Clases 1-5)
- API RESTful de OpenPayments (Clases 6-7)
- Firma y verificación con llaves Ed25519 (Clase 8)
- Configuración de billetera de prueba (Clase 9)
- Flujos y arquitectura de OpenPayments (Clase 10)
- Protocolo GNAP para autorización (Clase 11)
- Recursos y autorización de pagos (Clase 12)
"""

from .key_manager import KeyManager
from .openpayments_client import OpenPaymentsClient
from .gnap_client import GNAPClient, AccessRight, GrantRequest, AccessToken
from .resources_client import ResourceClient, IncomingPayment, OutgoingPayment

__all__ = [
    "KeyManager",
    "OpenPaymentsClient",
    "GNAPClient",
    "AccessRight",
    "GrantRequest",
    "AccessToken",
    "ResourceClient",
    "IncomingPayment",
    "OutgoingPayment",
]
__version__ = "0.2.0"
