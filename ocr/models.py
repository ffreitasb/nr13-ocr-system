"""
Modelos de dados do sistema NR13 OCR
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class PlacaNR13:
    """Modelo de dados para placa NR-13"""

    # Identificação
    identificacao: Optional[str] = None
    tag: Optional[str] = None
    numero_serie: Optional[str] = None
    numero_ordem: Optional[str] = None

    # Fabricação
    fabricante: Optional[str] = None
    ano_fabricacao: Optional[str] = None
    tipo: Optional[str] = None
    modelo: Optional[str] = None

    # Pressões
    pressao_maxima_trabalho: Optional[str] = None
    pressao_teste_hidrostatico: Optional[str] = None
    pressao_operacao: Optional[str] = None

    # Capacidades e Dimensões
    capacidade_producao_vapor: Optional[str] = None
    area_superficie_aquecimento: Optional[str] = None
    volume: Optional[str] = None

    # Materiais
    material_casco: Optional[str] = None
    material_espelhos: Optional[str] = None
    tipo_combustivel: Optional[str] = None

    # Normas e Códigos
    codigo_projeto: Optional[str] = None
    categoria: Optional[str] = None
    norma_fabricacao: Optional[str] = None

    # Inspeção
    empresa_inspecao: Optional[str] = None
    data_ultima_inspecao: Optional[str] = None
    proxima_inspecao: Optional[str] = None

    # Campos adicionais
    outros_dados: Dict[str, Any] = field(default_factory=dict)

    # Metadados (não fazem parte da placa)
    _metadata: Dict[str, Any] = field(default_factory=dict)
    _raw_extraction: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_metadata: bool = True) -> Dict:
        """
        Converte para dicionário

        Args:
            include_metadata: Se deve incluir metadados

        Returns:
            Dicionário com os dados
        """
        data = asdict(self)

        # Remove campos None
        data = {k: v for k, v in data.items() if v is not None}

        # Remove metadados se solicitado
        if not include_metadata:
            data.pop('_metadata', None)
            data.pop('_raw_extraction', None)

        return data

    def validate_nr13(self) -> Dict[str, Any]:
        """
        Valida campos obrigatórios NR-13

        Returns:
            Dicionário com resultado da validação
        """
        from config.settings import settings

        required_fields = settings.REQUIRED_FIELDS
        found = [f for f in required_fields if getattr(self, f, None)]
        missing = [f for f in required_fields if not getattr(self, f, None)]

        return {
            'valid': len(missing) == 0,
            'completeness': (len(found) / len(required_fields) * 100) if required_fields else 0,
            'found': found,
            'missing': missing,
            'total_required': len(required_fields)
        }

    def get_summary(self) -> Dict[str, str]:
        """Retorna resumo dos campos principais"""
        summary = {}
        main_fields = ['identificacao', 'fabricante', 'categoria', 
                      'pressao_maxima_trabalho', 'ano_fabricacao']
        
        for field in main_fields:
            value = getattr(self, field, None)
            if value:
                summary[field] = str(value)
        
        return summary


@dataclass
class BatchJob:
    """Modelo para job de processamento batch"""

    job_id: str
    status: str = "created"
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    total_images: int = 0
    processed: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    id_mapping: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)

    def update_status(self, status: str):
        """
        Atualiza status do job

        Args:
            status: Novo status
        """
        self.status = status
        self.updated_at = datetime.now().isoformat()

    def add_error(self, error: str):
        """Adiciona erro ao job"""
        self.errors.append(error)
        self.updated_at = datetime.now().isoformat()


@dataclass
class ProcessingResult:
    """Resultado de processamento de uma imagem"""

    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    image_path: Optional[str] = None
    processing_time: Optional[float] = None
    mode: str = "sync"  # sync ou batch
    validation: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)

    def get_filename(self) -> str:
        """Retorna nome do arquivo da imagem"""
        if self.image_path:
            from pathlib import Path
            return Path(self.image_path).name
        return "unknown"


@dataclass
class ProcessingSummary:
    """Resumo de processamento de um lote"""

    total_images: int
    processed: int = 0
    success: int = 0
    errors: int = 0
    mode: str = "sync"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    processing_time: Optional[float] = None
    results: List[ProcessingResult] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        data = asdict(self)
        # Converte results para dict também
        data['results'] = [r.to_dict() for r in self.results]
        return data

    def add_result(self, result: ProcessingResult):
        """Adiciona resultado ao resumo"""
        self.results.append(result)
        self.processed += 1
        if result.success:
            self.success += 1
        else:
            self.errors += 1

    def get_success_rate(self) -> float:
        """Retorna taxa de sucesso"""
        if self.processed == 0:
            return 0.0
        return (self.success / self.processed) * 100

    def finish(self):
        """Finaliza o processamento"""
        self.end_time = datetime.now().isoformat()
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.processing_time = (end - start).total_seconds()
