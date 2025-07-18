import os
import json
import time
import hashlib
from functools import wraps
from flask import current_app, request
import redis

class CacheManager:
    """Gerenciador de cache para AIAPad"""
    
    def __init__(self, app=None):
        self.redis_client = None
        self.enabled = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar cache com a aplicação Flask"""
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            self.enabled = True
            app.logger.info("Cache Redis inicializado")
        except Exception as e:
            app.logger.warning(f"Cache Redis não disponível: {e}")
            self.enabled = False
    
    def get(self, key):
        """Obter valor do cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value.decode('utf-8'))
        except Exception as e:
            current_app.logger.error(f"Erro ao ler cache: {e}")
        
        return None
    
    def set(self, key, value, timeout=300):
        """Definir valor no cache"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, timeout, serialized)
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao escrever cache: {e}")
            return False
    
    def delete(self, key):
        """Deletar chave do cache"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar cache: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Limpar chaves que correspondem ao padrão"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def exists(self, key):
        """Verificar se chave existe no cache"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except:
            return False
    
    def ttl(self, key):
        """Obter TTL de uma chave"""
        if not self.enabled:
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except:
            return -1

# Instância global do cache
cache = CacheManager()

def cached(timeout=300, key_prefix=None, unless=None):
    """Decorator para cache de funções"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar condição unless
            if unless and unless():
                return f(*args, **kwargs)
            
            # Gerar chave do cache
            cache_key = _generate_cache_key(f, key_prefix, args, kwargs)
            
            # Tentar obter do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return decorated_function
    return decorator

def cache_slide_metadata(slide_id, timeout=3600):
    """Cache específico para metadados de lâminas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"slide_metadata:{slide_id}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return decorated_function
    return decorator

def cache_user_permissions(user_id, timeout=900):
    """Cache específico para permissões de usuário"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"user_permissions:{user_id}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return decorated_function
    return decorator

def cache_ai_analysis(slide_id, analysis_type, timeout=7200):
    """Cache específico para análises de IA"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"ai_analysis:{slide_id}:{analysis_type}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return decorated_function
    return decorator

def invalidate_slide_cache(slide_id):
    """Invalidar cache relacionado a uma lâmina"""
    patterns = [
        f"slide_metadata:{slide_id}",
        f"slide_tiles:{slide_id}:*",
        f"ai_analysis:{slide_id}:*",
        f"slide_annotations:{slide_id}"
    ]
    
    for pattern in patterns:
        cache.clear_pattern(pattern)

def invalidate_user_cache(user_id):
    """Invalidar cache relacionado a um usuário"""
    patterns = [
        f"user_permissions:{user_id}",
        f"user_slides:{user_id}",
        f"user_stats:{user_id}"
    ]
    
    for pattern in patterns:
        cache.clear_pattern(pattern)

def _generate_cache_key(func, key_prefix, args, kwargs):
    """Gerar chave única para cache"""
    # Nome da função
    func_name = f"{func.__module__}.{func.__name__}"
    
    # Serializar argumentos
    args_str = str(args) + str(sorted(kwargs.items()))
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
    
    # Incluir informações da requisição se disponível
    request_info = ""
    try:
        if request:
            request_info = f":{request.method}:{request.endpoint}"
    except:
        pass
    
    # Montar chave final
    if key_prefix:
        return f"{key_prefix}:{func_name}:{args_hash}{request_info}"
    else:
        return f"cache:{func_name}:{args_hash}{request_info}"

class TileCache:
    """Cache específico para tiles de lâminas"""
    
    @staticmethod
    def get_tile_key(slide_id, level, x, y, width, height):
        """Gerar chave para tile"""
        return f"slide_tiles:{slide_id}:{level}:{x}:{y}:{width}:{height}"
    
    @staticmethod
    def cache_tile(slide_id, level, x, y, width, height, tile_data, timeout=3600):
        """Cachear tile"""
        key = TileCache.get_tile_key(slide_id, level, x, y, width, height)
        
        # Para tiles, usar cache binário se possível
        if cache.enabled:
            try:
                cache.redis_client.setex(f"{key}:binary", timeout, tile_data)
                return True
            except:
                return False
        
        return False
    
    @staticmethod
    def get_tile(slide_id, level, x, y, width, height):
        """Obter tile do cache"""
        key = TileCache.get_tile_key(slide_id, level, x, y, width, height)
        
        if cache.enabled:
            try:
                return cache.redis_client.get(f"{key}:binary")
            except:
                return None
        
        return None
    
    @staticmethod
    def invalidate_slide_tiles(slide_id):
        """Invalidar todos os tiles de uma lâmina"""
        cache.clear_pattern(f"slide_tiles:{slide_id}:*")

class SessionCache:
    """Cache para sessões de usuário"""
    
    @staticmethod
    def cache_user_session(user_id, session_data, timeout=3600):
        """Cachear dados da sessão"""
        key = f"user_session:{user_id}"
        return cache.set(key, session_data, timeout)
    
    @staticmethod
    def get_user_session(user_id):
        """Obter dados da sessão"""
        key = f"user_session:{user_id}"
        return cache.get(key)
    
    @staticmethod
    def invalidate_user_session(user_id):
        """Invalidar sessão do usuário"""
        key = f"user_session:{user_id}"
        return cache.delete(key)

class StatsCache:
    """Cache para estatísticas do sistema"""
    
    @staticmethod
    def cache_system_stats(stats, timeout=300):
        """Cachear estatísticas do sistema"""
        key = "system_stats"
        return cache.set(key, stats, timeout)
    
    @staticmethod
    def get_system_stats():
        """Obter estatísticas do sistema"""
        key = "system_stats"
        return cache.get(key)
    
    @staticmethod
    def cache_user_stats(user_id, stats, timeout=900):
        """Cachear estatísticas do usuário"""
        key = f"user_stats:{user_id}"
        return cache.set(key, stats, timeout)
    
    @staticmethod
    def get_user_stats(user_id):
        """Obter estatísticas do usuário"""
        key = f"user_stats:{user_id}"
        return cache.get(key)

