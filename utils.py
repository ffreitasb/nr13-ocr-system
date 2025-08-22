#!/usr/bin/env python3
"""
Utils - Utilitários e funções auxiliares
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import settings


def setup_logging() -> None:
    """Configura sistema de logging"""
    # Garante que diretório de logs existe
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Arquivo de log
    log_file = settings.LOGS_DIR / f"ocr_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configuração do logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna logger configurado"""
    return logging.getLogger(name)


def print_banner():
    """Imprime banner do sistema"""
    banner = f"""
🔧 SISTEMA OCR PARA PLACAS NR-13
    Versão Modular com IA
============================================================
📊 Total de imagens processadas: {get_total_processed()}
⚡ Modo: Híbrido Inteligente (Sync + Batch)
🤖 Engine: Mistral AI Pixtral-12b-2409
📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
============================================================
"""
    print(banner)


def print_summary(summary: Dict[str, Any]):
    """Imprime resumo do processamento"""
    print(f"\n📊 RESUMO DO PROCESSAMENTO")
    print("=" * 50)
    
    modo = summary.get('modo', 'N/A').upper()
    total = summary.get('total_imagens', 0)
    sucesso = summary.get('sucesso', 0)
    erros = summary.get('erros', 0)
    taxa = summary.get('taxa_sucesso', 0)
    tempo = summary.get('tempo_total', 0)
    
    print(f"🎯 Modo: {modo}")
    print(f"📷 Total de Imagens: {total}")
    print(f"✅ Sucessos: {sucesso}")
    print(f"❌ Erros: {erros}")
    print(f"📈 Taxa de Sucesso: {taxa:.1f}%")
    print(f"⏱️  Tempo Total: {format_time(tempo)}")
    
    if 'job_id' in summary:
        print(f"🆔 Job ID: {summary['job_id']}")
    
    # Economia no modo batch
    if modo == 'BATCH' and total > settings.BATCH_THRESHOLD:
        savings = calculate_batch_savings(total)
        print(f"💰 Economia: ~{savings:.1f}% (Batch API)")
    
    print("=" * 50)


def ask_confirmation(message: str) -> bool:
    """Pede confirmação do usuário"""
    while True:
        response = input(f"{message} (s/n): ").strip().lower()
        if response in ['s', 'sim', 'y', 'yes']:
            return True
        elif response in ['n', 'nao', 'não', 'no']:
            return False
        else:
            print("❌ Resposta inválida. Digite 's' para sim ou 'n' para não.")


def format_time(seconds: float) -> str:
    """Formata tempo em segundos para formato legível"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def calculate_batch_savings(image_count: int) -> float:
    """Calcula economia percentual do modo batch"""
    if image_count <= settings.BATCH_THRESHOLD:
        return 0.0
    
    # Batch API tem 50% de desconto
    return 50.0


def get_total_processed() -> int:
    """Retorna total de imagens já processadas"""
    try:
        json_files = list(settings.OUTPUT_JSON.glob("*_ocr.json"))
        return len(json_files)
    except Exception:
        return 0


def get_system_info() -> Dict[str, Any]:
    """Retorna informações do sistema"""
    try:
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': str(Path.cwd()),
            'project_directory': str(Path(__file__).parent.parent),
            'settings_valid': True,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def validate_nr13_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida resultado contra requisitos NR-13"""
    try:
        found_fields = []
        missing_fields = []
        
        for field in settings.REQUIRED_FIELDS:
            if field in data and data[field] and str(data[field]).strip():
                found_fields.append(field)
            else:
                missing_fields.append(field)
        
        total_required = len(settings.REQUIRED_FIELDS)
        completeness = (len(found_fields) / total_required) * 100 if total_required > 0 else 0
        is_valid = len(missing_fields) == 0
        
        return {
            'valid': is_valid,
            'completeness': completeness,
            'total_required': total_required,
            'found': found_fields,
            'missing': missing_fields
        }
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Erro na validação NR-13: {e}")
        return {
            'valid': False,
            'completeness': 0.0,
            'total_required': len(settings.REQUIRED_FIELDS),
            'found': [],
            'missing': settings.REQUIRED_FIELDS,
            'error': str(e)
        }


def ensure_directories():
    """Garante que todos os diretórios necessários existem"""
    directories = [
        settings.INPUT_DIR,
        settings.OUTPUT_JSON,
        settings.OUTPUT_BATCH,
        settings.OUTPUT_REPORTS,
        settings.LOGS_DIR,
        Path('data')
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
        # Cria .gitkeep se não existe
        gitkeep = directory / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.write_text('')


def clean_old_logs(days: int = 30):
    """Remove logs antigos"""
    try:
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for log_file in settings.LOGS_DIR.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                print(f"🗑️  Log removido: {log_file.name}")
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Erro limpando logs: {e}")


def format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo em formato legível"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca texto para exibição"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def sanitize_filename(filename: str) -> str:
    """Sanitiza nome de arquivo removendo caracteres inválidos"""
    import re
    # Remove caracteres inválidos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove espaços extras
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove underscores extras
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')


def load_json_safe(file_path: Path) -> Optional[Dict[str, Any]]:
    """Carrega arquivo JSON com tratamento de erro"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Erro carregando JSON {file_path}: {e}")
        return None


def save_json_safe(data: Dict[str, Any], file_path: Path) -> bool:
    """Salva arquivo JSON com tratamento de erro"""
    try:
        # Garante que diretório existe
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Erro salvando JSON {file_path}: {e}")
        return False


def progress_bar(current: int, total: int, width: int = 50) -> str:
    """Gera barra de progresso textual"""
    if total == 0:
        return "[" + "="*width + "] 100%"
    
    progress = current / total
    filled = int(width * progress)
    bar = "=" * filled + "-" * (width - filled)
    percentage = progress * 100
    
    return f"[{bar}] {percentage:.1f}% ({current}/{total})"


def estimate_processing_time(image_count: int, mode: str = "auto") -> float:
    """Estima tempo de processamento baseado no número de imagens"""
    if mode == "auto":
        mode = "batch" if image_count > settings.BATCH_THRESHOLD else "sync"
    
    if mode == "sync":
        # Processamento síncrono: ~3s por imagem
        return image_count * 3.0
    else:
        # Processamento batch: overhead inicial + processamento paralelo
        return 60 + (image_count * 0.5)  # 1min setup + 0.5s por imagem


def check_disk_space(required_mb: int = 100) -> bool:
    """Verifica se há espaço em disco suficiente"""
    try:
        import shutil
        free_bytes = shutil.disk_usage(Path.cwd()).free
        free_mb = free_bytes / (1024 * 1024)
        return free_mb >= required_mb
    except Exception:
        return True  # Assume que há espaço se não conseguir verificar


def get_file_hash(file_path: Path) -> str:
    """Calcula hash SHA256 de um arquivo"""
    import hashlib
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""


def format_currency(amount: float, currency: str = "USD") -> str:
    """Formata valor monetário"""
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "BRL":
        return f"R$ {amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"


def is_image_file(file_path: Path) -> bool:
    """Verifica se arquivo é uma imagem suportada"""
    return file_path.suffix.lower() in settings.SUPPORTED_FORMATS


def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> bool:
    """Cria backup de um arquivo"""
    try:
        if backup_dir is None:
            backup_dir = file_path.parent / "backup"
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        import shutil
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Erro criando backup de {file_path}: {e}")
        return False


# Inicializa logging quando módulo é importado
try:
    setup_logging()
except Exception:
    # Fallback se configuração falhar
    logging.basicConfig(level=logging.INFO)
