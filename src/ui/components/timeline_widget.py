# widgets/timeline_widget.py

from pathlib import Path
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QCursor, QAction
from PySide6.QtWidgets import QWidget, QMenu

from config import (
    PIXELS_PER_SECOND, THUMBNAIL_HEIGHT, ANNOTATION_TRACK_HEIGHT,
    RULER_HEIGHT, THUMBNAIL_INTERVAL_SECONDS
)

class TimelineWidget(QWidget):
    seek_requested = Signal(float)
    # Novos sinais para avisar a janela principal
    clip_reorder_requested = Signal(int, int) # (index_origem, index_destino)
    clip_remove_requested = Signal(int)       # (index_para_remover)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT + THUMBNAIL_HEIGHT + 20)
        self.clips = []
        self.annotations = []
        self.thumbnails = {}
        self.total_duration = 0
        self.playhead_position_sec = 0
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        
        # Estado para arrastar Anotações
        self.dragging_annotation = None
        self.resizing_annotation = None
        self.resize_edge = None
        self.drag_offset_x = 0
        self.potential_click_ann = None
        
        # Estado para arrastar Vídeos (NOVO)
        self.dragging_clip_index = None

    def set_data(self, clips_data, annotations_data):
        self.clips = clips_data
        self.annotations = annotations_data
        if self.clips:
            self.total_duration = sum(c['duration'] for c in self.clips)
        else:
            self.total_duration = 0
        
        # Largura mínima para caber tudo
        min_width = int(self.total_duration * PIXELS_PER_SECOND) + 100
        self.setMinimumWidth(max(min_width, self.parent().width() if self.parent() else 0))
        self.update()

    def add_thumbnail(self, path, index, pixmap):
        if path not in self.thumbnails: self.thumbnails[path] = {}
        self.thumbnails[path][index] = pixmap
        self.update()

    def clear_thumbnails(self):
        self.thumbnails = {}
        self.update()

    def update_playhead_position(self, seconds):
        self.playhead_position_sec = seconds
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#212121")) # Fundo mais escuro

        # --- Régua ---
        painter.setPen(QPen(QColor("#888888")))
        painter.setFont(QFont("Arial", 8))
        for i in range(int(self.total_duration) + 5):
            x = i * PIXELS_PER_SECOND
            if i % 5 == 0:
                painter.drawLine(int(x), 0, int(x), 10)
                painter.drawText(QPointF(x + 2, 10), str(i))
            else:
                painter.drawLine(int(x), 0, int(x), 5)

        video_track_y = RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT
        
        # --- Clipes de Vídeo ---
        for i, clip in enumerate(self.clips):
            rect_x = clip['startTime'] * PIXELS_PER_SECOND
            rect_width = clip['duration'] * PIXELS_PER_SECOND
            full_clip_rect = QRectF(rect_x, video_track_y, rect_width, THUMBNAIL_HEIGHT)
            
            # Feedback visual se estiver arrastando este clipe
            if i == self.dragging_clip_index:
                painter.setOpacity(0.5)
            
            painter.setBrush(QBrush(QColor("#007acc")))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(full_clip_rect)
            painter.setOpacity(1.0)

            # Thumbnails
            thumbs = self.thumbnails.get(clip['path'], {})
            if thumbs:
                for idx, pixmap in thumbs.items():
                    thumb_start_x = rect_x + (idx * THUMBNAIL_INTERVAL_SECONDS * PIXELS_PER_SECOND)
                    # Ajusta largura do último thumbnail se necessário
                    thumb_w = PIXELS_PER_SECOND * THUMBNAIL_INTERVAL_SECONDS
                    
                    target_rect = QRectF(thumb_start_x, video_track_y, thumb_w, THUMBNAIL_HEIGHT)
                    # Cortar (clip) o desenho para não vazar do retângulo do vídeo
                    painter.setClipRect(full_clip_rect)
                    painter.drawPixmap(target_rect.toRect(), pixmap)
                    painter.setClipping(False)

            # Nome e Borda
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.drawText(QPointF(rect_x + 5, video_track_y + 15), Path(clip['path']).name)
            
            # Borda separadora
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.drawLine(int(rect_x), int(video_track_y), int(rect_x), int(video_track_y + THUMBNAIL_HEIGHT))

        # --- Anotações ---
        for ann in self.annotations:
            ann_rect = QRectF(ann['startTime'] * PIXELS_PER_SECOND, RULER_HEIGHT + 5, ann['duration'] * PIXELS_PER_SECOND, ANNOTATION_TRACK_HEIGHT - 10)
            painter.setBrush(QBrush(QColor("#4CAF50"))) # Verde
            painter.setPen(QPen(QColor(Qt.GlobalColor.black)))
            painter.drawRoundedRect(ann_rect, 5, 5)
            painter.setPen(QPen(QColor("#FFFFFF")))
            painter.drawText(ann_rect, Qt.AlignmentFlag.AlignCenter, ann['label'])

        # --- Agulha ---
        playhead_x = self.playhead_position_sec * PIXELS_PER_SECOND
        painter.setPen(QPen(QColor("#FF5252"), 2))
        painter.drawLine(int(playhead_x), RULER_HEIGHT, int(playhead_x), self.height())
        painter.end()

    # ... (dragEnterEvent e dropEvent permanecem iguais) ...
    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.acceptProposedAction()
    def dropEvent(self, event):
        skill_name = event.mimeData().text()
        start_time = event.position().x() / PIXELS_PER_SECOND
        self.annotations.append({'label': skill_name, 'startTime': start_time, 'duration': 5.0})
        self.update()

    # --- INTERAÇÃO DO MOUSE (ATUALIZADA) ---
    def mousePressEvent(self, event):
        click_time = event.position().x() / PIXELS_PER_SECOND
        click_y = event.position().y()
        
        # 1. Verifica CLIQUE DIREITO (Menu de Contexto)
        if event.button() == Qt.MouseButton.RightButton:
            # Verifica se clicou em um vídeo
            video_track_y = RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT
            if click_y >= video_track_y and click_y <= video_track_y + THUMBNAIL_HEIGHT:
                for i, clip in enumerate(self.clips):
                    start = clip['startTime']
                    end = start + clip['duration']
                    if start <= click_time < end:
                        self._show_context_menu(event.globalPosition().toPoint(), i)
                        return
            return

        if event.button() != Qt.MouseButton.LeftButton: return

        # 2. Verifica se clicou em uma ANOTAÇÃO (Pista Superior)
        if click_y < RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT:
            self.potential_click_ann = None
            for ann in reversed(self.annotations):
                ann_start, ann_end = ann['startTime'], ann['startTime'] + ann['duration']
                if ann_start <= click_time < ann_end:
                    self.potential_click_ann = ann
                    edge_threshold = 0.5
                    if click_time < ann_start + edge_threshold: self.resizing_annotation, self.resize_edge = ann, 'left'
                    elif click_time > ann_end - edge_threshold: self.resizing_annotation, self.resize_edge = ann, 'right'
                    else: self.dragging_annotation, self.drag_offset_x = ann, click_time - ann_start
                    return

        # 3. Verifica se clicou em um VÍDEO (Pista Inferior) para Reordenar
        video_track_y = RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT
        if click_y >= video_track_y and click_y <= video_track_y + THUMBNAIL_HEIGHT:
            for i, clip in enumerate(self.clips):
                start = clip['startTime']
                end = start + clip['duration']
                if start <= click_time < end:
                    self.dragging_clip_index = i # Inicia o arraste do vídeo
                    self.update()
                    return

        # 4. Se não foi nada disso, move a agulha
        self.seek_requested.emit(click_time)

    def mouseMoveEvent(self, event):
        # ... (Lógica de mover anotação permanece igual, adicione no final:) ...
        self.potential_click_ann = None
        current_time = event.position().x() / PIXELS_PER_SECOND
        
        if self.dragging_annotation:
            self.dragging_annotation['startTime'] = max(0, current_time - self.drag_offset_x)
            self.update()
        elif self.resizing_annotation:
             # (Copie a lógica de resize anterior aqui se não estiver usando o código completo abaixo)
             if self.resize_edge == 'left':
                new_end = self.resizing_annotation['startTime'] + self.resizing_annotation['duration']
                self.resizing_annotation['startTime'] = max(0, current_time)
                self.resizing_annotation['duration'] = max(0.1, new_end - self.resizing_annotation['startTime'])
             elif self.resize_edge == 'right':
                self.resizing_annotation['duration'] = max(0.1, current_time - self.resizing_annotation['startTime'])
             self.update()
        
        elif self.dragging_clip_index is not None:
            # Lógica visual simples para arrastar vídeo:
            # Mudamos o cursor para indicar movimento
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        
        else:
            # Cursor padrão ou resize
            on_edge = False
            for ann in self.annotations:
                ann_start, ann_end = ann['startTime'], ann['startTime'] + ann['duration']
                if abs(current_time - ann_start) < 0.5 or abs(current_time - ann_end) < 0.5:
                    self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor)); on_edge = True; break
            if not on_edge: self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, event):
        # Lógica para soltar o Vídeo
        if self.dragging_clip_index is not None:
            drop_time = event.position().x() / PIXELS_PER_SECOND
            
            # Descobre onde soltou (qual o novo índice?)
            new_index = 0
            for i, clip in enumerate(self.clips):
                # Se soltou antes do meio deste clipe, assume essa posição
                mid_point = clip['startTime'] + (clip['duration'] / 2)
                if drop_time < mid_point:
                    new_index = i
                    break
                new_index = i + 1
            
            # Ajusta índice (se arrastou para o fim)
            new_index = min(new_index, len(self.clips) - 1)
            
            # Emite sinal para a MainWindow fazer a troca real
            if new_index != self.dragging_clip_index:
                self.clip_reorder_requested.emit(self.dragging_clip_index, new_index)
            
            self.dragging_clip_index = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.update()

        # Lógica para Anotações (Seek on Click)
        if self.potential_click_ann:
            self.seek_requested.emit(self.potential_click_ann['startTime'])
        
        self.dragging_annotation, self.resizing_annotation, self.potential_click_ann = None, None, None

    def _show_context_menu(self, pos, clip_index):
        menu = QMenu(self)
        delete_action = QAction("🗑️ Remover Vídeo", self)
        delete_action.triggered.connect(lambda: self.clip_remove_requested.emit(clip_index))
        menu.addAction(delete_action)
        menu.exec(pos)