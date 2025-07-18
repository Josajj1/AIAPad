import numpy as np
import cv2
from PIL import Image
import json
from typing import Dict, List, Tuple, Optional
import openslide

class BasicClassifier:
    """Classificador básico para análise de lâminas patológicas"""
    
    def __init__(self):
        self.model_name = "basic_classifier"
        self.version = "1.0"
        
    def analyze_slide(self, slide_path: str, analysis_type: str = "disease_detection") -> Dict:
        """Analisar uma lâmina e retornar resultados"""
        try:
            slide = openslide.OpenSlide(slide_path)
            
            # Obter thumbnail para análise rápida
            level = slide.level_count - 1
            thumbnail = slide.read_region((0, 0), level, slide.level_dimensions[level])
            thumbnail = thumbnail.convert('RGB')
            
            # Converter para array numpy
            img_array = np.array(thumbnail)
            
            # Análise básica baseada em características de cor e textura
            result = self._basic_analysis(img_array, analysis_type)
            
            slide.close()
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'prediction': 'Error',
                'confidence': 0.0,
                'regions_of_interest': []
            }
    
    def _basic_analysis(self, img_array: np.ndarray, analysis_type: str) -> Dict:
        """Realizar análise básica da imagem"""
        
        # Análise de cor para detectar tipo de coloração
        stain_type = self._detect_stain_type(img_array)
        
        # Análise de textura básica
        texture_features = self._extract_texture_features(img_array)
        
        # Detecção de regiões de interesse baseada em densidade de núcleos
        roi_regions = self._detect_roi_regions(img_array)
        
        if analysis_type == "disease_detection":
            prediction, confidence = self._disease_detection(img_array, texture_features)
        elif analysis_type == "stain_classification":
            prediction, confidence = stain_type, 0.8
        else:
            prediction, confidence = "Normal tissue", 0.7
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'stain_type': stain_type,
            'texture_features': texture_features,
            'regions_of_interest': roi_regions,
            'analysis_type': analysis_type
        }
    
    def _detect_stain_type(self, img_array: np.ndarray) -> str:
        """Detectar tipo de coloração baseado em análise de cor"""
        
        # Converter para HSV para melhor análise de cor
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Calcular histogramas de cor
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        
        # Análise básica baseada em características conhecidas
        # H&E: tons de azul/roxo (hematoxilina) e rosa/vermelho (eosina)
        blue_purple_ratio = np.sum(hist_h[100:140]) / np.sum(hist_h)
        pink_red_ratio = np.sum(hist_h[0:20]) / np.sum(hist_h)
        
        if blue_purple_ratio > 0.3 and pink_red_ratio > 0.2:
            return "H&E"
        elif blue_purple_ratio > 0.4:
            return "IHC"
        else:
            return "Unknown"
    
    def _extract_texture_features(self, img_array: np.ndarray) -> Dict:
        """Extrair características de textura básicas"""
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Calcular características básicas
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        
        # Detectar bordas usando Canny
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calcular entropia (medida de complexidade)
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist / np.sum(hist)  # Normalizar
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        return {
            'mean_intensity': float(mean_intensity),
            'std_intensity': float(std_intensity),
            'edge_density': float(edge_density),
            'entropy': float(entropy)
        }
    
    def _detect_roi_regions(self, img_array: np.ndarray) -> List[Dict]:
        """Detectar regiões de interesse baseadas em densidade de núcleos"""
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Aplicar threshold para destacar núcleos (geralmente mais escuros)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        binary = 255 - binary  # Inverter para núcleos ficarem brancos
        
        # Encontrar contornos
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por tamanho (possíveis núcleos)
        min_area = 10
        max_area = 1000
        nucleus_contours = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
        
        # Agrupar núcleos em regiões de alta densidade
        roi_regions = []
        if len(nucleus_contours) > 10:  # Só processar se houver núcleos suficientes
            
            # Calcular centros dos núcleos
            centers = []
            for contour in nucleus_contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centers.append((cx, cy))
            
            # Encontrar regiões de alta densidade (simplificado)
            if len(centers) > 20:
                # Dividir imagem em grid e contar núcleos por região
                h, w = img_array.shape[:2]
                grid_size = 5
                cell_h, cell_w = h // grid_size, w // grid_size
                
                for i in range(grid_size):
                    for j in range(grid_size):
                        x1, y1 = j * cell_w, i * cell_h
                        x2, y2 = min((j + 1) * cell_w, w), min((i + 1) * cell_h, h)
                        
                        # Contar núcleos nesta célula
                        count = sum(1 for cx, cy in centers if x1 <= cx < x2 and y1 <= cy < y2)
                        
                        # Se densidade alta, adicionar como ROI
                        if count > len(centers) / (grid_size * grid_size) * 2:
                            roi_regions.append({
                                'x': x1,
                                'y': y1,
                                'width': x2 - x1,
                                'height': y2 - y1,
                                'nucleus_count': count,
                                'type': 'high_density'
                            })
        
        return roi_regions
    
    def _disease_detection(self, img_array: np.ndarray, texture_features: Dict) -> Tuple[str, float]:
        """Detecção básica de doença baseada em características"""
        
        # Regras simples baseadas em características conhecidas
        edge_density = texture_features['edge_density']
        entropy = texture_features['entropy']
        std_intensity = texture_features['std_intensity']
        
        # Lógica simplificada para demonstração
        if edge_density > 0.15 and entropy > 6.5:
            if std_intensity > 50:
                return "Possible malignancy", 0.75
            else:
                return "Inflammatory changes", 0.65
        elif edge_density < 0.05 and entropy < 5.0:
            return "Normal tissue", 0.85
        else:
            return "Benign changes", 0.60

