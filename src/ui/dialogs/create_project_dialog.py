from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QHBoxLayout, QFileDialog)
from PySide6.QtCore import Qt, Signal
from src.ui.utils_ui import DraggableMixin

class CreateProjectDialog(DraggableMixin, QDialog):
    project_created = Signal(str, str) # Emite (nome, caminho)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(600, 350)
        self.setStyleSheet("""
            QDialog { background-color: #252526; border: 1px solid #444; border-radius: 10px; }
            QLabel { color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("Criação de projeto")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Inputs
        layout.addWidget(QLabel("Nome do projeto:"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ex: Grupo Intervenção X")
        layout.addWidget(self.input_name)

        layout.addSpacing(15)

        layout.addWidget(QLabel("Caminho do arquivo (Pasta):"))
        path_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        btn_browse = QPushButton("Escolher pasta")
        btn_browse.setProperty("class", "secondary") # Usa estilo do tema
        btn_browse.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(self.input_path)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        layout.addSpacing(20)

        # Botão Ação
        btn_create = QPushButton("Criar projeto ✅")
        btn_create.setProperty("class", "primary") # Usa estilo do tema
        btn_create.setFixedHeight(40)
        btn_create.clicked.connect(self.finish)
        layout.addWidget(btn_create)
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QHBoxLayout, QFileDialog)
from PySide6.QtCore import Qt, Signal
from src.ui.utils_ui import DraggableMixin

class CreateProjectDialog(DraggableMixin, QDialog):
    project_created = Signal(str, str) # Emite (nome, caminho)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(600, 350)
        self.setStyleSheet("""
            QDialog { background-color: #252526; border: 1px solid #444; border-radius: 10px; }
            QLabel { color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("Criação de projeto")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Inputs
        layout.addWidget(QLabel("Nome do projeto:"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ex: Grupo Intervenção X")
        layout.addWidget(self.input_name)

        layout.addSpacing(15)

        layout.addWidget(QLabel("Caminho do arquivo (Pasta):"))
        path_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        btn_browse = QPushButton("Escolher pasta")
        btn_browse.setProperty("class", "secondary") # Usa estilo do tema
        btn_browse.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(self.input_path)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        layout.addSpacing(20)

        # Botão Ação
        btn_create = QPushButton("Criar projeto ✅")
        btn_create.setProperty("class", "primary") # Usa estilo do tema
        btn_create.setFixedHeight(40)
        btn_create.clicked.connect(self.finish)
        layout.addWidget(btn_create)

        # Aviso Importante
        warning = QLabel("⚠ Importante:\nOs arquivos de vídeo devem estar na mesma pasta que o arquivo JSON.")
        warning.setStyleSheet("color: #FFC107; background: #333; padding: 10px; border-radius: 5px; margin-top: 10px;")
        layout.addWidget(warning)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Escolher Pasta do Projeto")
        if folder:
            self.input_path.setText(folder)

    def create_project_file(self, name, folder):
        import json
        import os
        from datetime import datetime

        # Sanitiza o nome para criar o arquivo
        safe_name = "".join([c if c.isalnum() else "_" for c in name]).lower()
        filename = f"{safe_name}.json"
        full_path = os.path.join(folder, filename)

        # Estrutura do JSON
        project_data = {
            "versaoSchema": "3.1",
            "infoProjeto": {
                "nome": name,
                "dataModificacao": datetime.utcnow().isoformat() + "Z",
                "isLocked": False,
                "autor": "Usuário"
            },
            "participantes": [],
            "arquivosDeVideo": []
        }

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            return full_path
        except Exception as e:
            print(f"Erro ao criar arquivo de projeto: {e}")
            return None

    def finish(self):
        name = self.input_name.text()
        folder = self.input_path.text()
        
        if name and folder:
            file_path = self.create_project_file(name, folder)
            if file_path:
                # Emite o nome e o caminho COMPLETO do arquivo criado
                self.project_created.emit(name, file_path)
                self.accept()