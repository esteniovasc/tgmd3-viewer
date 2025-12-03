import os

# Caminhos Base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Cores (Paleta Dark Modern)
COLOR_BG_DARK = "#1E1E1E"       # Fundo principal
COLOR_BG_PANEL = "#252526"      # Painéis laterais
COLOR_ACCENT = "#007ACC"        # Azul de destaque (Botões principais)
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#CCCCCC"
COLOR_BORDER = "#3E3E42"

# Configurações da Timeline
PIXELS_PER_SECOND = 50
THUMBNAIL_HEIGHT = 50
ANNOTATION_TRACK_HEIGHT = 50
RULER_HEIGHT = 20
THUMBNAIL_INTERVAL_SECONDS = 3

# Dados
SKILLS = [
    "Correr", "Galopar", "Saltar com um pé", "Skip", "Salto Horizontal",
    "Deslizar", "Rebater com 2 mãos", "Rebater com 1 mão", "Quicar",
    "Pegar", "Chutar", "Arremesso por baixo", "Arremesso por cima"
]

# Atalhos de Teclado
SHORTCUTS = {
    "PLAY_PAUSE": "Space",
    "SAVE_PROJECT": "Ctrl+S",
    "UNDO": "Ctrl+Z",
    "REDO": "Ctrl+Y",
    "TOGGLE_LOOP": "R",
    "FULLSCREEN": "F",
    "SPEED_UP": "Up",
    "SPEED_DOWN": "Down",
    "SKIP_FORWARD": "Right",
    "SKIP_BACKWARD": "Left",
    "NEXT_TRIAL": "Shift+Right",
    "PREV_TRIAL": "Shift+Left",
    "LOCK_TAGS": "Ctrl+L"
}

# Cores das Habilidades (Exemplo)
SKILL_COLORS = {
    "locomotor": "#FF9800", # Laranja
    "manipulative": "#00BCD4" # Azul Ciano
}