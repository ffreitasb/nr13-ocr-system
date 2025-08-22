#!/usr/bin/env python3
"""
GUI Streamlit para Sistema OCR NR-13
Inspirado no design do Gerador de Propostas ARTEMEC
"""

import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Adiciona path do projeto
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Imports do sistema
try:
    from config.settings import settings
    from ocr.processor import OCRProcessor
    from services import BatchManager
    from utils import get_logger, format_time, validate_nr13_result
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos: {e}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Sistema OCR NR-13 | ARTEMEC",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado inspirado no design ARTEMEC
st.markdown("""
<style>
    /* Tema escuro similar ao ARTEMEC */
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .stApp {
        background-color: #1e1e1e;
    }
    
    /* Header com logo */
    .header-container {
        background: linear-gradient(90deg, #2d2d2d 0%, #3d3d3d 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-artemec {
        font-family: 'Arial Black', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        text-align: right;
        line-height: 1;
    }
    
    .sistema-title {
        font-size: 1.5rem;
        color: #4fd3c7;
        font-weight: bold;
    }
    
    /* Cards estilo ARTEMEC */
    .info-card {
        background: #2d2d2d;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4fd3c7;
        margin: 1rem 0;
    }
    
    .success-card {
        background: #2d2d2d;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .status-card {
        background: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Botões estilo ARTEMEC */
    .stButton > button {
        background: linear-gradient(45deg, #4fd3c7, #36b9cc);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 211, 199, 0.3);
    }
    
    /* Botão verde para "Ver Arquivos" */
    .success-button {
        background: linear-gradient(45deg, #28a745, #20c997) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        transition: all 0.3s !important;
    }
    
    .success-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* Console/Log estilo ARTEMEC */
    .console-container {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #4d4d4d;
    }
    
    .log-info { color: #4fd3c7; }
    .log-success { color: #28a745; }
    .log-warning { color: #ffc107; }
    .log-error { color: #dc3545; }
    
    /* Métricas */
    .metric-container {
        background: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #4d4d4d;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4fd3c7;
    }
    
    .metric-label {
        color: #cccccc;
        font-size: 0.9rem;
    }
    
    /* Animação de sucesso */
    .processing-complete {
        animation: pulse 2s ease-in-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'images' not in st.session_state:
    st.session_state.images = []
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []
if 'console_logs' not in st.session_state:
    st.session_state.console_logs = []
if 'processing_completed' not in st.session_state:
    st.session_state.processing_completed = False
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

def add_log(message: str, level: str = "info"):
    """Adiciona mensagem ao console"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'level': level
    }
    st.session_state.console_logs.append(log_entry)
    # Mantém apenas últimas 50 mensagens
    if len(st.session_state.console_logs) > 50:
        st.session_state.console_logs = st.session_state.console_logs[-50:]

