#!/usr/bin/env python3
"""
Launcher para GUI Streamlit - Sistema OCR NR-13
Inspirado no design ARTEMEC
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    """Executa a GUI Streamlit"""
    
    print("🚀 Iniciando GUI do Sistema OCR NR-13...")
    print("📱 Interface inspirada no design ARTEMEC")
    print("-" * 50)
    
    # Caminho para o arquivo da GUI
    gui_file = Path(__file__).parent / "gui_streamlit.py"
    
    if not gui_file.exists():
        print("❌ Arquivo gui_streamlit.py não encontrado!")
        print("Execute primeiro: git pull origin main")
        return
    
    try:
        # Verifica se streamlit está instalado
        subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                      check=True, capture_output=True)
        
        print("✅ Streamlit encontrado")
        print("🌐 Abrindo navegador...")
        
        # Executa streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(gui_file),
            "--server.port=8501",
            "--server.address=localhost",
            "--theme.base=dark",
            "--theme.primaryColor=#4fd3c7",
            "--theme.backgroundColor=#1e1e1e",
            "--theme.secondaryBackgroundColor=#2d2d2d",
            "--theme.textColor=#ffffff"
        ]
        
        print(f"🔧 Comando: {' '.join(cmd)}")
        print("📱 GUI será aberta em: http://localhost:8501")
        print("-" * 50)
        print("💡 Para parar a GUI, pressione Ctrl+C")
        print("-" * 50)
        
        # Aguarda um pouco e abre navegador
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Executa streamlit
        subprocess.run(cmd)
        
    except subprocess.CalledProcessError:
        print("❌ Streamlit não está instalado!")
        print("📦 Para instalar:")
        print("   pip install streamlit plotly")
        print("   # ou")
        print("   pip install -r requirements.txt")
        
    except KeyboardInterrupt:
        print("\n👋 GUI encerrada pelo usuário")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar GUI: {e}")
        print("🔧 Tente executar manualmente:")
        print(f"   streamlit run {gui_file}")

if __name__ == "__main__":
    main()
