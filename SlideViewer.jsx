import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ZoomIn, ZoomOut, RotateCcw, Move, MousePointer, Square, Circle } from 'lucide-react';

const SlideViewer = ({ slide, onAnnotation }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [tool, setTool] = useState('pan'); // pan, point, rectangle, circle
  const [annotations, setAnnotations] = useState([]);
  const [currentAnnotation, setCurrentAnnotation] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    if (slide && canvasRef.current) {
      loadSlideImage();
    }
  }, [slide]);

  const loadSlideImage = async () => {
    try {
      // Carregar thumbnail da lâmina
      const response = await fetch(`/api/slides/${slide.id}/thumbnail`);
      if (response.ok) {
        const blob = await response.blob();
        const img = new Image();
        img.onload = () => {
          drawCanvas(img);
        };
        img.src = URL.createObjectURL(blob);
      }
    } catch (error) {
      console.error('Erro ao carregar lâmina:', error);
    }
  };

  const drawCanvas = (img) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Ajustar tamanho do canvas
    canvas.width = containerRef.current.clientWidth;
    canvas.height = containerRef.current.clientHeight;
    
    // Limpar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calcular posição e tamanho da imagem
    const imgWidth = img.width * zoom;
    const imgHeight = img.height * zoom;
    const x = (canvas.width - imgWidth) / 2 + pan.x;
    const y = (canvas.height - imgHeight) / 2 + pan.y;
    
    // Desenhar imagem
    ctx.drawImage(img, x, y, imgWidth, imgHeight);
    
    // Desenhar anotações
    drawAnnotations(ctx);
  };

  const drawAnnotations = (ctx) => {
    annotations.forEach(annotation => {
      ctx.strokeStyle = annotation.color || '#ff0000';
      ctx.lineWidth = 2;
      ctx.setLineDash([]);
      
      switch (annotation.type) {
        case 'point':
          ctx.beginPath();
          ctx.arc(annotation.x, annotation.y, 5, 0, 2 * Math.PI);
          ctx.stroke();
          break;
        case 'rectangle':
          ctx.strokeRect(annotation.x, annotation.y, annotation.width, annotation.height);
          break;
        case 'circle':
          ctx.beginPath();
          ctx.arc(
            annotation.x + annotation.width / 2,
            annotation.y + annotation.height / 2,
            Math.min(annotation.width, annotation.height) / 2,
            0,
            2 * Math.PI
          );
          ctx.stroke();
          break;
      }
      
      // Desenhar label se existir
      if (annotation.label) {
        ctx.fillStyle = annotation.color || '#ff0000';
        ctx.font = '12px Arial';
        ctx.fillText(annotation.label, annotation.x, annotation.y - 5);
      }
    });
    
    // Desenhar anotação atual sendo criada
    if (currentAnnotation && isDrawing) {
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      
      switch (tool) {
        case 'rectangle':
          ctx.strokeRect(
            currentAnnotation.startX,
            currentAnnotation.startY,
            currentAnnotation.width,
            currentAnnotation.height
          );
          break;
        case 'circle':
          ctx.beginPath();
          ctx.arc(
            currentAnnotation.startX + currentAnnotation.width / 2,
            currentAnnotation.startY + currentAnnotation.height / 2,
            Math.min(Math.abs(currentAnnotation.width), Math.abs(currentAnnotation.height)) / 2,
            0,
            2 * Math.PI
          );
          ctx.stroke();
          break;
      }
    }
  };

  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (tool === 'pan') {
      setIsDragging(true);
      setDragStart({ x: x - pan.x, y: y - pan.y });
    } else if (tool === 'point') {
      // Criar anotação de ponto
      const newAnnotation = {
        id: Date.now(),
        type: 'point',
        x: x,
        y: y,
        color: '#ff0000'
      };
      setAnnotations([...annotations, newAnnotation]);
      if (onAnnotation) onAnnotation(newAnnotation);
    } else if (tool === 'rectangle' || tool === 'circle') {
      setIsDrawing(true);
      setCurrentAnnotation({
        startX: x,
        startY: y,
        width: 0,
        height: 0
      });
    }
  };

  const handleMouseMove = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (isDragging && tool === 'pan') {
      setPan({
        x: x - dragStart.x,
        y: y - dragStart.y
      });
    } else if (isDrawing && currentAnnotation) {
      setCurrentAnnotation({
        ...currentAnnotation,
        width: x - currentAnnotation.startX,
        height: y - currentAnnotation.startY
      });
    }
  };

  const handleMouseUp = (e) => {
    if (isDragging) {
      setIsDragging(false);
    } else if (isDrawing && currentAnnotation) {
      // Finalizar anotação
      const newAnnotation = {
        id: Date.now(),
        type: tool,
        x: currentAnnotation.startX,
        y: currentAnnotation.startY,
        width: currentAnnotation.width,
        height: currentAnnotation.height,
        color: '#ff0000'
      };
      setAnnotations([...annotations, newAnnotation]);
      if (onAnnotation) onAnnotation(newAnnotation);
      setCurrentAnnotation(null);
      setIsDrawing(false);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.5, 10));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.5, 0.1));
  };

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const clearAnnotations = () => {
    setAnnotations([]);
  };

  // Redesenhar quando zoom, pan ou anotações mudarem
  useEffect(() => {
    if (slide && canvasRef.current) {
      loadSlideImage();
    }
  }, [zoom, pan, annotations, currentAnnotation, isDrawing]);

  if (!slide) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">Selecione uma lâmina para visualizar</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{slide.original_filename}</CardTitle>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Controles de zoom */}
          <div className="flex items-center gap-1">
            <Button size="sm" variant="outline" onClick={handleZoomOut}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-sm min-w-[60px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <Button size="sm" variant="outline" onClick={handleZoomIn}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>

          {/* Ferramentas de anotação */}
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant={tool === 'pan' ? 'default' : 'outline'}
              onClick={() => setTool('pan')}
            >
              <Move className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant={tool === 'point' ? 'default' : 'outline'}
              onClick={() => setTool('point')}
            >
              <MousePointer className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant={tool === 'rectangle' ? 'default' : 'outline'}
              onClick={() => setTool('rectangle')}
            >
              <Square className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant={tool === 'circle' ? 'default' : 'outline'}
              onClick={() => setTool('circle')}
            >
              <Circle className="h-4 w-4" />
            </Button>
          </div>

          {/* Controles de anotação */}
          <Button size="sm" variant="destructive" onClick={clearAnnotations}>
            Limpar Anotações
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-0">
        <div
          ref={containerRef}
          className="relative w-full h-full overflow-hidden bg-gray-100"
        >
          <canvas
            ref={canvasRef}
            className="absolute inset-0 cursor-crosshair"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={() => {
              setIsDragging(false);
              setIsDrawing(false);
              setCurrentAnnotation(null);
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default SlideViewer;

