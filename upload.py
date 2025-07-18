import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User
from src.models.slide import Slide, db
from src.utils.file_upload import ChunkedUploadManager, UploadProgressTracker
from src.utils.slide_processor import SlideProcessor

upload_bp = Blueprint('upload', __name__)

# Instâncias globais
upload_manager = ChunkedUploadManager()
progress_tracker = UploadProgressTracker()

def get_current_user():
    """Obter usuário atual autenticado"""
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id) if current_user_id else None

@upload_bp.route('/upload/init', methods=['POST'])
@jwt_required()
def init_upload():
    """Inicializar upload chunked"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    data = request.json
    
    # Validar dados obrigatórios
    required_fields = ['filename', 'file_size']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    try:
        # Inicializar upload
        metadata = upload_manager.init_upload(
            filename=data['filename'],
            file_size=data['file_size'],
            file_hash=data.get('file_hash')
        )
        
        # Iniciar rastreamento de progresso
        progress_tracker.start_tracking(metadata['upload_id'], data['file_size'])
        
        return jsonify({
            'upload_id': metadata['upload_id'],
            'chunk_size': metadata['chunk_size'],
            'total_chunks': metadata['total_chunks'],
            'status': 'initialized'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao inicializar upload: {str(e)}'}), 500

@upload_bp.route('/upload/<upload_id>/chunk/<int:chunk_index>', methods=['POST'])
@jwt_required()
def upload_chunk(upload_id, chunk_index):
    """Upload de chunk específico"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if 'chunk' not in request.files:
        return jsonify({'error': 'Chunk não encontrado'}), 400
    
    chunk_file = request.files['chunk']
    chunk_data = chunk_file.read()
    
    try:
        # Upload do chunk
        result = upload_manager.upload_chunk(upload_id, chunk_index, chunk_data)
        
        # Atualizar progresso
        progress_tracker.update_progress(upload_id, len(chunk_data))
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro no upload do chunk: {str(e)}'}), 500

