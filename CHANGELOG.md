# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2025-08-22

### Adicionado
- ✨ Sistema OCR completo para placas NR-13
- 🤖 Integração com Mistral AI (Pixtral-12b-2409)
- 🔄 Modo híbrido inteligente (síncrono/batch)
- 🧠 Normalização avançada de campos com IA
- ✅ Validação automática NR-13
- 📊 Sistema de relatórios e estatísticas
- 🎯 Interface de linha de comando completa
- 📁 Arquitetura modular e extensível
- 🔧 Sistema de configuração flexível
- 📝 Logging detalhado
- 🎨 Interface amigável com emojis
- 💾 Persistência de dados e histórico
- 🔍 Sistema de validação robusto

### Características Técnicas
- **Modo Híbrido**: ≤5 imagens (síncrono), >5 imagens (batch com 50% desconto)
- **Normalização Inteligente**: 4 níveis de matching (exato, regex, fuzzy, inferência)
- **Campos NR-13**: Suporte completo aos campos obrigatórios
- **Formatos**: JPG, JPEG, PNG, BMP, TIFF, WEBP
- **Validação**: Completude automática e campos faltantes
- **Relatórios**: JSON estruturado com metadados
- **Batch Processing**: Processamento assíncrono para grandes volumes
- **Sistema de Aprendizado**: Mapeamentos automáticos de novos campos

### Módulos
- `config/`: Configurações centralizadas e mapeamentos
- `ocr/`: Núcleo do sistema (processor, normalizer, models)
- `services.py`: Integração externa (Mistral, arquivos, batch)
- `utils.py`: Utilitários e helpers
- `main.py`: Interface principal

### Melhorias de Performance
- ⚡ Processamento paralelo para múltiplas imagens
- 🎯 Cache de mapeamentos aprendidos
- 📊 Otimização de prompts para melhor precisão
- 🔄 Retry automático em caso de falhas
- 💾 Salvamento incremental de resultados

### Correções de Bugs
- 🐛 Fix: `best_score` agora é float ao invés de int
- 🐛 Fix: Validação de dados antes de salvar
- 🐛 Fix: Tratamento robusto de erros na API
- 🐛 Fix: Encoding UTF-8 para caracteres especiais
- 🐛 Fix: Validação de formatos de imagem
- 🐛 Fix: Normalização de campos com valores vazios
- 🐛 Fix: Timeout apropriado para jobs batch
- 🐛 Fix: Criação automática de diretórios

### Segurança
- 🔒 Validação rigorosa de entrada
- 🛡️ Sanitização de nomes de arquivos
- 🔐 Configuração segura de API keys
- 📋 Logs sem exposição de dados sensíveis

---

## Próximas Versões Planejadas

### [1.1.0] - Futuro
- 🌐 Interface web com Streamlit
- 📊 Dashboard de analytics
- 📤 Exportação para Excel/PDF
- 🔄 API REST para integração
- 📱 Interface mobile-friendly

### [1.2.0] - Futuro
- 🤖 Modelos de IA customizáveis
- 📚 Templates para diferentes tipos de placas
- 🔄 Sincronização com sistemas externos
- 📈 Analytics avançados
- 🌍 Suporte multilíngue

### [2.0.0] - Futuro
- 🏢 Versão enterprise
- ☁️ Deploy em nuvem
- 👥 Multi-usuário
- 🔄 Integração com ERPs
- 🤖 AutoML para otimização
