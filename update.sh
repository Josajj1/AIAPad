#!/bin/bash

# AIAPad - Script de Atualização
# Atualiza o sistema AIAPad para uma nova versão

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
BACKUP_DIR="/opt/aiapad/backups"

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

check_installation() {
    if [[ ! -d "$AIAPAD_HOME" ]]; then
        log_error "AIAPad não está instalado"
        exit 1
    fi
    
    if ! id "$AIAPAD_USER" &>/dev/null; then
        log_error "Usuário $AIAPAD_USER não encontrado"
        exit 1
    fi
}

create_backup() {
    log_info "Criando backup antes da atualização..."
    
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/aiapad_pre_update_$DATE.tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    # Parar serviços
    supervisorctl stop aiapad-backend
    
    # Criar backup
    tar -czf "$BACKUP_FILE" \
        --exclude="*/node_modules" \
        --exclude="*/venv" \
        --exclude="*/logs/*" \
        --exclude="*/uploads/chunks" \
        "$AIAPAD_HOME"
    
    log_success "Backup criado: $BACKUP_FILE"
}

update_system() {
    log_info "Atualizando sistema operacional..."
    
    apt update -y
    apt upgrade -y
    
    log_success "Sistema atualizado"
}

download_new_version() {
    log_info "Baixando nova versão..."
    
    # Criar diretório temporário
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Simular download da nova versão
    # Na prática, seria de um repositório Git ou arquivo de release
    log_info "Simulando download da nova versão..."
    
    # Copiar arquivos atualizados (exemplo)
    if [[ -d "/home/ubuntu/aiapad-backend" ]]; then
        cp -r /home/ubuntu/aiapad-backend ./backend-new
    fi
    
    if [[ -d "/home/ubuntu/aiapad-frontend" ]]; then
        cp -r /home/ubuntu/aiapad-frontend ./frontend-new
    fi
    
    log_success "Nova versão baixada"
}

update_backend() {
    log_info "Atualizando backend..."
    
    cd "$TEMP_DIR"
    
    if [[ -d "backend-new" ]]; then
        # Preservar configurações
        cp "$AIAPAD_HOME/backend/config.py" ./backend-new/ 2>/dev/null || true
        cp -r "$AIAPAD_HOME/backend/database" ./backend-new/ 2>/dev/null || true
        
        # Backup do backend atual
        mv "$AIAPAD_HOME/backend" "$AIAPAD_HOME/backend.old"
        
        # Instalar nova versão
        mv ./backend-new "$AIAPAD_HOME/backend"
        chown -R "$AIAPAD_USER:$AIAPAD_USER" "$AIAPAD_HOME/backend"
        
        # Atualizar dependências
        cd "$AIAPAD_HOME/backend"
        sudo -u "$AIAPAD_USER" bash -c "source venv/bin/activate && pip install -r requirements.txt"
        
        # Executar migrações de banco de dados
        sudo -u "$AIAPAD_USER" bash -c "source venv/bin/activate && python -c 'from src.main import app, db; app.app_context().push(); db.create_all()'"
        
        log_success "Backend atualizado"
    else
        log_warning "Nenhuma atualização de backend encontrada"
    fi
}

update_frontend() {
    log_info "Atualizando frontend..."
    
    cd "$TEMP_DIR"
    
    if [[ -d "frontend-new" ]]; then
        # Preservar configurações
        cp "$AIAPAD_HOME/frontend/.env.production" ./frontend-new/ 2>/dev/null || true
        
        # Backup do frontend atual
        mv "$AIAPAD_HOME/frontend" "$AIAPAD_HOME/frontend.old"
        
        # Instalar nova versão
        mv ./frontend-new "$AIAPAD_HOME/frontend"
        chown -R "$AIAPAD_USER:$AIAPAD_USER" "$AIAPAD_HOME/frontend"
        
        # Build da nova versão
        cd "$AIAPAD_HOME/frontend"
        sudo -u "$AIAPAD_USER" pnpm install
        sudo -u "$AIAPAD_USER" pnpm run build
        
        log_success "Frontend atualizado"
    else
        log_warning "Nenhuma atualização de frontend encontrada"
    fi
}

update_configurations() {
    log_info "Atualizando configurações..."
    
    # Verificar se há novas configurações do Nginx
    if [[ -f "$TEMP_DIR/nginx.conf" ]]; then
        cp "$TEMP_DIR/nginx.conf" /etc/nginx/sites-available/aiapad
        nginx -t && systemctl reload nginx
        log_success "Configuração do Nginx atualizada"
    fi
    
    # Verificar se há novas configurações do Supervisor
    if [[ -f "$TEMP_DIR/supervisor.conf" ]]; then
        cp "$TEMP_DIR/supervisor.conf" /etc/supervisor/conf.d/aiapad-backend.conf
        supervisorctl reread
        supervisorctl update
        log_success "Configuração do Supervisor atualizada"
    fi
}

