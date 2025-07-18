import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import SlideViewer from './components/SlideViewer';
import SlideUpload from './components/SlideUpload';
import SlideDashboard from './components/SlideDashboard';
import { Upload, FileImage, Brain, User } from 'lucide-react';
import './App.css';

function App() {
  const [selectedSlide, setSelectedSlide] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleSlideSelect = (slide) => {
    setSelectedSlide(slide);
    setActiveTab('viewer');
  };

  const handleUploadComplete = (slideData) => {
    console.log('Upload concluído:', slideData);
    // Atualizar dashboard automaticamente
    setActiveTab('dashboard');
  };

  const handleSlideDelete = (slideId) => {
    if (selectedSlide && selectedSlide.id === slideId) {
      setSelectedSlide(null);
      setActiveTab('dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
                <Brain className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">AIAPad</h1>
                <p className="text-sm text-muted-foreground">
                  Sistema de Análise de Lâminas Anatomopatológicas
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <User className="h-4 w-4 mr-2" />
                Login
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <FileImage className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="viewer" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Visualizador
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <SlideDashboard
              onSlideSelect={handleSlideSelect}
              onSlideDelete={handleSlideDelete}
              selectedSlideId={selectedSlide?.id}
            />
          </TabsContent>

          <TabsContent value="upload" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload de Lâminas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <SlideUpload
                  onUploadComplete={handleUploadComplete}
                  onUploadStart={(upload) => console.log('Upload iniciado:', upload)}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="viewer" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
              {/* Painel Lateral */}
              <div className="lg:col-span-1 space-y-4">
                <Card className="h-fit">
                  <CardHeader>
                    <CardTitle className="text-lg">Informações da Lâmina</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {selectedSlide ? (
                      <div className="space-y-3 text-sm">
                        <div>
                          <p className="font-medium">Nome:</p>
                          <p className="text-muted-foreground">{selectedSlide.original_filename}</p>
                        </div>
                        <div>
                          <p className="font-medium">Scanner:</p>
                          <p className="text-muted-foreground">{selectedSlide.scanner_type || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="font-medium">Coloração:</p>
                          <p className="text-muted-foreground">{selectedSlide.stain_type || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="font-medium">Dimensões:</p>
                          <p className="text-muted-foreground">
                            {selectedSlide.width && selectedSlide.height 
                              ? `${selectedSlide.width} × ${selectedSlide.height}` 
                              : 'N/A'
                            }
                          </p>
                        </div>
                        <div>
                          <p className="font-medium">Níveis de Zoom:</p>
                          <p className="text-muted-foreground">{selectedSlide.levels || 'N/A'}</p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-muted-foreground">
                        Selecione uma lâmina no dashboard para visualizar
                      </p>
                    )}
                  </CardContent>
                </Card>

                {selectedSlide && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Análise de IA</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <Button 
                          className="w-full" 
                          onClick={() => {
                            // Implementar análise de IA
                            alert('Análise de IA será implementada');
                          }}
                        >
                          <Brain className="h-4 w-4 mr-2" />
                          Analisar Lâmina
                        </Button>
                        <div className="text-sm text-muted-foreground">
                          <p>Funcionalidades disponíveis:</p>
                          <ul className="list-disc list-inside mt-2 space-y-1">
                            <li>Detecção de doenças</li>
                            <li>Classificação de tecidos</li>
                            <li>Identificação de reagentes</li>
                            <li>Análise morfológica</li>
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Visualizador Principal */}
              <div className="lg:col-span-3">
                <SlideViewer
                  slide={selectedSlide}
                  onAnnotation={(annotation) => {
                    console.log('Nova anotação:', annotation);
                  }}
                />
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default App;
