"""
Paquete principal para trabajar con OpenPayments e Interledger.

Basado en las notas de aprendizaje sobre:
- Interoperabilidad en pagos digitales
- API RESTful de OpenPayments
- Firma y verificación con llaves Ed25519
- Protocolo GNAP para autorización
"""

from .key_manager import KeyManager
from .openpayments_client import OpenPaymentsClient

__all__ = ["KeyManager", "OpenPaymentsClient"]
__version__ = "0.1.0"
