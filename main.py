#!/usr/bin/env python3
"""
Sistema OCR para Placas NR-13
Entry point principal
"""
import sys
import json
import os
from pathlib import Path

# Adiciona diretório raiz ao path para imports
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Agora importa os módulos do projeto
try:
    from config.settings import settings
    from ocr.processor import OCRProcessor
    from ocr.models import PlacaNR13
    from services import BatchManager
    from utils import (
        get_logger, print_banner, print_summary, ask_confirmation,
        validate_nr13_result, format_time, get_system_info
    )
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("\n🔧 Soluções possíveis:")
    print("1. Verifique se está no diretório correto do projeto")
    print("2. Execute: pip install -r requirements.txt")
    print("3. Ative o ambiente virtual se estiver usando")
    print("4. Verifique se todos os arquivos .py estão presentes")
    print("5. Execute: python setup.py")
    print(f"6. Diretório atual: {Path.cwd()}")
    print(f"7. Diretório do projeto: {Path(__file__).parent.absolute()}")
    sys.exit(1)

logger = get_logger(__name__)


def print_menu():
    """Imprime menu principal"""
    print(f"\n📊 Modo Híbrido Inteligente:")
    print(f"   • 1-{settings.BATCH_THRESHOLD}: Processamento Síncrono")
    print(f"   • >{settings.BATCH_THRESHOLD}: Batch API (50% desconto)")
    print("\n" + "-"*60)
    print("\n1. Processar imagens (automático)")
    print("2. Processar imagem específica")
    print("3. Validar JSONs processados")
    print("4. Ver histórico de jobs batch")
    print("5. Ver relatórios")
    print("6. Configurações")
    print("7. Teste de conexão")
    print("8. Estatísticas")
    print("9. Sair")
    print("-"*60)


def check_project_structure():
    """Verifica se a estrutura do projeto está correta"""
    required_files = [
        'config/settings.py',
        'config/field_mappings.yaml',
        'ocr/processor.py',
        'ocr/models.py',
        'ocr/normalizer.py',
        'services.py',
        'utils.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Arquivos obrigatórios não encontrados:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print("\n🔧 Certifique-se de que todos os arquivos do projeto estão presentes.")
        print("💡 Execute: python setup.py")
        return False
    
    return True


def process_images(processor: OCRProcessor):
    """Processa imagens no diretório de entrada"""
    print("\n🔄 Processando imagens...")

    # Verifica se há imagens
    images = processor.files.list_images(settings.INPUT_DIR)
    if not images:
        print(f"\n⚠️ Nenhuma imagem encontrada em {settings.INPUT_DIR}")
        print(f"Coloque as imagens das placas na pasta '{settings.INPUT_DIR}' e tente novamente.")
        print(f"Formatos suportados: {', '.join(settings.SUPPORTED_FORMATS)}")
        return

    summary = processor.process()

    if 'error' in summary:
        print(f"\n❌ {summary.get('message', 'Erro no processamento')}")
    else:
        print_summary(summary)

        if summary.get('sucesso', 0) > 0:
            print(f"\n✅ Resultados salvos em: {settings.OUTPUT_JSON}")
            
            # Mostra alguns resultados
            show_recent_results()


def show_recent_results(limit: int = 3):
    """Mostra resultados recentes"""
    try:
        json_files = sorted(settings.OUTPUT_JSON.glob("*_ocr.json"), 
                           key=lambda x: x.stat().st_mtime, reverse=True)
        
        if json_files:
            print(f"\n📋 Últimos {min(limit, len(json_files))} resultados:")
            print("-" * 40)
            
            for json_file in json_files[:limit]:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"\n📄 {json_file.name}:")
                    
                    # Mostra campos principais
                    main_fields = ['identificacao', 'fabricante', 'categoria', 'pressao_maxima_trabalho']
                    for field in main_fields:
                        if field in data and data[field]:
                            print(f"  • {field}: {data[field]}")
                    
                    # Mostra validação se disponível
                    if '_metadata' in data and 'validacao' in data['_metadata']:
                        val = data['_metadata']['validacao']
                        status = "✅" if val.get('valid') else "⚠️"
                        print(f"  {status} Completude: {val.get('completeness', 0):.1f}%")
                        
                except Exception as e:
                    print(f"  ❌ Erro ao ler {json_file.name}: {e}")
    except Exception as e:
        print(f"❌ Erro ao listar resultados: {e}")


