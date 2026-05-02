# ==============================================================================
# Weeb API - Script d'installation pour le développement local (Windows)
# ==============================================================================
# Ce script automatise la mise en place de l'environnement de développement.
# A executer depuis la racine du repo weeb_API.
#
# Usage : .\setup.ps1
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==> Verification de Python..." -ForegroundColor Cyan
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.12+ est requis. Installation : https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-Host "==> Creation de l'environnement virtuel..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    python -m venv venv
} else {
    Write-Host "    venv existe deja, on saute cette etape."
}

Write-Host "==> Activation de l'environnement virtuel..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

Write-Host "==> Installation des dependances..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "==> Verification du fichier .env..." -ForegroundColor Cyan
if (-not (Test-Path "weebapi\.env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" "weebapi\.env"
        Write-Host "    .env cree depuis .env.example. Pensez a le completer si besoin." -ForegroundColor Yellow
    }
}

Write-Host "==> Application des migrations..." -ForegroundColor Cyan
Set-Location weebapi
python manage.py migrate

Write-Host ""
Write-Host "Installation terminee." -ForegroundColor Green
Write-Host "Pour creer un superutilisateur : python manage.py createsuperuser"
Write-Host "Pour lancer le serveur de developpement : python manage.py runserver"
