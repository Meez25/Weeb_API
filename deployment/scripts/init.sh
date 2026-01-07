#!/bin/bash

# Script d'installation initiale de Weeb_API en production
# Usage: sudo bash initial_setup.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# Vérifier root
if [ "$EUID" -ne 0 ]; then 
    print_error "Ce script doit être exécuté avec sudo"
    exit 1
fi

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════╗
║   Installation Initiale Weeb_API - Production    ║
╚═══════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Variables
PROJECT_DIR="/var/www/Weeb_API"
VENV_DIR="$PROJECT_DIR/venv"
APP_DIR="$PROJECT_DIR/weebapi"
APP_USER="weebapi"
APP_GROUP="www-data"

# Demander des informations
print_header "Configuration"
read -p "Nom de domaine (ex: api.example.com): " DOMAIN
read -p "Nom de la base de données [weebapi_db]: " DB_NAME
DB_NAME=${DB_NAME:-weebapi_db}
read -p "Utilisateur PostgreSQL [weebapi_user]: " DB_USER
DB_USER=${DB_USER:-weebapi_user}
read -sp "Mot de passe PostgreSQL: " DB_PASSWORD
echo ""
read -p "Email pour Let's Encrypt: " ADMIN_EMAIL

# 1. Mise à jour système
print_header "1. Mise à jour du système"
apt update && apt upgrade -y
print_success "Système mis à jour"

# 2. Installation des dépendances
print_header "2. Installation des dépendances"
apt install -y python3.11 python3.11-venv python3-pip python3-dev \
    postgresql postgresql-contrib libpq-dev \
    nginx certbot python3-certbot-nginx \
    git curl build-essential fail2ban
print_success "Dépendances installées"

# 3. Configuration PostgreSQL
print_header "3. Configuration PostgreSQL"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
print_success "PostgreSQL configuré"

# 4. Créer utilisateur système
print_header "4. Création utilisateur système"
useradd -m -s /bin/bash $APP_USER 2>/dev/null || true
usermod -aG $APP_GROUP $APP_USER
print_success "Utilisateur $APP_USER créé"

# 5. Vérifier si le projet existe déjà
print_header "5. Installation de l'application"
if [ ! -d "$PROJECT_DIR" ]; then
    print_info "Clonage du dépôt..."
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/Meez25/Weeb_API.git
    chown -R $APP_USER:$APP_GROUP $PROJECT_DIR
    print_success "Dépôt cloné"
else
    print_info "Le répertoire existe déjà, mise à jour..."
    cd $PROJECT_DIR
    sudo -u $APP_USER git pull origin main
fi

# 6. Environnement virtuel
print_header "6. Création environnement virtuel"
sudo -u $APP_USER python3.11 -m venv $VENV_DIR
sudo -u $APP_USER $VENV_DIR/bin/pip install --upgrade pip
sudo -u $APP_USER $VENV_DIR/bin/pip install -r $PROJECT_DIR/requirements.txt
print_success "Environnement virtuel créé"

# 7. Configuration .env
print_header "7. Configuration des variables d'environnement"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    # Générer SECRET_KEY
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    cat > $PROJECT_DIR/.env << EOL
# Django Configuration
DJANGO_ENV=production
DJANGO_SECRET_KEY=$SECRET_KEY

# Database Configuration
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Domain Configuration
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Email Configuration (à configurer)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SERVER_EMAIL=noreply@$DOMAIN
EOL
    
    chown $APP_USER:$APP_GROUP $PROJECT_DIR/.env
    chmod 600 $PROJECT_DIR/.env
    print_success "Fichier .env créé"
else
    print_info "Fichier .env existe déjà, conservation de la configuration"
fi

# 8. Créer répertoires
print_header "8. Création des répertoires"
mkdir -p /var/log/gunicorn
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/staticfiles
mkdir -p $PROJECT_DIR/media
chown -R $APP_USER:$APP_GROUP /var/log/gunicorn
chown -R $APP_USER:$APP_GROUP $PROJECT_DIR/logs
chown -R $APP_USER:$APP_GROUP $PROJECT_DIR/staticfiles
chown -R $APP_USER:$APP_GROUP $PROJECT_DIR/media
print_success "Répertoires créés"

