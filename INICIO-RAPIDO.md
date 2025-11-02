# 🚀 Guía de Inicio Rápido

## ¿Qué acabas de crear?

Un entorno de desarrollo completo en Python para trabajar con:
- **OpenPayments**: API para pagos interoperables
- **Interledger Protocol (ILP)**: La "autopista" que conecta sistemas de pago

## 📋 Checklist de Configuración

### ✅ Ya completado automáticamente:

- [x] Python 3.12 instalado con `mise`
- [x] Entorno virtual creado en `.venv`
- [x] Dependencias instaladas (httpx, cryptography, etc.)
- [x] Llaves Ed25519 generadas en `keys/`
- [x] Estructura del proyecto lista
- [x] Archivo `.env` creado

### ⏳ Pendiente (lo haces tú):

- [ ] Crear cuenta en [wallet.interledger-test.dev](https://wallet.interledger-test.dev)
- [ ] Obtener tu **Wallet Address**
- [ ] Configurar WALLET_ADDRESS en `.env`

## 🎯 Primeros Pasos

### 1. Verifica que todo esté bien

```powershell
.\run.ps1 verify
```

Deberías ver todo en verde ✅ excepto WALLET_ADDRESS.

### 2. Obtén tu Wallet Address

1. Ve a https://wallet.interledger-test.dev
2. Haz clic en "Sign Up" o "Create Account"
3. Completa el registro
4. En tu dashboard, busca tu **Wallet Address**
   - Se verá algo como: `https://ilp.rafiki.money/tunombre`

### 3. Configura tu .env

Abre el archivo `.env` y actualiza esta línea:

```env
WALLET_ADDRESS=https://ilp.rafiki.money/tunombre
```

Guarda el archivo.

### 4. Verifica de nuevo

```powershell
.\run.ps1 verify
```

Ahora TODO debería estar en verde ✅

## 🧪 Prueba los Ejemplos

### Ejemplo 1: Ver info de tu wallet

```powershell
.\run.ps1 wallet
```

Esto consultará la información pública de tu wallet usando la API.

### Ejemplo 2: Crear una cotización

Para este necesitas **dos wallets**:
- La tuya (ya la tienes)
- Otra de prueba (crea una segunda cuenta o pide a alguien más)

```powershell
.\run.ps1 quote
```

El script te pedirá:
1. Wallet address del receptor
2. Monto a enviar
3. Moneda

Y te devolverá una cotización con:
- ✅ Quote ID
- ✅ Monto exacto que enviarás
- ✅ Monto exacto que recibirá
- ✅ Comisiones (si las hay)
- ✅ Fecha de expiración

### Ejemplo 3: Flujo completo

```powershell
.\run.ps1 flow
```

Este ejemplo te guía por todo el proceso de crear un pago.

## 🔑 Conceptos Clave que Estás Usando

### 1. **Wallet Address** (de tus notas Clase-08)
- Es pública, como un email pero para dinero
- Formato: `https://ilp.rafiki.money/usuario`
- No expone información sensible

### 2. **Llaves Ed25519** (de tus notas Clase-08)
- **Privada**: Firma cada solicitud HTTP (en `keys/key-1_private.pem`)
- **Pública**: Se publica para verificación (en `keys/public_keys.json`)
- **Key ID**: Identifica qué llave usaste

### 3. **Quote (Cotización)** (de tus notas Clase-06)
- Define monto, comisiones y conversión ANTES de pagar
- Transparencia total: sin cargos ocultos
- Expira después de un tiempo

### 4. **API RESTful** (de tus notas Clase-06)
- Recursos: `quotes`, `payments`, `accounts`
- Métodos: GET (obtener), POST (crear), PUT (actualizar), DELETE (eliminar)

### 5. **GNAP** (de tus notas Clase-06)
- Protocolo para autorización
- Usa tokens de acceso
- Protege recursos sin compartir contraseñas

## 📚 Estructura de Archivos

```
practicaOPInteledger/
├── run.ps1                    # 🎮 Script de ayuda (usa este!)
├── verify.py                  # ✅ Verifica configuración
├── setup.py                   # ⚙️  Asistente de setup
│
├── src/                       # 📦 Código fuente
│   ├── key_manager.py         # Gestión de llaves Ed25519
│   └── openpayments_client.py # Cliente HTTP para OpenPayments
│
├── examples/                  # 📖 Ejemplos prácticos
│   ├── 01_generate_keys.py    # Generar llaves
│   ├── 02_get_wallet_info.py  # Consultar wallet
│   ├── 03_create_quote.py     # Crear cotización
│   └── 04_complete_flow.py    # Flujo completo
│
├── keys/                      # 🔐 Tus llaves (PRIVADO!)
│   ├── key-1_private.pem      # ⛔ NUNCA compartir
│   ├── key-1_public.pem       # ✅ Pública
│   └── public_keys.json       # ✅ Para publicar en servidor
│
├── .env                       # ⚙️  Variables de entorno
├── .mise.toml                 # 🔧 Configuración de mise
├── requirements.txt           # 📦 Dependencias Python
└── README.md                  # 📘 Documentación completa
```

## 🎓 Flujo de un Pago (según tus notas)

1. **Cliente** crea solicitud de pago
2. **Cliente** la firma con llave privada
3. **Servidor OpenPayments** descarga tu llave pública
4. **Servidor** verifica la firma (autenticidad + integridad)
5. **Servidor** crea el Quote con detalles transparentes
6. **Usuario** revisa y aprueba
7. **Autorización** vía GNAP (tokens de acceso)
8. **Pago** se ejecuta sobre Interledger
9. **Liquidación** entre los conectores

## 🆘 Solución de Problemas

### Error: "No se encontró Python"
```powershell
mise install
```

### Error: "Import 'httpx' could not be resolved"
```powershell
.\run.ps1 install
```

### Error: "WALLET_ADDRESS no configurada"
1. Crea cuenta en wallet.interledger-test.dev
2. Copia tu wallet address
3. Edita `.env` y pega tu wallet address

### Error: "No se encontraron las llaves"
```powershell
.\run.ps1 keys
```

## 🎯 Siguiente Nivel

Una vez que domines estos ejemplos, puedes:

1. **Implementar GNAP completo** - Autorización real con tokens
2. **Manejar estados de pago** - pending, completed, failed
3. **Webhooks** - Notificaciones en tiempo real
4. **Rotación de llaves** - Múltiples Key IDs
5. **Producción** - Usar secretos seguros, monitoring, rate limiting

## 📞 Recursos

- **OpenPayments Docs**: https://openpayments.dev
- **Interledger**: https://interledger.org
- **Test Wallet**: https://wallet.interledger-test.dev
- **Tus notas**: `../Aprendizaje flash/`

## ✅ Estás listo!

Ejecuta:
```powershell
.\run.ps1 verify
```

Si todo está en verde ✅, ¡comienza a experimentar!

---

💡 **Tip**: Usa `.\run.ps1 help` para ver todos los comandos disponibles.
