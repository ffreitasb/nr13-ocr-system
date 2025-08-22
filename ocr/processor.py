#!/usr/bin/env python3
"""
OCR Processor - Núcleo do sistema de processamento
"""
import base64
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from config.settings import settings
from ocr.models import PlacaNR13
from ocr.normalizer import FieldNormalizer
from utils import get_logger, format_time
from services import BatchManager


class FileManager:
    """Gerenciador de arquivos"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def list_images(self, directory: Path) -> List[Path]:
        """Lista imagens no diretório"""
        images = []
        for ext in settings.SUPPORTED_FORMATS:
            images.extend(directory.glob(f"*{ext}"))
        return sorted(images)
    
    def encode_image(self, image_path: Path) -> str:
        """Codifica imagem em base64"""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Erro ao codificar imagem {image_path}: {e}")
            raise


class OCRProcessor:
    """Processador principal de OCR"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.normalizer = FieldNormalizer()
        self.batch_manager = BatchManager()
        self.files = FileManager()
        
        # Estatísticas
        self.processed_count = 0
        self.error_count = 0
        
        self.logger.info("OCRProcessor inicializado")
    
    def process(self) -> Dict[str, Any]:
        """Processa todas as imagens do diretório de entrada"""
        try:
            start_time = time.time()
            
            # Lista imagens
            images = self.files.list_images(settings.INPUT_DIR)
            if not images:
                return {
                    'error': True,
                    'message': f'Nenhuma imagem encontrada em {settings.INPUT_DIR}'
                }
            
            total_images = len(images)
            self.logger.info(f"Processando {total_images} imagens")
            
            # Decide modo de processamento
            if total_images <= settings.BATCH_THRESHOLD:
                return self._process_sync(images, start_time)
            else:
                return self._process_batch(images, start_time)
                
        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            return {
                'error': True,
                'message': str(e)
            }
    
    def _process_sync(self, images: List[Path], start_time: float) -> Dict[str, Any]:
        """Processamento síncrono (até 5 imagens)"""
        results = []
        success_count = 0
        
        for i, image_path in enumerate(images, 1):
            self.logger.info(f"Processando {i}/{len(images)}: {image_path.name}")
            
            try:
                result = self._process_single_image(image_path)
                if result.get('success'):
                    results.append(result['data'])
                    success_count += 1
                    self.processed_count += 1
                else:
                    self.error_count += 1
                    self.logger.error(f"Erro em {image_path.name}: {result.get('error')}")
                    
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Erro processando {image_path.name}: {e}")
        
        # Salva resultados
        if results:
            self._save_results(results, 'sync')
        
        processing_time = time.time() - start_time
        
        return {
            'modo': 'sync',
            'total_imagens': len(images),
            'sucesso': success_count,
            'erros': len(images) - success_count,
            'taxa_sucesso': (success_count / len(images)) * 100,
            'tempo_total': processing_time,
            'resultados': results
        }
    
    def _process_batch(self, images: List[Path], start_time: float) -> Dict[str, Any]:
        """Processamento em batch (>5 imagens)"""
        self.logger.info(f"Iniciando processamento batch de {len(images)} imagens")
        
        try:
            # Submete job batch
            job_id = self.batch_manager.submit_job(images)
            
            # Aguarda conclusão
            results = self.batch_manager.wait_for_completion(job_id)
            
            if results:
                # Normaliza e salva resultados
                normalized_results = []
                for result in results:
                    if 'data' in result:
                        normalized = self.normalizer.normalize(result['data'])
                        normalized_results.append(normalized)
                
                if normalized_results:
                    self._save_results(normalized_results, 'batch')
                
                processing_time = time.time() - start_time
                success_count = len(normalized_results)
                
                return {
                    'modo': 'batch',
                    'job_id': job_id,
                    'total_imagens': len(images),
                    'sucesso': success_count,
                    'erros': len(images) - success_count,
                    'taxa_sucesso': (success_count / len(images)) * 100,
                    'tempo_total': processing_time,
                    'resultados': normalized_results
                }
            else:
                return {
                    'error': True,
                    'message': 'Falha no processamento batch'
                }
                
        except Exception as e:
            self.logger.error(f"Erro no processamento batch: {e}")
            return {
                'error': True,
                'message': str(e)
            }
    
    def process_single(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Processa uma única imagem"""
        image_path = Path(image_path)
        
        try:
            result = self._process_single_image(image_path)
            
            if result.get('success'):
                # Salva resultado individual
                filename = f"{image_path.stem}_ocr.json"
                output_path = settings.OUTPUT_JSON / filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Resultado salvo: {output_path}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro processando {image_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_single_image(self, image_path: Path) -> Dict[str, Any]:
        """Processa uma imagem individual"""
        start_time = time.time()
        
        try:
            # Codifica imagem
            image_data = self.files.encode_image(image_path)
            
            # Simula processamento OCR (substitua pela integração real com Mistral)
            ocr_result = self._mock_ocr_processing(image_path.name)
            
            # Normaliza campos
            normalized_data = self.normalizer.normalize(ocr_result)
            
            # Adiciona metadata
            normalized_data['_metadata'] = {
                'arquivo': image_path.name,
                'processado_em': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'modo': 'sync',
                'processing_time': time.time() - start_time
            }
            
            # Valida resultado
            validation = self._validate_result(normalized_data)
            normalized_data['_metadata']['validacao'] = validation
            
            return {
                'success': True,
                'data': normalized_data,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _mock_ocr_processing(self, filename: str) -> Dict[str, Any]:
        """Mock do processamento OCR (substitua pela integração real)"""
        # Simula resultado de OCR
        return {
            'Manufacturer': 'ACME Corporation',
            'Serial Number': f'SN-{filename[:8]}',
            'PMTA': '14.5 kgf/cm²',
            'Category': 'I',
            'Year': '2020',
            'Tag': f'TAG-{filename[:5]}',
            'Material': 'Carbon Steel',
            'Diameter': '1200 mm'
        }
    
    def _validate_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida resultado contra requisitos NR-13"""
        found_fields = []
        missing_fields = []
        
        for field in settings.REQUIRED_FIELDS:
            if field in data and data[field]:
                found_fields.append(field)
            else:
                missing_fields.append(field)
        
        total_required = len(settings.REQUIRED_FIELDS)
        completeness = (len(found_fields) / total_required) * 100
        is_valid = len(missing_fields) == 0
        
        return {
            'valid': is_valid,
            'completeness': completeness,
            'total_required': total_required,
            'found': found_fields,
            'missing': missing_fields
        }
    
    def _save_results(self, results: List[Dict], mode: str):
        """Salva resultados em arquivos JSON"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Salva cada resultado individualmente
        for i, result in enumerate(results):
            filename = f"placa_{timestamp}_{i+1:03d}_ocr.json"
            output_path = settings.OUTPUT_JSON / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Salva resumo do processamento
        summary = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'modo': mode,
            'total_imagens': len(results),
            'sucesso': len(results),
            'erros': 0,
            'taxa_sucesso': 100.0,
            'arquivos_gerados': len(results)
        }
        
        summary_path = settings.OUTPUT_REPORTS / f"resumo_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Resultados salvos: {len(results)} arquivos")
    
    def test_api_connection(self) -> bool:
        """Testa conexão com a API"""
        try:
            # Mock do teste de conexão
            # Substitua pela verificação real com Mistral AI
            self.logger.info("Testando conexão com API...")
            time.sleep(1)  # Simula latência
            return True
        except Exception as e:
            self.logger.error(f"Erro no teste de conexão: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do processador"""
        total_processed = self.processed_count + self.error_count
        success_rate = (self.processed_count / total_processed * 100) if total_processed > 0 else 0
        
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'normalizer_stats': self.normalizer.get_stats(),
            'batch_stats': self.batch_manager.get_stats()
        }
