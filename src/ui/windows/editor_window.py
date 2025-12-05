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
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. Top Bar ---
        self.top_bar = TopBar()
        self.top_bar.exit_clicked.connect(self.close)
        self.top_bar.home_clicked.connect(self.on_home_clicked)
        self.top_bar.save_clicked.connect(self.save_project)
        self.top_bar.settings_clicked.connect(self.open_settings)
        main_layout.addWidget(self.top_bar) 

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
        
        # Botões de Play/Pause deveriam ser conectados aqui
        # self.video_controls.play_clicked.connect(self.video_player.play) # (TODO: Atualizar VideoControls)
        
        left_layout.addWidget(self.video_player, stretch=91)
        left_layout.addWidget(self.video_controls, stretch=9)
        
        # Coluna Direita (30%)
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        self.side_panel = SkillListWidget()
        self.export_panel = ExportPanelWidget()
        
        right_layout.addWidget(self.side_panel, stretch=91)
        right_layout.addWidget(self.export_panel, stretch=9)

        workspace_layout.addWidget(left_col, stretch=70)
        workspace_layout.addWidget(right_col, stretch=30)
        
        main_layout.addWidget(workspace_area, stretch=68)

        # --- 3. Timeline Area (Rodapé) ---
        timeline_area = QWidget()
        timeline_area.setStyleSheet("background-color: #212121; border-top: 1px solid #333;")
        timeline_layout = QHBoxLayout(timeline_area)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setSpacing(0)
        
        self.track_headers = TrackHeaderWidget()
        self.timeline = TimelineWidget()
        
        # Conexão crucial: Solicitação de Seek vinda da Timeline
        self.timeline.seek_requested.connect(self.handle_seek_request)
        
        timeline_layout.addWidget(self.track_headers, stretch=8)
        timeline_layout.addWidget(self.timeline, stretch=92)
        
        main_layout.addWidget(timeline_area, stretch=25)

        self.project_data = {}
        self.project_file_path = None
        self.is_dirty = False
        
        # Estado de Playback Atual
        self.current_video_index = -1
        self.current_local_time = 0.0
        
        # Conexões de Importação
        self.video_player.add_video_clicked.connect(self.start_import_video)
        self.track_headers.video_add_clicked.connect(self.start_import_video)
        
        # Conexões do Player (Media Status)
        # self.video_player.player.mediaStatusChanged.connect(self.on_media_status_changed) # Precisa expor o player ou sinal

    def set_dirty(self, dirty: bool):
        self.is_dirty = dirty
        self.top_bar.set_dirty_state(dirty)

    def closeEvent(self, event):
        if not self.check_save_barrier():
            event.ignore()
        else:
            event.accept()

    def check_save_barrier(self) -> bool:
        if not self.is_dirty:
            return True
        reply = QMessageBox.question(self, "Alterações não salvas", "Há alterações não salvas no projeto. Deseja salvar antes de sair?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
        if reply == QMessageBox.Save:
            self.save_project()
            return True
        elif reply == QMessageBox.Discard:
            return True
        else:
            return False

    def start_import_video(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Importar Vídeos", "", "Arquivos de Vídeo (*.mp4 *.avi *.mov *.mkv)")
        if not file_paths: return
            
        self.progress_dialog = QProgressDialog("Processando vídeos...", "Cancelar", 0, len(file_paths), self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        self.import_worker = VideoImportWorker(file_paths)
        self.import_worker.progress.connect(self.progress_dialog.setValue)
        self.import_worker.finished.connect(self.on_import_finished)
        self.import_worker.start()
        
    def on_import_finished(self, new_videos):
        self.progress_dialog.close()
        if not new_videos: return

        if "arquivosDeVideo" not in self.project_data: self.project_data["arquivosDeVideo"] = []
        self.project_data["arquivosDeVideo"].extend(new_videos)
        
        self.set_dirty(True)
        self.video_player.set_has_video(True)
        
        # Atualizar Timeline
        self.timeline.set_videos(self.project_data["arquivosDeVideo"])
        
        # Se for o primeiro vídeo, carregar
        if self.current_video_index == -1 and self.project_data["arquivosDeVideo"]:
            self.load_video_at_index(0)
        
        print(f"Importados {len(new_videos)} vídeos.")

    # --- LÓGICA DE PLAYBACK E SEEK ---
    def handle_seek_request(self, video_index, local_time, global_time):
        print(f"Seek Solicitado: Vídeo {video_index} @ {local_time}s (Global: {global_time}s)")
        
        # Atualiza o playhead visual imediatamente
        self.timeline.update_playhead_position(global_time)
        
        if video_index != self.current_video_index:
            # Troca de vídeo (Cross-Video Seek)
            self.load_video_at_index(video_index, start_paused=True, seek_time=local_time)
        else:
            # Mesmo vídeo, apenas seek local
            self.video_player.set_position(int(local_time * 1000))

    def load_video_at_index(self, index, start_paused=True, seek_time=0.0):
        if index < 0 or index >= len(self.project_data.get("arquivosDeVideo", [])):
            return

        videos = self.project_data["arquivosDeVideo"]
        video_data = videos[index]
        file_path = video_data["caminho"]
        
        self.current_video_index = index
        
        # UI Feedback: Loading
        self.video_player.pause()
        self.video_player.show_loading(f"Carregando: {video_data['nome']}...")
        
        # Simula delay para percepção de carregamento e evitar glitch (opcional, pode ser removido depois)
        # QTimer.singleShot(500, lambda: self._perform_load(file_path, seek_time, start_paused))
        # Para ser mais responsivo, vamos direto, mas o overlay mascara
        self._perform_load(file_path, seek_time, start_paused)

    def _perform_load(self, path, seek_time, start_paused):
        self.video_player.load_video(path)
        self.video_player.set_position(int(seek_time * 1000))
        
        # Aguardar um buffer mínimo? 
        # Por simplificação, removemos o loading após um curto delay para garantir renderização
        QTimer.singleShot(800, self.video_player.hide_loading)
        
        if not start_paused:
            self.video_player.play()

    def load_project_data(self, data, file_path=None):
        self.project_data = data
        if file_path: self.project_file_path = file_path
            
        name = data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        
        videos = data.get("arquivosDeVideo", [])
        if videos:
            self.timeline.set_videos(videos)
            self.video_player.set_has_video(True)
            self.load_video_at_index(0)

    def on_home_clicked(self):
        if self.check_save_barrier():
            self.home_requested.emit()
            self.close()

    def save_project(self):
        import json
        if not hasattr(self, 'project_file_path') or not self.project_file_path:
            print("Erro: Caminho do arquivo não definido.")
            return

        try:
            with open(self.project_file_path, "w", encoding="utf-8") as f:
                json.dump(self.project_data, f, indent=2, ensure_ascii=False)
            self.top_bar.update_last_saved()
            self.set_dirty(False)
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