# 9. Django - Migrations et collectstatic
print_header "9. Configuration Django"
cd $APP_DIR
print_info "Collection des fichiers statiques..."
sudo -u $APP_USER $VENV_DIR/bin/python manage.py collectstatic --settings=core.settings_production --noinput

print_info "Application des migrations..."
sudo -u $APP_USER $VENV_DIR/bin/python manage.py migrate --settings=core.settings_production

print_success "Django configuré"

# 10. Configuration Gunicorn
print_header "10. Configuration Gunicorn"
cp $PROJECT_DIR/deployment/systemd/gunicorn.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn
print_success "Gunicorn configuré et démarré"

# 11. Certificat SSL
print_header "11. Obtention du certificat SSL"
print_info "Configuration Nginx temporaire pour Let's Encrypt..."

# Configuration Nginx temporaire
cat > /etc/nginx/sites-available/weebapi << EOL
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        return 200 "Weeb_API Setup";
    }
}
EOL

ln -sf /etc/nginx/sites-available/weebapi /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

print_info "Obtention du certificat SSL avec Let's Encrypt..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $ADMIN_EMAIL --agree-tos --non-interactive --redirect

print_success "Certificat SSL obtenu"

# 12. Configuration Nginx finale
print_header "12. Configuration Nginx finale"
cp $PROJECT_DIR/deployment/nginx/weebapi.conf /etc/nginx/sites-available/weebapi

# Remplacer yourdomain.com par le vrai domaine
sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/weebapi.conf

nginx -t && systemctl reload nginx
print_success "Nginx configuré"

# 13. Configuration Firewall
print_header "13. Configuration du firewall"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
print_success "Firewall configuré"

# 14. Configuration Fail2Ban
print_header "14. Configuration Fail2Ban"
cp $PROJECT_DIR/deployment/security/fail2ban-jail.local /etc/fail2ban/jail.local
sed -i "s/admin@yourdomain.com/admin@$DOMAIN/g" /etc/fail2ban/jail.local
sed -i "s/noreply@yourdomain.com/noreply@$DOMAIN/g" /etc/fail2ban/jail.local
systemctl enable fail2ban
systemctl restart fail2ban
print_success "Fail2Ban configuré"

# 15. Tests finaux
print_header "15. Tests et validation"

# Vérifier Gunicorn
if systemctl is-active --quiet gunicorn; then
    print_success "Gunicorn actif"
else
    print_error "Gunicorn n'est pas actif"
    systemctl status gunicorn
fi

# Vérifier Nginx
if systemctl is-active --quiet nginx; then
    print_success "Nginx actif"
else
    print_error "Nginx n'est pas actif"
fi

# Vérifier le site
sleep 2
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN | grep -q "200\|301\|302"; then
    print_success "Site accessible en HTTPS"
else
    print_warning "Site peut-être pas encore accessible (DNS?)"
fi

# Résumé
print_header "🎉 Installation Terminée"
echo ""
echo -e "${GREEN}✓ Weeb_API est installé et configuré !${NC}"
echo ""
echo -e "${BLUE}Informations importantes:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "• URL: https://$DOMAIN"
echo "• Base de données: $DB_NAME"
echo "• Utilisateur système: $APP_USER"
echo "• Répertoire: $PROJECT_DIR"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo "1. Créer un superutilisateur Django:"
echo "   cd $APP_DIR"
echo "   sudo -u $APP_USER $VENV_DIR/bin/python manage.py createsuperuser --settings=core.settings_production"
echo ""
echo "2. Tester votre site:"
echo "   • https://$DOMAIN"
echo "   • https://$DOMAIN/admin"
echo "   • https://$DOMAIN/api/posts/"
echo ""
echo "3. Vérifier la sécurité SSL:"
echo "   bash $PROJECT_DIR/deployment/test_https_config.sh $DOMAIN"
echo ""
echo "4. Pour les mises à jour futures:"
echo "   sudo bash $PROJECT_DIR/deployment/deploy.sh"
echo ""
echo -e "${BLUE}Logs utiles:${NC}"
echo "• Gunicorn: sudo journalctl -u gunicorn -f"
echo "• Nginx: sudo tail -f /var/log/nginx/weebapi_error.log"
echo "• Django: sudo tail -f $PROJECT_DIR/logs/django_errors.log"
echo ""
echo -e "${GREEN}Bon déploiement ! 🚀${NC}"
