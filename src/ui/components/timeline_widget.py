from pathlib import Path
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QCursor, QAction
from PySide6.QtWidgets import QWidget, QMenu

from config import (
    THUMBNAIL_HEIGHT, ANNOTATION_TRACK_HEIGHT,
    RULER_HEIGHT, THUMBNAIL_INTERVAL_SECONDS,
    RULER_TICK_HEIGHT, CLIP_DIVIDER_WIDTH
)

class TimelineWidget(QWidget):
    # (video_index, local_time, global_time)
    seek_requested = Signal(int, float, float) # MODIFICADO: Passa index e local time
    
    clip_reorder_requested = Signal(int, int)
    clip_remove_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT + THUMBNAIL_HEIGHT + 20)
        
        self.clips = []
        self.annotations = []
        self.thumbnails = {}
        
        self.total_duration_display = 0 # Duração para fins de cálculo de width
        self.playhead_position_global = 0 # Posição absoluta na renderização
        
        self.pixels_per_second = 50.0 # Será recalculado

        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        
        # Estado (apenas anotações por enquanto)
        self.dragging_annotation = None
        self.resizing_annotation = None
        self.resize_edge = None
        self.drag_offset_x = 0
        
    def set_videos(self, videos_list):
        self.clips = videos_list
        # O offset de cada clipe deve ser calculado pelo controller, mas aqui recalculamos 
        # para fins de desenho linear se necessário.
        # Assumiremos que a lista vem ordenada.
        
        self.update()

    def set_data(self, clips_data, annotations_data):
        self.clips = clips_data
        self.annotations = annotations_data
        self.update()

    def add_thumbnail(self, path, index, qimage):
        if path not in self.thumbnails: self.thumbnails[path] = {}
        # Converte QImage para QPixmap para desenhar
        from PySide6.QtGui import QPixmap
        self.thumbnails[path][index] = QPixmap.fromImage(qimage)
        self.update()

    def clear_thumbnails(self):
        self.thumbnails = {}
        self.update()

    def reset(self):
        self.clips = []
        self.annotations = []
        self.thumbnails = {}
        self.total_duration_display = 0
        self.playhead_position_global = 0
        self.pixels_per_second = 50.0 # Reset
        self.update()

    def update_playhead_position(self, seconds):
        # Aqui seconds deve ser global (soma das durações anteriores + local)
        self.playhead_position_global = seconds
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#212121"))

        if not self.clips:
            painter.setPen(QColor("#666"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Nenhum vídeo carregado")
            painter.end()
            return

        # 1. Calcular Zoom Dinâmico e Largura Total
        # Pega a largura do viewport (a area visível do scroll), não o widget inteiro
        # Quando setWidget é usado no QScrollArea, o parent() é o viewport.
        viewport_width = self.parent().width() if self.parent() else self.width()
        viewport_duration = 30.0
        
        # Pixels por segundo base para mostrar 30s na tela
        self.pixels_per_second = max(viewport_width / viewport_duration, 10.0) 
        
        # Define o tamanho total do widget para forçar o scroll
        total_width = 0
        for clip in self.clips:
            dur = clip.get('duracao', 0) if isinstance(clip, dict) else clip.duration
            total_width += dur * self.pixels_per_second
            
        # Margem extra e atualiza geometria
        min_w = int(total_width + 100)
        if self.minimumWidth() != min_w:
            self.setMinimumWidth(min_w)
        
        # Altura de componentes
        ruler_y_end = RULER_HEIGHT
        video_track_y = RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT
        
        current_x_offset = 0.0
        
        painter.setFont(QFont("Arial", 8))
        
        for i, clip in enumerate(self.clips):
            duration = clip.get('duracao', 0) if isinstance(clip, dict) else clip.duration
            clip_width = duration * self.pixels_per_second
            
            # --- Fundo do Clipe ---
            clip_rect = QRectF(current_x_offset, video_track_y, clip_width, THUMBNAIL_HEIGHT)
            
            # Otimização: Só desenha se estiver visível (intersecção com evento de paint)
            # Mas o paintEvent do widget dentro do scroll geralmente pede tudo ou região.
            # Vamos desenhar tudo por simplicidade, o Qt faz clip do backend.
            
            # (Alternar cores levemente para distinguir visualmente se não tiver thumbnails)
            bg_color = QColor("#007acc") if i % 2 == 0 else QColor("#006bbb")
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(clip_rect)
            
            # --- Régua Local ---
            # Desenha tiques e números relativos ao clipe (0..duration)
            painter.setPen(QPen(QColor("#888888")))
            
            # Intervalo de ticks da régua
            tick_interval = 1.0 
            
            t = 0.0
            while t <= duration:
                tick_x = current_x_offset + (t * self.pixels_per_second)
                
                # Tique Maior (segundos inteiros)
                if int(t) % 5 == 0: 
                    painter.drawLine(int(tick_x), 0, int(tick_x), 12)
                    painter.drawText(QPointF(tick_x + 2, 10), f"{int(t)}s")
                else:
                    painter.drawLine(int(tick_x), 0, int(tick_x), RULER_TICK_HEIGHT)
                    
                t += tick_interval

            # --- Thumbnails ---
            path = clip.get('caminho', "")
            thumbs = self.thumbnails.get(path, {})
            if thumbs:
                for idx, pixmap in thumbs.items():
                    # idx é o indice do thumbnail (ex: 0, 1, 2...) baseado no intervalo
                    thumb_time = idx * THUMBNAIL_INTERVAL_SECONDS
                    # if thumb_time > duration: continue # (Pode acontecer no ultimo)
                    
                    thumb_x = current_x_offset + (thumb_time * self.pixels_per_second)
                    thumb_w = THUMBNAIL_INTERVAL_SECONDS * self.pixels_per_second
                    
                    # Ajuste para não vazar do clipe (último thumb)
                    if thumb_time + THUMBNAIL_INTERVAL_SECONDS > duration:
                        thumb_w = (duration - thumb_time) * self.pixels_per_second

                    target_rect = QRectF(thumb_x, video_track_y, thumb_w, THUMBNAIL_HEIGHT)
                    
                    if thumb_w > 0:
                        painter.setClipRect(clip_rect) # Clipar no retângulo do vídeo pai
                        painter.drawPixmap(target_rect.toRect(), pixmap)
                        painter.setClipping(False)

            # --- Labels ---
            painter.setPen(QPen(QColor("#FFFFFF")))
            name = clip.get('nome', f"Video {i+1}")
            # Shadow no texto para ler sobre thumbnail
            painter.drawText(QPointF(current_x_offset + 5, video_track_y + 15), name)

            # --- Divisor Visual ---
            if i < len(self.clips) - 1:
                painter.setPen(QPen(QColor("#000000"), CLIP_DIVIDER_WIDTH))
                div_x = current_x_offset + clip_width
                painter.drawLine(int(div_x), 0, int(div_x), self.height())

            # Avançar cursor global
            current_x_offset += clip_width

        # --- Agulha ---
        # Desenhar agulha na posição global
        playhead_x = self.playhead_position_global * self.pixels_per_second
        painter.setPen(QPen(QColor("#FF5252"), 2))
        painter.drawLine(int(playhead_x), 0, int(playhead_x), self.height())
        
        # Triangulo no topo
        painter.setBrush(QBrush(QColor("#FF5252")))
        points = [QPointF(playhead_x - 5, 0), QPointF(playhead_x + 5, 0), QPointF(playhead_x, 10)]
        painter.drawPolygon(points)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            
            # Converter X para Global Time
            if self.pixels_per_second == 0: return
            click_global_time = x / self.pixels_per_second
            
            # Identificar qual vídeo foi clicado
            current_offset = 0.0
            target_video_index = -1
            local_time = 0.0
            
            for i, clip in enumerate(self.clips):
                duration = clip.get('duracao', 0)
                if current_offset <= click_global_time < (current_offset + duration):
                    target_video_index = i
                    local_time = click_global_time - current_offset
                    break
                current_offset += duration
            
            # Se clicou além do último vídeo (espaço vazio), selecionar o último frame do último vídeo
            if target_video_index == -1 and self.clips:
                 target_video_index = len(self.clips) - 1
                 last_clip = self.clips[-1]
                 local_time = last_clip.get('duracao', 0)
            
            if target_video_index != -1:
                # Emitir sinal completo
                self.seek_requested.emit(target_video_index, local_time, click_global_time)

    # Manter stubs do resto para não quebrar interface se necessário, mas simplificar
    def dragEnterEvent(self, event): pass
    def dropEvent(self, event): pass