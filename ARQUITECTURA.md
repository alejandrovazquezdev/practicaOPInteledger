# 🏗️ Arquitectura de OpenPayments e Interledger

Documentación basada en las Clases 1-12 sobre interoperabilidad de pagos digitales.

## 📐 Componentes de la Arquitectura

### 1. **Account Servicing Entity (ACE)** 🏦

La entidad que administra cuentas financieras de los clientes.

**Qué es:**
- Bancos
- Proveedores de dinero móvil
- Billeteras digitales
- Fintechs

**Responsabilidades:**
- Gestionar cuentas de usuarios
- Realizar liquidación real de pagos
- Cumplir con KYC (Know Your Customer)
- Cumplir con AML (Anti-Money Laundering)
- Implementar OpenPayments API

**Ejemplo:** El banco de Bob, la billetera digital de Alicia

---

### 2. **Wallet Address Server** 📬

Servidor que guarda información de direcciones de billetera.

**Qué hace:**
- Almacena direcciones públicas de billetera
- Expone endpoints públicos para consulta
- Proporciona información como:
  - Moneda de la cuenta
  - URLs de Authorization Server
  - URLs de Resource Server

**Formato de dirección:**
```
https://ilp.rafiki.money/bob
https://example.com/alicia
```

**Datos que expone:**
```json
{
  "id": "https://ilp.rafiki.money/bob",
  "assetCode": "USD",
  "assetScale": 2,
  "authServer": "https://auth.rafiki.money",
  "resourceServer": "https://backend.rafiki.money"
}
```

**Es público:** ✅ Punto de inicio del sistema

---

### 3. **Authorization Server (AS)** 🔐

Servidor que otorga permisos a aplicaciones cliente.

**Protocolo:** GNAP (Grant Negotiation and Authorization Protocol)

**Qué hace:**
- Recibe solicitudes de concesión (grants)
- Valida identidad del cliente
- Emite tokens de acceso
- Gestiona permisos y límites
- Coordina con Identity Provider

**Tipos de concesiones:**

#### No Interactivas
```json
{
  "access_token": [
    {
      "type": "incoming-payment",
      "actions": ["create", "read"]
    }
  ],
  "client": "music-site-client"
}
```

**Uso:** Acceso automatizado entre servicios

#### Interactivas
```json
{
  "access_token": [
    {
      "type": "outgoing-payment",
      "actions": ["create"]
    }
  ],
  "client": "music-site-client",
  "interact": {
    "start": ["redirect"],
    "finish": {
      "method": "redirect",
      "uri": "https://app.com/callback"
    }
  }
}
```

**Uso:** Requiere consentimiento del usuario

**Respuesta:**
```json
{
  "access_token": {
    "value": "token-abc123",
    "manage": "https://auth.server/token/xyz",
    "expires_in": 3600
  }
}
```

---

### 4. **Resource Server** 📦

Servidor que almacena y gestiona recursos de la API.

**Recursos que maneja:**
- Incoming Payments (pagos entrantes)
- Outgoing Payments (pagos salientes)
- Quotes (cotizaciones)

**Protección:** Requiere access token del AS

**Operaciones:**

#### Incoming Payment
```http
POST /incoming-payments
Authorization: GNAP <access_token>

{
  "walletAddress": "https://bank.com/bob",
  "incomingAmount": {
    "value": "1000",
    "assetCode": "USD",
    "assetScale": 2
  },
  "expiresAt": "2025-12-31T23:59:00Z",
  "metadata": {
    "description": "Pago por producto X"
  }
}
```

#### Quote
```http
POST /quotes
Authorization: GNAP <access_token>

{
  "walletAddress": "https://wallet.com/alicia",
  "receiver": "https://bank.com/bob",
  "method": "ILP"
}
```

#### Outgoing Payment
```http
POST /outgoing-payments
Authorization: GNAP <access_token>

{
  "walletAddress": "https://wallet.com/alicia",
  "quoteId": "https://wallet.com/quotes/abc123",
  "metadata": {
    "note": "Pago aprobado"
  }
}
```

