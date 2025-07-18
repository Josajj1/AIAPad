#!/bin/bash

# AIAPad - Script de Desinstalação
# Remove completamente o sistema AIAPad

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
AIAPAD_USER="aiapad"
AIAPAD_HOME="/opt/aiapad"
DOMAIN="lip.fm.usp.br"

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

confirm_uninstall() {
    echo "=== AIAPad - Desinstalação ==="
    echo
    log_warning "ATENÇÃO: Esta operação irá remover completamente o AIAPad!"
    echo
    echo "Será removido:"
    echo "- Aplicação e dados ($AIAPAD_HOME)"
    echo "- Usuário do sistema ($AIAPAD_USER)"
    echo "- Configurações do Nginx"
    echo "- Certificados SSL"
    echo "- Configurações do Supervisor"
    echo "- Regras do firewall"
    echo
    read -p "Tem certeza que deseja continuar? (digite 'CONFIRMAR' para prosseguir): " confirm
    
    if [[ "$confirm" != "CONFIRMAR" ]]; then
        log_info "Desinstalação cancelada"
        exit 0
    fi
}

create_backup() {
    log_info "Criando backup antes da desinstalação..."
    
    BACKUP_DIR="/tmp/aiapad_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [[ -d "$AIAPAD_HOME" ]]; then
        tar -czf "$BACKUP_DIR/aiapad_data.tar.gz" "$AIAPAD_HOME" 2>/dev/null || true
    fi
    
    # Backup das configurações
    cp /etc/nginx/sites-available/aiapad "$BACKUP_DIR/" 2>/dev/null || true
    cp /etc/supervisor/conf.d/aiapad-backend.conf "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Backup criado em: $BACKUP_DIR"
}

stop_services() {
    log_info "Parando serviços..."
    
    # Parar aplicação
    supervisorctl stop aiapad-backend 2>/dev/null || true
    
    # Parar serviços
    systemctl stop nginx 2>/dev/null || true
    systemctl stop supervisor 2>/dev/null || true
    
    log_success "Serviços parados"
}

remove_nginx_config() {
    log_info "Removendo configuração do Nginx..."
    
    # Remover site
    rm -f /etc/nginx/sites-enabled/aiapad
    rm -f /etc/nginx/sites-available/aiapad
    
    # Restaurar site padrão
    if [[ -f /etc/nginx/sites-available/default ]]; then
        ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
    fi
    
    # Testar configuração
    nginx -t && systemctl reload nginx
    
    log_success "Configuração do Nginx removida"
}

remove_ssl() {
    log_info "Removendo certificados SSL..."
    
    # Remover certificados do Let's Encrypt
    certbot delete --cert-name "$DOMAIN" --non-interactive 2>/dev/null || true
    
    # Remover cron job
    crontab -l | grep -v "certbot renew" | crontab - 2>/dev/null || true
    
    log_success "Certificados SSL removidos"
}

remove_supervisor_config() {
    log_info "Removendo configuração do Supervisor..."
    
    # Remover configuração
    rm -f /etc/supervisor/conf.d/aiapad-backend.conf
    
    # Recarregar
    supervisorctl reread
    supervisorctl update
    
    log_success "Configuração do Supervisor removida"
}

remove_application() {
    log_info "Removendo aplicação..."
    
    # Remover diretório da aplicação
    if [[ -d "$AIAPAD_HOME" ]]; then
        rm -rf "$AIAPAD_HOME"
    fi
    
    log_success "Aplicação removida"
}

remove_user() {
    log_info "Removendo usuário do sistema..."
    
    # Remover usuário
    if id "$AIAPAD_USER" &>/dev/null; then
        userdel -r "$AIAPAD_USER" 2>/dev/null || true
    fi
    
    log_success "Usuário removido"
}

remove_firewall_rules() {
    log_info "Removendo regras do firewall..."
    
    # Resetar UFW (opcional)
    read -p "Deseja resetar completamente o firewall? (y/N): " reset_fw
    if [[ "$reset_fw" =~ ^[Yy]$ ]]; then
        ufw --force reset
        log_success "Firewall resetado"
    else
        log_info "Firewall mantido"
    fi
}

remove_packages() {
    log_info "Removendo pacotes (opcional)..."
    
    read -p "Deseja remover pacotes instalados? (y/N): " remove_pkgs
    if [[ "$remove_pkgs" =~ ^[Yy]$ ]]; then
        apt remove -y \
            nginx \
            supervisor \
            certbot \
            python3-certbot-nginx \
            openslide-tools \
            libopenslide0 \
            fail2ban 2>/dev/null || true
        
        apt autoremove -y
        log_success "Pacotes removidos"
    else
        log_info "Pacotes mantidos"
    fi
}

cleanup() {
    log_info "Limpeza final..."
    
    # Remover logs
    rm -rf /var/log/aiapad* 2>/dev/null || true
    
    # Remover arquivos temporários
    rm -rf /tmp/aiapad* 2>/dev/null || true
    
    log_success "Limpeza concluída"
}

show_summary() {
    log_success "Desinstalação concluída!"
    echo
    echo "=== RESUMO ==="
    echo "- Aplicação removida: $AIAPAD_HOME"
    echo "- Usuário removido: $AIAPAD_USER"
    echo "- Configurações removidas"
    echo "- Certificados SSL removidos"
    echo
    if [[ -n "$BACKUP_DIR" ]]; then
        echo "Backup disponível em: $BACKUP_DIR"
    fi
    echo
    log_info "O sistema foi completamente removido"
}

main() {
    check_root
    confirm_uninstall
    
    create_backup
    stop_services
    remove_supervisor_config
    remove_nginx_config
    remove_ssl
    remove_application
    remove_user
    remove_firewall_rules
    remove_packages
    cleanup
    
    show_summary
}

main "$@"