class StainNormalizer:
    """Normalizador de coloração para padronizar imagens"""
    
    def __init__(self):
        # Valores de referência para H&E (Macenko et al.)
        self.target_stains = np.array([
            [0.5626, 0.2159],
            [0.7201, 0.8012],
            [0.4062, 0.5581]
        ])
        
    def normalize_he_stain(self, img_array: np.ndarray) -> np.ndarray:
        """Normalizar coloração H&E"""
        try:
            # Implementação simplificada de normalização de coloração
            # Em produção, usaria métodos mais sofisticados como Macenko ou Vahadane
            
            # Converter para float
            img_float = img_array.astype(np.float32) / 255.0
            
            # Aplicar correção de gamma simples
            gamma = 1.2
            img_corrected = np.power(img_float, gamma)
            
            # Normalizar canais individualmente
            for i in range(3):
                channel = img_corrected[:, :, i]
                channel = (channel - np.min(channel)) / (np.max(channel) - np.min(channel))
                img_corrected[:, :, i] = channel
            
            # Converter de volta para uint8
            return (img_corrected * 255).astype(np.uint8)
            
        except Exception as e:
            print(f"Erro na normalização: {e}")
            return img_array

class AnnotationProcessor:
    """Processador para análise de anotações e treinamento"""
    
    def __init__(self):
        self.annotation_types = {
            'normal': 0,
            'abnormal': 1,
            'malignant': 2,
            'benign': 3
        }
    
    def process_annotations_for_training(self, slide_path: str, annotations: List[Dict]) -> Dict:
        """Processar anotações para gerar dados de treinamento"""
        
        training_data = {
            'patches': [],
            'labels': [],
            'metadata': []
        }
        
        try:
            slide = openslide.OpenSlide(slide_path)
            
            for annotation in annotations:
                # Extrair patch da região anotada
                x, y = int(annotation['x']), int(annotation['y'])
                width = int(annotation.get('width', 256))
                height = int(annotation.get('height', 256))
                
                # Ler região
                patch = slide.read_region((x, y), 0, (width, height))
                patch = patch.convert('RGB')
                patch_array = np.array(patch)
                
                # Obter label
                label = annotation.get('label', 'normal')
                label_id = self.annotation_types.get(label.lower(), 0)
                
                training_data['patches'].append(patch_array)
                training_data['labels'].append(label_id)
                training_data['metadata'].append({
                    'x': x, 'y': y, 'width': width, 'height': height,
                    'label': label, 'annotation_id': annotation.get('id')
                })
            
            slide.close()
            
        except Exception as e:
            print(f"Erro ao processar anotações: {e}")
        
        return training_data
    
    def extract_features_from_patch(self, patch: np.ndarray) -> Dict:
        """Extrair características de um patch anotado"""
        
        # Características de cor
        mean_rgb = np.mean(patch, axis=(0, 1))
        std_rgb = np.std(patch, axis=(0, 1))
        
        # Características de textura
        gray = cv2.cvtColor(patch, cv2.COLOR_RGB2GRAY)
        
        # LBP (Local Binary Pattern) simplificado
        lbp_hist = self._calculate_lbp_histogram(gray)
        
        # Características de forma (se houver contornos)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_features = {
            'num_contours': len(contours),
            'total_contour_area': sum(cv2.contourArea(c) for c in contours),
            'edge_density': np.sum(edges > 0) / edges.size
        }
        
        return {
            'color_features': {
                'mean_rgb': mean_rgb.tolist(),
                'std_rgb': std_rgb.tolist()
            },
            'texture_features': {
                'lbp_histogram': lbp_hist
            },
            'shape_features': shape_features
        }
    
    def _calculate_lbp_histogram(self, gray_image: np.ndarray, radius: int = 1, n_points: int = 8) -> List[float]:
        """Calcular histograma LBP simplificado"""
        
        # Implementação básica de LBP
        h, w = gray_image.shape
        lbp = np.zeros((h, w), dtype=np.uint8)
        
        for i in range(radius, h - radius):
            for j in range(radius, w - radius):
                center = gray_image[i, j]
                binary_string = ""
                
                # Comparar com vizinhos em círculo
                for k in range(n_points):
                    angle = 2 * np.pi * k / n_points
                    x = int(i + radius * np.cos(angle))
                    y = int(j + radius * np.sin(angle))
                    
                    if 0 <= x < h and 0 <= y < w:
                        if gray_image[x, y] >= center:
                            binary_string += "1"
                        else:
                            binary_string += "0"
                
                lbp[i, j] = int(binary_string, 2) if binary_string else 0
        
        # Calcular histograma
        hist, _ = np.histogram(lbp, bins=2**n_points, range=(0, 2**n_points))
        hist = hist / np.sum(hist)  # Normalizar
        
        return hist.tolist()

