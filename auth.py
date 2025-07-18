from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt, verify_jwt_in_request
)
from datetime import datetime, timedelta
import uuid
from src.models.user import User, UserSession, db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def init_jwt(app):
    """Inicializar JWT"""
    app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'  # TODO: Usar variável de ambiente
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    jwt = JWTManager(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Verificar se token foi revogado"""
        jti = jwt_payload['jti']
        # TODO: Implementar blacklist de tokens
        return False
    
    return jwt

def require_permission(permission):
    """Decorator para verificar permissões"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'Usuário não encontrado ou inativo'}), 401
            
            if not user.has_permission(permission):
                return jsonify({'error': 'Permissão insuficiente'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar novo usuário"""
    data = request.json
    
    # Validar dados obrigatórios
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Nome de usuário já existe'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já está em uso'}), 400
    
    # Validar tipo de usuário
    valid_user_types = ['admin', 'doctor', 'researcher', 'student']
    if data['user_type'] not in valid_user_types:
        return jsonify({'error': 'Tipo de usuário inválido'}), 400
    
    try:
        # Criar novo usuário
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=data['user_type'],
            institution=data.get('institution'),
            department=data.get('department'),
            registration_number=data.get('registration_number')
        )
        
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Fazer login"""
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    # Buscar usuário
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Conta desativada'}), 401
    
    try:
        # Atualizar último login
        user.last_login = datetime.utcnow()
        
        # Criar tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Criar sessão
        session = UserSession(
            user_id=user.id,
            session_token=str(uuid.uuid4()),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_sensitive=True),
            'session_id': session.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro no login: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Fazer logout"""
    try:
        current_user_id = get_jwt_identity()
        
        # Desativar sessões ativas do usuário
        UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).update({'is_active': False})
        
        db.session.commit()
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro no logout: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar token de acesso"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'Usuário não encontrado ou inativo'}), 401
        
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao renovar token: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obter informações do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter usuário: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Alterar senha"""
    data = request.json
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Senha atual incorreta'}), 400
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao alterar senha: {str(e)}'}), 500

@auth_bp.route('/users', methods=['GET'])
@require_permission('manage_users')
def list_users():
    """Listar usuários (apenas admins)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar usuários: {str(e)}'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@require_permission('manage_users')
def get_user(user_id):
    """Obter usuário específico (apenas admins)"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter usuário: {str(e)}'}), 500

@auth_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@require_permission('manage_users')
def activate_user(user_id):
    """Ativar/desativar usuário (apenas admins)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        user.is_active = data.get('is_active', True)
        db.session.commit()
        
        status = 'ativado' if user.is_active else 'desativado'
        return jsonify({
            'message': f'Usuário {status} com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao alterar status do usuário: {str(e)}'}), 500

@auth_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Obter sessões ativas do usuário"""
    try:
        current_user_id = get_jwt_identity()
        sessions = UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter sessões: {str(e)}'}), 500

@auth_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def revoke_session(session_id):
    """Revogar sessão específica"""
    try:
        current_user_id = get_jwt_identity()
        session = UserSession.query.filter_by(
            id=session_id,
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Sessão não encontrada'}), 404
        
        session.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Sessão revogada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao revogar sessão: {str(e)}'}), 500

