#!/usr/bin/env python3
"""
Services - Serviços externos e integrações
"""
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.settings import settings
from utils import get_logger


class BatchManager:
    """Gerenciador de jobs batch da Mistral AI"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.jobs_file = settings.OUTPUT_BATCH / "batch_jobs.json"
        self.jobs_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Carrega histórico de jobs
        self.jobs_history = self._load_jobs_history()
    
    def _load_jobs_history(self) -> Dict[str, Any]:
        """Carrega histórico de jobs do arquivo"""
        try:
            if self.jobs_file.exists():
                with open(self.jobs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Erro carregando histórico de jobs: {e}")
            return {}
    
    def _save_jobs_history(self):
        """Salva histórico de jobs no arquivo"""
        try:
            with open(self.jobs_file, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro salvando histórico de jobs: {e}")
    
    def submit_job(self, images: List[Path]) -> str:
        """Submete job batch para processamento"""
        try:
            job_id = f"batch_{int(time.time())}_{len(images)}"
            
            self.logger.info(f"Submetendo batch job {job_id} com {len(images)} imagens")
            
            # Prepara dados do job
            job_data = {
                'job_id': job_id,
                'created_at': datetime.now().isoformat(),
                'status': 'created',
                'total_images': len(images),
                'images': [str(img) for img in images],
                'results_count': 0
            }
            
            # Simula submissão do job
            # Em implementação real, aqui seria a chamada para Mistral Batch API
            time.sleep(1)  # Simula latência de rede
            
            # Atualiza status para running
            job_data['status'] = 'running'
            job_data['started_at'] = datetime.now().isoformat()
            
            # Salva no histórico
            self.jobs_history[job_id] = job_data
            self._save_jobs_history()
            
            self.logger.info(f"Job {job_id} submetido com sucesso")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Erro submetendo job batch: {e}")
            raise
    
    def wait_for_completion(self, job_id: str, max_wait: int = None) -> Optional[List[Dict]]:
        """Aguarda conclusão do job batch"""
        if max_wait is None:
            max_wait = settings.MAX_WAIT_TIME
        
        start_time = time.time()
        check_interval = settings.BATCH_CHECK_INTERVAL
        
        self.logger.info(f"Aguardando conclusão do job {job_id}")
        
        while (time.time() - start_time) < max_wait:
            status = self.check_job_status(job_id)
            
            if status == 'completed':
                return self._get_job_results(job_id)
            elif status == 'failed':
                self.logger.error(f"Job {job_id} falhou")
                return None
            elif status in ['created', 'running']:
                self.logger.info(f"Job {job_id} ainda processando... aguardando {check_interval}s")
                time.sleep(check_interval)
            else:
                self.logger.warning(f"Status desconhecido para job {job_id}: {status}")
                time.sleep(check_interval)
        
        self.logger.error(f"Timeout aguardando job {job_id}")
        return None
    
    def check_job_status(self, job_id: str) -> str:
        """Verifica status do job"""
        try:
            if job_id not in self.jobs_history:
                return 'not_found'
            
            job_data = self.jobs_history[job_id]
            current_status = job_data.get('status', 'unknown')
            
            # Simula progressão do job
            if current_status == 'running':
                # Simula processamento baseado no tempo
                created_at = datetime.fromisoformat(job_data['created_at'])
                elapsed = (datetime.now() - created_at).total_seconds()
                
                # Simula que jobs completam em 30-60 segundos
                if elapsed > 45:
                    job_data['status'] = 'completed'
                    job_data['completed_at'] = datetime.now().isoformat()
                    job_data['results_count'] = job_data['total_images']
                    self._save_jobs_history()
                    return 'completed'
            
            return current_status
            
        except Exception as e:
            self.logger.error(f"Erro verificando status do job {job_id}: {e}")
            return 'error'
    
    def _get_job_results(self, job_id: str) -> List[Dict]:
        """Obtém resultados do job"""
        try:
            if job_id not in self.jobs_history:
                return []
            
            job_data = self.jobs_history[job_id]
            
            # Simula resultados do processamento
            results = []
            for i in range(job_data['total_images']):
                result = {
                    'image_index': i,
                    'success': True,
                    'data': {
                        'fabricante': f'Fabricante {i+1}',
                        'numero_serie': f'SN-{job_id[-8:]}-{i:03d}',
                        'categoria': 'I',
                        'pressao_maxima_trabalho': '14.5 kgf/cm²',
                        'ano_fabricacao': '2020',
                        'identificacao': f'TAG-{i+1:03d}'
                    }
                }
                results.append(result)
            
            self.logger.info(f"Obtidos {len(results)} resultados para job {job_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro obtendo resultados do job {job_id}: {e}")
            return []
    
    def list_jobs(self, limit: int = 50) -> Dict[str, Any]:
        """Lista jobs do histórico"""
        try:
            # Ordena jobs por data de criação (mais recente primeiro)
            sorted_jobs = dict(sorted(
                self.jobs_history.items(),
                key=lambda x: x[1].get('created_at', ''),
                reverse=True
            ))
            
            # Limita resultado
            if limit:
                limited_jobs = dict(list(sorted_jobs.items())[:limit])
                return limited_jobs
            
            return sorted_jobs
            
        except Exception as e:
            self.logger.error(f"Erro listando jobs: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos jobs batch"""
        try:
            total_jobs = len(self.jobs_history)
            
            if total_jobs == 0:
                return {
                    'total_jobs': 0,
                    'status_breakdown': {},
                    'total_images_processed': 0
                }
            
            # Conta status
            status_count = {}
            total_images = 0
            
            for job_data in self.jobs_history.values():
                status = job_data.get('status', 'unknown')
                status_count[status] = status_count.get(status, 0) + 1
                
                if status == 'completed':
                    total_images += job_data.get('total_images', 0)
            
            return {
                'total_jobs': total_jobs,
                'status_breakdown': status_count,
                'total_images_processed': total_images
            }
            
        except Exception as e:
            self.logger.error(f"Erro obtendo estatísticas: {e}")
            return {
                'total_jobs': 0,
                'status_breakdown': {},
                'total_images_processed': 0
            }


