#!/bin/bash

# Script de déploiement automatisé pour Weeb_API
# Usage: sudo bash deploy.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Démarrage du déploiement de Weeb_API..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="/var/www/Weeb_API"
VENV_DIR="$PROJECT_DIR/venv"
APP_DIR="$PROJECT_DIR/weebapi"
APP_USER="weebapi"
APP_GROUP="www-data"

# Fonction pour afficher les messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Vérifier que le script est exécuté en tant que root
if [ "$EUID" -ne 0 ]; then 
    print_error "Ce script doit être exécuté avec sudo"
    exit 1
fi

# 1. Mise à jour du code
print_info "Mise à jour du code depuis Git..."
cd $PROJECT_DIR
sudo -u $APP_USER git pull origin main
print_success "Code mis à jour"

# 2. Activer l'environnement virtuel et installer les dépendances
print_info "Installation des dépendances Python..."
sudo -u $APP_USER $VENV_DIR/bin/pip install -r requirements.txt --quiet
sudo -u $APP_USER $VENV_DIR/bin/pip install gunicorn psycopg2-binary python-dotenv --quiet
print_success "Dépendances installées"

# 3. Vérifier que le fichier .env existe
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_error "Le fichier .env n'existe pas. Copiez .env.example et configurez-le."
    exit 1
fi

# 4. Collecter les fichiers statiques
print_info "Collection des fichiers statiques..."
cd $APP_DIR
sudo -u $APP_USER $VENV_DIR/bin/python manage.py collectstatic \
    --settings=core.settings_production \
    --noinput \
    --clear
print_success "Fichiers statiques collectés"

# 5. Appliquer les migrations
print_info "Application des migrations de base de données..."
sudo -u $APP_USER $VENV_DIR/bin/python manage.py migrate \
    --settings=core.settings_production \
    --noinput
print_success "Migrations appliquées"

# 6. Vérifier la configuration Django
print_info "Vérification de la configuration Django..."
sudo -u $APP_USER $VENV_DIR/bin/python manage.py check \
    --settings=core.settings_production \
    --deploy
print_success "Configuration Django vérifiée"

# 7. Tester la configuration Nginx
print_info "Test de la configuration Nginx..."
if nginx -t; then
    print_success "Configuration Nginx valide"
else
    print_error "Configuration Nginx invalide"
    exit 1
fi

# 8. Redémarrer Gunicorn
print_info "Redémarrage de Gunicorn..."
systemctl restart gunicorn
sleep 2

if systemctl is-active --quiet gunicorn; then
    print_success "Gunicorn redémarré avec succès"
else
    print_error "Échec du redémarrage de Gunicorn"
    systemctl status gunicorn
    exit 1
fi

# 9. Recharger Nginx
print_info "Rechargement de Nginx..."
systemctl reload nginx
print_success "Nginx rechargé"

# 10. Vérifier que le service répond
print_info "Vérification de la disponibilité du service..."
sleep 2
if curl -s -o /dev/null -w "%{http_code}" --unix-socket $PROJECT_DIR/gunicorn.sock http://localhost/api/posts/ | grep -q "200\|301\|302"; then
    print_success "Service disponible"
else
    print_error "Le service ne répond pas correctement"
    exit 1
fi

# 11. Afficher les logs récents
print_info "Logs récents de Gunicorn:"
tail -n 5 /var/log/gunicorn/weebapi_error.log

echo ""
print_success "🎉 Déploiement terminé avec succès!"
echo ""
print_info "Commandes utiles:"
echo "  - Logs Gunicorn: sudo tail -f /var/log/gunicorn/weebapi_error.log"
echo "  - Logs Nginx: sudo tail -f /var/log/nginx/weebapi_error.log"
echo "  - Status Gunicorn: sudo systemctl status gunicorn"
echo "  - Redémarrer Gunicorn: sudo systemctl restart gunicorn"
