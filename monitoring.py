import os
import time
import psutil
import sqlite3
from datetime import datetime
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from src.models.user import User
from src.models.slide import Slide

monitoring_bp = Blueprint('monitoring', __name__)

class SystemMonitor:
    """Monitor de sistema para AIAPad"""
    
    @staticmethod
    def get_system_info():
        """Obter informações do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = memory.total
            memory_available = memory.available
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_total = disk.total
            disk_free = disk.free
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory_percent,
                    'total': memory_total,
                    'available': memory_available,
                    'used': memory_total - memory_available
                },
                'disk': {
                    'percent': disk_percent,
                    'total': disk_total,
                    'free': disk_free,
                    'used': disk.used
                },
                'uptime': uptime,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_application_info():
        """Obter informações da aplicação"""
        try:
            # Estatísticas do banco de dados
            total_users = User.query.count()
            total_slides = Slide.query.count()
            
            # Tamanho total dos uploads
            upload_dir = current_app.config.get('UPLOAD_FOLDER', '/opt/aiapad/uploads')
            total_upload_size = 0
            
            if os.path.exists(upload_dir):
                for root, dirs, files in os.walk(upload_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_upload_size += os.path.getsize(file_path)
            
            # Status do banco de dados
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            db_size = 0
            db_status = 'unknown'
            
            if os.path.exists(db_path):
                db_size = os.path.getsize(db_path)
                try:
                    conn = sqlite3.connect(db_path)
                    conn.execute('SELECT 1')
                    conn.close()
                    db_status = 'healthy'
                except:
                    db_status = 'error'
            
            return {
                'users': {
                    'total': total_users
                },
                'slides': {
                    'total': total_slides
                },
                'storage': {
                    'uploads_size': total_upload_size,
                    'database_size': db_size
                },
                'database': {
                    'status': db_status,
                    'path': db_path
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def check_health():
        """Verificação de saúde do sistema"""
        health_status = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Verificar CPU
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                health_status['checks']['cpu'] = {'status': 'warning', 'value': cpu_percent}
            else:
                health_status['checks']['cpu'] = {'status': 'healthy', 'value': cpu_percent}
        except:
            health_status['checks']['cpu'] = {'status': 'error', 'message': 'Cannot read CPU'}
        
        # Verificar memória
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                health_status['checks']['memory'] = {'status': 'warning', 'value': memory.percent}
            else:
                health_status['checks']['memory'] = {'status': 'healthy', 'value': memory.percent}
        except:
            health_status['checks']['memory'] = {'status': 'error', 'message': 'Cannot read memory'}
        
        # Verificar disco
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                health_status['checks']['disk'] = {'status': 'warning', 'value': disk_percent}
            else:
                health_status['checks']['disk'] = {'status': 'healthy', 'value': disk_percent}
        except:
            health_status['checks']['disk'] = {'status': 'error', 'message': 'Cannot read disk'}
        
        # Verificar banco de dados
        try:
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.execute('SELECT 1')
                conn.close()
                health_status['checks']['database'] = {'status': 'healthy'}
            else:
                health_status['checks']['database'] = {'status': 'error', 'message': 'Database file not found'}
        except Exception as e:
            health_status['checks']['database'] = {'status': 'error', 'message': str(e)}
        
        # Verificar diretório de uploads
        try:
            upload_dir = current_app.config.get('UPLOAD_FOLDER', '/opt/aiapad/uploads')
            if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
                health_status['checks']['uploads'] = {'status': 'healthy'}
            else:
                health_status['checks']['uploads'] = {'status': 'error', 'message': 'Upload directory not accessible'}
        except Exception as e:
            health_status['checks']['uploads'] = {'status': 'error', 'message': str(e)}
        
        # Determinar status geral
        if any(check['status'] == 'error' for check in health_status['checks'].values()):
            health_status['status'] = 'unhealthy'
        elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
            health_status['status'] = 'degraded'
        
        return health_status

@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check público"""
    try:
        health = SystemMonitor.check_health()
        status_code = 200 if health['status'] == 'healthy' else 503
        return jsonify(health), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/health/detailed', methods=['GET'])
@jwt_required()
def detailed_health():
    """Endpoint de health check detalhado (requer autenticação)"""
    try:
        system_info = SystemMonitor.get_system_info()
        app_info = SystemMonitor.get_application_info()
        health = SystemMonitor.check_health()
        
        return jsonify({
            'health': health,
            'system': system_info,
            'application': app_info
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/metrics', methods=['GET'])
@jwt_required()
def metrics():
    """Endpoint de métricas para monitoramento"""
    try:
        system_info = SystemMonitor.get_system_info()
        app_info = SystemMonitor.get_application_info()
        
        # Formato Prometheus-like
        metrics_text = f"""# HELP aiapad_cpu_percent CPU usage percentage
# TYPE aiapad_cpu_percent gauge
aiapad_cpu_percent {system_info.get('cpu', {}).get('percent', 0)}

# HELP aiapad_memory_percent Memory usage percentage
# TYPE aiapad_memory_percent gauge
aiapad_memory_percent {system_info.get('memory', {}).get('percent', 0)}

# HELP aiapad_disk_percent Disk usage percentage
# TYPE aiapad_disk_percent gauge
aiapad_disk_percent {system_info.get('disk', {}).get('percent', 0)}

# HELP aiapad_users_total Total number of users
# TYPE aiapad_users_total counter
aiapad_users_total {app_info.get('users', {}).get('total', 0)}

# HELP aiapad_slides_total Total number of slides
# TYPE aiapad_slides_total counter
aiapad_slides_total {app_info.get('slides', {}).get('total', 0)}

# HELP aiapad_uploads_size_bytes Total size of uploads in bytes
# TYPE aiapad_uploads_size_bytes gauge
aiapad_uploads_size_bytes {app_info.get('storage', {}).get('uploads_size', 0)}

# HELP aiapad_database_size_bytes Database size in bytes
# TYPE aiapad_database_size_bytes gauge
aiapad_database_size_bytes {app_info.get('storage', {}).get('database_size', 0)}
"""
        
        return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"# Error generating metrics: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}

@monitoring_bp.route('/status', methods=['GET'])
def status():
    """Endpoint de status simples"""
    return jsonify({
        'status': 'running',
        'service': 'aiapad-backend',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

