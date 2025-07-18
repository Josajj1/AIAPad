#!/bin/bash

# AIAPad - Sistema de Análise de Lâminas Anatomopatológicas
# Script de Instalação Automatizada
# Versão: 1.0
# Compatível com: Debian 10+, Ubuntu 18.04+

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
AIAPAD_USER="aiapad"
AIAPAD_HOME="/opt/aiapad"
DOMAIN="lip.fm.usp.br"
SERVER_IP="143.107.178.21"
PYTHON_VERSION="3.11"
NODE_VERSION="20"

# Funções auxiliares
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script deve ser executado como root (sudo)"
        exit 1
    fi
}

detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "Não foi possível detectar o sistema operacional"
        exit 1
    fi
    
    log_info "Sistema detectado: $OS $VER"
    
    # Verificar compatibilidade
    case $OS in
        "Debian GNU/Linux")
            if [[ $(echo "$VER >= 10" | bc -l) -eq 0 ]]; then
                log_error "Debian 10+ é necessário"
                exit 1
            fi
            PACKAGE_MANAGER="apt"
            ;;
        "Ubuntu")
            if [[ $(echo "$VER >= 18.04" | bc -l) -eq 0 ]]; then
                log_error "Ubuntu 18.04+ é necessário"
                exit 1
            fi
            PACKAGE_MANAGER="apt"
            ;;
        *)
            log_error "Sistema operacional não suportado: $OS"
            exit 1
            ;;
    esac
}

update_system() {
    log_info "Atualizando sistema..."
    $PACKAGE_MANAGER update -y
    $PACKAGE_MANAGER upgrade -y
    log_success "Sistema atualizado"
}

install_dependencies() {
    log_info "Instalando dependências do sistema..."
    
    # Dependências básicas
    $PACKAGE_MANAGER install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        unzip \
        supervisor \
        nginx \
        certbot \
        python3-certbot-nginx \
        sqlite3 \
        bc \
        htop \
        ufw \
        fail2ban
    
    # Dependências para OpenSlide
    $PACKAGE_MANAGER install -y \
        openslide-tools \
        libopenslide0 \
        libopenslide-dev \
        libvips \
        libvips-dev
    
    log_success "Dependências instaladas"
}

install_python() {
    log_info "Instalando Python $PYTHON_VERSION..."
    
    # Adicionar repositório deadsnakes para versões mais recentes
    add-apt-repository ppa:deadsnakes/ppa -y
    $PACKAGE_MANAGER update -y
    
    # Instalar Python
    $PACKAGE_MANAGER install -y \
        python$PYTHON_VERSION \
        python$PYTHON_VERSION-dev \
        python$PYTHON_VERSION-venv \
        python$PYTHON_VERSION-pip
    
    # Criar link simbólico
    ln -sf /usr/bin/python$PYTHON_VERSION /usr/local/bin/python3
    ln -sf /usr/bin/pip$PYTHON_VERSION /usr/local/bin/pip3
    
    log_success "Python $PYTHON_VERSION instalado"
}

install_nodejs() {
    log_info "Instalando Node.js $NODE_VERSION..."
    
    # Instalar NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    $PACKAGE_MANAGER install -y nodejs
    
    # Instalar pnpm
    npm install -g pnpm
    
    log_success "Node.js $NODE_VERSION instalado"
}

create_user() {
    log_info "Criando usuário do sistema..."
    
    # Criar usuário se não existir
    if ! id "$AIAPAD_USER" &>/dev/null; then
        useradd -r -m -d "$AIAPAD_HOME" -s /bin/bash "$AIAPAD_USER"
        log_success "Usuário $AIAPAD_USER criado"
    else
        log_warning "Usuário $AIAPAD_USER já existe"
    fi
    
    # Criar diretórios necessários
    mkdir -p "$AIAPAD_HOME"/{backend,frontend,uploads,logs,backups}
    chown -R "$AIAPAD_USER:$AIAPAD_USER" "$AIAPAD_HOME"
}

