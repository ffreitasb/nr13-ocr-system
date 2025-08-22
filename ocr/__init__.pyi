"""
Arquivo de tipo stubs para o módulo OCR
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class OCRProcessor:
    """Processador OCR para placas NR-13"""
    
    def __init__(self) -> None: ...
    
    def process(self) -> Dict[str, Any]: ...
    
    def process_single(self, image_path: Union[str, Path]) -> Dict[str, Any]: ...
    
    def test_api_connection(self) -> bool: ...
    
    def get_stats(self) -> Dict[str, Any]: ...

class PlacaNR13:
    """Modelo para dados de placa NR-13"""
    
    def __init__(self, **kwargs: Any) -> None: ...
    
    def to_dict(self) -> Dict[str, Any]: ...
    
    def validate(self) -> Dict[str, Any]: ...

class FieldNormalizer:
    """Normalizador de campos"""
    
    def __init__(self) -> None: ...
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]: ...
    
    def learn_mapping(self, original: str, normalized: str) -> None: ...
