"""
Configurações centralizadas do sistema NR13 OCR
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Settings:
    """Configurações do sistema"""

    # API Configuration
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "pixtral-12b-2409")

    # Batch Processing
    BATCH_THRESHOLD = int(os.getenv("BATCH_THRESHOLD", "5"))
    MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "500"))
    BATCH_CHECK_INTERVAL = int(os.getenv("BATCH_CHECK_INTERVAL", "30"))
    MAX_WAIT_TIME = int(os.getenv("MAX_WAIT_TIME", "3600"))

    # Paths
    ROOT = Path(__file__).parent.parent
    CONFIG_DIR = ROOT / "config"
    DATA_DIR = ROOT / "data"
    INPUT_DIR = ROOT / "input"
    OUTPUT_DIR = ROOT / "output"
    OUTPUT_JSON = OUTPUT_DIR / "json"
    OUTPUT_BATCH = OUTPUT_DIR / "batch"
    OUTPUT_REPORTS = OUTPUT_DIR / "reports"
    LOGS_DIR = ROOT / "logs"

    # Processing
    SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # NR-13 Requirements
    REQUIRED_FIELDS = [
        "identificacao",
        "fabricante",
        "categoria",
        "pressao_maxima_trabalho",
        "numero_ordem"
    ]

    @classmethod
    def validate(cls):
        """Valida configurações essenciais"""
        if not cls.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY não configurada no arquivo .env")

        # Cria diretórios se não existirem
        for path in [cls.INPUT_DIR, cls.OUTPUT_JSON, cls.OUTPUT_BATCH,
                     cls.OUTPUT_REPORTS, cls.LOGS_DIR, cls.DATA_DIR]:
            path.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def get_env_info(cls) -> dict:
        """Retorna informações do ambiente para debug"""
        return {
            "api_key_configured": bool(cls.MISTRAL_API_KEY),
            "model": cls.MISTRAL_MODEL,
            "batch_threshold": cls.BATCH_THRESHOLD,
            "similarity_threshold": cls.SIMILARITY_THRESHOLD,
            "directories_exist": all([
                cls.INPUT_DIR.exists(),
                cls.OUTPUT_JSON.exists(),
                cls.DATA_DIR.exists()
            ])
        }

# Instância global
settings = Settings()
