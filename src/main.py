import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

# Ajusta o path para garantir que o Python encontre os módulos 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import ASSETS_DIR
from src.ui.windows.splash_screen import SplashScreen
from src.ui.windows.home_screen import HomeScreen
from src.ui.windows.editor_window import EditorWindow
from src.ui.dialogs.create_project_dialog import CreateProjectDialog

def main():
    app = QApplication(sys.argv)

    # --- IDENTIDADE DA APLICAÇÃO ---
    app.setApplicationName("TGMD-3 Viewer")
    app.setOrganizationName("GCOMPH")
    
    icon_path = os.path.join(ASSETS_DIR, "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Carrega Estilo
    style_path = os.path.join(os.path.dirname(__file__), "ui/styles/theme.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

    # --- INSTANCIA JANELAS ---
    splash = SplashScreen()
    home = HomeScreen()
    editor = EditorWindow()

    # --- LÓGICA DE TRANSIÇÃO ---
    
    def show_home():
        home.show()
        splash.close()

    def show_create_dialog():
        dialog = CreateProjectDialog(home)
        dialog.project_created.connect(open_editor_new)
        dialog.exec()

    def open_editor_new(name, file_path):
        import json
        print(f"Criando projeto '{name}' em '{file_path}'")
        
        # Carrega os dados do arquivo recém-criado
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Reutiliza a lógica de carregamento
            on_project_loaded(file_path, data)
            
        except Exception as e:
            print(f"Erro ao carregar projeto recém-criado: {e}")

    # A função agora aceita (path, data) vindos da Home
    def on_project_loaded(path, data):
        print(f"Projeto carregado de: {path}")
        
        # Pega o nome do projeto de dentro do JSON para botar no título
        project_name = data.get("infoProjeto", {}).get("nome", "Projeto Sem Nome")
        editor.setWindowTitle(f"{project_name} - TGMD-3 Viewer")
        
        # Passa os dados e o caminho para o editor
        editor.load_project_data(data, path)
        
        home.hide()
        editor.showMaximized()

    # --- CONECTA SINAIS ---
    
    # Splash -> Home
    QTimer.singleShot(4000, show_home)

    # Home -> Criar
    home.create_project_clicked.connect(show_create_dialog)
    
    # Home -> Abrir
    home.open_project_loaded.connect(on_project_loaded)

    # Editor -> Home
    editor.home_requested.connect(show_home)

    # Inicia
    splash.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()