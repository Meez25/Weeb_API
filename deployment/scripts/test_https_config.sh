#!/bin/bash

# Script de validation de la configuration HTTPS
# Usage: bash test_https_config.sh yourdomain.com

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'affichage
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Vérifier les arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <domain>"
    echo "Exemple: $0 yourdomain.com"
    exit 1
fi

DOMAIN=$1
URL="https://$DOMAIN"

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════╗
║     Test de Configuration HTTPS - Weeb_API       ║
╚═══════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "Test du domaine: $DOMAIN"

# 1. Test de résolution DNS
print_header "1. Résolution DNS"
if host $DOMAIN > /dev/null 2>&1; then
    IP=$(host $DOMAIN | grep "has address" | awk '{print $4}' | head -n 1)
    print_success "DNS résolu: $DOMAIN → $IP"
else
    print_error "Impossible de résoudre $DOMAIN"
    exit 1
fi

# 2. Test de connectivité port 443
print_header "2. Connectivité HTTPS (Port 443)"
if timeout 5 bash -c "</dev/tcp/$DOMAIN/443" 2>/dev/null; then
    print_success "Port 443 ouvert et accessible"
else
    print_error "Port 443 non accessible"
    exit 1
fi

# 3. Test de redirection HTTP → HTTPS
print_header "3. Redirection HTTP → HTTPS"
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -L "http://$DOMAIN" --max-time 10)
if [ "$HTTP_RESPONSE" == "200" ] || [ "$HTTP_RESPONSE" == "301" ] || [ "$HTTP_RESPONSE" == "302" ]; then
    FINAL_URL=$(curl -s -o /dev/null -w "%{url_effective}" -L "http://$DOMAIN" --max-time 10)
    if [[ $FINAL_URL == https://* ]]; then
        print_success "Redirection HTTP → HTTPS active"
    else
        print_warning "HTTP accessible mais pas de redirection vers HTTPS"
    fi
else
    print_warning "Réponse HTTP: $HTTP_RESPONSE"
fi

# 4. Test du certificat SSL
print_header "4. Certificat SSL/TLS"
CERT_INFO=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer 2>/dev/null)

if [ $? -eq 0 ]; then
    print_success "Certificat SSL valide"
    
    # Date d'expiration
    EXPIRY=$(echo "$CERT_INFO" | grep "notAfter" | cut -d= -f2)
    print_info "Expire le: $EXPIRY"
    
    # Émetteur
    ISSUER=$(echo "$CERT_INFO" | grep "issuer" | cut -d= -f2-)
    if [[ $ISSUER == *"Let's Encrypt"* ]]; then
        print_success "Émetteur: Let's Encrypt"
    else
        print_info "Émetteur: $ISSUER"
    fi
else
    print_error "Erreur lors de la vérification du certificat"
fi

# 5. Test des protocoles SSL/TLS
print_header "5. Protocoles SSL/TLS"

# TLS 1.3
if openssl s_client -tls1_3 -connect $DOMAIN:443 </dev/null 2>/dev/null | grep -q "Protocol.*TLSv1.3"; then
    print_success "TLS 1.3 supporté"
else
    print_warning "TLS 1.3 non supporté"
fi

# TLS 1.2
if openssl s_client -tls1_2 -connect $DOMAIN:443 </dev/null 2>/dev/null | grep -q "Protocol.*TLSv1.2"; then
    print_success "TLS 1.2 supporté"
else
    print_error "TLS 1.2 non supporté"
fi

# TLS 1.1 (devrait être désactivé)
if openssl s_client -tls1_1 -connect $DOMAIN:443 </dev/null 2>/dev/null | grep -q "Protocol.*TLSv1.1"; then
    print_warning "TLS 1.1 supporté (non recommandé, désactiver)"
else
    print_success "TLS 1.1 désactivé (bon)"
fi

# TLS 1.0 (devrait être désactivé)
if openssl s_client -tls1 -connect $DOMAIN:443 </dev/null 2>/dev/null | grep -q "Protocol.*TLSv1"; then
    print_error "TLS 1.0 supporté (VULNÉRABLE, désactiver immédiatement)"
else
    print_success "TLS 1.0 désactivé (bon)"
fi

# 6. Test des en-têtes de sécurité
print_header "6. En-têtes de Sécurité HTTP"

HEADERS=$(curl -s -I "$URL" --max-time 10)

# HSTS
if echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
    HSTS_VALUE=$(echo "$HEADERS" | grep -i "Strict-Transport-Security" | cut -d: -f2-)
    print_success "HSTS activé:$HSTS_VALUE"
    
    if echo "$HSTS_VALUE" | grep -qi "includeSubDomains"; then
        print_success "  - includeSubDomains: oui"
    else
        print_warning "  - includeSubDomains: non (recommandé)"
    fi
    
    if echo "$HSTS_VALUE" | grep -qi "preload"; then
        print_success "  - preload: oui"
    else
        print_info "  - preload: non"
    fi
else
    print_error "HSTS absent (CRITIQUE)"
fi

# X-Frame-Options
if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
    XFO=$(echo "$HEADERS" | grep -i "X-Frame-Options" | cut -d: -f2-)
    print_success "X-Frame-Options:$XFO"
else
    print_warning "X-Frame-Options absent"
fi

# X-Content-Type-Options
if echo "$HEADERS" | grep -qi "X-Content-Type-Options"; then
    print_success "X-Content-Type-Options présent"
else
    print_warning "X-Content-Type-Options absent"
fi

# X-XSS-Protection
if echo "$HEADERS" | grep -qi "X-XSS-Protection"; then
    print_success "X-XSS-Protection présent"
else
    print_info "X-XSS-Protection absent"
fi

# Content-Security-Policy
if echo "$HEADERS" | grep -qi "Content-Security-Policy"; then
    print_success "Content-Security-Policy présent"
else
    print_warning "Content-Security-Policy absent (recommandé)"
fi

# Referrer-Policy
if echo "$HEADERS" | grep -qi "Referrer-Policy"; then
    print_success "Referrer-Policy présent"
else
    print_info "Referrer-Policy absent"
fi

# 7. Test de l'API
print_header "7. Test de l'API Django"

# Test endpoint de base
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/api/posts/" --max-time 10)
if [ "$API_RESPONSE" == "200" ]; then
    print_success "API accessible (200 OK)"
elif [ "$API_RESPONSE" == "301" ] || [ "$API_RESPONSE" == "302" ]; then
    print_info "API redirige (code $API_RESPONSE)"
elif [ "$API_RESPONSE" == "403" ]; then
    print_warning "API retourne 403 (vérifier ALLOWED_HOSTS)"
else
    print_error "API retourne code $API_RESPONSE"
fi

# Test CORS (si applicable)
CORS_RESPONSE=$(curl -s -H "Origin: https://example.com" -I "$URL/api/posts/" --max-time 10)
if echo "$CORS_RESPONSE" | grep -qi "Access-Control-Allow-Origin"; then
    print_info "CORS configuré"
else
    print_info "CORS non détecté dans la réponse"
fi

# 8. Résumé et recommandations
print_header "8. Résumé"

echo -e "\n${BLUE}Liens utiles:${NC}"
echo "• SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "• Security Headers: https://securityheaders.com/?q=$DOMAIN"
echo "• HSTS Preload: https://hstspreload.org/?domain=$DOMAIN"

print_header "Recommandations"

if ! echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
    echo "⚠ Activer HSTS dans Nginx"
fi

if ! echo "$HEADERS" | grep -qi "Content-Security-Policy"; then
    echo "⚠ Ajouter Content-Security-Policy"
fi

if ! openssl s_client -tls1_3 -connect $DOMAIN:443 </dev/null 2>/dev/null | grep -q "Protocol.*TLSv1.3"; then
    echo "⚠ Activer TLS 1.3 dans Nginx"
fi

echo -e "\n${GREEN}✓ Test de configuration HTTPS terminé${NC}\n"
