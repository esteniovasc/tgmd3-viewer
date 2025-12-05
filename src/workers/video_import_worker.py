import os
import cv2
import uuid
from PySide6.QtCore import QThread, Signal

class VideoImportWorker(QThread):
    """
    Worker thread that processes video files asynchronously to extract metadata.
    """
    finished = Signal(list)  # Emits list of video data dictionaries
    progress = Signal(int, int) # Emits current, total
    error = Signal(str)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        video_data_list = []
        total = len(self.file_paths)
        
        for index, file_path in enumerate(self.file_paths):
            try:
                if not os.path.exists(file_path):
                    continue

                # Extrair Metadados
                cap = cv2.VideoCapture(file_path)
                if not cap.isOpened():
                    print(f"Erro ao abrir vídeo: {file_path}")
                    continue

                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration_sec = frame_count / fps if fps > 0 else 0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                size_bytes = os.path.getsize(file_path)
                
                # Criar Objeto de Dados
                video_item = {
                    "id": str(uuid.uuid4()),
                    "caminho": file_path,
                    "nome": os.path.basename(file_path),
                    "duracao": duration_sec,
                    "tamanho": size_bytes,
                    "fps": fps,
                    "resolucao": [width, height],
                    "offset": 0.0 # Posição inicial na timeline global (será ajustado pelo controller)
                }
                
                video_data_list.append(video_item)
                self.progress.emit(index + 1, total)
                
            except Exception as e:
                print(f"Erro ao processar {file_path}: {e}")
                # Não aborta tudo por um erro, mas loga
        
        self.finished.emit(video_data_list)