---

### 5. **Identity Provider (IdP)** 👤

Proveedor que verifica identidad del usuario.

**Qué hace:**
- Autentica al usuario
- Obtiene consentimiento
- Redirige de vuelta al AS
- Valida sesión activa

**Flujo de consentimiento:**
```
1. AS genera URL de interacción
2. Usuario es redirigido al IdP
3. IdP autentica (contraseña, biometría, 2FA)
4. IdP muestra pantalla de consentimiento:
   - Monto: $10.00 USD
   - Receptor: Bob
   - Concepto: Canción
5. Usuario aprueba
6. IdP redirige al callback con código
7. AS finaliza concesión
8. AS emite access token
```

---

### 6. **Application Client** 💻

Cualquier software que consume la API de OpenPayments.

**Ejemplos:**
- Sitio de e-commerce
- App de streaming
- Plataforma de donaciones
- Sistema de facturación

**Requisitos:**
- Wallet Address pública
- Par de llaves Ed25519 (pública/privada)
- Key ID para identificar llaves
- Capacidad de firmar solicitudes HTTP

**Firma de solicitudes:**
```http
POST /resource
Signature-Input: sig1=();created=1234567890;keyid="key-1"
Signature: keyId="key-1",algorithm="ed25519",signature="abc123..."
Content-Type: application/json

{
  "walletAddress": "https://example.com/alice"
}
```

---

## 🔄 Flujo Completo de un Pago

### Escenario: Bob vende canción a Alicia

```
👨‍🎤 Bob (Receptor)
  └─ Banco con OpenPayments
     └─ Wallet: https://bank.com/bob

👩‍💼 Alicia (Remitente)
  └─ Billetera digital con OpenPayments
     └─ Wallet: https://wallet.com/alicia

🎼 Sitio de Música (Cliente)
  └─ Intermediario que usa API
```

### Paso a Paso

#### 1. Pago Entrante (Lado del Receptor)
```
Sitio → AS de Bob: "Permiso para crear incoming payment"
AS de Bob → Sitio: access_token_1

Sitio → Resource Server de Bob: 
  POST /incoming-payments
  Authorization: GNAP <access_token_1>
  {
    "walletAddress": "https://bank.com/bob",
    "incomingAmount": {"value": "500", "assetCode": "USD", "assetScale": 2}
  }

Resource Server → Sitio: 
  {
    "id": "https://bank.com/incoming-payments/xyz",
    "walletAddress": "https://bank.com/bob"
  }
```

#### 2. Cotización (Lado del Remitente)
```
Sitio → AS de Alicia: "Permiso para crear quote"
AS de Alicia → Sitio: access_token_2

Sitio → Resource Server de Alicia:
  POST /quotes
  Authorization: GNAP <access_token_2>
  {
    "walletAddress": "https://wallet.com/alicia",
    "receiver": "https://bank.com/bob",
    "method": "ILP"
  }

Resource Server → Sitio:
  {
    "id": "https://wallet.com/quotes/abc",
    "sendAmount": {"value": "530", "assetCode": "USD", "assetScale": 2},
    "receiveAmount": {"value": "500", "assetCode": "USD", "assetScale": 2},
    "fees": "30",
    "expiresAt": "2025-11-02T12:30:00Z"
  }
```

#### 3. Autorización Interactiva (Consentimiento)
```
Sitio → AS de Alicia: 
  "Permiso INTERACTIVO para outgoing payment"
  {
    "access_token": [{"type": "outgoing-payment", "actions": ["create"]}],
    "interact": {"start": ["redirect"], "finish": {...}}
  }

AS de Alicia → Sitio:
  {
    "interact": {
      "redirect": "https://idp.wallet.com/authorize?code=xyz"
    },
    "continue": {
      "access_token": {"value": "continue-token"},
      "uri": "https://as.wallet.com/continue"
    }
  }

Sitio → Alicia: Redirige a IdP

Alicia → IdP: Autentica (biometría/contraseña)
IdP → Alicia: Muestra pantalla de confirmación
Alicia: ✅ Aprueba pago de $5.30
IdP → Sitio: Redirige con código de autorización

Sitio → AS de Alicia: 
  POST /continue
  Authorization: GNAP <continue-token>

AS de Alicia → Sitio:
  {
    "access_token": {"value": "access_token_3"}
  }
```