restart_services() {
    log_info "Reiniciando serviços..."
    
    # Reiniciar aplicação
    supervisorctl restart aiapad-backend
    
    # Verificar status
    sleep 5
    if supervisorctl status aiapad-backend | grep -q "RUNNING"; then
        log_success "Aplicação reiniciada com sucesso"
    else
        log_error "Falha ao reiniciar aplicação"
        rollback
        exit 1
    fi
    
    # Recarregar Nginx
    systemctl reload nginx
    
    log_success "Serviços reiniciados"
}

rollback() {
    log_warning "Executando rollback..."
    
    # Parar serviços
    supervisorctl stop aiapad-backend
    
    # Restaurar backend
    if [[ -d "$AIAPAD_HOME/backend.old" ]]; then
        rm -rf "$AIAPAD_HOME/backend"
        mv "$AIAPAD_HOME/backend.old" "$AIAPAD_HOME/backend"
    fi
    
    # Restaurar frontend
    if [[ -d "$AIAPAD_HOME/frontend.old" ]]; then
        rm -rf "$AIAPAD_HOME/frontend"
        mv "$AIAPAD_HOME/frontend.old" "$AIAPAD_HOME/frontend"
    fi
    
    # Reiniciar serviços
    supervisorctl start aiapad-backend
    
    log_success "Rollback concluído"
}

cleanup() {
    log_info "Limpeza pós-atualização..."
    
    # Remover backups antigos (manter apenas os últimos 5)
    find "$BACKUP_DIR" -name "aiapad_pre_update_*.tar.gz" -type f | sort -r | tail -n +6 | xargs rm -f
    
    # Remover versões antigas se atualização foi bem-sucedida
    rm -rf "$AIAPAD_HOME/backend.old" 2>/dev/null || true
    rm -rf "$AIAPAD_HOME/frontend.old" 2>/dev/null || true
    
    # Limpar diretório temporário
    rm -rf "$TEMP_DIR" 2>/dev/null || true
    
    log_success "Limpeza concluída"
}

verify_update() {
    log_info "Verificando atualização..."
    
    # Verificar se serviços estão rodando
    if ! supervisorctl status aiapad-backend | grep -q "RUNNING"; then
        log_error "Backend não está rodando"
        return 1
    fi
    
    # Verificar se aplicação responde
    if ! curl -f http://localhost:5000/api/auth/me >/dev/null 2>&1; then
        log_warning "API não está respondendo (pode ser normal se não houver token)"
    fi
    
    # Verificar se frontend está acessível
    if [[ ! -f "$AIAPAD_HOME/frontend/dist/index.html" ]]; then
        log_error "Frontend não foi construído corretamente"
        return 1
    fi
    
    log_success "Verificação concluída"
}

show_summary() {
    log_success "Atualização concluída com sucesso!"
    echo
    echo "=== RESUMO DA ATUALIZAÇÃO ==="
    echo "Data: $(date)"
    echo "Backup criado: $BACKUP_FILE"
    echo
    echo "=== STATUS DOS SERVIÇOS ==="
    supervisorctl status aiapad-backend
    echo
    echo "=== PRÓXIMOS PASSOS ==="
    echo "1. Teste a aplicação: https://lip.fm.usp.br"
    echo "2. Verifique os logs: tail -f $AIAPAD_HOME/logs/backend.log"
    echo "3. Em caso de problemas, execute rollback manual"
    echo
    log_info "Atualização concluída!"
}

main() {
    echo "=== AIAPad - Atualização ==="
    echo
    
    check_root
    check_installation
    
    log_info "Iniciando atualização..."
    
    create_backup
    update_system
    download_new_version
    update_backend
    update_frontend
    update_configurations
    restart_services
    
    if verify_update; then
        cleanup
        show_summary
    else
        log_error "Verificação falhou, executando rollback"
        rollback
        exit 1
    fi
}

# Verificar argumentos
case "${1:-}" in
    --rollback)
        log_info "Executando rollback manual..."
        rollback
        exit 0
        ;;
    --help)
        echo "Uso: $0 [--rollback|--help]"
        echo "  --rollback  Executar rollback manual"
        echo "  --help      Mostrar esta ajuda"
        exit 0
        ;;
esac

main "$@"

