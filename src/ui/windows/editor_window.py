from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFileDialog, QProgressDialog, QMessageBox
from PySide6.QtCore import Qt, Signal, QTimer

# Componentes
from src.ui.components.top_bar import TopBar
from src.ui.components.video_player_widget import VideoPlayerWidget
from src.ui.components.video_controls import VideoControlsWidget
from src.ui.components.skill_list_widget import SkillListWidget
from src.ui.components.export_panel import ExportPanelWidget
from src.ui.components.timeline_widget import TimelineWidget
from src.ui.components.track_header_widget import TrackHeaderWidget
from src.workers.video_import_worker import VideoImportWorker

class EditorWindow(QMainWindow):
    home_requested = Signal() 

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1366, 768)

        # Widget Central
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1E1E1E;")
        self.setCentralWidget(central_widget)
        
        # Layout Principal (Vertical)
        # 1. Top Bar (Fixo)
        # 2. Workspace (68%)
        # 3. Timeline (25%)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. Top Bar ---
        self.top_bar = TopBar()
        self.top_bar.exit_clicked.connect(self.close)
        self.top_bar.home_clicked.connect(self.on_home_clicked)
        self.top_bar.save_clicked.connect(self.save_project)
        self.top_bar.settings_clicked.connect(self.open_settings)
        main_layout.addWidget(self.top_bar) # Altura fixa definida no componente

        # --- 2. Workspace Area (Centro) ---
        workspace_area = QWidget()
        workspace_layout = QHBoxLayout(workspace_area)
        workspace_layout.setContentsMargins(10, 10, 10, 0)
        workspace_layout.setSpacing(10)
        
        # Coluna Esquerda (70%)
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        self.video_player = VideoPlayerWidget()
        self.video_controls = VideoControlsWidget()
        
        left_layout.addWidget(self.video_player, stretch=91) # 91% altura
        left_layout.addWidget(self.video_controls, stretch=9) # 9% altura
        
        # Coluna Direita (30%)
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        self.side_panel = SkillListWidget()
        #self.side_panel.setFixedWidth(350) # Pode remover se quiser flexível, mas o widget tem fixo interno
        # Vamos remover o fixed width interno do SkillListWidget depois para ser responsivo
        
        self.export_panel = ExportPanelWidget()
        
        right_layout.addWidget(self.side_panel, stretch=91) # 91% altura
        right_layout.addWidget(self.export_panel, stretch=9) # 9% altura

        workspace_layout.addWidget(left_col, stretch=70)
        workspace_layout.addWidget(right_col, stretch=30)
        
        main_layout.addWidget(workspace_area, stretch=68) # 68% da tela

        # --- 3. Timeline Area (Rodapé) ---
        timeline_area = QWidget()
        timeline_area.setStyleSheet("background-color: #212121; border-top: 1px solid #333;")
        timeline_layout = QHBoxLayout(timeline_area)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setSpacing(0)
        
        self.track_headers = TrackHeaderWidget()
        self.timeline = TimelineWidget()
        
        timeline_layout.addWidget(self.track_headers, stretch=8) # 8% largura
        timeline_layout.addWidget(self.timeline, stretch=92) # 92% largura
        
        main_layout.addWidget(timeline_area, stretch=25) # 25% da tela

        self.project_data = {}
        self.project_file_path = None
        self.is_dirty = False
        
        # Conexões de Importação
        self.video_player.add_video_clicked.connect(self.start_import_video)
        self.track_headers.video_add_clicked.connect(self.start_import_video)

    def set_dirty(self, dirty: bool):
        self.is_dirty = dirty
        self.top_bar.set_dirty_state(dirty)

    def closeEvent(self, event):
        if not self.check_save_barrier():
            event.ignore()
        else:
            event.accept()

    def check_save_barrier(self) -> bool:
        """Retorna True se puder fechar/sair, False se cancelado."""
        if not self.is_dirty:
            return True
            
        reply = QMessageBox.question(
            self, "Alterações não salvas", 
            "Há alterações não salvas no projeto. Deseja salvar antes de sair?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Save:
            self.save_project()
            return True # Assumindo que save_project é síncrono ou sucesso garantido por enquanto
        elif reply == QMessageBox.Discard:
            return True
        else:
            return False

    def start_import_video(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Importar Vídeos", "", "Arquivos de Vídeo (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if not file_paths:
            return
            
        # Modal de Progresso
        self.progress_dialog = QProgressDialog("Processando vídeos...", "Cancelar", 0, len(file_paths), self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        # Worker
        self.import_worker = VideoImportWorker(file_paths)
        self.import_worker.progress.connect(self.progress_dialog.setValue)
        self.import_worker.finished.connect(self.on_import_finished)
        self.import_worker.start()
        
    def on_import_finished(self, new_videos):
        self.progress_dialog.close()
        
        if not new_videos:
            return

        # Adicionar ao JSON Project Data
        if "arquivosDeVideo" not in self.project_data:
            self.project_data["arquivosDeVideo"] = []
            
        self.project_data["arquivosDeVideo"].extend(new_videos)
        
        # Atualizar Estado
        self.set_dirty(True)
        self.video_player.set_has_video(True) # Simplesmente liga o player se tiver vídeo
        
        # TODO: Atualizar Timeline aqui
        print(f"Importados {len(new_videos)} vídeos.")

    def load_project_data(self, data, file_path=None):
        """Recebe os dados do JSON carregado e atualiza a UI"""
        self.project_data = data
        if file_path:
            self.project_file_path = file_path
            
        name = data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        
        # Passa dados para timeline (futuro)
        # self.timeline.set_data(data.get("arquivosDeVideo", []), [])

    def on_home_clicked(self):
        if self.check_save_barrier():
            self.home_requested.emit()
            self.close()

    def save_project(self):
        import json
        if not hasattr(self, 'project_file_path') or not self.project_file_path:
            # TODO: Implementar Save As se não tiver path
            print("Erro: Caminho do arquivo não definido.")
            return

        try:
            with open(self.project_file_path, "w", encoding="utf-8") as f:
                json.dump(self.project_data, f, indent=2, ensure_ascii=False)
            
            self.top_bar.update_last_saved()
            self.set_dirty(False) # Limpa o estado dirty após salvar
            print("Projeto salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar projeto: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao salvar projeto: {str(e)}")

    def open_settings(self):
        from src.ui.dialogs.project_settings_dialog import ProjectSettingsDialog
        dialog = ProjectSettingsDialog(self.project_data, self)
        dialog.settings_saved.connect(self.on_settings_saved)
        dialog.exec()

    def on_settings_saved(self, new_data):
        self.project_data = new_data
        name = new_data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        self.save_project()