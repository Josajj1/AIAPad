# AIAPad - Guia de Início Rápido

## Instalação em 5 Minutos

### 1. Preparação do Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Baixar instalador
wget https://github.com/aiapad/installer/archive/main.zip
unzip main.zip
cd aiapad-installer-main
```

### 2. Configuração

Edite o arquivo `install.sh` e configure:

```bash
DOMAIN="lip.fm.usp.br"
SERVER_IP="143.107.178.21"
```

### 3. Instalação

```bash
chmod +x install.sh
sudo ./install.sh
```

### 4. Primeiro Acesso

1. Acesse: https://lip.fm.usp.br
2. Login: `admin`
3. Senha: `admin123`
4. **IMPORTANTE:** Altere a senha imediatamente!

## Primeiros Passos

### Upload de Lâmina

1. Clique na aba "Upload"
2. Arraste arquivo .svs, .tiff ou .ndpi
3. Aguarde processamento
4. Lâmina aparecerá no Dashboard

### Visualização

1. Clique na lâmina no Dashboard
2. Use mouse wheel para zoom
3. Arraste para navegar
4. Clique direito para anotações

### Análise de IA

1. Selecione região de interesse
2. Clique "Analisar com IA"
3. Escolha tipo de análise
4. Aguarde resultados

## Comandos Úteis

```bash
# Status dos serviços
sudo supervisorctl status

# Logs da aplicação
tail -f /opt/aiapad/logs/aiapad.log

# Backup manual
sudo /opt/aiapad/backup.sh

# Reiniciar aplicação
sudo supervisorctl restart aiapad-backend

# Verificar saúde do sistema
curl https://lip.fm.usp.br/api/health
```

## Solução de Problemas Rápidos

### Aplicação não carrega
```bash
sudo supervisorctl restart aiapad-backend
sudo systemctl reload nginx
```

### Erro de upload
```bash
# Verificar espaço em disco
df -h /opt/aiapad

# Limpar uploads incompletos
curl -X POST -H "Authorization: Bearer <token>" \
  https://lip.fm.usp.br/api/upload/cleanup
```

### Esqueci a senha
```bash
cd /opt/aiapad/backend
source venv/bin/activate
python -c "
from src.main import app, db
from src.models.user import User
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.set_password('nova_senha')
    db.session.commit()
"
```

## Próximos Passos

1. **Segurança:** Altere senhas padrão
2. **Usuários:** Crie contas para sua equipe
3. **Backup:** Configure backup automático
4. **Monitoramento:** Configure alertas
5. **Treinamento:** Treine usuários no sistema

## Suporte

- **Email:** admin@aiapad.com
- **Documentação:** Consulte AIAPad_Documentation.md
- **Logs:** `/opt/aiapad/logs/`

