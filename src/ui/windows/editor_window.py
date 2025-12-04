from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt, Signal

# Importa os componentes que acabamos de criar
from src.ui.components.top_bar import TopBar
from src.ui.components.video_player_widget import VideoPlayerWidget
from src.ui.components.skill_list_widget import SkillListWidget
from src.ui.components.timeline_widget import TimelineWidget

class EditorWindow(QMainWindow):
    home_requested = Signal() # Sinal para pedir à main.py para voltar para Home

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1366, 768)

        # Widget Central
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1E1E1E;")
        self.setCentralWidget(central_widget)
        
        # Layout Principal (Vertical)
        # [Top Bar]
        # [ Conteúdo (Video | Painel) ]
        # [ Timeline ]
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Bar
        self.top_bar = TopBar()
        self.top_bar.exit_clicked.connect(self.close) # Fecha o app
        self.top_bar.home_clicked.connect(self.on_home_clicked)
        self.top_bar.save_clicked.connect(self.save_project)
        self.top_bar.settings_clicked.connect(self.open_settings)
        
        main_layout.addWidget(self.top_bar)

        # Área do Meio
        middle_area = QWidget()
        middle_layout = QHBoxLayout(middle_area)
        middle_layout.setContentsMargins(10, 10, 10, 0)
        
        self.video_player = VideoPlayerWidget()
        self.side_panel = SkillListWidget()
        
        middle_layout.addWidget(self.video_player, stretch=1) # Ocupa espaço livre
        middle_layout.addWidget(self.side_panel) # Largura fixa definida no componente
        
        main_layout.addWidget(middle_area, stretch=1)

        # 3. Timeline
        self.timeline = TimelineWidget()
        main_layout.addWidget(self.timeline)

        self.project_data = {}
        self.project_file_path = None

    def load_project_data(self, data, file_path=None):
        """Recebe os dados do JSON carregado e atualiza a UI"""
        self.project_data = data
        if file_path:
            self.project_file_path = file_path
            
        name = data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        # Futuro: self.timeline.set_data(...)

    def on_home_clicked(self):
        """Chamado quando o botão Home é clicado (após confirmação na TopBar)"""
        self.home_requested.emit()
        self.close() # Fecha a janela do editor (a main vai mostrar a home)

    def save_project(self):
        """Salva o projeto no disco"""
        import json
        
        # Se não tiver caminho do arquivo, não salva (ou pede Save As - futuro)
        if not hasattr(self, 'project_file_path') or not self.project_file_path:
            print("Erro: Caminho do arquivo não definido.")
            return

        try:
            with open(self.project_file_path, "w", encoding="utf-8") as f:
                json.dump(self.project_data, f, indent=2, ensure_ascii=False)
            
            self.top_bar.update_last_saved()
            print("Projeto salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar projeto: {e}")

    def open_settings(self):
        """Abre as configurações"""
        from src.ui.dialogs.project_settings_dialog import ProjectSettingsDialog
        
        dialog = ProjectSettingsDialog(self.project_data, self)
        dialog.settings_saved.connect(self.on_settings_saved)
        dialog.exec()

    def on_settings_saved(self, new_data):
        """Chamado quando as configurações são salvas"""
        self.project_data = new_data
        
        # Atualiza UI
        name = new_data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        
        # Salva no disco
        self.save_project()