import os
import hashlib
import json
import time
from typing import Dict, Optional, Tuple
from werkzeug.datastructures import FileStorage
from flask import current_app

class ChunkedUploadManager:
    """Gerenciador de upload de arquivos grandes com chunking"""
    
    def __init__(self, upload_dir: str = 'uploads/chunks'):
        self.upload_dir = upload_dir
        self.chunk_size = 1024 * 1024  # 1MB chunks
        self.max_file_size = 5 * 1024 * 1024 * 1024  # 5GB
        self.cleanup_interval = 3600  # 1 hora para limpeza de chunks órfãos
        
    def init_upload(self, filename: str, file_size: int, file_hash: str = None) -> Dict:
        """Inicializar upload chunked"""
        
        if file_size > self.max_file_size:
            raise ValueError(f"Arquivo muito grande. Máximo permitido: {self.max_file_size} bytes")
        
        # Gerar ID único para o upload
        upload_id = hashlib.md5(f"{filename}_{file_size}_{time.time()}".encode()).hexdigest()
        
        # Criar diretório para chunks
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        os.makedirs(chunk_dir, exist_ok=True)
        
        # Calcular número total de chunks
        total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        
        # Salvar metadados do upload
        metadata = {
            'upload_id': upload_id,
            'filename': filename,
            'file_size': file_size,
            'file_hash': file_hash,
            'total_chunks': total_chunks,
            'chunk_size': self.chunk_size,
            'uploaded_chunks': [],
            'created_at': time.time(),
            'status': 'initialized'
        }
        
        metadata_path = os.path.join(chunk_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return metadata
    
    def upload_chunk(self, upload_id: str, chunk_index: int, chunk_data: bytes) -> Dict:
        """Upload de um chunk específico"""
        
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        metadata_path = os.path.join(chunk_dir, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            raise ValueError("Upload não encontrado")
        
        # Carregar metadados
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Validar chunk
        if chunk_index >= metadata['total_chunks']:
            raise ValueError("Índice de chunk inválido")
        
        if chunk_index in metadata['uploaded_chunks']:
            return {'status': 'chunk_already_exists', 'chunk_index': chunk_index}
        
        # Salvar chunk
        chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_index:06d}')
        with open(chunk_path, 'wb') as f:
            f.write(chunk_data)
        
        # Atualizar metadados
        metadata['uploaded_chunks'].append(chunk_index)
        metadata['uploaded_chunks'].sort()
        
        # Verificar se upload está completo
        if len(metadata['uploaded_chunks']) == metadata['total_chunks']:
            metadata['status'] = 'ready_for_assembly'
        else:
            metadata['status'] = 'uploading'
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return {
            'status': metadata['status'],
            'chunk_index': chunk_index,
            'uploaded_chunks': len(metadata['uploaded_chunks']),
            'total_chunks': metadata['total_chunks'],
            'progress': len(metadata['uploaded_chunks']) / metadata['total_chunks'] * 100
        }
    
    def assemble_file(self, upload_id: str, output_path: str) -> Dict:
        """Montar arquivo final a partir dos chunks"""
        
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        metadata_path = os.path.join(chunk_dir, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            raise ValueError("Upload não encontrado")
        
        # Carregar metadados
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        if metadata['status'] != 'ready_for_assembly':
            raise ValueError("Upload não está pronto para montagem")
        
        # Criar diretório de saída se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Montar arquivo
        with open(output_path, 'wb') as output_file:
            for chunk_index in range(metadata['total_chunks']):
                chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_index:06d}')
                
                if not os.path.exists(chunk_path):
                    raise ValueError(f"Chunk {chunk_index} não encontrado")
                
                with open(chunk_path, 'rb') as chunk_file:
                    output_file.write(chunk_file.read())
        
        # Verificar integridade se hash foi fornecido
        if metadata.get('file_hash'):
            file_hash = self.calculate_file_hash(output_path)
            if file_hash != metadata['file_hash']:
                os.remove(output_path)
                raise ValueError("Falha na verificação de integridade do arquivo")
        
        # Atualizar metadados
        metadata['status'] = 'completed'
        metadata['output_path'] = output_path
        metadata['completed_at'] = time.time()
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        # Limpar chunks
        self.cleanup_chunks(upload_id)
        
        return {
            'status': 'completed',
            'output_path': output_path,
            'file_size': os.path.getsize(output_path)
        }
    
    def get_upload_status(self, upload_id: str) -> Dict:
        """Obter status do upload"""
        
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        metadata_path = os.path.join(chunk_dir, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            return {'status': 'not_found'}
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        progress = 0
        if metadata['total_chunks'] > 0:
            progress = len(metadata['uploaded_chunks']) / metadata['total_chunks'] * 100
        
        return {
            'upload_id': upload_id,
            'status': metadata['status'],
            'filename': metadata['filename'],
            'file_size': metadata['file_size'],
            'uploaded_chunks': len(metadata['uploaded_chunks']),
            'total_chunks': metadata['total_chunks'],
            'progress': progress,
            'created_at': metadata['created_at']
        }
    
    def resume_upload(self, upload_id: str) -> Dict:
        """Retomar upload interrompido"""
        
        status = self.get_upload_status(upload_id)
        
        if status['status'] == 'not_found':
            raise ValueError("Upload não encontrado")
        
        if status['status'] == 'completed':
            return status
        
        # Verificar chunks existentes
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        existing_chunks = []
        
        for i in range(status['total_chunks']):
            chunk_path = os.path.join(chunk_dir, f'chunk_{i:06d}')
            if os.path.exists(chunk_path):
                existing_chunks.append(i)
        
        # Atualizar metadados com chunks encontrados
        metadata_path = os.path.join(chunk_dir, 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        metadata['uploaded_chunks'] = existing_chunks
        
        if len(existing_chunks) == metadata['total_chunks']:
            metadata['status'] = 'ready_for_assembly'
        else:
            metadata['status'] = 'uploading'
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return self.get_upload_status(upload_id)
    
    def cleanup_chunks(self, upload_id: str):
        """Limpar chunks após montagem"""
        
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        
        if os.path.exists(chunk_dir):
            # Remover chunks individuais
            for filename in os.listdir(chunk_dir):
                if filename.startswith('chunk_'):
                    os.remove(os.path.join(chunk_dir, filename))
    
    def cleanup_orphaned_uploads(self):
        """Limpar uploads órfãos antigos"""
        
        if not os.path.exists(self.upload_dir):
            return
        
        current_time = time.time()
        
        for upload_id in os.listdir(self.upload_dir):
            upload_path = os.path.join(self.upload_dir, upload_id)
            
            if not os.path.isdir(upload_path):
                continue
            
            metadata_path = os.path.join(upload_path, 'metadata.json')
            
            if not os.path.exists(metadata_path):
                # Diretório sem metadados, remover
                import shutil
                shutil.rmtree(upload_path)
                continue
            
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Remover uploads antigos não completados
                if (current_time - metadata['created_at'] > self.cleanup_interval and 
                    metadata['status'] not in ['completed']):
                    import shutil
                    shutil.rmtree(upload_path)
                    
            except (json.JSONDecodeError, KeyError):
                # Metadados corrompidos, remover
                import shutil
                shutil.rmtree(upload_path)
    
    def calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """Calcular hash do arquivo"""
        
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def validate_file_format(self, filename: str, file_data: bytes) -> Dict:
        """Validar formato do arquivo"""
        
        # Extensões permitidas
        allowed_extensions = {
            '.svs', '.tif', '.tiff', '.ndpi', '.scn', '.mrxs', '.vms', '.vmu'
        }
        
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return {
                'valid': False,
                'error': f'Extensão {file_ext} não permitida'
            }
        
        # Verificar assinaturas de arquivo (magic numbers)
        magic_numbers = {
            b'\x49\x49\x2A\x00': 'TIFF',  # TIFF Little Endian
            b'\x4D\x4D\x00\x2A': 'TIFF',  # TIFF Big Endian
        }
        
        file_header = file_data[:4] if len(file_data) >= 4 else b''
        
        detected_format = None
        for magic, format_name in magic_numbers.items():
            if file_header.startswith(magic):
                detected_format = format_name
                break
        
        # Para arquivos TIFF/SVS, verificar se é válido
        if file_ext in ['.tif', '.tiff', '.svs'] and detected_format != 'TIFF':
            return {
                'valid': False,
                'error': 'Arquivo não é um TIFF válido'
            }
        
        return {
            'valid': True,
            'detected_format': detected_format,
            'extension': file_ext
        }

class UploadProgressTracker:
    """Rastreador de progresso de upload em tempo real"""
    
    def __init__(self):
        self.active_uploads = {}
    
    def start_tracking(self, upload_id: str, total_size: int):
        """Iniciar rastreamento de upload"""
        self.active_uploads[upload_id] = {
            'total_size': total_size,
            'uploaded_size': 0,
            'start_time': time.time(),
            'last_update': time.time(),
            'speed': 0
        }
    
    def update_progress(self, upload_id: str, chunk_size: int):
        """Atualizar progresso do upload"""
        if upload_id not in self.active_uploads:
            return
        
        upload_info = self.active_uploads[upload_id]
        current_time = time.time()
        
        upload_info['uploaded_size'] += chunk_size
        
        # Calcular velocidade
        time_diff = current_time - upload_info['last_update']
        if time_diff > 0:
            upload_info['speed'] = chunk_size / time_diff
        
        upload_info['last_update'] = current_time
    
    def get_progress(self, upload_id: str) -> Dict:
        """Obter progresso atual"""
        if upload_id not in self.active_uploads:
            return {'status': 'not_found'}
        
        upload_info = self.active_uploads[upload_id]
        current_time = time.time()
        
        progress_percent = (upload_info['uploaded_size'] / upload_info['total_size']) * 100
        elapsed_time = current_time - upload_info['start_time']
        
        # Estimar tempo restante
        if upload_info['speed'] > 0:
            remaining_bytes = upload_info['total_size'] - upload_info['uploaded_size']
            eta = remaining_bytes / upload_info['speed']
        else:
            eta = 0
        
        return {
            'upload_id': upload_id,
            'progress_percent': progress_percent,
            'uploaded_size': upload_info['uploaded_size'],
            'total_size': upload_info['total_size'],
            'speed': upload_info['speed'],
            'elapsed_time': elapsed_time,
            'eta': eta
        }
    
    def finish_tracking(self, upload_id: str):
        """Finalizar rastreamento"""
        if upload_id in self.active_uploads:
            del self.active_uploads[upload_id]

