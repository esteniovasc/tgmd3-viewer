import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import ASSETS_DIR

print(f"ASSETS_DIR: {ASSETS_DIR}")
print(f"Exists: {os.path.exists(ASSETS_DIR)}")

icon_files = [
    "1-correr.png", "2-galopar.png", "3-saltar.png"
]

icons_dir = os.path.join(ASSETS_DIR, "icones_habilidades")
print(f"Icons Dir: {icons_dir}")
print(f"Icons Dir Exists: {os.path.exists(icons_dir)}")

for f in icon_files:
    p = os.path.join(icons_dir, f)
    print(f"File: {f} -> Exists: {os.path.exists(p)}")

#esse código provavelmente não será necessário