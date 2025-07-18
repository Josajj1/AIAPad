import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.slide import slide_bp
from src.routes.auth import auth_bp, init_jwt
from src.routes.upload import upload_bp
from src.utils.monitoring import monitoring_bp
from src.utils.rate_limiting import init_rate_limiter
from src.utils.cache import cache

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB max file size

# Configurar CORS para permitir requisições do frontend
CORS(app, origins="*")

# Inicializar JWT
jwt = init_jwt(app)

# Inicializar rate limiter
limiter = init_rate_limiter(app)

# Inicializar cache
cache.init_app(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(slide_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(monitoring_bp, url_prefix='/api')

# Configurar banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Configurar upload
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/tmp/aiapad/uploads')

db.init_app(app)
with app.app_context():
    # Criar diretórios necessários
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.environ.get('LOG_DIR', '/tmp/aiapad/logs'), exist_ok=True)
    
    db.create_all()
    
    # Criar usuário admin padrão se não existir
    from src.models.user import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@aiapad.com',
            first_name='Administrador',
            last_name='Sistema',
            user_type='admin',
            institution='AIAPad',
            is_verified=True
        )
        admin_user.set_password('admin123')  # TODO: Alterar senha padrão
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin criado: admin/admin123")

# Configurar logging para produção
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Configurar log de aplicação
    log_dir = os.environ.get('LOG_DIR', '/tmp/aiapad/logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'aiapad.log'), 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('AIAPad startup')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Servir frontend React"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(error):
    """Handler para 404 - servir frontend para SPA routing"""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    db.session.rollback()
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    # Desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Produção via WSGI
    application = app

