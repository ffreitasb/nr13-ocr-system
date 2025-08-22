"""
Sistema de normalização de campos para placas NR-13
"""
import re
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher
from config.settings import settings


class FieldNormalizer:
    """Normalizador inteligente de campos"""

    def __init__(self):
        self.mappings = self._load_mappings()
        self.learned = self._load_learned()
        self.threshold = settings.SIMILARITY_THRESHOLD

    def _load_mappings(self) -> Dict:
        """Carrega mapeamentos do arquivo YAML"""
        mapping_file = settings.CONFIG_DIR / "field_mappings.yaml"
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Aviso: Não foi possível carregar mapeamentos: {e}")
            return {}

    def _load_learned(self) -> Dict:
        """Carrega mapeamentos aprendidos"""
        learned_file = settings.DATA_DIR / "learned_mappings.json"
        if learned_file.exists():
            try:
                with open(learned_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def normalize(self, raw_data: Dict) -> Dict:
        """
        Normaliza campos extraídos do OCR

        Args:
            raw_data: Dados brutos do OCR

        Returns:
            Dados normalizados com campos padronizados
        """
        normalized = {}
        unmatched = {}

        for raw_key, value in raw_data.items():
            # Pula metadados
            if raw_key.startswith('_'):
                normalized[raw_key] = value
                continue

            # Pula valores vazios
            if not value or (isinstance(value, str) and not value.strip()):
                continue

            # Tenta encontrar campo correspondente
            field = self._find_field(raw_key, value)

            if field:
                normalized_value = self._normalize_value(field, value)
                if normalized_value is not None:
                    normalized[field] = normalized_value
            else:
                # Limpa a chave antes de adicionar aos não mapeados
                clean_key = self._clean_field_name(raw_key)
                if clean_key and value:
                    unmatched[clean_key] = value

        # Adiciona campos não mapeados em outros_dados
        if unmatched:
            normalized['outros_dados'] = unmatched

        return normalized

    def _find_field(self, raw_key: str, value: Any) -> Optional[str]:
        """
        Encontra campo correspondente para uma chave bruta

        Args:
            raw_key: Chave original do OCR
            value: Valor do campo

        Returns:
            Nome do campo normalizado ou None
        """
        # 1. Match exato
        field = self._exact_match(raw_key)
        if field:
            return field

        # 2. Match com regex
        field = self._regex_match(raw_key)
        if field:
            return field

        # 3. Match por similaridade
        field = self._fuzzy_match(raw_key)
        if field:
            return field

        # 4. Inferência pelo conteúdo
        field = self._infer_by_content(raw_key, value)
        if field:
            return field

        # 5. Verifica aprendidos
        return self._check_learned(raw_key)

    def _clean_text(self, text: str) -> str:
        """Limpa texto para comparação"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove pontuação e normaliza espaços
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _clean_field_name(self, field_name: str) -> str:
        """Limpa nome do campo para usar como chave"""
        if not isinstance(field_name, str):
            field_name = str(field_name)
        
        # Remove caracteres especiais e normaliza
        clean = re.sub(r'[^\w\s]', '_', field_name.lower())
        clean = re.sub(r'\s+', '_', clean)
        clean = re.sub(r'_+', '_', clean)
        return clean.strip('_')

    def _exact_match(self, raw_key: str) -> Optional[str]:
        """Match exato com aliases"""
        clean_key = self._clean_text(raw_key)

        for field_name, config in self.mappings.items():
            if 'aliases' in config:
                for alias in config['aliases']:
                    if self._clean_text(alias) == clean_key:
                        return field_name
        return None

    def _regex_match(self, raw_key: str) -> Optional[str]:
        """Match usando regex patterns"""
        clean_key = self._clean_text(raw_key)

        for field_name, config in self.mappings.items():
            if 'regex' in config:
                for pattern in config['regex']:
                    try:
                        if re.search(pattern, clean_key, re.IGNORECASE):
                            return field_name
                    except re.error:
                        # Ignora padrões regex inválidos
                        continue
        return None

    def _fuzzy_match(self, raw_key: str) -> Optional[str]:
        """Match por similaridade de strings"""
        clean_key = self._clean_text(raw_key)
        best_match = None
        best_score = 0.0

        for field_name, config in self.mappings.items():
            if 'aliases' in config:
                for alias in config['aliases']:
                    try:
                        score = SequenceMatcher(None, clean_key,
                                              self._clean_text(alias)).ratio()
                        if score > best_score and score >= self.threshold:
                            best_score = score
                            best_match = field_name
                    except Exception:
                        # Ignora erros de comparação
                        continue

        return best_match

    def _infer_by_content(self, raw_key: str, value: Any) -> Optional[str]:
        """Infere o campo baseado no conteúdo"""
        if not value:
            return None

        value_str = str(value).lower().strip()
        raw_key_lower = raw_key.lower()

        # Detecta pressões por unidades
        pressure_units = ['kgf', 'bar', 'psi', 'kpa', 'mpa', 'kg/cm']
        if any(unit in value_str for unit in pressure_units):
            if any(word in raw_key_lower for word in ['test', 'hidro']):
                return 'pressao_teste_hidrostatico'
            elif any(word in raw_key_lower for word in ['oper']):
                return 'pressao_operacao'
            elif any(word in raw_key_lower for word in ['max', 'trab', 'pmta']):
                return 'pressao_maxima_trabalho'

        # Detecta anos (formato 19XX ou 20XX)
        if re.match(r'^(19|20)\d{2}$', value_str):
            return 'ano_fabricacao'

        # Detecta categorias NR-13
        if value_str.upper() in ['I', 'II', 'III', 'IV', 'V', 'A', 'B', 'C', 'D', 'E']:
            return 'categoria'

        # Detecta capacidade de vapor
        if any(unit in value_str for unit in ['kg/h', 't/h', 'ton/h']):
            return 'capacidade_producao_vapor'

        # Detecta área
        if any(unit in value_str for unit in ['m²', 'm2']):
            return 'area_superficie_aquecimento'

        # Detecta volume
        if any(unit in value_str for unit in ['l', 'm³', 'm3', 'litros']):
            return 'volume'

        return None

    def _check_learned(self, raw_key: str) -> Optional[str]:
        """Verifica mapeamentos aprendidos"""
        clean_key = self._clean_text(raw_key)

        for field_name, learned_keys in self.learned.items():
            if clean_key in [self._clean_text(k) for k in learned_keys]:
                return field_name

        return None

    def _normalize_value(self, field: str, value: Any) -> Any:
        """
        Normaliza o valor de um campo

        Args:
            field: Nome do campo
            value: Valor a normalizar

        Returns:
            Valor normalizado
        """
        if not value:
            return None

        value_str = str(value).strip()
        
        # Remove valores muito curtos ou inválidos
        if len(value_str) < 1:
            return None

        # Campos numéricos - limpa mas mantém formato
        if field in ['ano_fabricacao', 'numero_ordem', 'numero_serie']:
            # Remove caracteres não numéricos mas mantém hífens e barras
            cleaned = re.sub(r'[^\d\-\/]', '', value_str)
            return cleaned if cleaned else None

        # Pressões - padroniza formato decimal
        if 'pressao' in field:
            # Substitui vírgula por ponto e limpa
            normalized = value_str.replace(',', '.')
            return normalized

        # Categoria - sempre maiúscula
        if field == 'categoria':
            category = value_str.strip().upper()
            # Valida se é uma categoria válida
            valid_categories = ['I', 'II', 'III', 'IV', 'V', 'A', 'B', 'C', 'D', 'E']
            return category if category in valid_categories else None

        # Default - apenas limpa espaços
        return value_str

    def learn_mapping(self, raw_key: str, field: str):
        """
        Aprende novo mapeamento

        Args:
            raw_key: Chave original
            field: Campo correspondente
        """
        if not raw_key or not field:
            return
            
        if field not in self.learned:
            self.learned[field] = []

        clean_key = self._clean_text(raw_key)
        if clean_key not in [self._clean_text(k) for k in self.learned[field]]:
            self.learned[field].append(raw_key)
            self._save_learned()

    def _save_learned(self):
        """Salva mapeamentos aprendidos"""
        learned_file = settings.DATA_DIR / "learned_mappings.json"
        try:
            with open(learned_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar mapeamentos aprendidos: {e}")

    def get_mapping_stats(self) -> Dict:
        """Retorna estatísticas dos mapeamentos"""
        total_mappings = len(self.mappings)
        total_learned = sum(len(keys) for keys in self.learned.values())
        
        return {
            'total_predefined': total_mappings,
            'total_learned': total_learned,
            'threshold': self.threshold,
            'learned_fields': list(self.learned.keys())
        }
