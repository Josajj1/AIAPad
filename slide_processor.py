import openslide
import os
import re
from typing import Dict, Optional

class SlideProcessor:
    """Classe para processamento e extração de metadados de lâminas digitais"""
    
    def __init__(self):
        self.stain_patterns = {
            'H&E': ['hematoxylin', 'eosin', 'h&e', 'he'],
            'IHC': ['ihc', 'immunohistochemistry', 'cd', 'ki-67', 'p53'],
            'PAS': ['pas', 'periodic acid'],
            'Masson': ['masson', 'trichrome'],
            'Congo Red': ['congo', 'red'],
            'Silver': ['silver', 'reticulin']
        }
        
        self.scanner_patterns = {
            'Aperio': ['aperio', 'leica'],
            'Hamamatsu': ['hamamatsu', 'nanozoomer'],
            'Philips': ['philips', 'ultra fast scanner'],
            'Zeiss': ['zeiss', 'mirax'],
            'Olympus': ['olympus', 'vs120'],
            'Ventana': ['ventana', 'iscan']
        }
    
    def extract_metadata(self, slide_path: str) -> Dict:
        """Extrair metadados de uma lâmina digital"""
        try:
            slide = openslide.OpenSlide(slide_path)
            
            metadata = {
                'width': slide.dimensions[0],
                'height': slide.dimensions[1],
                'levels': slide.level_count,
                'mpp_x': self._get_mpp(slide, 'x'),
                'mpp_y': self._get_mpp(slide, 'y'),
                'scanner_type': self._detect_scanner(slide),
                'stain_type': self._detect_stain(slide),
                'objective_power': self._get_objective_power(slide),
                'vendor': slide.detect_format(slide_path) if hasattr(slide, 'detect_format') else None
            }
            
            slide.close()
            return metadata
            
        except Exception as e:
            print(f"Erro ao extrair metadados: {e}")
            return {
                'width': None,
                'height': None,
                'levels': None,
                'mpp_x': None,
                'mpp_y': None,
                'scanner_type': None,
                'stain_type': None,
                'objective_power': None,
                'vendor': None
            }
    
    def _get_mpp(self, slide: openslide.OpenSlide, axis: str) -> Optional[float]:
        """Obter microns per pixel"""
        try:
            if axis.lower() == 'x':
                mpp_key = openslide.PROPERTY_NAME_MPP_X
            else:
                mpp_key = openslide.PROPERTY_NAME_MPP_Y
            
            if mpp_key in slide.properties:
                return float(slide.properties[mpp_key])
            
            # Tentar outras chaves comuns
            alt_keys = [
                f'aperio.MPP{axis.upper()}',
                f'hamamatsu.XHPF',
                f'philips.DICOM_PIXEL_SPACING'
            ]
            
            for key in alt_keys:
                if key in slide.properties:
                    return float(slide.properties[key])
                    
        except (ValueError, KeyError):
            pass
        
        return None
    
    def _detect_scanner(self, slide: openslide.OpenSlide) -> Optional[str]:
        """Detectar tipo de scanner baseado nos metadados"""
        properties_text = ' '.join([
            str(slide.properties.get('openslide.vendor', '')),
            str(slide.properties.get('aperio.Title', '')),
            str(slide.properties.get('hamamatsu.SourceLens', '')),
            str(slide.properties.get('philips.DICOM_MANUFACTURER', ''))
        ]).lower()
        
        for scanner, patterns in self.scanner_patterns.items():
            for pattern in patterns:
                if pattern in properties_text:
                    return scanner
        
        # Verificar pelo formato do arquivo
        vendor = slide.properties.get('openslide.vendor', '').lower()
        if 'aperio' in vendor:
            return 'Aperio'
        elif 'hamamatsu' in vendor:
            return 'Hamamatsu'
        elif 'philips' in vendor:
            return 'Philips'
        
        return 'Unknown'
    
    def _detect_stain(self, slide: openslide.OpenSlide) -> Optional[str]:
        """Detectar tipo de coloração baseado nos metadados"""
        # Verificar propriedades que podem conter informações sobre coloração
        stain_sources = [
            slide.properties.get('aperio.Title', ''),
            slide.properties.get('aperio.Label', ''),
            slide.properties.get('hamamatsu.SourceLens', ''),
            slide.properties.get('openslide.comment', '')
        ]
        
        stain_text = ' '.join(str(source) for source in stain_sources).lower()
        
        for stain_type, patterns in self.stain_patterns.items():
            for pattern in patterns:
                if pattern in stain_text:
                    return stain_type
        
        # Se não encontrou padrão específico, assumir H&E como padrão
        return 'H&E'
    
    def _get_objective_power(self, slide: openslide.OpenSlide) -> Optional[str]:
        """Obter magnificação da objetiva"""
        try:
            # Tentar diferentes propriedades que podem conter informação de magnificação
            mag_keys = [
                'aperio.AppMag',
                'openslide.objective-power',
                'hamamatsu.SourceLens'
            ]
            
            for key in mag_keys:
                if key in slide.properties:
                    value = slide.properties[key]
                    # Extrair número da string
                    match = re.search(r'(\d+)', str(value))
                    if match:
                        return f"{match.group(1)}x"
            
        except Exception:
            pass
        
        return None
    
    def get_tile_coordinates(self, slide_path: str, level: int, tile_size: int = 256) -> list:
        """Gerar coordenadas para tiles de uma lâmina"""
        try:
            slide = openslide.OpenSlide(slide_path)
            
            if level >= slide.level_count:
                level = slide.level_count - 1
            
            width, height = slide.level_dimensions[level]
            downsample = slide.level_downsamples[level]
            
            tiles = []
            for y in range(0, height, tile_size):
                for x in range(0, width, tile_size):
                    # Coordenadas no nível 0
                    x0 = int(x * downsample)
                    y0 = int(y * downsample)
                    
                    # Tamanho do tile ajustado
                    w = min(tile_size, width - x)
                    h = min(tile_size, height - y)
                    
                    tiles.append({
                        'x': x0,
                        'y': y0,
                        'width': w,
                        'height': h,
                        'level': level
                    })
            
            slide.close()
            return tiles
            
        except Exception as e:
            print(f"Erro ao gerar coordenadas de tiles: {e}")
            return []
    
    def validate_slide(self, slide_path: str) -> Dict:
        """Validar se o arquivo é uma lâmina válida"""
        result = {
            'valid': False,
            'error': None,
            'format': None
        }
        
        try:
            if not os.path.exists(slide_path):
                result['error'] = 'Arquivo não encontrado'
                return result
            
            # Tentar abrir com OpenSlide
            slide = openslide.OpenSlide(slide_path)
            
            # Verificar se tem dimensões válidas
            if slide.dimensions[0] == 0 or slide.dimensions[1] == 0:
                result['error'] = 'Dimensões inválidas'
                slide.close()
                return result
            
            result['valid'] = True
            result['format'] = slide.properties.get('openslide.vendor', 'Unknown')
            
            slide.close()
            
        except openslide.OpenSlideError as e:
            result['error'] = f'Erro do OpenSlide: {str(e)}'
        except Exception as e:
            result['error'] = f'Erro geral: {str(e)}'
        
        return result

