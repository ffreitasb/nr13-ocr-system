# Guia de Instalação - Sistema OCR NR-13

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+, etc.)

### Software
- **Python 3.8+** (recomendado: Python 3.9 ou 3.10)
- **pip** (gerenciador de pacotes Python)
- **git** (para clonagem do repositório)

### API
- **Mistral AI API Key** - Obtenha em [console.mistral.ai](https://console.mistral.ai)

## 🚀 Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/ffreitasb/nr13-ocr-system.git
cd nr13-ocr-system
```

### 2. Crie Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env
# Windows: notepad .env
# macOS/Linux: nano .env
```

Adicione sua API key:
```env
MISTRAL_API_KEY=sua_chave_aqui
```

### 5. Execute o Sistema
```bash
python main.py
```

## 🔧 Instalação Detalhada

### Verificando Python
```bash
# Verifique a versão do Python
python --version
# ou
python3 --version

# Deve ser 3.8 ou superior
```

### Instalando Python (se necessário)

#### Windows
1. Baixe de [python.org](https://python.org/downloads/)
2. Execute o instalador
3. ✅ Marque "Add Python to PATH"
4. ✅ Marque "Install pip"

#### macOS
```bash
# Usando Homebrew (recomendado)
brew install python

# Ou baixe de python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install python3 python3-pip
# ou
sudo dnf install python3 python3-pip
```

### Obtendo API Key da Mistral

1. Acesse [console.mistral.ai](https://console.mistral.ai)
2. Faça login ou crie uma conta
3. Vá para "API Keys"
4. Clique em "Create API Key"
5. Copie a chave gerada

⚠️ **Importante**: Mantenha sua API key segura e nunca a compartilhe!

## 📁 Estrutura de Diretórios

Após a instalação, sua estrutura será:

```
nr13-ocr-system/
├── config/           # Configurações
├── ocr/             # Módulos OCR
├── data/            # Dados aprendidos
├── input/           # 📤 Coloque suas imagens aqui
├── output/          # 📥 Resultados aparecem aqui
│   ├── json/       # JSONs extraídos
│   ├── batch/      # Arquivos batch
│   └── reports/    # Relatórios
├── logs/            # Logs do sistema
├── main.py          # 🚀 Execute este arquivo
└── .env            # 🔑 Sua API key vai aqui
```

## ⚙️ Configuração Avançada

### Arquivo .env Completo
```env
# API Configuration
MISTRAL_API_KEY=sua_chave_aqui
MISTRAL_MODEL=pixtral-12b-2409

# Processing
BATCH_THRESHOLD=5
MAX_BATCH_SIZE=500
BATCH_CHECK_INTERVAL=30
MAX_WAIT_TIME=3600

# System
LOG_LEVEL=INFO
SIMILARITY_THRESHOLD=0.85
TEMPERATURE=0.1
MAX_TOKENS=2000
```

### Parâmetros Explicados

| Parâmetro | Descrição | Valor Padrão |
|-----------|-----------|-------------|
| `BATCH_THRESHOLD` | Limite para usar batch API | 5 |
| `SIMILARITY_THRESHOLD` | Threshold para matching fuzzy | 0.85 |
| `TEMPERATURE` | Criatividade da IA (0-1) | 0.1 |
| `MAX_TOKENS` | Tokens máximos por resposta | 2000 |
| `LOG_LEVEL` | Nível de log (DEBUG/INFO/WARNING/ERROR) | INFO |

## 🧪 Teste da Instalação

### 1. Teste Básico
```bash
python main.py
```

Deve aparecer o menu principal.

### 2. Teste de Conexão
No menu, escolha opção "7. Teste de conexão".

### 3. Teste com Imagem
1. Coloque uma imagem de placa em `input/`
2. Execute opção "1. Processar imagens"
3. Verifique resultado em `output/json/`

## 🐛 Solução de Problemas

### Erro: "MISTRAL_API_KEY não configurada"
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Verifique o conteúdo
cat .env

# Certifique-se que a chave está correta
```

### Erro: "ModuleNotFoundError"
```bash
# Verifique se o ambiente virtual está ativo
which python

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "Permission denied"
```bash
# Linux/macOS
chmod +x main.py

# Ou execute com python
python main.py
```

### Problema: "Slow API responses"
- Verifique sua conexão com internet
- Tente reduzir `MAX_TOKENS`
- Aumente `BATCH_CHECK_INTERVAL`

### Problema: "Low accuracy"
- Verifique qualidade das imagens
- Ajuste `TEMPERATURE` (menor = mais conservador)
- Revise os mapeamentos em `config/field_mappings.yaml`

## 🔄 Atualizações

### Atualizar o Sistema
```bash
# Faça backup dos seus dados
cp -r data/ data_backup/
cp -r output/ output_backup/

# Atualize o código
git pull origin main

# Atualize dependências
pip install -r requirements.txt --upgrade
```

### Verificar Versão
```bash
# No menu principal, escolha "8. Estatísticas"
# Ou verifique o arquivo CHANGELOG.md
cat CHANGELOG.md | head -20
```

## 🆘 Suporte

Se ainda tiver problemas:

1. 📖 Consulte a [documentação completa](README.md)
2. 🐛 Abra uma [issue no GitHub](https://github.com/ffreitasb/nr13-ocr-system/issues)
3. 📧 Entre em contato com suporte

## 🎯 Próximos Passos

Após a instalação:

1. 📚 Leia o [README.md](README.md) para entender o funcionamento
2. 🖼️ Coloque algumas imagens de teste em `input/`
3. 🚀 Execute o sistema e explore as funcionalidades
4. ⚙️ Ajuste as configurações conforme necessário
5. 📊 Analise os relatórios gerados

---

**✅ Instalação concluída com sucesso!**
Seu sistema OCR NR-13 está pronto para uso.
