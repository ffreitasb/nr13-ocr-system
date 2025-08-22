# Guia de Uso - Sistema OCR NR-13

## 🚀 Início Rápido

### 1. Preparação
```bash
# 1. Coloque suas imagens na pasta input/
cp suas_placas/*.jpg input/

# 2. Execute o sistema
python main.py

# 3. Escolha opção 1 (Processar imagens)
```

### 2. Resultado
- ✅ JSONs extraídos em `output/json/`
- 📊 Relatório em `output/reports/`
- 📝 Logs em `logs/`

## 📋 Menu Principal

### 1. 🔄 Processar imagens (automático)
- **Função**: Processa todas as imagens em `input/`
- **Modo**: Decide automaticamente entre síncrono/batch
- **Saída**: JSONs individuais + relatório consolidado

**Como usar**:
1. Coloque imagens em `input/`
2. Escolha opção 1
3. Aguarde processamento
4. Verifique resultados em `output/`

### 2. 🎯 Processar imagem específica
- **Função**: Processa uma única imagem
- **Modo**: Sempre síncrono
- **Uso**: Testes ou imagens individuais

**Como usar**:
1. Escolha opção 2
2. Digite caminho da imagem
3. Visualize resultado imediatamente

### 3. ✅ Validar JSONs processados
- **Função**: Verifica conformidade NR-13
- **Analisa**: Campos obrigatórios e completude
- **Relatório**: Estatísticas de validação

### 4. 📦 Ver histórico de jobs batch
- **Função**: Lista jobs batch anteriores
- **Info**: Status, datas, resultados
- **Útil**: Monitoramento de processos longos

### 5. 📊 Ver relatórios
- **Função**: Lista relatórios de processamento
- **Dados**: Estatísticas, tempo, taxa de sucesso
- **Histórico**: Últimos 10 processamentos

### 6. ⚙️ Configurações
- **Função**: Mostra configurações atuais
- **Info**: Modelos, diretórios, parâmetros
- **Status**: Validação de ambiente

### 7. 🔍 Teste de conexão
- **Função**: Verifica conectividade com API
- **Útil**: Diagnóstico de problemas
- **Resultado**: Status da conexão

### 8. 📈 Estatísticas
- **Função**: Métricas detalhadas do sistema
- **Dados**: Performance, mapeamentos, arquivos
- **Análise**: Eficiência do processamento

### 9. 🚪 Sair
- **Função**: Encerra o sistema
- **Confirmação**: Solicita confirmação

## 🧠 Modo Híbrido Inteligente

### Decisão Automática

#### ⚡ Modo Síncrono (≤5 imagens)
- **Vantagens**: 
  - Resultado imediato
  - Feedback em tempo real
  - Menor latência
- **Ideal para**: 
  - Testes
  - Poucos arquivos
  - Processamento rápido

#### 📦 Modo Batch (>5 imagens)
- **Vantagens**:
  - 50% de desconto!
  - Processamento paralelo
  - Otimizado para volume
- **Ideal para**:
  - Grandes lotes
  - Processamento noturno
  - Economia de custos

### Monitoramento Batch
```
📦 Processando Batch 1/1 (25 imagens)
============================================================
📤 Fazendo upload do arquivo batch...
🚀 Criando job batch...
✅ Job criado: batch_abc123
⏳ Aguardando processamento...
   Status: running | Tempo: 2m 30s
   Status: completed | Tempo: 5m 15s
✅ Batch concluído! Baixando resultados...
```

## 📊 Normalização de Campos

### Processo de Normalização

1. **Match Exato** 🎯
   ```
   "Fabricante" → fabricante
   "Manufacturer" → fabricante
   ```

2. **Match Regex** 🔍
   ```
   "PMTA" → pressao_maxima_trabalho
   "Press. Max. Trab." → pressao_maxima_trabalho
   ```

3. **Match Fuzzy** 🧠
   ```
   "Fabricado por" → fabricante (similaridade 89%)
   "Ano Fabr." → ano_fabricacao (similaridade 92%)
   ```