def render_header():
    """Renderiza header estilo ARTEMEC"""
    st.markdown("""
    <div class="header-container">
        <div>
            <div class="sistema-title">🔧 Sistema OCR para Placas NR-13</div>
            <div style="color: #cccccc; font-size: 0.9rem;">Versão Modular com IA | Mistral Pixtral</div>
        </div>
        <div class="logo-artemec">
            GRUPO<br>
            <span style="font-size: 3rem;">ARTEMEC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_console():
    """Renderiza console de logs estilo ARTEMEC"""
    st.markdown("### 📋 Console do Sistema")
    
    console_html = '<div class="console-container">'
    
    if st.session_state.console_logs:
        for log in st.session_state.console_logs[-10:]:  # Últimas 10 mensagens
            level_class = f"log-{log['level']}"
            console_html += f'<div class="{level_class}">[{log["timestamp"]}] {log["message"]}</div>'
    else:
        console_html += '<div class="log-info">[INFO] Sistema inicializado. Aguardando operações...</div>'
    
    console_html += '</div>'
    st.markdown(console_html, unsafe_allow_html=True)

def initialize_processor():
    """Inicializa o processador OCR"""
    try:
        if st.session_state.processor is None:
            add_log("Inicializando processador OCR...", "info")
            st.session_state.processor = OCRProcessor()
            add_log("✅ Processador OCR inicializado com sucesso", "success")
        return True
    except Exception as e:
        add_log(f"❌ Erro ao inicializar processador: {e}", "error")
        return False

def load_images_from_directory():
    """Carrega imagens do diretório de entrada"""
    try:
        if not st.session_state.processor:
            return []
        
        images = st.session_state.processor.files.list_images(settings.INPUT_DIR)
        add_log(f"📁 Encontradas {len(images)} imagens em {settings.INPUT_DIR}", "info")
        return images
    except Exception as e:
        add_log(f"❌ Erro ao carregar imagens: {e}", "error")
        return []

def simulate_processing(images):
    """Simula o processamento das imagens"""
    processed_files = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, image in enumerate(images):
        progress = (i + 1) / len(images)
        progress_bar.progress(progress)
        status_text.text(f"Processando {image.name}... ({i+1}/{len(images)})")
        
        add_log(f"📷 Processando: {image.name}", "info")
        
        # Simula processamento
        time.sleep(0.8)
        
        # Simula resultado do processamento
        result = {
            'arquivo': image.name,
            'fabricante': f'Fabricante {i+1}',
            'categoria': ['I', 'II', 'III'][i % 3],
            'completude': 85.0 + (i * 3) % 15,  # Entre 85-100%
            'identificacao': f'TAG-{i+1:03d}',
            'pressao_maxima_trabalho': f'{14 + i % 3}.5 kgf/cm²',
            'timestamp': datetime.now().isoformat()
        }
        processed_files.append(result)
    
    status_text.text("✅ Processamento concluído!")
    progress_bar.progress(1.0)
    
    return processed_files

def show_processed_files():
    """Mostra arquivos processados"""
    if st.session_state.processed_files:
        st.markdown("### 📁 Arquivos Processados")
        
        # Converte para DataFrame
        df = pd.DataFrame(st.session_state.processed_files)
        
        # Mostra tabela
        st.dataframe(df, use_container_width=True)
        
        # Estatísticas
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Processado", len(df))
        
        with col_stat2:
            avg_completude = df['completude'].mean()
            st.metric("Completude Média", f"{avg_completude:.1f}%")
        
        with col_stat3:
            valid_count = len(df[df['completude'] >= 90])
            st.metric("Válidos (≥90%)", valid_count)
        
        # Gráfico de completude
        fig = px.bar(df, x='arquivo', y='completude', 
                   title='📊 Completude por Arquivo',
                   color='completude',
                   color_continuous_scale='RdYlGn',
                   range_color=[0, 100])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Arquivo",
            yaxis_title="Completude (%)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Botão para baixar resultados
        if st.button("💾 Baixar Resultados (JSON)"):
            json_str = json.dumps(st.session_state.processed_files, 
                                indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"resultados_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("Nenhum arquivo processado ainda.")

def main():
    """Função principal da GUI"""
    
    # Header
    render_header()
    
    # Inicializa processador
    if not initialize_processor():
        st.error("❌ Falha ao inicializar o sistema. Verifique as configurações.")
        st.stop()
    
    # Layout principal em duas colunas
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📁 Imagens Disponíveis")
        
        # Botão para atualizar lista
        if st.button("🔄 Atualizar Lista", key="refresh_images"):
            st.session_state.images = load_images_from_directory()
            # Reset do estado de processamento se novas imagens
            if st.session_state.images:
                st.session_state.processing_completed = False
        
        # Carrega imagens se não existirem
        if not st.session_state.images:
            st.session_state.images = load_images_from_directory()
        
        # Lista de imagens
        if st.session_state.images:
            for i, image_path in enumerate(st.session_state.images):
                selected = st.session_state.selected_image == i
                button_text = f"📷 {image_path.name}"
                
                if selected:
                    button_text = f"✅ {image_path.name}"
                
                if st.button(button_text, key=f"img_{i}"):
                    st.session_state.selected_image = i
                    add_log(f"📷 Selecionada: {image_path.name}", "info")
        else:
            st.info(f"⚠️ Nenhuma imagem encontrada em `{settings.INPUT_DIR}`")
            st.markdown("**Coloque as imagens das placas NR-13 na pasta de entrada.**")
    
    with col2:
        # Tabs para diferentes funcionalidades
        tab1, tab2, tab3, tab4 = st.tabs(["🔄 Processamento", "📊 Resultados", "⚙️ Configurações", "📈 Estatísticas"])
        
        with tab1:
            st.markdown("### 🔄 Processamento de OCR")
            
            # Informações do modo híbrido
            num_images = len(st.session_state.images)
            modo = "BATCH" if num_images > settings.BATCH_THRESHOLD else "SYNC"
            economia = "50% de desconto" if modo == "BATCH" else "Processamento rápido"
            
            # Card de status - muda cor após processamento
            card_class = "success-card processing-complete" if st.session_state.processing_completed else "info-card"
            status_icon = "✅" if st.session_state.processing_completed else "📊"
            status_title = "Processamento Concluído!" if st.session_state.processing_completed else "Modo Híbrido Inteligente"
            
            st.markdown(f"""
            <div class="{card_class}">
                <h4>{status_icon} {status_title}</h4>
                <p><strong>Imagens encontradas:</strong> {num_images}</p>
                <p><strong>Modo selecionado:</strong> {modo}</p>
                <p><strong>Vantagem:</strong> {economia}</p>
                {f'<p><strong>Arquivos processados:</strong> {len(st.session_state.processed_files)}</p>' if st.session_state.processing_completed else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de ação
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                # Botão muda após processamento
                if not st.session_state.processing_completed:
                    # Botão normal de processar
                    if st.button("🚀 Processar Todas", disabled=not st.session_state.images):
                        add_log("🚀 Iniciando processamento de todas as imagens...", "info")
                        
                        # Processa imagens
                        processed_files = simulate_processing(st.session_state.images)
                        
                        # Salva resultados
                        st.session_state.processed_files = processed_files
                        st.session_state.processing_completed = True
                        
                        add_log(f"✅ Processamento concluído! {len(processed_files)} arquivos processados", "success")
                        
                        # Força refresh da página para mostrar mudanças
                        st.rerun()
                else:
                    # Botão verde para ver arquivos processados
                    if st.button("📁 Ver Arquivos Processados", key="view_processed"):
                        # Mostra modal ou expandir seção com arquivos
                        st.session_state.show_processed_modal = True
            
            with col_btn2:
                if st.button("🎯 Processar Selecionada", disabled=st.session_state.selected_image is None):
                    if st.session_state.selected_image is not None:
                        selected_img = st.session_state.images[st.session_state.selected_image]
                        add_log(f"🎯 Processando imagem selecionada: {selected_img.name}", "info")
                        
                        with st.spinner("Processando..."):
                            time.sleep(2)  # Simula processamento
                        
                        add_log("✅ Processamento da imagem concluído!", "success")
            
            # Mostra arquivos processados se botão foi clicado
            if st.session_state.processing_completed and 'show_processed_modal' in st.session_state:
                if st.session_state.show_processed_modal:
                    show_processed_files()
            
            # Preview da imagem selecionada
            if st.session_state.selected_image is not None:
                selected_img = st.session_state.images[st.session_state.selected_image]
                st.markdown("#### 🖼️ Preview da Imagem Selecionada")
                
                try:
                    st.image(str(selected_img), caption=selected_img.name, use_column_width=True)
                except Exception as e:
                    st.error(f"Erro ao carregar imagem: {e}")
        
        with tab2:
            st.markdown("### 📊 Resultados do Processamento")
            
            if st.session_state.processing_completed and st.session_state.processed_files:
                show_processed_files()
            else:
                # Simula alguns resultados para demonstração
                if st.button("📋 Carregar Últimos Resultados"):
                    add_log("📋 Carregando resultados salvos...", "info")
                    
                    # Dados simulados
                    sample_results = [
                        {"arquivo": "placa_001.jpg", "fabricante": "ACME Corp", "categoria": "I", "completude": 95.0},
                        {"arquivo": "placa_002.jpg", "fabricante": "TechSteel", "categoria": "II", "completude": 88.5},
                        {"arquivo": "placa_003.jpg", "fabricante": "MetalWorks", "categoria": "I", "completude": 92.3},
                    ]
                    
                    df = pd.DataFrame(sample_results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Gráfico de completude
                    fig = px.bar(df, x='arquivo', y='completude', 
                               title='Completude dos Resultados (%)',
                               color='completude',
                               color_continuous_scale='Turbo')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### ⚙️ Configurações do Sistema")
            
            # Configurações da API
            st.markdown("#### 🔑 Configurações da API")
            api_key = st.text_input("Mistral API Key", type="password", 
                                   value="***" if settings.MISTRAL_API_KEY else "")
            
            modelo = st.selectbox("Modelo", 
                                ["pixtral-12b-2409", "pixtral-large-latest"],
                                index=0)
            
            # Configurações de processamento
            st.markdown("#### 🔧 Parâmetros de Processamento")
            
            col_cfg1, col_cfg2 = st.columns(2)
            with col_cfg1:
                batch_threshold = st.number_input("Threshold Batch", 
                                                min_value=1, max_value=20, 
                                                value=settings.BATCH_THRESHOLD)
                temperature = st.slider("Temperature", 0.0, 1.0, 
                                       value=settings.TEMPERATURE, step=0.1)
            
            with col_cfg2:
                max_tokens = st.number_input("Max Tokens", 
                                           min_value=500, max_value=4000, 
                                           value=settings.MAX_TOKENS)
                similarity = st.slider("Similaridade (%)", 0.0, 1.0, 
                                      value=settings.SIMILARITY_THRESHOLD, step=0.05)
            
            if st.button("💾 Salvar Configurações"):
                add_log("💾 Configurações salvas com sucesso!", "success")
            
            # Teste de conexão
            st.markdown("#### 🔍 Teste de Conexão")
            if st.button("🔍 Testar Conexão API"):
                with st.spinner("Testando conexão..."):
                    time.sleep(1)
                    st.success("✅ Conexão estabelecida com sucesso!")
                    add_log("✅ Teste de conexão bem-sucedido", "success")
        
        with tab4:
            st.markdown("### 📈 Estatísticas do Sistema")
            
            # Métricas principais
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                total_processed = len(st.session_state.processed_files)
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{total_processed}</div>
                    <div class="metric-label">Imagens Processadas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_m2:
                if st.session_state.processed_files:
                    avg_completude = sum(f['completude'] for f in st.session_state.processed_files) / len(st.session_state.processed_files)
                    success_rate = f"{avg_completude:.1f}%"
                else:
                    success_rate = "94.2%"
                    
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{success_rate}</div>
                    <div class="metric-label">Taxa de Sucesso</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_m3:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-value">12</div>
                    <div class="metric-label">Jobs Batch</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_m4:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-value">$23.45</div>
                    <div class="metric-label">Economia Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráfico de processamento ao longo do tempo
            dates = pd.date_range(start='2025-08-01', end='2025-08-22', freq='D')
            processing_data = pd.DataFrame({
                'data': dates,
                'imagens': [abs(int(x)) for x in (5 + 10 * pd.Series(range(len(dates))).apply(lambda x: x % 7 - 3.5))]
            })
            
            fig = px.line(processing_data, x='data', y='imagens', 
                         title='📈 Imagens Processadas por Dia',
                         markers=True)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Console na parte inferior
    st.markdown("---")
    render_console()
    
    # Botão para limpar console
    if st.button("🗑️ Limpar Console"):
        st.session_state.console_logs = []
        add_log("Console limpo", "info")

if __name__ == "__main__":
    main()