def process_single_image(processor: OCRProcessor):
    """Processa uma imagem específica"""
    path = input("\nCaminho da imagem: ").strip()

    if not path:
        print("❌ Caminho inválido")
        return

    if not Path(path).exists():
        print(f"❌ Arquivo não encontrado: {path}")
        return

    print(f"\n🔄 Processando: {path}")
    result = processor.process_single(path)

    if result.get('success'):
        print("\n✅ Processamento concluído!")

        data = result.get('data', {})

        # Mostra validação NR-13
        if '_metadata' in data and 'validacao' in data['_metadata']:
            val = data['_metadata']['validacao']
            print(f"\n📊 Validação NR-13:")
            print(f"   • Completude: {val['completeness']:.1f}%")
            print(f"   • Campos obrigatórios: {len(val['found'])}/{val['total_required']}")

            if val['missing']:
                print(f"   • Faltando: {', '.join(val['missing'])}")

        # Mostra campos principais
        print("\n📋 Campos extraídos:")
        campos_mostrar = [
            'identificacao', 'tag', 'fabricante', 'categoria',
            'pressao_maxima_trabalho', 'ano_fabricacao'
        ]

        for campo in campos_mostrar:
            if campo in data and data[campo]:
                print(f"   • {campo}: {data[campo]}")

        # Mostra campos adicionais se existirem
        if 'outros_dados' in data and data['outros_dados']:
            print(f"\n📌 Campos adicionais: {len(data['outros_dados'])}")
            for key, value in list(data['outros_dados'].items())[:5]:
                print(f"   • {key}: {value}")
                
        # Mostra tempo de processamento
        if 'processing_time' in result:
            print(f"\n⏱️ Tempo: {format_time(result['processing_time'])}")
            
    else:
        print(f"\n❌ Erro: {result.get('error', 'Desconhecido')}")


def validate_jsons():
    """Valida JSONs já processados"""
    try:
        json_files = list(settings.OUTPUT_JSON.glob("*_ocr.json"))

        if not json_files:
            print(f"\n⚠️ Nenhum JSON encontrado em {settings.OUTPUT_JSON}")
            return

        print(f"\n📊 Validando {len(json_files)} arquivos...")
        print("-"*60)

        stats = {'validos': 0, 'incompletos': 0, 'erros': 0}
        detailed_results = []

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if '_metadata' in data and 'validacao' in data['_metadata']:
                    val = data['_metadata']['validacao']
                    
                    result = {
                        'file': json_file.name,
                        'valid': val['valid'],
                        'completeness': val['completeness'],
                        'missing': val.get('missing', [])
                    }
                    
                    if val['valid']:
                        print(f"✅ {json_file.name}: {val['completeness']:.1f}% completo")
                        stats['validos'] += 1
                    else:
                        missing = ', '.join(val['missing'])
                        print(f"⚠️  {json_file.name}: Faltam: {missing}")
                        stats['incompletos'] += 1
                        
                    detailed_results.append(result)
                else:
                    # Tenta validar manualmente
                    val = validate_nr13_result(data)
                    
                    result = {
                        'file': json_file.name,
                        'valid': val['valid'],
                        'completeness': val['completeness'],
                        'missing': val.get('missing', [])
                    }
                    
                    if val['valid']:
                        print(f"✅ {json_file.name}: Válido")
                        stats['validos'] += 1
                    else:
                        print(f"⚠️  {json_file.name}: Incompleto")
                        stats['incompletos'] += 1
                        
                    detailed_results.append(result)

            except Exception as e:
                print(f"❌ {json_file.name}: Erro - {e}")
                stats['erros'] += 1

        print("-"*60)
        print(f"📈 Resumo: {stats['validos']} válidos, {stats['incompletos']} incompletos, {stats['erros']} erros")
        
        # Mostra estatísticas mais detalhadas
        if detailed_results:
            total_valid = len([r for r in detailed_results if r['valid']])
            avg_completeness = sum(r['completeness'] for r in detailed_results) / len(detailed_results)
            print(f"📊 Taxa de sucesso: {total_valid/len(detailed_results)*100:.1f}%")
            print(f"📊 Completude média: {avg_completeness:.1f}%")
    except Exception as e:
        print(f"❌ Erro na validação: {e}")


def show_batch_history():
    """Mostra histórico de jobs batch"""
    try:
        batch_manager = BatchManager()
        jobs = batch_manager.list_jobs(limit=10)

        if not jobs:
            print("\n⚠️ Nenhum job batch encontrado")
            return

        print(f"\n📦 Histórico de Jobs Batch ({len(jobs)} jobs)")
        print("-"*60)

        # Ordena por data de criação (mais recente primeiro)
        sorted_jobs = sorted(jobs.items(),
                            key=lambda x: x[1].get('created_at', ''),
                            reverse=True)

        for job_id, info in sorted_jobs:
            print(f"\n🔹 Job: {job_id[:12]}...")
            print(f"   Status: {info.get('status', 'desconhecido')}")
            print(f"   Criado: {info.get('created_at', 'N/A')}")
            print(f"   Imagens: {info.get('total_images', 'N/A')}")

            if 'results_count' in info:
                print(f"   Resultados: {info['results_count']}")
                
            if info.get('status') == 'completed':
                print(f"   ✅ Concluído")
            elif info.get('status') == 'failed':
                print(f"   ❌ Falhou")
            elif info.get('status') in ['created', 'running']:
                print(f"   ⏳ Em andamento")
    except Exception as e:
        print(f"❌ Erro ao carregar histórico: {e}")


