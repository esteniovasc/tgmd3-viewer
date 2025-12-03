from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QMovie
import os
from src.config import ASSETS_DIR

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        # Configuração Frameless e TopMost
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground) # Importante para cantos arredondados se houver
        self.resize(700, 450) # Tamanho aproximado da imagem

        # Layout Principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- CONTAINER PRINCIPAL (Cor #0D2C5C) ---
        self.container = QWidget()
        self.container.setObjectName("SplashContainer")
        self.container.setStyleSheet("""
            QWidget#SplashContainer {
                background-color: #0D2C5C;
                border-radius: 20px; /* Bordas arredondadas suaves */
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignCenter)

        # 1. IMAGEM JPG (Logo/Branding)
        lbl_image = QLabel()
        image_path = os.path.join(ASSETS_DIR, "splash_logo.png") # Nome do arquivo na pasta assets
        
        # Fallback se a imagem não existir
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Redimensiona mantendo a proporção se for muito grande
            lbl_image.setPixmap(pixmap.scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            lbl_image.setText("TGMD-3 Viewer")
            lbl_image.setStyleSheet("font-size: 40px; font-weight: bold; color: white; background-color: transparent;")
        
        lbl_image.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(lbl_image)

        container_layout.addSpacing(20)

        # 2. TEXTO DE LOADING ANIMADO ("Carregando recursos...")
        self.lbl_loading = QLabel("Carregando recursos")
        self.lbl_loading.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            color: #FFFFFF;
            font-style: italic;
            background-color: transparent;
        """)
        self.lbl_loading.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.lbl_loading)

        layout.addWidget(self.container)

        # --- LÓGICA DE ANIMAÇÃO E FECHAMENTO ---
        
        # Variáveis de Estado
        self.dots = 0
        self.max_duration = 8000 # 8 segundos de splash (ajustável)
        self.current_time = 0
        
        # Timer da Animação dos Pontinhos (A cada 500ms)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_dots)
        self.anim_timer.start(500)

        # Timer de Fechamento (Progresso simulado)
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.check_close)
        self.close_timer.start(100) # Checa a cada 100ms

    def animate_dots(self):
        """Anima o texto adicionando pontinhos sequencialmente."""
        self.dots = (self.dots + 1) % 4 # Ciclo: 0, 1, 2, 3
        text = "Carregando recursos" + "." * self.dots
        self.lbl_loading.setText(text)

    def check_close(self):
        """Simula o tempo de carregamento e fecha a janela."""
        self.current_time += 100
        if self.current_time >= self.max_duration:
            self.anim_timer.stop()
            self.close_timer.stop()
            self.close() # O main.py vai detectar o fechamento e abrir a Home