4. **Inferência por Conteúdo** 🤖
   ```
   "2020" → ano_fabricacao (detecta formato de ano)
   "14 kgf/cm²" → pressao_maxima_trabalho (detecta unidade)
   "I" → categoria (detecta categoria NR-13)
   ```

### Exemplo de Transformação

**Entrada bruta**:
```json
{
  "Manufacturer": "ACME Corp",
  "Serial No.": "ABC123",
  "PMTA": "14,5 kgf/cm²",
  "Ano": "2020",
  "Cat.": "I"
}
```

**Saída normalizada**:
```json
{
  "fabricante": "ACME Corp",
  "numero_serie": "ABC123",
  "pressao_maxima_trabalho": "14.5 kgf/cm²",
  "ano_fabricacao": "2020",
  "categoria": "I"
}
```

## ✅ Validação NR-13

### Campos Obrigatórios
- ✅ `identificacao`
- ✅ `fabricante`
- ✅ `categoria`
- ✅ `pressao_maxima_trabalho`
- ✅ `numero_ordem`

### Métricas de Validação
```json
"validacao": {
  "valid": true,
  "completeness": 100.0,
  "found": ["identificacao", "fabricante", "categoria", "pressao_maxima_trabalho", "numero_ordem"],
  "missing": [],
  "total_required": 5
}
```

### Interpretação
- **valid**: `true` se todos campos obrigatórios presentes
- **completeness**: Percentual de campos obrigatórios encontrados
- **found**: Lista de campos obrigatórios encontrados
- **missing**: Lista de campos obrigatórios faltantes

## 📁 Estrutura de Arquivos

### Entrada (input/)
```
input/
├── placa001.jpg
├── placa002.png
└── placa003.tiff
```

### Saída (output/)
```
output/
├── json/
│   ├── placa001_ocr.json    # Dados extraídos
│   ├── placa002_ocr.json
│   └── placa003_ocr.json
├── batch/
│   ├── batch_20250822_143022.jsonl  # Arquivo batch
│   └── results_job123.jsonl         # Resultados batch
└── reports/
    └── resumo_20250822_143500.json  # Relatório consolidado
```

### Logs (logs/)
```
logs/
├── ocr_20250822.log    # Log do dia
├── ocr_20250821.log
└── ocr_20250820.log
```

### Dados (data/)
```
data/
├── learned_mappings.json   # Mapeamentos aprendidos
└── batch_jobs.json        # Histórico de jobs
```

## 📄 Formato de Saída

### JSON Individual
```json
{
  "identificacao": "CV-001",
  "fabricante": "ACME Corporation",
  "categoria": "I",
  "pressao_maxima_trabalho": "14 kgf/cm²",
  "numero_ordem": "12345",
  "ano_fabricacao": "2020",
  "tipo_combustivel": "Gás Natural",
  "outros_dados": {
    "campo_adicional": "valor"
  },
  "_metadata": {
    "arquivo": "placa001.jpg",
    "processado_em": "2025-08-22T14:30:00",
    "modo": "sync",
    "tempo_processamento": 2.5,
    "validacao": {
      "valid": true,
      "completeness": 100.0
    }
  }
}
```

### Relatório Consolidado
```json
{
  "timestamp": "2025-08-22T14:35:00",
  "total_imagens": 10,
  "sucesso": 9,
  "erros": 1,
  "taxa_sucesso": 90.0,
  "modo": "sync",
  "tempo_total": 25.3,
  "start_time": "2025-08-22T14:30:00",
  "end_time": "2025-08-22T14:35:00"
}
```

## 🎯 Melhores Práticas

### Preparação de Imagens

#### ✅ Imagens Ideais
- **Resolução**: 1080p ou superior
- **Formato**: JPG, PNG (recomendado)
- **Iluminação**: Uniforme, sem sombras
- **Foco**: Texto nítido e legível
- **Ângulo**: Frontal, sem distorção

