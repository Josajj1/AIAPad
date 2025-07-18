import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  Eye, 
  Download, 
  Trash2, 
  Brain, 
  Calendar,
  FileImage,
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react';

const SlideDashboard = ({ onSlideSelect, onSlideDelete, selectedSlideId }) => {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('upload_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadSlides();
  }, []);

  const loadSlides = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/slides');
      if (response.ok) {
        const data = await response.json();
        setSlides(data);
      } else {
        console.error('Erro ao carregar lâminas');
      }
    } catch (error) {
      console.error('Erro ao carregar lâminas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSlide = async (slideId) => {
    if (window.confirm('Tem certeza que deseja deletar esta lâmina?')) {
      try {
        const response = await fetch(`/api/slides/${slideId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          setSlides(prev => prev.filter(slide => slide.id !== slideId));
          if (onSlideDelete) {
            onSlideDelete(slideId);
          }
        } else {
          alert('Erro ao deletar lâmina');
        }
      } catch (error) {
        console.error('Erro ao deletar lâmina:', error);
        alert('Erro ao deletar lâmina');
      }
    }
  };

  const handleAnalyzeSlide = async (slideId) => {
    try {
      const response = await fetch(`/api/slides/${slideId}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          analysis_type: 'disease_detection'
        })
      });
      
      if (response.ok) {
        const analysis = await response.json();
        alert(`Análise iniciada! Resultado: ${analysis.result}`);
        loadSlides(); // Recarregar para atualizar status
      } else {
        alert('Erro ao iniciar análise');
      }
    } catch (error) {
      console.error('Erro ao analisar lâmina:', error);
      alert('Erro ao analisar lâmina');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStainColor = (stainType) => {
    switch (stainType) {
      case 'H&E': return 'bg-blue-100 text-blue-800';
      case 'IHC': return 'bg-purple-100 text-purple-800';
      case 'PAS': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Filtrar e ordenar lâminas
  const filteredAndSortedSlides = slides
    .filter(slide => {
      const matchesSearch = slide.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           slide.scanner_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           slide.stain_type?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesFilter = filterStatus === 'all' || slide.status === filterStatus;
      
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'upload_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <p>Carregando lâminas...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controles de Busca e Filtro */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Gerenciamento de Lâminas
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Busca */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nome, scanner ou coloração..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Filtro por Status */}
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-input rounded-md bg-background"
            >
              <option value="all">Todos os Status</option>
              <option value="ready">Pronto</option>
              <option value="processing">Processando</option>
              <option value="error">Erro</option>
            </select>
            
            {/* Ordenação */}
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-input rounded-md bg-background"
              >
                <option value="upload_date">Data de Upload</option>
                <option value="original_filename">Nome</option>
                <option value="file_size">Tamanho</option>
                <option value="scanner_type">Scanner</option>
              </select>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Lâminas */}
      <div className="grid gap-4">
        {filteredAndSortedSlides.length === 0 ? (
          <Card>
            <CardContent className="flex items-center justify-center py-12">
              <p className="text-muted-foreground">
                {searchTerm || filterStatus !== 'all' 
                  ? 'Nenhuma lâmina encontrada com os filtros aplicados'
                  : 'Nenhuma lâmina encontrada. Faça upload de uma lâmina para começar.'
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredAndSortedSlides.map((slide) => (
            <Card 
              key={slide.id} 
              className={`cursor-pointer transition-colors hover:bg-muted/50 ${
                selectedSlideId === slide.id ? 'ring-2 ring-primary' : ''
              }`}
              onClick={() => onSlideSelect && onSlideSelect(slide)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold truncate">
                        {slide.original_filename}
                      </h3>
                      <Badge className={getStatusColor(slide.status)}>
                        {slide.status}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-muted-foreground">
                      <div>
                        <p className="font-medium">Tamanho</p>
                        <p>{formatFileSize(slide.file_size)}</p>
                      </div>
                      <div>
                        <p className="font-medium">Dimensões</p>
                        <p>{slide.width && slide.height ? `${slide.width} × ${slide.height}` : 'N/A'}</p>
                      </div>
                      <div>
                        <p className="font-medium">Scanner</p>
                        <p>{slide.scanner_type || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="font-medium">Coloração</p>
                        {slide.stain_type ? (
                          <Badge className={getStainColor(slide.stain_type)}>
                            {slide.stain_type}
                          </Badge>
                        ) : (
                          <p>N/A</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(slide.upload_date)}
                      </div>
                      {slide.levels && (
                        <div>
                          {slide.levels} níveis de zoom
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSlideSelect && onSlideSelect(slide);
                      }}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAnalyzeSlide(slide.id);
                      }}
                      disabled={slide.status !== 'ready'}
                    >
                      <Brain className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteSlide(slide.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default SlideDashboard;