download_application() {
    log_info "Baixando aplicação AIAPad..."
    
    # Criar diretório temporário
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Simular download (na prática, seria de um repositório Git)
    log_info "Copiando arquivos da aplicação..."
    
    # Copiar backend
    cp -r /home/ubuntu/aiapad-backend/* "$AIAPAD_HOME/backend/"
    
    # Copiar frontend
    cp -r /home/ubuntu/aiapad-frontend/* "$AIAPAD_HOME/frontend/"
    
    # Ajustar permissões
    chown -R "$AIAPAD_USER:$AIAPAD_USER" "$AIAPAD_HOME"
    
    # Limpar
    rm -rf "$TEMP_DIR"
    
    log_success "Aplicação baixada"
}

setup_backend() {
    log_info "Configurando backend..."
    
    cd "$AIAPAD_HOME/backend"
    
    # Criar ambiente virtual
    sudo -u "$AIAPAD_USER" python3 -m venv venv
    
    # Instalar dependências
    sudo -u "$AIAPAD_USER" bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    # Criar configuração de produção
    cat > "$AIAPAD_HOME/backend/config.py" << EOF
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '$(openssl rand -hex 32)'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///$AIAPAD_HOME/backend/database/production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024  # 5GB
    UPLOAD_FOLDER = '$AIAPAD_HOME/uploads'
    JWT_SECRET_KEY = '$(openssl rand -hex 32)'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 dias
EOF
    
    # Criar banco de dados
    sudo -u "$AIAPAD_USER" bash -c "source venv/bin/activate && python -c 'from src.main import app, db; app.app_context().push(); db.create_all()'"
    
    log_success "Backend configurado"
}

setup_frontend() {
    log_info "Configurando frontend..."
    
    cd "$AIAPAD_HOME/frontend"
    
    # Instalar dependências
    sudo -u "$AIAPAD_USER" pnpm install
    
    # Criar configuração de produção
    cat > "$AIAPAD_HOME/frontend/.env.production" << EOF
VITE_API_URL=https://$DOMAIN/api
VITE_APP_TITLE=AIAPad - Sistema de Análise de Lâminas Anatomopatológicas
VITE_APP_VERSION=1.0.0
EOF
    
    # Build da aplicação
    sudo -u "$AIAPAD_USER" pnpm run build
    
    log_success "Frontend configurado"
}

setup_nginx() {
    log_info "Configurando Nginx..."
    
    # Criar configuração do site
    cat > "/etc/nginx/sites-available/aiapad" << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration (será configurado pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend
    location / {
        root $AIAPAD_HOME/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Upload configuration
        client_max_body_size 5G;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Upload progress
    location /upload-progress {
        upload_progress_json_output;
        report_uploads uploads;
    }
}
EOF
    
    # Ativar site
    ln -sf /etc/nginx/sites-available/aiapad /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Testar configuração
    nginx -t
    
    log_success "Nginx configurado"
}

setup_ssl() {
    log_info "Configurando SSL com Let's Encrypt..."
    
    # Parar nginx temporariamente
    systemctl stop nginx
    
    # Obter certificado
    certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN"
    
    # Iniciar nginx
    systemctl start nginx
    
    # Configurar renovação automática
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
    
    log_success "SSL configurado"
}

setup_supervisor() {
    log_info "Configurando Supervisor..."
    
    # Configuração do backend
    cat > "/etc/supervisor/conf.d/aiapad-backend.conf" << EOF
[program:aiapad-backend]
command=$AIAPAD_HOME/backend/venv/bin/python src/main.py
directory=$AIAPAD_HOME/backend
user=$AIAPAD_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$AIAPAD_HOME/logs/backend.log
environment=FLASK_ENV=production,PYTHONPATH=$AIAPAD_HOME/backend
EOF
    
    # Recarregar configuração
    supervisorctl reread
    supervisorctl update
    
    log_success "Supervisor configurado"
}

setup_firewall() {
    log_info "Configurando firewall..."
    
    # Configurar UFW
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Permitir SSH
    ufw allow ssh
    
    # Permitir HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Ativar firewall
    ufw --force enable
    
    log_success "Firewall configurado"
}

setup_fail2ban() {
    log_info "Configurando Fail2Ban..."
    
    # Configuração para Nginx
    cat > "/etc/fail2ban/jail.local" << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
EOF
    
    systemctl restart fail2ban
    
    log_success "Fail2Ban configurado"
}

create_backup_script() {
    log_info "Criando script de backup..."
    
    cat > "$AIAPAD_HOME/backup.sh" << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/aiapad/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="aiapad_backup_$DATE.tar.gz"

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

# Parar serviços
supervisorctl stop aiapad-backend

# Criar backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude="*/node_modules" \
    --exclude="*/venv" \
    --exclude="*/logs/*" \
    --exclude="*/uploads/chunks" \
    /opt/aiapad

# Reiniciar serviços
supervisorctl start aiapad-backend

# Manter apenas os últimos 7 backups
find "$BACKUP_DIR" -name "aiapad_backup_*.tar.gz" -mtime +7 -delete

echo "Backup criado: $BACKUP_FILE"
EOF
    
    chmod +x "$AIAPAD_HOME/backup.sh"
    chown "$AIAPAD_USER:$AIAPAD_USER" "$AIAPAD_HOME/backup.sh"
    
    # Agendar backup diário
    echo "0 2 * * * $AIAPAD_HOME/backup.sh" | crontab -u "$AIAPAD_USER" -
    
    log_success "Script de backup criado"
}

