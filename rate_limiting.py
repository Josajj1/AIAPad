from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity
import redis
import os

def get_user_id():
    """Obter ID do usuário para rate limiting personalizado"""
    try:
        user_id = get_jwt_identity()
        return str(user_id) if user_id else get_remote_address()
    except:
        return get_remote_address()

def init_rate_limiter(app):
    """Inicializar rate limiter"""
    
    # Configurar Redis se disponível, senão usar memória
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    try:
        # Tentar conectar ao Redis
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        storage_uri = redis_url
        app.logger.info("Rate limiting usando Redis")
    except:
        # Fallback para memória
        storage_uri = "memory://"
        app.logger.warning("Rate limiting usando memória (não recomendado para produção)")
    
    limiter = Limiter(
        app=app,
        key_func=get_user_id,
        storage_uri=storage_uri,
        default_limits=["1000 per hour", "100 per minute"],
        headers_enabled=True,
        swallow_errors=True
    )
    
    # Handler para quando limite é excedido
    @limiter.request_filter
    def exempt_health_checks():
        """Isentar health checks do rate limiting"""
        return request.endpoint in ['monitoring.health_check', 'monitoring.status']
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handler personalizado para rate limit exceeded"""
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': e.retry_after
        }), 429
    
    return limiter

# Decoradores personalizados para diferentes tipos de operações
def auth_rate_limit():
    """Rate limit para operações de autenticação"""
    return "5 per minute"

def upload_rate_limit():
    """Rate limit para uploads"""
    return "10 per hour"

def api_rate_limit():
    """Rate limit padrão para API"""
    return "100 per minute"

def admin_rate_limit():
    """Rate limit para operações administrativas"""
    return "200 per minute"

# Configurações de rate limiting por endpoint
RATE_LIMIT_CONFIG = {
    # Autenticação
    'auth.login': auth_rate_limit(),
    'auth.register': auth_rate_limit(),
    'auth.refresh': "20 per minute",
    'auth.change_password': "3 per minute",
    
    # Upload
    'upload.init_upload': upload_rate_limit(),
    'upload.upload_chunk': "1000 per hour",  # Muitos chunks por upload
    'upload.complete_upload': upload_rate_limit(),
    
    # Slides
    'slide.upload_slide': upload_rate_limit(),
    'slide.get_slides': api_rate_limit(),
    'slide.get_slide': api_rate_limit(),
    'slide.analyze_slide': "5 per minute",  # IA é custosa
    
    # Admin
    'auth.list_users': admin_rate_limit(),
    'monitoring.detailed_health': admin_rate_limit(),
    'monitoring.metrics': admin_rate_limit(),
}

def apply_rate_limits(limiter):
    """Aplicar rate limits específicos aos endpoints"""
    
    def get_limit_for_endpoint():
        """Obter limite específico para o endpoint atual"""
        endpoint = request.endpoint
        return RATE_LIMIT_CONFIG.get(endpoint, api_rate_limit())
    
    # Aplicar rate limits dinâmicos
    limiter.limit(get_limit_for_endpoint, per_method=True)

class RateLimitManager:
    """Gerenciador de rate limiting avançado"""
    
    def __init__(self, limiter):
        self.limiter = limiter
    
    def get_user_limits(self, user_id):
        """Obter limites atuais do usuário"""
        try:
            # Obter informações de rate limiting do usuário
            limits = {}
            
            # Verificar diferentes janelas de tempo
            for window in ['minute', 'hour', 'day']:
                key = f"user:{user_id}:{window}"
                current = self.limiter.storage.get(key) or 0
                limits[window] = {
                    'current': current,
                    'limit': self._get_limit_for_window(window),
                    'remaining': max(0, self._get_limit_for_window(window) - current),
                    'reset_time': self._get_reset_time(window)
                }
            
            return limits
        except Exception as e:
            return {'error': str(e)}
    
    def _get_limit_for_window(self, window):
        """Obter limite para janela de tempo"""
        limits = {
            'minute': 100,
            'hour': 1000,
            'day': 10000
        }
        return limits.get(window, 100)
    
    def _get_reset_time(self, window):
        """Obter tempo de reset para janela"""
        import time
        now = time.time()
        
        if window == 'minute':
            return int(now) + 60 - (int(now) % 60)
        elif window == 'hour':
            return int(now) + 3600 - (int(now) % 3600)
        elif window == 'day':
            return int(now) + 86400 - (int(now) % 86400)
        
        return int(now) + 60
    
    def is_user_blocked(self, user_id):
        """Verificar se usuário está bloqueado"""
        try:
            # Verificar se usuário excedeu limites críticos
            limits = self.get_user_limits(user_id)
            
            # Bloquear se excedeu limite por minuto
            if limits.get('minute', {}).get('remaining', 1) <= 0:
                return True, "Rate limit exceeded for minute window"
            
            # Bloquear se excedeu muito o limite por hora
            hour_limit = limits.get('hour', {})
            if hour_limit.get('current', 0) > hour_limit.get('limit', 1000) * 1.5:
                return True, "Severe rate limit violation"
            
            return False, None
        except:
            return False, None
    
    def whitelist_user(self, user_id):
        """Adicionar usuário à whitelist (sem rate limiting)"""
        try:
            key = f"whitelist:{user_id}"
            self.limiter.storage.set(key, "1", ex=86400)  # 24 horas
            return True
        except:
            return False
    
    def blacklist_user(self, user_id, duration=3600):
        """Adicionar usuário à blacklist temporária"""
        try:
            key = f"blacklist:{user_id}"
            self.limiter.storage.set(key, "1", ex=duration)
            return True
        except:
            return False
    
    def is_whitelisted(self, user_id):
        """Verificar se usuário está na whitelist"""
        try:
            key = f"whitelist:{user_id}"
            return bool(self.limiter.storage.get(key))
        except:
            return False
    
    def is_blacklisted(self, user_id):
        """Verificar se usuário está na blacklist"""
        try:
            key = f"blacklist:{user_id}"
            return bool(self.limiter.storage.get(key))
        except:
            return False
    
    def get_stats(self):
        """Obter estatísticas de rate limiting"""
        try:
            stats = {
                'total_requests': 0,
                'blocked_requests': 0,
                'top_users': [],
                'timestamp': time.time()
            }
            
            # Implementar coleta de estatísticas
            # (requer estrutura mais complexa no Redis)
            
            return stats
        except Exception as e:
            return {'error': str(e)}

