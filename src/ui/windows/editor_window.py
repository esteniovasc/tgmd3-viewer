from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFileDialog, QProgressDialog, QMessageBox, QScrollArea
from PySide6.QtCore import Qt, Signal, QTimer, QTime
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtMultimedia import QMediaPlayer

# Componentes
from src.ui.components.top_bar import TopBar
from src.ui.components.video_player_widget import VideoPlayerWidget
from src.ui.components.video_controls import VideoControlsWidget
from src.ui.components.skill_list_widget import SkillListWidget
from src.ui.components.export_panel import ExportPanelWidget
from src.ui.components.timeline_widget import TimelineWidget
from src.ui.components.track_header_widget import TrackHeaderWidget
from src.workers.video_import_worker import VideoImportWorker
from src.workers.thumbnail_worker import ThumbnailWorker

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
        
        # Scroll Area da Timeline
        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidgetResizable(True)
        self.timeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.timeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.timeline_scroll.setStyleSheet("""
            QScrollArea { border: none; background: #212121; }
            QScrollBar:horizontal { height: 12px; background: #333; }
            QScrollBar::handle:horizontal { background: #555; border-radius: 6px; min-width: 20px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """)
        
        self.timeline = TimelineWidget()
        self.timeline_scroll.setWidget(self.timeline)
        
        # Conexão crucial: Solicitação de Seek vinda da Timeline
        self.timeline.seek_requested.connect(self.handle_seek_request)
        self.video_player.positionChanged.connect(self.on_player_position_changed)
        
        timeline_layout.addWidget(self.track_headers, stretch=8)
        timeline_layout.addWidget(self.timeline_scroll, stretch=92) # Agora adiciona o Scroll
        
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
        self.video_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.video_player.errorOccurred.connect(self.on_player_error)

        # Opções de Playback
        self.seek_step_seconds = 2.0 # Variável para controlar o pulo via teclado

        # --- ATALHOS GLOBAIS (QShortcuts tem prioridade sobre foco) ---
        self.play_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.play_shortcut.activated.connect(self.video_player.toggle_play)
        
        self.left_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.left_shortcut.activated.connect(self._on_left_key)
        
        self.right_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.right_shortcut.activated.connect(self._on_right_key)

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
        # Se for o primeiro vídeo, carregar
        if self.current_video_index == -1 and self.project_data["arquivosDeVideo"]:
            self.load_video_at_index(0)
        
        # Iniciar Geração de Thumbnails
        self.thumb_worker = ThumbnailWorker(new_videos)
        self.thumb_worker.thumbnail_generated.connect(self.on_thumbnail_generated)
        self.thumb_worker.start()
        
        print(f"Importados {len(new_videos)} vídeos.")

    def on_thumbnail_generated(self, path, index, qimage):
        self.timeline.add_thumbnail(path, index, qimage)

    # ... (métodos auxiliares)

    def _on_left_key(self):
        # Retroceder X segundos
        new_time = max(0.0, self.current_local_time - self.seek_step_seconds)
        self.perform_seek_shortcut(new_time)

    def _on_right_key(self):
        # Avançar X segundos
        if self.current_video_index != -1:
            videos = self.project_data.get("arquivosDeVideo", [])
            if self.current_video_index < len(videos):
                vid = videos[self.current_video_index]
                dur = vid.get("duracao", 0) if isinstance(vid, dict) else vid.duration
                
                new_time = min(dur, self.current_local_time + self.seek_step_seconds)
                self.perform_seek_shortcut(new_time)

    def perform_seek_shortcut(self, local_time):
        """Helper para executar seek via atalho mantendo contexto global"""
        if self.current_video_index == -1: return

        # Calcular Tempo Global para atualizar Timeline corretamente
        global_offset = 0.0
        videos = self.project_data.get("arquivosDeVideo", [])
        for i, vid in enumerate(videos):
            if i == self.current_video_index:
                break
            dur = vid.get("duracao", 0) if isinstance(vid, dict) else vid.duration
            global_offset += dur
            
        global_time = global_offset + local_time
        
        # Chama o handler padrão de seek (mesma lógica do clique)
        # Force pause? Geralmente edição frame-a-frame ou seek curto prefere manter o estado ou pausar?
        # Vamos manter o estado atual (se estava tocando, continua? ou pausa?)
        # O user pediu "pular", comportamento padrão de editores é seek e pause ou seek e play.
        # Vamos fazer seek simples. Se estiver tocando, vai pular e continuar.
        self.handle_seek_request(self.current_video_index, local_time, global_time, force_pause=False)

    # --- LÓGICA DE PLAYBACK E SEEK ---
    # --- CALLBACKS DO PLAYER ---
    def on_player_position_changed(self, position_ms):
        """Chamado continuamente enquanto o vídeo toca."""
        if self.current_video_index == -1: return
        
        # Evita que o playhead pule para 0 enquanto carregamos um novo vídeo
        if hasattr(self, 'pending_seek_time'):
            return

        # Converter para segundos
        local_time_sec = position_ms / 1000.0
        self.current_local_time = local_time_sec
        
        # Calcular Tempo Global
        global_offset = 0.0
        videos = self.project_data.get("arquivosDeVideo", [])
        
        for i, vid in enumerate(videos):
            if i == self.current_video_index:
                break
            # Soma durações
            dur = vid.get("duracao", 0) if isinstance(vid, dict) else vid.duration
            global_offset += dur
            
        global_time = global_offset + local_time_sec
        
        # Atualiza Timeline
        self.timeline.update_playhead_position(global_time)
        
        # Autoscroll
        self.ensure_playhead_visible(global_time)

    def handle_seek_request(self, video_index, local_time, global_time, force_pause=False):
        print(f"Seek Solicitado: Vídeo {video_index} @ {local_time}s (Global: {global_time}s) Pause={force_pause}")
        
        # Atualiza o playhead visual imediatamente
        self.timeline.update_playhead_position(global_time)
        
        # Auto-Scroll se necessário
        self.ensure_playhead_visible(global_time)
        
        if video_index != self.current_video_index:
            # Troca de vídeo (Cross-Video Seek)
            # Ao trocar de vídeo, start_paused=True é o padrão seguro para evitar glitch,
            # mas se force_pause for True, garantimos o pause. 
            self.load_video_at_index(video_index, start_paused=True, seek_time=local_time)
        else:
            # Mesmo vídeo
            if force_pause:
                self.video_player.pause()
                
            self.video_player.set_position(int(local_time * 1000))

    def ensure_playhead_visible(self, global_time):
        if not self.timeline.pixels_per_second: return
            
        playhead_x = global_time * self.timeline.pixels_per_second
        
        scroll_bar = self.timeline_scroll.horizontalScrollBar()
        scroll_val = scroll_bar.value()
        viewport_width = self.timeline_scroll.viewport().width()
        
        # Margem de segurança (90%)
        visible_end = scroll_val + viewport_width
        threshold = scroll_val + (viewport_width * 0.9)
        
        if playhead_x > threshold:
             # Próxima página
             target_scroll = scroll_val + (viewport_width * 0.95)
             scroll_bar.setValue(int(target_scroll))
        elif playhead_x < scroll_val:
             # Retrocesso
             scroll_bar.setValue(int(playhead_x - 50))

    def load_video_at_index(self, index, start_paused=True, seek_time=0.0):
        if index < 0 or index >= len(self.project_data.get("arquivosDeVideo", [])):
            return

        videos = self.project_data["arquivosDeVideo"]
        video_data = videos[index]
        file_path = video_data["caminho"]
        self.current_video_index = index
        
        # Armazena estado - Adicionado tempo de inicio para UX
        self.pending_seek_time = seek_time
        self.pending_start_paused = start_paused
        self.load_start_time = QTime.currentTime().msecsSinceStartOfDay()
        
        print(f"DEBUG: Loading video {index} ({file_path}), seek={seek_time}")
        
        # UI Feedback
        self.video_player.show_loading(f"Carregando: {video_data['nome']}...")
        QApplication.processEvents()
        
        # Workaround para Seek Reverso: 
        # Às vezes o player reutiliza o estado antigo se for rápido. Parar antes de carregar ajuda.
        self.video_player.player.stop() 
        self.video_player.load_video(file_path)

    # Nova lógica de status (Always-on Display + UX Delay)
    def on_media_status_changed(self, status):
        # BufferedMedia ou LoadedMedia: O player tem dados suficientes
        if status == QMediaPlayer.MediaStatus.BufferedMedia or status == QMediaPlayer.MediaStatus.LoadedMedia:
            if hasattr(self, 'pending_seek_time'):
                print(f"DEBUG: Media Ready. Status={status}. Pending Seek={self.pending_seek_time}")
                
                pos_ms = int(self.pending_seek_time * 1000)
                
                # Calcular quanto tempo resta para completar o fake delay (2000ms)
                MIN_LOAD_DURATION = 1000 # 1 segundos
                elapsed = QTime.currentTime().msecsSinceStartOfDay() - self.load_start_time
                remaining = max(0, MIN_LOAD_DURATION - elapsed)
                
                # Função interna para executar o seek e fechar loading
                def perform_delayed_seek_and_hide():
                     if not hasattr(self, 'video_player'): return
                     
                     # Verifica se ainda temos um seek pendente (evita race condition)
                     if not hasattr(self, 'pending_seek_time'): return

                     # Seek Efetivo
                     self.video_player.set_position(pos_ms)
                     
                     start_paused = getattr(self, 'pending_start_paused', True)
                     if start_paused:
                          self.video_player.pause()
                     else:
                          self.video_player.play()
                     
                     print(f"DEBUG: Seek Executed to {pos_ms}ms")
                     
                     # Limpeza
                     if hasattr(self, 'pending_seek_time'): del self.pending_seek_time
                     if hasattr(self, 'pending_start_paused'): del self.pending_start_paused
                     if hasattr(self, 'load_start_time'): del self.load_start_time
                     
                     # Remove loading SOMENTE AGORA
                     self.video_player.hide_loading()

                # Se o buffering foi rápido, esperamos o restante do tempo
                # Se demorou mais que 2s, executa quase imediatamente (pequeno buffer de segurança)
                delay_total = remaining + 50 
                QTimer.singleShot(delay_total, perform_delayed_seek_and_hide)

    def handle_seek_request(self, video_index, local_time, global_time, force_pause=False):
        print(f"Seek Solicitado: Vídeo {video_index} @ {local_time}s (Global: {global_time}s) Pause={force_pause}")
        
        # Atualiza o playhead visual imediatamente
        self.timeline.update_playhead_position(global_time)
        
        # Scroll Inteligente: Apenas garante visibilidade (sem forçar centro, como pedido)
        self.ensure_playhead_visible(global_time)
        
        if video_index != self.current_video_index:
            # Troca de vídeo
            # Delay aumentado levemente no load_video_at_index poderá ajudar na consistência
            self.load_video_at_index(video_index, start_paused=True, seek_time=local_time)
        else:
            # Mesmo vídeo
            if force_pause:
                self.video_player.pause()
            self.video_player.set_position(int(local_time * 1000))

    def ensure_playhead_visible(self, global_time):
        # Lógica de Paginação (Para Playback e Seek)
        if not self.timeline.pixels_per_second: return
        
        playhead_x = global_time * self.timeline.pixels_per_second
        scroll_bar = self.timeline_scroll.horizontalScrollBar()
        current_scroll = scroll_bar.value()
        viewport_width = self.timeline_scroll.viewport().width()
        
        # --- CONFIGURAÇÃO DO SALTO ---
        # Porcentagem da tela onde o salto ocorre (ex: 95% da tela)
        SCROLL_TRIGGER_PERCENT = 0.95 
        
        # Onde a agulha deve cair na NOVA tela após o salto (ex: 2% da esquerda)
        # Isso garante que ela não fique escondida na esquerda
        NEW_VIEW_START_PERCENT = 0.02
        
        # Margem de segurança para retrocesso (ex: se voltar antes do inicio, mostra inicio)
        # -----------------------------

        # Limite direito para trigger
        threshold_right = current_scroll + (viewport_width * SCROLL_TRIGGER_PERCENT)
        
        if playhead_x > threshold_right:
             # SALTO PARA FRENTE
             # Calcula o novo scroll de forma que a agulha fique no inicio da tela (NEW_VIEW_START_PERCENT)
             target_scroll = playhead_x - (viewport_width * NEW_VIEW_START_PERCENT)
             scroll_bar.setValue(int(target_scroll))
             
        elif playhead_x < current_scroll:
             # SALTO PARA TRÁS (Se a agulha saiu pela esquerda)
             # Centraliza ou coloca no fim? Vamos colocar no meio para contexto
             target_scroll = playhead_x - (viewport_width * 0.5)
             scroll_bar.setValue(max(0, int(target_scroll)))

    def ensure_playhead_centered(self, global_time):
        # (Mantido como utilitário caso queira usar no futuro, mas desligado do fluxo principal)
        if not self.timeline.pixels_per_second: return
        playhead_x = global_time * self.timeline.pixels_per_second
        viewport_width = self.timeline_scroll.viewport().width()
        target_scroll = playhead_x - (viewport_width / 2)
        self.timeline_scroll.horizontalScrollBar().setValue(max(0, int(target_scroll)))

    def on_player_error(self, error):
        print(f"Erro no player: {error}")
        self.video_player.show_error(f"Erro ao carregar mídia.")

    # --- LÓGICA DE LIMPEZA ---
    def reset_ui_state(self):
        
        if hasattr(self, 'import_worker') and self.import_worker.isRunning():
            self.import_worker.terminate()
            
        if hasattr(self, 'thumb_worker') and self.thumb_worker.isRunning():
            self.thumb_worker.stop()
            
        self.project_data = {}
        self.project_file_path = None
        self.is_dirty = False
        self.current_video_index = -1
        self.top_bar.set_project_name("Sem Nome")
        self.top_bar.set_dirty_state(False)

    def load_project_data(self, data, file_path=None):
        """Recebe os dados do JSON carregado e atualiza a UI"""
        self.reset_ui_state() # Limpa tudo antes de carregar
        
        self.project_data = data
        if file_path:
            self.project_file_path = file_path
            
        name = data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        
        videos = data.get("arquivosDeVideo", [])
        if videos:
            self.timeline.set_videos(videos)
            self.video_player.set_has_video(True)
            self.load_video_at_index(0)
            
            # Iniciar Thumbnails para projetos carregados
            # (Adicionando aqui também para persistência funcionar ao carregar JSON)
            self.thumb_worker = ThumbnailWorker(videos)
            self.thumb_worker.thumbnail_generated.connect(self.on_thumbnail_generated)
            self.thumb_worker.start()

    def on_home_clicked(self):
        if self.check_save_barrier():
            self.reset_ui_state() # Limpa ao sair
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
        
        # Garante que o foco volte para a timeline/janela principal ao fechar
        # Isso evita que o foco fique "perdido" ou em um botão da TopBar
        self.setFocus()
        self.timeline.setFocus()

    def on_settings_saved(self, new_data):
        self.project_data = new_data
        name = new_data.get("infoProjeto", {}).get("nome", "Sem Nome")
        self.top_bar.set_project_name(name)
        self.save_project()