start_services() {
    log_info "Iniciando serviços..."
    
    # Iniciar e habilitar serviços
    systemctl enable nginx
    systemctl enable supervisor
    systemctl enable fail2ban
    
    systemctl start nginx
    systemctl start supervisor
    systemctl start fail2ban
    
    # Iniciar aplicação
    supervisorctl start aiapad-backend
    
    log_success "Serviços iniciados"
}

show_summary() {
    log_success "Instalação concluída com sucesso!"
    echo
    echo "=== RESUMO DA INSTALAÇÃO ==="
    echo "Domínio: https://$DOMAIN"
    echo "IP do servidor: $SERVER_IP"
    echo "Usuário do sistema: $AIAPAD_USER"
    echo "Diretório da aplicação: $AIAPAD_HOME"
    echo
    echo "=== CREDENCIAIS PADRÃO ==="
    echo "Usuário: admin"
    echo "Senha: admin123"
    echo
    echo "=== COMANDOS ÚTEIS ==="
    echo "Status dos serviços: supervisorctl status"
    echo "Logs do backend: tail -f $AIAPAD_HOME/logs/backend.log"
    echo "Backup manual: $AIAPAD_HOME/backup.sh"
    echo "Renovar SSL: certbot renew"
    echo
    echo "=== PRÓXIMOS PASSOS ==="
    echo "1. Altere a senha padrão do admin"
    echo "2. Configure DNS para apontar $DOMAIN para $SERVER_IP"
    echo "3. Teste o upload de uma lâmina"
    echo
    log_warning "IMPORTANTE: Altere as senhas padrão antes de usar em produção!"
}

# Função principal
main() {
    echo "=== AIAPad - Instalação Automatizada ==="
    echo
    
    check_root
    detect_os
    
    log_info "Iniciando instalação..."
    
    update_system
    install_dependencies
    install_python
    install_nodejs
    create_user
    download_application
    setup_backend
    setup_frontend
    setup_nginx
    setup_ssl
    setup_supervisor
    setup_firewall
    setup_fail2ban
    create_backup_script
    start_services
    
    show_summary
}

# Executar instalação
main "$@"