def show_reports():
    """Mostra relatórios disponíveis"""
    try:
        reports = list(settings.OUTPUT_REPORTS.glob("resumo_*.json"))

        if not reports:
            print("\n⚠️ Nenhum relatório encontrado")
            return

        print(f"\n📊 Últimos Relatórios")
        print("-"*60)

        # Ordena por data (mais recente primeiro)
        reports_sorted = sorted(reports, key=lambda x: x.stat().st_mtime, reverse=True)

        for report in reports_sorted[:10]:
            try:
                with open(report, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                timestamp = data.get('timestamp', 'N/A')
                total = data.get('total_imagens', 0)
                sucesso = data.get('sucesso', 0)
                taxa = data.get('taxa_sucesso', 0)
                modo = data.get('modo', 'N/A')
                tempo = data.get('tempo_total')

                print(f"\n📄 {report.name}")
                print(f"   Data: {timestamp[:19] if timestamp != 'N/A' else 'N/A'}")
                print(f"   Total: {total} | Sucesso: {sucesso} | Taxa: {taxa:.1f}%")
                print(f"   Modo: {modo.upper() if modo != 'N/A' else 'N/A'}")
                
                if tempo:
                    print(f"   Tempo: {format_time(tempo)}")

            except Exception as e:
                print(f"\n📄 {report.name} (erro ao ler: {e})")
    except Exception as e:
        print(f"❌ Erro ao carregar relatórios: {e}")


def show_settings():
    """Mostra configurações atuais"""
    print("\n⚙️  CONFIGURAÇÕES ATUAIS")
    print("-"*60)

    print("\n🔧 Processamento:")
    print(f"   • Modelo: {settings.MISTRAL_MODEL}")
    print(f"   • Threshold Batch: {settings.BATCH_THRESHOLD} imagens")
    print(f"   • Tamanho Máx Batch: {settings.MAX_BATCH_SIZE}")
    print(f"   • Timeout: {format_time(settings.MAX_WAIT_TIME)}")
    print(f"   • Similaridade: {settings.SIMILARITY_THRESHOLD * 100:.0f}%")
    print(f"   • Temperature: {settings.TEMPERATURE}")
    print(f"   • Max Tokens: {settings.MAX_TOKENS}")

    print("\n📁 Diretórios:")
    print(f"   • Input: {settings.INPUT_DIR}")
    print(f"   • Output JSON: {settings.OUTPUT_JSON}")
    print(f"   • Output Batch: {settings.OUTPUT_BATCH}")
    print(f"   • Logs: {settings.LOGS_DIR}")

    print("\n📄 Formatos suportados:")
    print(f"   {', '.join(settings.SUPPORTED_FORMATS)}")

    print("\n✅ Campos obrigatórios NR-13:")
    for field in settings.REQUIRED_FIELDS:
        print(f"   • {field}")
        
    # Mostra info do ambiente
    try:
        env_info = settings.get_env_info()
        print("\n🌍 Ambiente:")
        print(f"   • API Key configurada: {'✅' if env_info['api_key_configured'] else '❌'}")
        print(f"   • Diretórios existem: {'✅' if env_info['directories_exist'] else '❌'}")
    except Exception as e:
        print(f"\n❌ Erro ao verificar ambiente: {e}")


def test_connection(processor: OCRProcessor):
    """Testa conexão com a API"""
    print("\n🔍 Testando conexão com Mistral AI...")
    
    try:
        if processor.test_api_connection():
            print("✅ Conexão com API estabelecida com sucesso!")
            print(f"   • Modelo: {settings.MISTRAL_MODEL}")
            print(f"   • Endpoint: https://api.mistral.ai")
        else:
            print("❌ Falha na conexão com a API")
            print("   • Verifique sua MISTRAL_API_KEY")
            print("   • Verifique sua conexão com internet")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")


def show_statistics(processor: OCRProcessor):
    """Mostra estatísticas do sistema"""
    print("\n📈 ESTATÍSTICAS DO SISTEMA")
    print("-"*60)
    
    try:
        stats = processor.get_stats()
        
        print("\n🔧 Processador:")
        print(f"   • Imagens processadas: {stats['processed_count']}")
        print(f"   • Erros: {stats['error_count']}")
        print(f"   • Taxa de sucesso: {stats['success_rate']:.1f}%")
        
        print("\n🗂️  Normalizador:")
        norm_stats = stats['normalizer_stats']
        print(f"   • Mapeamentos predefinidos: {norm_stats['total_predefined']}")
        print(f"   • Mapeamentos aprendidos: {norm_stats['total_learned']}")
        print(f"   • Threshold similaridade: {norm_stats['threshold']*100:.0f}%")
        
        if norm_stats['learned_fields']:
            print(f"   • Campos aprendidos: {', '.join(norm_stats['learned_fields'][:5])}")
        
        print("\n📦 Batch Manager:")
        batch_stats = stats['batch_stats']
        print(f"   • Total jobs: {batch_stats['total_jobs']}")
        
        if batch_stats['status_breakdown']:
            print("   • Status breakdown:")
            for status, count in batch_stats['status_breakdown'].items():
                print(f"     - {status}: {count}")
        
        # Estatísticas de arquivos
        print("\n📁 Arquivos:")
        json_files = list(settings.OUTPUT_JSON.glob("*_ocr.json"))
        batch_files = list(settings.OUTPUT_BATCH.glob("*.jsonl"))
        reports = list(settings.OUTPUT_REPORTS.glob("*.json"))
        
        print(f"   • JSONs processados: {len(json_files)}")
        print(f"   • Arquivos batch: {len(batch_files)}")
        print(f"   • Relatórios: {len(reports)}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")


def main():
    """Função principal"""
    try:
        # Verificações iniciais
        print("🔍 Verificando estrutura do projeto...")
        if not check_project_structure():
            print("\n💡 Dica: Execute 'python setup.py' para configurar automaticamente")
            sys.exit(1)
        
        print("✅ Estrutura do projeto OK")
        
        # Valida configurações
        print("🔍 Validando configurações...")
        settings.validate()
        print("✅ Configurações OK")
        
        logger.info("Sistema NR13 OCR iniciado")

        # Inicializa processador
        print("🔍 Inicializando processador OCR...")
        processor = OCRProcessor()
        print("✅ Processador inicializado")

        while True:
            print_banner()
            print_menu()

            choice = input("\nEscolha uma opção (1-9): ").strip()

            if choice == "1":
                process_images(processor)
                input("\nPressione Enter para continuar...")

            elif choice == "2":
                process_single_image(processor)
                input("\nPressione Enter para continuar...")

            elif choice == "3":
                validate_jsons()
                input("\nPressione Enter para continuar...")

            elif choice == "4":
                show_batch_history()
                input("\nPressione Enter para continuar...")

            elif choice == "5":
                show_reports()
                input("\nPressione Enter para continuar...")

            elif choice == "6":
                show_settings()
                input("\nPressione Enter para continuar...")
                
            elif choice == "7":
                test_connection(processor)
                input("\nPressione Enter para continuar...")
                
            elif choice == "8":
                show_statistics(processor)
                input("\nPressione Enter para continuar...")

            elif choice == "9":
                if ask_confirmation("Deseja realmente sair?"):
                    print("\n👋 Encerrando sistema...")
                    break

            else:
                print("\n⚠️ Opção inválida!")
                input("\nPressione Enter para continuar...")

    except KeyboardInterrupt:
        print("\n\n👋 Sistema interrompido pelo usuário")
        logger.info("Sistema interrompido pelo usuário")

    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
        print(f"\n❌ Erro de configuração: {e}")
        print("\n🔧 Soluções:")
        print("1. Verifique o arquivo .env")
        print("2. Configure sua MISTRAL_API_KEY")
        print("3. Execute: cp .env.example .env")
        print("4. Execute: python setup.py")
        
        # Mostra informações de debug
        print("\n🔍 Informações de debug:")
        try:
            sys_info = get_system_info()
            print(f"   • Python: {sys_info['python_version'].split()[0]}")
            print(f"   • Diretório: {sys_info['working_directory']}")
            print(f"   • Projeto: {project_root}")
        except Exception:
            print(f"   • Diretório do projeto: {project_root}")
            print(f"   • Python: {sys.version.split()[0]}")
            
        sys.exit(1)

    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\n❌ Erro fatal: {e}")
        print("\n🔧 Soluções:")
        print("1. Verifique o arquivo de log para mais detalhes")
        print("2. Reinstale as dependências: pip install -r requirements.txt")
        print("3. Verifique se todos os arquivos estão presentes")
        print("4. Execute: python setup.py")
        print(f"5. Verifique se está no diretório correto: {project_root}")
        sys.exit(1)


if __name__ == "__main__":
    main()
