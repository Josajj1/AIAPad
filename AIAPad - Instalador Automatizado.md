# AIAPad - Instalador Automatizado

Sistema de Análise de Lâminas Anatomopatológicas com instalação automatizada para servidores Debian/Ubuntu.

## Requisitos do Sistema

### Sistema Operacional
- Debian 10+ ou Ubuntu 18.04+
- Arquitetura x86_64
- Mínimo 4GB RAM
- Mínimo 50GB de espaço em disco
- Conexão com internet

### Permissões
- Acesso root (sudo)
- Portas 80 e 443 disponíveis
- Domínio configurado (DNS)

## Instalação

### 1. Download do Instalador

```bash
# Baixar o instalador
wget https://github.com/aiapad/installer/archive/main.zip
unzip main.zip
cd aiapad-installer-main
```

### 2. Configuração

Edite o arquivo `install.sh` e configure:

```bash
# Configurações principais
DOMAIN="seu-dominio.com"
SERVER_IP="seu.ip.do.servidor"
```

### 3. Execução

```bash
# Tornar executável
chmod +x install.sh

# Executar instalação
sudo ./install.sh
```

## Componentes Instalados

### Backend (Flask)
- **Localização**: `/opt/aiapad/backend`
- **Porta**: 5000 (interno)
- **Banco de dados**: SQLite
- **Logs**: `/opt/aiapad/logs/backend.log`

### Frontend (React)
- **Localização**: `/opt/aiapad/frontend`
- **Build**: `/opt/aiapad/frontend/dist`
- **Servido por**: Nginx

### Servidor Web (Nginx)
- **Configuração**: `/etc/nginx/sites-available/aiapad`
- **SSL**: Let's Encrypt (automático)
- **Proxy reverso**: Backend API

### Supervisor
- **Configuração**: `/etc/supervisor/conf.d/aiapad-backend.conf`
- **Gerencia**: Processo do backend Flask

### Segurança
- **Firewall**: UFW configurado
- **Fail2Ban**: Proteção contra ataques
- **SSL**: Certificados automáticos

## Credenciais Padrão

```
Usuário: admin
Senha: admin123
```

**⚠️ IMPORTANTE**: Altere a senha padrão imediatamente após a instalação!

## Comandos Úteis

### Gerenciamento de Serviços

```bash
# Status dos serviços
sudo supervisorctl status

# Reiniciar backend
sudo supervisorctl restart aiapad-backend

# Logs do backend
sudo tail -f /opt/aiapad/logs/backend.log

# Status do Nginx
sudo systemctl status nginx

# Recarregar Nginx
sudo systemctl reload nginx
```

### Backup e Restore

```bash
# Backup manual
sudo /opt/aiapad/backup.sh

# Listar backups
ls -la /opt/aiapad/backups/

# Restore (exemplo)
sudo tar -xzf /opt/aiapad/backups/aiapad_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

### SSL/Certificados

```bash
# Status dos certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew

# Teste de renovação
sudo certbot renew --dry-run
```

### Monitoramento

```bash
# Uso de disco
df -h /opt/aiapad

# Uso de memória
free -h

# Processos do AIAPad
ps aux | grep aiapad

# Conexões ativas
sudo netstat -tulpn | grep :443
```

## Atualização

```bash
# Executar script de atualização
sudo ./update.sh

# Rollback em caso de problemas
sudo ./update.sh --rollback
```

## Desinstalação

```bash
# Executar script de desinstalação
sudo ./uninstall.sh
```

**⚠️ ATENÇÃO**: A desinstalação remove todos os dados!

## Estrutura de Diretórios

```
/opt/aiapad/
├── backend/           # Aplicação Flask
│   ├── src/          # Código fonte
│   ├── venv/         # Ambiente virtual Python
│   ├── database/     # Banco de dados SQLite
│   └── config.py     # Configurações
├── frontend/         # Aplicação React
│   ├── src/          # Código fonte
│   └── dist/         # Build de produção
├── uploads/          # Arquivos de lâminas
├── logs/            # Logs da aplicação
├── backups/         # Backups automáticos
└── backup.sh        # Script de backup
```

## Configuração de DNS

Configure seu DNS para apontar o domínio para o IP do servidor:

```
Tipo: A
Nome: seu-dominio.com
Valor: seu.ip.do.servidor
TTL: 300
```

## Firewall

Portas abertas automaticamente:
- **22**: SSH
- **80**: HTTP (redirect para HTTPS)
- **443**: HTTPS

## Troubleshooting

### Backend não inicia

```bash
# Verificar logs
sudo tail -f /opt/aiapad/logs/backend.log

# Verificar configuração
sudo supervisorctl status aiapad-backend

# Reiniciar manualmente
cd /opt/aiapad/backend
sudo -u aiapad bash -c "source venv/bin/activate && python src/main.py"
```

### Erro de SSL

```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew --force-renewal

# Verificar configuração do Nginx
sudo nginx -t
```

### Problemas de upload

```bash
# Verificar espaço em disco
df -h /opt/aiapad

# Verificar permissões
ls -la /opt/aiapad/uploads

# Ajustar permissões
sudo chown -R aiapad:aiapad /opt/aiapad/uploads
```

### Performance

```bash
# Monitorar recursos
htop

# Verificar logs de erro do Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar conexões
sudo ss -tulpn | grep :443
```

## Suporte

Para suporte técnico:
- **Email**: admin@aiapad.com
- **Documentação**: https://docs.aiapad.com
- **Issues**: https://github.com/aiapad/issues

## Licença

Este software é distribuído sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**AIAPad v1.0** - Sistema de Análise de Lâminas Anatomopatológicas