class MistralAPI:
    """Cliente para integração com Mistral AI"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.api_key = settings.MISTRAL_API_KEY
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Testa conexão com a API"""
        try:
            # Mock do teste de conexão
            # Em implementação real, faria chamada para endpoint de teste
            self.logger.info("Testando conexão com Mistral AI...")
            
            if not self.api_key or self.api_key == "your_api_key_here":
                self.logger.error("API key não configurada")
                return False
            
            # Simula teste bem-sucedido
            time.sleep(0.5)
            self.logger.info("Conexão com Mistral AI bem-sucedida")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro testando conexão: {e}")
            return False
    
    def process_image(self, image_data: str, image_name: str) -> Dict[str, Any]:
        """Processa uma imagem via API"""
        try:
            # Mock do processamento
            # Em implementação real, enviaria imagem para Mistral Pixtral
            
            self.logger.info(f"Processando imagem {image_name} via Mistral AI")
            
            # Simula latência da API
            time.sleep(2)
            
            # Simula resultado de OCR
            mock_result = {
                'Manufacturer': 'ACME Corporation',
                'Serial Number': f'SN-{image_name[:8]}',
                'PMTA': '14.5 kgf/cm²',
                'Category': 'I',
                'Year': '2020',
                'Tag': f'TAG-{image_name[:5]}',
                'Material': 'Carbon Steel',
                'Diameter': '1200 mm',
                'Inspection Date': '2023-01-15'
            }
            
            return {
                'success': True,
                'data': mock_result
            }
            
        except Exception as e:
            self.logger.error(f"Erro processando imagem {image_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class ReportGenerator:
    """Gerador de relatórios"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def generate_summary_report(self, results: List[Dict], processing_info: Dict) -> Dict[str, Any]:
        """Gera relatório resumo do processamento"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Calcula estatísticas
            total_images = len(results)
            valid_results = [r for r in results if r.get('_metadata', {}).get('validacao', {}).get('valid', False)]
            success_rate = (len(valid_results) / total_images * 100) if total_images > 0 else 0
            
            # Analisa completude
            completeness_values = [
                r.get('_metadata', {}).get('validacao', {}).get('completeness', 0)
                for r in results
            ]
            avg_completeness = sum(completeness_values) / len(completeness_values) if completeness_values else 0
            
            # Campos mais encontrados
            field_counts = {}
            for result in results:
                for field in settings.REQUIRED_FIELDS:
                    if field in result and result[field]:
                        field_counts[field] = field_counts.get(field, 0) + 1
            
            report = {
                'timestamp': timestamp,
                'processing_info': processing_info,
                'statistics': {
                    'total_images': total_images,
                    'valid_results': len(valid_results),
                    'success_rate': success_rate,
                    'average_completeness': avg_completeness
                },
                'field_analysis': {
                    'field_counts': field_counts,
                    'most_found_fields': sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                },
                'summary': {
                    'modo': processing_info.get('modo', 'unknown'),
                    'tempo_total': processing_info.get('tempo_total', 0),
                    'taxa_sucesso': success_rate,
                    'completude_media': avg_completeness
                }
            }
            
            # Salva relatório
            report_filename = f"relatorio_completo_{timestamp.replace(':', '-').split('.')[0]}.json"
            report_path = settings.OUTPUT_REPORTS / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório gerado: {report_path}")
            return report
            
        except Exception as e:
            self.logger.error(f"Erro gerando relatório: {e}")
            return {}
