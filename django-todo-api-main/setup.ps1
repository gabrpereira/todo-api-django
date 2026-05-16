#!/usr/bin/env pwsh
# =============================================================================
# setup.ps1 - Script de configuração do Task Manager API
# Execute: .\setup.ps1
# =============================================================================

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Task Manager API - Setup Automatico      " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# --- Verifica Python ---
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $pythonCmd = $cmd
            Write-Host "[OK] Python encontrado: $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "[ERRO] Python 3 nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale o Python 3.10+ em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Marque a opcao 'Add Python to PATH' durante a instalacao." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# --- Cria ambiente virtual ---
Write-Host ""
Write-Host "[1/4] Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "      Ambiente virtual ja existe, pulando criacao." -ForegroundColor Gray
} else {
    & $pythonCmd -m venv venv
    Write-Host "      Ambiente virtual criado com sucesso!" -ForegroundColor Green
}

# --- Ativa o venv ---
Write-Host ""
Write-Host "[2/4] Ativando ambiente virtual..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
    Write-Host "      Ambiente virtual ativado!" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Nao foi possivel ativar o venv." -ForegroundColor Red
    exit 1
}

# --- Instala dependências ---
Write-Host ""
Write-Host "[3/4] Instalando dependencias (requirements.txt)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "      Dependencias instaladas!" -ForegroundColor Green

# --- Roda as migrations ---
Write-Host ""
Write-Host "[4/4] Executando migracoes do banco de dados..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "      Banco de dados configurado!" -ForegroundColor Green

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "   Setup concluido com sucesso!             " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para rodar os testes:" -ForegroundColor Cyan
Write-Host "   python manage.py test tasks --verbosity=2" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar o servidor:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "API disponivel em: http://127.0.0.1:8000/api/" -ForegroundColor Cyan
Write-Host "Admin em:          http://127.0.0.1:8000/admin/" -ForegroundColor Cyan
Write-Host ""
