import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';

const SlideUpload = ({ onUploadComplete, onUploadStart }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([]);
  const fileInputRef = useRef(null);

  const allowedTypes = [
    'image/tiff',
    'image/tif',
    '.svs',
    '.ndpi',
    '.scn',
    '.mrxs',
    '.vms',
    '.vmu'
  ];

  const isValidFile = (file) => {
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    return allowedTypes.includes(file.type) || 
           allowedTypes.includes(extension) ||
           file.type.includes('tiff');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const validFiles = files.filter(isValidFile);
    const invalidFiles = files.filter(file => !isValidFile(file));

    if (invalidFiles.length > 0) {
      alert(`Arquivos não suportados: ${invalidFiles.map(f => f.name).join(', ')}`);
    }

    if (validFiles.length > 0) {
      const newUploads = validFiles.map(file => ({
        id: Date.now() + Math.random(),
        file,
        name: file.name,
        size: file.size,
        progress: 0,
        status: 'pending', // pending, uploading, completed, error
        error: null
      }));

      setUploadQueue(prev => [...prev, ...newUploads]);
      
      // Iniciar uploads
      newUploads.forEach(upload => {
        uploadFile(upload);
      });
    }
  };

  const uploadFile = async (uploadItem) => {
    try {
      // Atualizar status para uploading
      setUploadQueue(prev => prev.map(item => 
        item.id === uploadItem.id 
          ? { ...item, status: 'uploading', progress: 0 }
          : item
      ));

      if (onUploadStart) {
        onUploadStart(uploadItem);
      }

      const formData = new FormData();
      formData.append('file', uploadItem.file);

      const xhr = new XMLHttpRequest();

      // Monitorar progresso
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadQueue(prev => prev.map(item => 
            item.id === uploadItem.id 
              ? { ...item, progress }
              : item
          ));
        }
      });

      // Configurar resposta
      xhr.addEventListener('load', () => {
        if (xhr.status === 201) {
          const response = JSON.parse(xhr.responseText);
          setUploadQueue(prev => prev.map(item => 
            item.id === uploadItem.id 
              ? { ...item, status: 'completed', progress: 100, slideData: response }
              : item
          ));
          
          if (onUploadComplete) {
            onUploadComplete(response);
          }
        } else {
          throw new Error(`Erro no upload: ${xhr.status}`);
        }
      });

      xhr.addEventListener('error', () => {
        setUploadQueue(prev => prev.map(item => 
          item.id === uploadItem.id 
            ? { ...item, status: 'error', error: 'Erro de conexão' }
            : item
        ));
      });

      // Enviar requisição
      xhr.open('POST', '/api/slides/upload');
      xhr.send(formData);

    } catch (error) {
      setUploadQueue(prev => prev.map(item => 
        item.id === uploadItem.id 
          ? { ...item, status: 'error', error: error.message }
          : item
      ));
    }
  };

  const removeFromQueue = (id) => {
    setUploadQueue(prev => prev.filter(item => item.id !== id));
  };

  const retryUpload = (uploadItem) => {
    uploadFile(uploadItem);
  };

  const clearCompleted = () => {
    setUploadQueue(prev => prev.filter(item => item.status !== 'completed'));
  };

  return (
    <div className="space-y-4">
      {/* Área de Drop */}
      <Card 
        className={`border-2 border-dashed transition-colors ${
          isDragOver 
            ? 'border-primary bg-primary/5' 
            : 'border-muted-foreground/25 hover:border-primary/50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <Upload className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            Arraste lâminas aqui ou clique para selecionar
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            Formatos suportados: SVS, TIFF, NDPI, SCN, MRXS, VMS, VMU
          </p>
          <p className="text-xs text-muted-foreground mb-4">
            Tamanho máximo: 5GB por arquivo
          </p>
          <Button onClick={() => fileInputRef.current?.click()}>
            Selecionar Arquivos
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".svs,.tiff,.tif,.ndpi,.scn,.mrxs,.vms,.vmu"
            onChange={handleFileSelect}
            className="hidden"
          />
        </CardContent>
      </Card>

      {/* Fila de Upload */}
      {uploadQueue.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Fila de Upload</CardTitle>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={clearCompleted}
              disabled={!uploadQueue.some(item => item.status === 'completed')}
            >
              Limpar Concluídos
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {uploadQueue.map((upload) => (
              <div key={upload.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <File className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {upload.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(upload.size)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {upload.status === 'completed' && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    {upload.status === 'error' && (
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-red-500" />
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => retryUpload(upload)}
                        >
                          Tentar Novamente
                        </Button>
                      </div>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeFromQueue(upload.id)}
                      disabled={upload.status === 'uploading'}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Barra de Progresso */}
                {(upload.status === 'uploading' || upload.status === 'pending') && (
                  <div className="space-y-1">
                    <Progress value={upload.progress} className="h-2" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>
                        {upload.status === 'pending' ? 'Aguardando...' : 'Enviando...'}
                      </span>
                      <span>{upload.progress}%</span>
                    </div>
                  </div>
                )}

                {/* Mensagem de Erro */}
                {upload.status === 'error' && upload.error && (
                  <p className="text-xs text-red-500">
                    Erro: {upload.error}
                  </p>
                )}

                {/* Status de Sucesso */}
                {upload.status === 'completed' && (
                  <p className="text-xs text-green-600">
                    Upload concluído com sucesso
                  </p>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SlideUpload;

