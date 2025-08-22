# Sistema OCR NR-13

Sistema avançado para extração automática de dados de placas de identificação NR-13 usando Mistral AI com modo híbrido inteligente.

## 🚀 Características Principais

- **Modo Híbrido Inteligente**: Processamento síncrono para poucas imagens, Batch API para volumes maiores (50% desconto)
- **Normalização Avançada**: Sistema inteligente de mapeamento de campos com aliases, regex e fuzzy matching
- **Validação NR-13**: Verificação automática de campos obrigatórios conforme norma
- **Sistema de Aprendizado**: Aprende novos mapeamentos automaticamente
- **Arquitetura Modular**: Código organizado em módulos reutilizáveis

## 📋 Requisitos

- Python 3.8+
- Mistral AI API Key
- Dependências listadas em `requirements.txt`

## 🛠️ Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/ffreitasb/nr13-ocr-system.git
cd nr13-ocr-system
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure a API Key:**
```bash
cp .env.example .env
# Edite o arquivo .env e adicione sua MISTRAL_API_KEY
```

## 🔧 Uso

### Processamento Automático
```bash
python main.py
```

### Menu Interativo
O sistema oferece um menu com as seguintes opções:
1. Processar imagens (automático)
2. Processar imagem específica
3. Validar JSONs processados
4. Ver histórico de jobs batch
5. Ver relatórios
6. Configurações
7. Sair

## 📁 Estrutura do Projeto

```
nr13_ocr_system/
├── config/              # Configurações
│   ├── settings.py      # Configurações centralizadas
│   └── field_mappings.yaml  # Mapeamentos de campos
├── ocr/                 # Núcleo do sistema OCR
│   ├── processor.py     # Processador principal
│   ├── normalizer.py    # Normalização de campos
│   └── models.py        # Modelos de dados
├── services.py          # Serviços externos (Mistral, arquivos, batch)
├── utils.py             # Utilitários e helpers
├── main.py              # Ponto de entrada
├── input/               # Imagens para processar
├── output/              # Resultados
│   ├── json/           # JSONs extraídos
│   ├── batch/          # Arquivos de batch
│   └── reports/        # Relatórios
├── logs/                # Logs do sistema
└── data/                # Dados aprendidos e cache
```

## ⚙️ Configurações

Edite o arquivo `.env` para personalizar:

- `MISTRAL_API_KEY`: Sua chave da API Mistral
- `BATCH_THRESHOLD`: Limite para usar processamento batch (padrão: 5)
- `LOG_LEVEL`: Nível de log (DEBUG, INFO, WARNING, ERROR)
- `SIMILARITY_THRESHOLD`: Threshold para matching fuzzy (padrão: 0.85)

## 📊 Como Funciona

### Modo Híbrido Inteligente

- **≤5 imagens**: Processamento síncrono rápido
- **>5 imagens**: Batch API com 50% de desconto

### Normalização de Campos

O sistema identifica campos através de:
1. **Match exato** com aliases conhecidos
2. **Regex patterns** para variações comuns
3. **Fuzzy matching** por similaridade de texto
4. **Inferência por conteúdo** (ex: detecta pressões por unidades)
5. **Aprendizado** de novos mapeamentos

### Campos NR-13 Suportados

- Identificação e TAG
- Fabricante e dados de fabricação
- Pressões (trabalho, teste, operação)
- Capacidades e dimensões
- Materiais e códigos de projeto
- Empresa de inspeção

## 🎯 Validação NR-13

Campos obrigatórios verificados:
- `identificacao`
- `fabricante`
- `categoria`
- `pressao_maxima_trabalho`
- `numero_ordem`

## 📝 Formato de Saída

```json
{
  "identificacao": "CV-001",
  "fabricante": "Empresa ABC",
  "categoria": "I",
  "pressao_maxima_trabalho": "14 kgf/cm²",
  "numero_ordem": "12345",
  "outros_dados": {
    "campo_adicional": "valor"
  },
  "_metadata": {
    "arquivo": "placa001.jpg",
    "processado_em": "2025-08-22T15:30:00",
    "validacao": {
      "valid": true,
      "completeness": 100.0
    }
  }
}
```

## 🐛 Solução de Problemas

### Erro de API Key
```
❌ Erro: MISTRAL_API_KEY não encontrada no arquivo .env
```
**Solução**: Configure sua API key no arquivo `.env`

### Nenhuma imagem encontrada
```
⚠️ Nenhuma imagem encontrada em ./input
```
**Solução**: Coloque as imagens na pasta `input/`

### Problemas de reconhecimento
- Verifique a qualidade da imagem
- Certifique-se que o texto está legível
- Use imagens com boa resolução

## 🚀 Próximas Features

- [ ] Interface web com Streamlit
- [ ] Exportação para Excel/PDF
- [ ] API REST para integração
- [ ] Sistema de templates customizáveis
- [ ] Dashboard de analytics

## 📝 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato.