@upload_bp.route('/upload/<upload_id>/complete', methods=['POST'])
@jwt_required()
def complete_upload(upload_id):
    """Completar upload e processar arquivo"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    try:
        # Verificar status do upload
        status = upload_manager.get_upload_status(upload_id)
        
        if status['status'] != 'ready_for_assembly':
            return jsonify({'error': 'Upload não está pronto para montagem'}), 400
        
        # Gerar nome único para o arquivo final
        file_extension = os.path.splitext(status['filename'])[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Definir caminho de saída
        upload_path = os.path.join(current_app.root_path, '..', 'uploads/slides')
        os.makedirs(upload_path, exist_ok=True)
        output_path = os.path.join(upload_path, unique_filename)
        
        # Montar arquivo
        assembly_result = upload_manager.assemble_file(upload_id, output_path)
        
        # Processar metadados da lâmina
        processor = SlideProcessor()
        
        # Validar arquivo primeiro
        with open(output_path, 'rb') as f:
            file_header = f.read(1024)  # Ler primeiro KB para validação
        
        validation = upload_manager.validate_file_format(status['filename'], file_header)
        if not validation['valid']:
            os.remove(output_path)
            return jsonify({'error': validation['error']}), 400
        
        # Extrair metadados
        slide_metadata = processor.extract_metadata(output_path)
        
        # Criar registro no banco de dados
        slide = Slide(
            filename=unique_filename,
            original_filename=status['filename'],
            file_path=output_path,
            file_size=assembly_result['file_size'],
            scanner_type=slide_metadata.get('scanner_type'),
            stain_type=slide_metadata.get('stain_type'),
            width=slide_metadata.get('width'),
            height=slide_metadata.get('height'),
            levels=slide_metadata.get('levels'),
            mpp_x=slide_metadata.get('mpp_x'),
            mpp_y=slide_metadata.get('mpp_y'),
            uploaded_by=current_user.id,
            status='ready'
        )
        
        db.session.add(slide)
        db.session.commit()
        
        # Finalizar rastreamento
        progress_tracker.finish_tracking(upload_id)
        
        return jsonify({
            'message': 'Upload completado com sucesso',
            'slide': slide.to_dict(),
            'upload_id': upload_id,
            'file_size': assembly_result['file_size']
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao completar upload: {str(e)}'}), 500

@upload_bp.route('/upload/<upload_id>/status', methods=['GET'])
@jwt_required()
def get_upload_status(upload_id):
    """Obter status do upload"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    try:
        # Status do upload manager
        upload_status = upload_manager.get_upload_status(upload_id)
        
        # Progresso em tempo real
        progress = progress_tracker.get_progress(upload_id)
        
        # Combinar informações
        result = {**upload_status}
        if progress['status'] != 'not_found':
            result.update({
                'real_time_progress': progress['progress_percent'],
                'upload_speed': progress['speed'],
                'eta': progress['eta'],
                'elapsed_time': progress['elapsed_time']
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter status: {str(e)}'}), 500

@upload_bp.route('/upload/<upload_id>/resume', methods=['POST'])
@jwt_required()
def resume_upload(upload_id):
    """Retomar upload interrompido"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    try:
        result = upload_manager.resume_upload(upload_id)
        
        # Reiniciar rastreamento se necessário
        if result['status'] in ['uploading', 'initialized']:
            progress_tracker.start_tracking(upload_id, result['file_size'])
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao retomar upload: {str(e)}'}), 500

@upload_bp.route('/upload/<upload_id>/cancel', methods=['DELETE'])
@jwt_required()
def cancel_upload(upload_id):
    """Cancelar upload"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    try:
        # Limpar chunks
        upload_manager.cleanup_chunks(upload_id)
        
        # Parar rastreamento
        progress_tracker.finish_tracking(upload_id)
        
        return jsonify({'message': 'Upload cancelado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao cancelar upload: {str(e)}'}), 500

@upload_bp.route('/upload/cleanup', methods=['POST'])
@jwt_required()
def cleanup_uploads():
    """Limpar uploads órfãos (apenas admins)"""
    current_user = get_current_user()
    if not current_user or not current_user.has_permission('system_config'):
        return jsonify({'error': 'Permissão insuficiente'}), 403
    
    try:
        upload_manager.cleanup_orphaned_uploads()
        return jsonify({'message': 'Limpeza realizada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro na limpeza: {str(e)}'}), 500

@upload_bp.route('/upload/validate', methods=['POST'])
@jwt_required()
def validate_file():
    """Validar arquivo antes do upload"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'Arquivo não encontrado'}), 400
    
    file = request.files['file']
    
    # Ler apenas o cabeçalho para validação
    file_header = file.read(1024)
    file.seek(0)  # Resetar posição
    
    try:
        validation = upload_manager.validate_file_format(file.filename, file_header)
        
        return jsonify({
            'valid': validation['valid'],
            'error': validation.get('error'),
            'detected_format': validation.get('detected_format'),
            'extension': validation.get('extension')
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro na validação: {str(e)}'}), 500

@upload_bp.route('/upload/stats', methods=['GET'])
@jwt_required()
def get_upload_stats():
    """Obter estatísticas de upload (apenas admins)"""
    current_user = get_current_user()
    if not current_user or not current_user.has_permission('system_config'):
        return jsonify({'error': 'Permissão insuficiente'}), 403
    
    try:
        # Estatísticas básicas
        total_slides = Slide.query.count()
        total_size = db.session.query(db.func.sum(Slide.file_size)).scalar() or 0
        
        # Uploads ativos
        active_uploads = len(progress_tracker.active_uploads)
        
        # Estatísticas por usuário
        user_stats = db.session.query(
            User.username,
            db.func.count(Slide.id).label('slide_count'),
            db.func.sum(Slide.file_size).label('total_size')
        ).join(Slide, User.id == Slide.uploaded_by).group_by(User.id).all()
        
        return jsonify({
            'total_slides': total_slides,
            'total_size': total_size,
            'active_uploads': active_uploads,
            'user_stats': [
                {
                    'username': stat.username,
                    'slide_count': stat.slide_count,
                    'total_size': stat.total_size or 0
                }
                for stat in user_stats
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter estatísticas: {str(e)}'}), 500

