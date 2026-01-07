# HTTPS Deployment Guide - Weeb_API

This guide walks you through securely deploying your Django API with HTTPS/SSL.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Preparation](#server-preparation)
3. [SSL Certificate Installation](#ssl-certificate-installation)
4. [Application Configuration](#application-configuration)
5. [Gunicorn Deployment](#gunicorn-deployment)
6. [Nginx Configuration](#nginx-configuration)

---

## 🔧 Prerequisites

### Server

- Ubuntu 22.04 LTS (or equivalent)
- Root or sudo access
- Domain name pointing to your server
- Ports 80 and 443 open

### Software

- Python 3.10+
- PostgreSQL 14+
- Nginx
- Certbot (Let's Encrypt)

---

## 🖥️ Server Preparation

### 1. System Update

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Dependencies Installation

```bash
# Python and development tools
sudo apt install -y python3.11 python3.11-venv python3-pip python3-dev build-essential

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Nginx
sudo apt install -y nginx

# Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Other useful tools
sudo apt install -y git curl fail2ban
```

### 3. PostgreSQL Configuration

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE weebapi_db;
CREATE USER weebapi_user WITH PASSWORD 'your_secure_password';
ALTER ROLE weebapi_user SET client_encoding TO 'utf8';
ALTER ROLE weebapi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE weebapi_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE weebapi_db TO weebapi_user;
\q
```

### 4. Create System User

```bash
# Create user for the application
sudo useradd -m -s /bin/bash weebapi
sudo usermod -aG www-data weebapi
```

### 5. Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

---

## 🔐 SSL Certificate Installation

```bash
# Obtain SSL certificate with Let's Encrypt
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Certificates location: `/etc/letsencrypt/live/yourdomain.com/`

---

## ⚙️ Application Configuration

### 1. Clone Repository

```bash
# Navigate to web directory
sudo mkdir -p /var/www
cd /var/www

# Clone the project
sudo git clone https://github.com/Meez25/Weeb_API.git
sudo chown -R weebapi:www-data Weeb_API
```

### 2. Create Virtual Environment

```bash
cd /var/www/Weeb_API
sudo -u weebapi python3.11 -m venv venv
sudo -u weebapi venv/bin/pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install Python packages
sudo -u weebapi venv/bin/pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example file
sudo -u weebapi cp .env.example .env

# Edit .env file
sudo -u weebapi nano .env
```

Fill in the values:

```bash
# Generate new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update .env with your actual values
DJANGO_ENV=production
DJANGO_SECRET_KEY=your_generated_secret_key
DB_NAME=weebapi_db
DB_USER=weebapi_user
DB_PASSWORD=your_postgresql_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Prepare Django

```bash
cd weebapi

# Collect static files
sudo -u weebapi ../venv/bin/python manage.py collectstatic --settings=core.settings_production --noinput

# Apply migrations
sudo -u weebapi ../venv/bin/python manage.py migrate --settings=core.settings_production

# Create superuser
sudo -u weebapi ../venv/bin/python manage.py createsuperuser --settings=core.settings_production
```

### Create Necessary Directories (optionnal)

```bash
# Directories for logs
sudo mkdir -p /var/log/gunicorn
sudo chown -R weebapi:www-data /var/log/gunicorn

sudo mkdir -p /var/www/Weeb_API/logs
sudo chown -R weebapi:www-data /var/www/Weeb_API/logs

# Directories for files
sudo mkdir -p /var/www/Weeb_API/staticfiles
sudo mkdir -p /var/www/Weeb_API/media
sudo chown -R weebapi:www-data /var/www/Weeb_API/staticfiles
sudo chown -R weebapi:www-data /var/www/Weeb_API/media
```

---

# ⚠️MANUAL STEPS (all required files are in deployment/config/\*)

## Gunicorn Deployment

### 1. Create systemd Service

```bash
# Copy service file
sudo cp /var/www/Weeb_API/deployment/systemd/gunicorn.service /etc/systemd/system/

# Edit if necessary
sudo nano /etc/systemd/system/gunicorn.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Check status
sudo systemctl status gunicorn
```

### 2. Verify Gunicorn Socket

```bash
# Socket should exist
ls -la /var/www/Weeb_API/gunicorn.sock

# Test with curl
curl --unix-socket /var/www/Weeb_API/gunicorn.sock http://localhost/api/posts/
```

---

## Nginx Configuration

### 1. Copy Nginx Configuration

```bash
# Copy configuration file
sudo cp /var/www/Weeb_API/deployment/nginx/weebapi.conf /etc/nginx/sites-available/

# Edit to update domains
sudo nano /etc/nginx/sites-available/weebapi.conf
# Replace 'yourdomain.com' with your actual domain
```

**Required edits in `weebapi.conf`:**

- Replace all `yourdomain.com` with your domain
- Verify SSL certificate paths
- Verify paths to `gunicorn.sock`, `staticfiles/`, `media/`

### 2. Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/weebapi.conf /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

```bash
# Edit main configuration
sudo nano /etc/nginx/nginx.conf
```

Add in the `http` section:

```nginx
# Optimizations
client_body_buffer_size 128k;
client_max_body_size 10M;
keepalive_timeout 65;
send_timeout 5m;

# Gzip Compression
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript
           application/json application/javascript application/xml+rss;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```
