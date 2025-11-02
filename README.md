# 🌐 Práctica OpenPayments e Interledger

Proyecto de desarrollo para trabajar con **OpenPayments** e **Interledger Protocol (ILP)** en Python.

Basado en el material de aprendizaje sobre interoperabilidad en pagos digitales.

## 📚 Contexto

Este proyecto implementa los conceptos aprendidos en las clases sobre:

- **Interledger**: La "autopista" que mueve valor entre sistemas distintos
- **OpenPayments**: La "API" que permite operar sobre Interledger
- **Firma de mensajes HTTP**: Usando llaves Ed25519 para autenticidad
- **Protocolo GNAP**: Para autorización y tokens de acceso
- **API RESTful**: Recursos como quotes, payments, accounts

## 🛠️ Requisitos Previos

- **Python 3.12** (gestionado con `mise`)
- **mise** (para gestión de versiones)
- Cuenta en [Interledger Test Wallet](https://wallet.interledger-test.dev)

## 🚀 Instalación Rápida

### Opción 1: Usando el script de ayuda (Recomendado)

```powershell
# 1. Verificar entorno
.\run.ps1 verify

# 2. Instalar dependencias (si hace falta)
.\run.ps1 install

# 3. Generar llaves
.\run.ps1 keys

# 4. Configurar wallet
.\run.ps1 setup
```

### Opción 2: Instalación manual

```powershell
# 1. Confiar en el directorio
mise trust

# 2. Instalar Python 3.12
mise install

# 3. Instalar dependencias
mise exec -- python -m pip install --upgrade pip
mise exec -- python -m pip install -r requirements.txt

# 4. Generar llaves
mise exec -- python examples/01_generate_keys.py

# 5. Configurar .env
Copy-Item .env.example .env
# Editar .env con tu wallet address
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# (Primero genera las llaves - ver siguiente sección)
```

## 🔐 Generación de Llaves

### Paso 1: Generar par de llaves Ed25519

```bash
mise exec -- python examples/01_generate_keys.py
```

Esto creará:
- `keys/key-1_private.pem` - Tu llave privada (¡NUNCA la compartas!)
- `keys/key-1_public.pem` - Tu llave pública
- `keys/public_keys.json` - Llave pública en formato JWK

### Paso 2: Obtener tu Wallet Address

1. Visita [wallet.interledger-test.dev](https://wallet.interledger-test.dev)
2. Crea una cuenta de prueba
3. Copia tu **Wallet Address** (ejemplo: `https://ilp.rafiki.money/alice`)

### Paso 3: Configurar .env

Edita el archivo `.env` con tus datos:

```env
WALLET_ADDRESS=https://ilp.rafiki.money/tu-wallet
PRIVATE_KEY_PATH=keys/key-1_private.pem
PUBLIC_KEY_PATH=keys/key-1_public.pem
KEY_ID=key-1
```

## 📖 Ejemplos de Uso

### Usando el script de ayuda (run.ps1)

```powershell
# Ver todos los comandos disponibles
.\run.ps1 help

# Verificar configuración
.\run.ps1 verify

# Generar llaves
.\run.ps1 keys

# Consultar wallet
.\run.ps1 wallet

# Crear cotización
.\run.ps1 quote

# Flujo completo
.\run.ps1 flow
```

### Usando mise directamente

```powershell
# Ejemplo 1: Generar Llaves
mise exec -- python examples/01_generate_keys.py

# Ejemplo 2: Consultar Wallet Info
mise exec -- python examples/02_get_wallet_info.py

# Ejemplo 3: Crear Cotización (Quote)
mise exec -- python examples/03_create_quote.py

# Ejemplo 4: Flujo completo
mise exec -- python examples/04_complete_flow.py
```

## 📁 Estructura del Proyecto

```
practicaOPInteledger/
├── src/
│   ├── __init__.py
│   ├── key_manager.py          # Gestión de llaves Ed25519
│   └── openpayments_client.py  # Cliente HTTP para OpenPayments
├── examples/
│   ├── 01_generate_keys.py     # Generar llaves
│   ├── 02_get_wallet_info.py   # Consultar wallet
│   └── 03_create_quote.py      # Crear cotización
├── keys/                        # Llaves (git-ignored)
├── .mise.toml                   # Configuración de mise
├── .env.example                 # Variables de entorno ejemplo
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## 🔑 Conceptos Clave

### Wallet Address
- Es pública, como un email pero para dinero
- Formato URL: `https://ilp.rafiki.money/usuario`
- No expone información sensible

### Llaves Ed25519
- **Privada**: Se mantiene segura en tu backend, firma cada solicitud
- **Pública**: Se publica en formato JWK para verificación
- **Key ID**: Identificador único para rotar llaves

### Quote (Cotización)
- Define monto, comisiones y conversión antes de pagar
- Transparencia total: sin cargos ocultos
- Debe aprobarse antes de ejecutar el pago

### Flujo de Pago

1. **Solicitar Quote** con monto y wallet destino
2. **Revisar cotización** (monto final, comisiones, expiration)
3. **Crear pago** usando el Quote ID
4. **Autorizar** con GNAP (tokens de acceso)
5. **Ejecutar** el pago sobre Interledger

## 🧪 Ambiente de Desarrollo

Este proyecto usa **mise** para:
- ✅ Gestión automática de versiones de Python
- ✅ Creación automática de entorno virtual
- ✅ Aislamiento del proyecto

## 📚 Recursos

- [OpenPayments Documentation](https://openpayments.dev)
- [Interledger Protocol](https://interledger.org)
- [Test Wallet](https://wallet.interledger-test.dev)
- [GNAP Protocol](https://datatracker.ietf.org/doc/html/draft-ietf-gnap-core-protocol)

## 🔒 Seguridad

- ❌ **NUNCA** commitees llaves privadas al repositorio
- ✅ El directorio `keys/` está en `.gitignore`
- ✅ Usa `.env` para credenciales (también ignorado)
- ✅ Las llaves públicas SÍ pueden compartirse

## 📝 Notas

Este proyecto es para **desarrollo y aprendizaje**. Para producción:

1. Usa secretos seguros (Azure Key Vault, AWS Secrets, etc.)
2. Implementa rotación de llaves
3. Agrega logging y monitoreo
4. Valida todas las entradas
5. Implementa rate limiting

## 👤 Autor

Desarrollo basado en las notas de aprendizaje sobre OpenPayments e Interledger.

## 📄 Licencia

MIT
