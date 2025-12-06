from pathlib import Path
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QCursor, QAction
from PySide6.QtWidgets import QWidget, QMenu

from config import (
    THUMBNAIL_HEIGHT, ANNOTATION_TRACK_HEIGHT,
    RULER_HEIGHT, THUMBNAIL_INTERVAL_SECONDS,
    RULER_TICK_HEIGHT, CLIP_DIVIDER_WIDTH,
    ASSETS_DIR, SKILLS
)
import os
from PySide6.QtGui import QPixmap

class TimelineWidget(QWidget):
    # (video_index, local_time, global_time, force_pause)
    seek_requested = Signal(int, float, float, bool)
    
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
            # Shadow no texto para ler sobre thumbnail
            painter.drawText(QPointF(current_x_offset + 5, video_track_y + 15), name)





            # --- Divisor Visual ---
            if i < len(self.clips) - 1:
                painter.setPen(QPen(QColor("#000000"), CLIP_DIVIDER_WIDTH))
                div_x = current_x_offset + clip_width
                painter.drawLine(int(div_x), 0, int(div_x), self.height())

            # Avançar cursor global
            current_x_offset += clip_width

        # --- Annotations (Labels) ---
        annotation_y = RULER_HEIGHT
        annotation_h = ANNOTATION_TRACK_HEIGHT
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        
        for ann in self.annotations:
            start_time = ann.get('time', 0)
            duration = ann.get('duration', 3.0) 
            text = ann.get('text', 'Label')
            
            # Retrieve style info
            bg_color = ann.get('color', "#4CAF50")
            icon_path = ann.get('icon_path', "")
            
            # Only show Name (split if "Index. Name")
            display_text = text.split(". ", 1)[1] if ". " in text else text
            
            ann_x = start_time * self.pixels_per_second
            ann_w = duration * self.pixels_per_second
            
            ann_rect = QRectF(ann_x, annotation_y + 5, ann_w, annotation_h - 10)
            
            # Draw Box
            painter.setBrush(QBrush(QColor(bg_color)))
            painter.setPen(QPen(QColor("#333"), 1)) # Darker border
            painter.drawRoundedRect(ann_rect, 6, 6)
            
            # Draw Icon
            icon_rect_w = 24
            if icon_path and os.path.exists(icon_path):
                # Load on fly (optimization: cache later)
                pixmap = QPixmap(icon_path)
                target_icon_rect = QRectF(ann_x + 5, annotation_y + 5 + (annotation_h - 10 - icon_rect_w)/2, icon_rect_w, icon_rect_w)
                painter.drawPixmap(target_icon_rect.toRect(), pixmap.scaled(icon_rect_w, icon_rect_w, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            # Draw Separator Pipe
            separator_x = ann_x + 5 + icon_rect_w + 5
            painter.setPen(QPen(QColor("#000"), 1))
            painter.drawLine(int(separator_x), int(annotation_y + 10), int(separator_x), int(annotation_y + annotation_h - 10))
            
            # Draw Text
            text_rect = QRectF(separator_x + 5, annotation_y + 5, ann_w - (separator_x - ann_x) - 5, annotation_h - 10)
            painter.setPen(QColor("black")) # Text black for contrast on pastel
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, display_text)

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

    def mouseMoveEvent(self, event):
        # 1. Resize Logic
        if self.resizing_annotation is not None:
            ann = self.annotations[self.resizing_annotation]
            delta_pixels = event.position().x() - self.drag_start_pos
            delta_time = delta_pixels / self.pixels_per_second if self.pixels_per_second > 0 else 0
            
            init_time = self.initial_ann_state['time']
            init_dur = self.initial_ann_state['duration']
            
            if self.resize_edge == 'right':
                # Constraint: cannot go past video end
                bounds = self._get_video_bounds(init_time)
                video_end = bounds[2] if bounds else (init_time + 1000)
                
                new_end = init_time + max(0.5, init_dur + delta_time)
                if new_end > video_end:
                   new_end = video_end
                   
                new_dur = new_end - init_time
                ann['duration'] = max(0.5, new_dur)
                
            elif self.resize_edge == 'left':
                bounds = self._get_video_bounds(init_time)
                video_start = bounds[1] if bounds else 0
                
                # Cannot move start past end (minus min dur)
                # Max start time = init_time + init_dur - 0.5
                new_start = init_time + delta_time
                
                if new_start < video_start:
                    new_start = video_start
                    
                if new_start > init_time + init_dur - 0.5:
                    new_start = init_time + init_dur - 0.5
                
                if new_start < 0: new_start = 0
                
                # Duration change = (old_end - new_start)
                old_end = init_time + init_dur
                new_dur = old_end - new_start
                
                ann['time'] = new_start
                ann['duration'] = new_dur
                
            self.update()
            return

        # 2. Hover Logic
        y = event.position().y()
        x = event.position().x()
        
        # Check hover over annotations
        ann_idx = self._get_annotation_at(x, y)
        if ann_idx is not None:
            edge = self._get_resize_edge(ann_idx, x)
            if edge:
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.PointingHandCursor)
        elif y <= RULER_HEIGHT:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            y = event.position().y()
            
            # Check interaction with annotation first
            ann_idx = self._get_annotation_at(x, y)
            if ann_idx is not None:
                # Check for resize attempt
                edge = self._get_resize_edge(ann_idx, x)
                if edge:
                    self.resizing_annotation = ann_idx
                    self.resize_edge = edge
                    self.drag_start_pos = x
                    self.initial_ann_state = self.annotations[ann_idx].copy()
                    return # Consume event
            
            # Regra: Só faz seek na Régua
            if event.position().y() <= RULER_HEIGHT:
                self._process_seek(event.position().x(), force_pause=False)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
             self.resizing_annotation = None
             self.resize_edge = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()
            y = event.position().y()
            
            # 1. Double Click on Annotation -> Seek to Start
            ann_idx = self._get_annotation_at(x, y)
            if ann_idx is not None:
                 ann_time = self.annotations[ann_idx].get('time', 0)
                 # Force seek to this global timestmap
                 # We need to reverse map global time to video index
                 self._seek_to_global(ann_time)
                 return

            # 2. Double Click on Track -> Regular Seek
            if event.position().y() > RULER_HEIGHT:
                self._process_seek(event.position().x(), force_pause=False)
                
    def _seek_to_global(self, global_seconds):
        # Similar logic to process seek but for exact value
        if not self.clips: return
        
        t = global_seconds
        current_dur_sum = 0
        target_idx = -1
        local_t = 0
        
        # Calculate total duration first to avoid scope confusion? 
        # Better to just iterate and break.
        
        total_duration = 0
        for clip in self.clips:
             total_duration += clip.get('duracao', 0) if isinstance(clip, dict) else clip.duration

        if t >= total_duration:
             target_idx = len(self.clips) - 1
             local_t = 0 # Or end
        else:
            for i, clip in enumerate(self.clips):
                dur = clip.get('duracao', 0) if isinstance(clip, dict) else clip.duration
                if current_dur_sum <= t < current_dur_sum + dur:
                    target_idx = i
                    local_t = t - current_dur_sum
                    break
                current_dur_sum += dur
             
        if target_idx != -1:
            self.seek_requested.emit(target_idx, local_t, t, True) # Force pause usually nice for jumping

    def _process_seek(self, mouse_x, force_pause):
        if not self.clips: return

        if self.pixels_per_second == 0: return # Evita divisão por zero
        click_time = mouse_x / self.pixels_per_second
        
        current_dur_sum = 0
        target_video_index = -1
        local_time = 0
        
        # Achar em qual vídeo clicou
        for i, clip in enumerate(self.clips):
            dur = clip.get('duracao', 0) if isinstance(clip, dict) else clip.duration
            if current_dur_sum <= click_time < current_dur_sum + dur:
                target_video_index = i
                local_time = click_time - current_dur_sum
                break
            current_dur_sum += dur
            
        # Se clicou após o último vídeo (espaço vazio final), pega o último
        if target_video_index == -1 and self.clips:
            target_video_index = len(self.clips) - 1
            last_clip_dur = self.clips[-1].get('duracao', 0) if isinstance(self.clips[-1], dict) else self.clips[-1].duration
            local_time = last_clip_dur
            click_time = current_dur_sum # ou o tempo exato clicado, mas sem video? Vamos travar no final.
            
        if target_video_index != -1:
            self.seek_requested.emit(target_video_index, local_time, click_time, force_pause)

    # Manter stubs
    # --- Drag & Drop Implementation ---
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        # Check if drop zone is within the Annotation Track
        y = event.position().y()
        if RULER_HEIGHT <= y <= (RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()
            x = event.position().x()
            
            # Calculate time
            if self.pixels_per_second > 0:
                time = x / self.pixels_per_second
                
                # Resolve Style
                # Parse index from text "1. SkillName"
                idx = -1
                if ". " in text:
                    try:
                        idx = int(text.split(". ")[0]) - 1 # 0-based
                    except:
                        pass
                
                # Fallback: Lookup name in SKILLS list
                if idx == -1:
                    try:
                        # Normalize text (remove "1. " if parse failed but it exists, or just use text)
                        clean_text = text
                        if ". " in text: clean_text = text.split(". ", 1)[1]
                        
                        if clean_text in SKILLS:
                            idx = SKILLS.index(clean_text)
                    except: pass
                
                bg_color, icon_path = self._get_skill_style(idx)
                
                # Enforce Video Boundaries on Drop
                # Get bounds for the drop time
                bounds = self._get_video_bounds(time)
                if bounds:
                    video_idx, v_start, v_end = bounds
                    
                    # If drop time + default duration > video end, shift it left
                    if time + 3.0 > v_end:
                         time = max(v_start, v_end - 3.0)
                         
                    # Clamp duration if still doesn't fit (short video)
                    duration = min(3.0, v_end - time)
                else:
                    duration = 3.0 # Fallback
                
                # Create annotation
                new_ann = {
                    'time': time,
                    'text': text,
                    'duration': duration, 
                    'color': bg_color,
                    'icon_path': icon_path,
                    'skill_index': idx
                }
                
                self.annotations.append(new_ann)
                self.update()
                
                # Notify (Can emit signal if controller needs to know)
                # self.annotation_added.emit(new_ann)
                
            event.acceptProposedAction()

    def _get_skill_style(self, index):
        # 0-based index
        # 0-5 (Skills 1-6) -> #FFCC84 (Muted Orange)
        # 6-12 (Skills 7-13) -> #B9F5FF (Muted Cyan)
        
        if 0 <= index <= 5:
            color = "#FFCC84"
        elif 6 <= index <= 12:
            color = "#B9F5FF"
        else:
            color = "#CCCCCC" # Default gray if unknown
            
        # Icon Mapping (Same as widget)
        icon_files = [
            "1-correr.png", "2-galopar.png", "3-saltar.png", "4-saltitar.png",
            "5-saltar-horizontal.png", "6-deslizar.png", "7-rebater2maos.png", 
            "8-rebater1mao.png", "9-quicar.png", "10-pegar.png", "11-chutar.png",
            "13-lançar-por-baixo.png", "12-arremessar-por-cima.png"
        ]
        
        icon_path = ""
        if 0 <= index < len(icon_files):
            icon_path = os.path.join(ASSETS_DIR, "icones_habilidades", icon_files[index])
            
        return color, icon_path

    # --- Helpers for Interaction ---

    def _get_annotation_at(self, x, y):
        # Check Y range
        min_y = RULER_HEIGHT
        max_y = RULER_HEIGHT + ANNOTATION_TRACK_HEIGHT
        if not (min_y <= y <= max_y):
            return None
            
        # Check X range (timeline)
        if self.pixels_per_second <= 0: return None
        click_time = x / self.pixels_per_second
        
        # Reverse iterate (topmost first if overlap, though functionality assumes simple list)
        for i in range(len(self.annotations) - 1, -1, -1):
            ann = self.annotations[i]
            start = ann.get('time', 0)
            dur = ann.get('duration', 3.0)
            if start <= click_time <= start + dur:
                return i
        return None

    def _get_resize_edge(self, index, mouse_x):
        # Return 'left', 'right' or None
        ann = self.annotations[index]
        start_x = ann.get('time', 0) * self.pixels_per_second
        end_x = (ann.get('time', 0) + ann.get('duration', 3.0)) * self.pixels_per_second
        
        threshold = 8 # pixels
        if abs(mouse_x - start_x) <= threshold:
            return 'left'
        if abs(mouse_x - end_x) <= threshold:
            return 'right'
        return None

    def _get_video_bounds(self, global_time):
        """Returns (video_index, start_global, end_global) for the video at global_time"""
        current_dur_sum = 0
        for i, clip in enumerate(self.clips):
            dur = clip.get('duracao', 0) if isinstance(clip, dict) else clip.duration
            if current_dur_sum <= global_time < current_dur_sum + dur:
                return (i, current_dur_sum, current_dur_sum + dur)
            current_dur_sum += dur
        return None
