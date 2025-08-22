"""
Módulo OCR do sistema NR13
"""

from .models import PlacaNR13, BatchJob, ProcessingResult, ProcessingSummary
from .normalizer import FieldNormalizer
from .processor import OCRProcessor

__all__ = [
    'PlacaNR13',
    'BatchJob', 
    'ProcessingResult',
    'ProcessingSummary',
    'FieldNormalizer',
    'OCRProcessor'
]