#### 4. Pago Saliente (Ejecución)
```
Sitio → Resource Server de Alicia:
  POST /outgoing-payments
  Authorization: GNAP <access_token_3>
  {
    "walletAddress": "https://wallet.com/alicia",
    "quoteId": "https://wallet.com/quotes/abc"
  }

Resource Server → Sitio:
  {
    "id": "https://wallet.com/outgoing-payments/def",
    "sentAmount": {"value": "530", "assetCode": "USD", "assetScale": 2}
  }
```

#### 5. Liquidación (Interledger)
```
Billetera de Alicia → Conectores ILP → Banco de Bob

- OpenPayments decide: ¿Se hace la transferencia? ✅
- ILP ejecuta: Enruta paquetes de valor
- ACEs liquidan: Mueven el dinero real

Resultado:
  Alicia: -$5.30 USD
  Bob: +$5.00 USD
  Comisiones: $0.30 USD
```

---

## 🔑 Conceptos Clave

### Wallet Address vs Payment Pointer

**Wallet Address (URL):**
```
https://ilp.rafiki.money/bob
```
- Formato técnico
- Usado en API
- Es un endpoint

**Payment Pointer (Alias):**
```
$ilp.rafiki.money/bob
```
- Formato amigable
- Fácil de compartir
- Apunta a wallet address

### Modalidades de Pago

**FixReceive:**
- El receptor recibe cantidad exacta
- El remitente paga cantidad + comisiones

**FixSend:**
- El remitente envía cantidad exacta
- El receptor recibe cantidad - comisiones

### Seguridad

**Llaves Asimétricas:**
- Privada: Firma solicitudes (NUNCA compartir)
- Pública: Verifica firmas (publicar en JSON)

**Validación:**
1. Cliente firma con llave privada
2. Servidor obtiene llave pública del cliente
3. Servidor verifica firma
4. Si válida → solicitud auténtica e íntegra

---

## 📚 Mapeo a las Clases

| Componente | Clase(s) | Conceptos |
|------------|----------|-----------|
| ACE | 5, 10, 12 | Entidades reguladas, KYC, AML |
| Wallet Address | 5, 10, 12 | Direcciones públicas, endpoints |
| AS | 11 | GNAP, concesiones, tokens |
| Resource Server | 10, 12 | Recursos protegidos, API |
| IdP | 11, 12 | Autenticación, consentimiento |
| ILP | 2, 3, 4 | Paquetes, conectores, liquidación |
| Firma HTTP | 8, 11 | Ed25519, integridad, autenticidad |

---

## 🎯 Para Desarrolladores

### Checklist de Implementación

- [ ] Generar par de llaves Ed25519
- [ ] Obtener wallet address de prueba
- [ ] Publicar llave pública en JSON
- [ ] Implementar firma de solicitudes HTTP
- [ ] Solicitar concesiones al AS
- [ ] Crear incoming payments
- [ ] Crear quotes
- [ ] Manejar flujo interactivo para outgoing payments
- [ ] Probar con billeteras de prueba

### Herramientas Disponibles

**En este proyecto:**
- `KeyManager`: Genera y gestiona llaves Ed25519
- `GNAPClient`: Maneja concesiones y autorización
- `ResourceClient`: Crea recursos (payments, quotes)
- `OpenPaymentsClient`: Cliente HTTP general

**Endpoints de prueba:**
- https://wallet.interledger-test.dev
- https://rafiki.money

---

**¡Arquitectura completa implementada!** 🚀

Basado en Clases 1-12 de Interledger y OpenPayments.