#### ❌ Evitar
- Imagens borradas ou tremidas
- Iluminação muito baixa ou alta
- Reflexos na placa
- Ângulos muito inclinados
- Resolução muito baixa (<720p)

### Organização

#### Nomenclatura
```
input/
├── linha1_placa001.jpg
├── linha1_placa002.jpg
├── linha2_placa001.jpg
└── projeto_especial_placa001.jpg
```

#### Backup
```bash
# Antes de processar grandes lotes
cp -r input/ backup_input_$(date +%Y%m%d)/
```

### Processamento Eficiente

#### Para Poucos Arquivos (1-5)
- Use **Modo Síncrono**
- Monitore resultados em tempo real
- Ajuste configurações se necessário

#### Para Muitos Arquivos (>5)
- Use **Modo Batch**
- Processe fora do horário de pico
- Monitore jobs através do menu

#### Para Volumes Grandes (>100)
- Divida em lotes menores
- Processe durante a madrugada
- Use scripts automatizados

## 🔧 Solução de Problemas

### Baixa Precisão

#### Sintomas
- Campos importantes não reconhecidos
- Valores incorretos extraídos
- Muitos campos em "outros_dados"

#### Soluções
1. **Melhore a qualidade da imagem**
2. **Ajuste configurações**:
   ```env
   TEMPERATURE=0.05  # Mais conservador
   SIMILARITY_THRESHOLD=0.80  # Menos restritivo
   ```
3. **Adicione mapeamentos customizados**
4. **Use o sistema de aprendizado**

### Processamento Lento

#### Sintomas
- Tempo excessivo por imagem
- Timeouts frequentes
- API lenta

#### Soluções
1. **Use modo batch para volumes grandes**
2. **Reduza MAX_TOKENS**:
   ```env
   MAX_TOKENS=1500
   ```
3. **Aumente intervalos**:
   ```env
   BATCH_CHECK_INTERVAL=60
   ```

### Erros de Conexão

#### Sintomas
- "Connection timeout"
- "API key invalid"
- "Rate limit exceeded"

#### Soluções
1. **Verifique API key**
2. **Teste conexão** (opção 7)
3. **Aguarde se hit rate limit**
4. **Use modo batch para economia**

## 📈 Otimização

### Performance

#### CPU
- Processe em lotes
- Use modo batch para >5 imagens
- Monitore uso de memória

#### API
- Aproveite desconto batch (50%)
- Evite horários de pico
- Use cache de mapeamentos

#### Armazenamento
- Limpe logs antigos regularmente
- Archive resultados processados
- Monitore espaço em disco

### Precisão

#### Prompt Engineering
- O sistema já usa prompts otimizados
- Ajuste TEMPERATURE conforme necessário
- Monitore taxas de sucesso

#### Mapeamentos
- Sistema aprende automaticamente
- Adicione aliases manuais se necessário
- Valide mapeamentos aprendidos

## 🎓 Casos de Uso

### 1. Inspeção Individual
```bash
# Coloque uma imagem em input/
cp nova_placa.jpg input/

# Execute processamento
python main.py
# Escolha opção 1

# Verifique resultado
cat output/json/nova_placa_ocr.json
```

### 2. Auditoria de Lote
```bash
# Copie todas as placas do setor
cp setor_a/*.jpg input/

# Processe em batch (automático se >5)
python main.py
# Escolha opção 1

# Valide resultados
# Escolha opção 3
```

### 3. Migração de Sistema
```bash
# Processe arquivo histórico
cp arquivo_historico/* input/

# Execute em lotes
for batch in input_batch_*/; do
  cp $batch/* input/
  python main.py  # Opção 1
  mv output/json/* arquivo_processado/
done
```

---

## 🆘 Suporte

Para suporte adicional:
- 📖 Consulte [documentação técnica](README.md)
- 🐛 Reporte bugs no [GitHub](https://github.com/ffreitasb/nr13-ocr-system/issues)
- 💬 Entre em contato para suporte

**🎯 Sistema pronto para uso profissional!**
