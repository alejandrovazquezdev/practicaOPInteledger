# 🚀 Scripts de ayuda para OpenPayments & Interledger
# Ejecuta: .\run.ps1 <comando>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "OpenPayments & Interledger - Comandos Disponibles" -ForegroundColor Green
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Configuracion inicial:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 verify      - Verificar que todo este configurado"
    Write-Host "  .\run.ps1 keys        - Generar llaves Ed25519"
    Write-Host "  .\run.ps1 setup       - Configurar variables de entorno"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 wallet      - Consultar informacion de wallet"
    Write-Host "  .\run.ps1 quote       - Crear una cotizacion de pago"
    Write-Host "  .\run.ps1 flow        - Ejecutar flujo completo de pago"
    Write-Host ""
    Write-Host "Otros:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 install     - Instalar/actualizar dependencias"
    Write-Host "  .\run.ps1 clean       - Limpiar archivos temporales"
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
}

function Run-Command {
    param([string]$Script)
    
    Write-Host "Ejecutando: $Script" -ForegroundColor Cyan
    Write-Host ""
    & mise exec -- python $Script
}

switch ($Command.ToLower()) {
    "help" {
        Show-Help
    }
    "verify" {
        Run-Command "verify.py"
    }
    "keys" {
        Run-Command "examples/01_generate_keys.py"
    }
    "setup" {
        Run-Command "setup.py"
    }
    "wallet" {
        Run-Command "examples/02_get_wallet_info.py"
    }
    "quote" {
        Run-Command "examples/03_create_quote.py"
    }
    "flow" {
        Run-Command "examples/04_complete_flow.py"
    }
    "install" {
        Write-Host "Instalando dependencias..." -ForegroundColor Cyan
        Write-Host ""
        & mise exec -- python -m pip install --upgrade pip
        & mise exec -- python -m pip install -r requirements.txt
        Write-Host ""
        Write-Host "Dependencias instaladas" -ForegroundColor Green
    }
    "clean" {
        Write-Host "Limpiando archivos temporales..." -ForegroundColor Cyan
        
        if (Test-Path "__pycache__") {
            Remove-Item -Recurse -Force "__pycache__"
            Write-Host "  Eliminado __pycache__" -ForegroundColor Gray
        }
        
        if (Test-Path "src/__pycache__") {
            Remove-Item -Recurse -Force "src/__pycache__"
            Write-Host "  Eliminado src/__pycache__" -ForegroundColor Gray
        }
        
        Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
        Write-Host "  Eliminados archivos .pyc" -ForegroundColor Gray
        
        Write-Host ""
        Write-Host "Limpieza completada" -ForegroundColor Green
    }
    default {
        Write-Host "Comando desconocido: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
