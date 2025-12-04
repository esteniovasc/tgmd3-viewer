from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QHBoxLayout, QScrollArea, QWidget, 
                               QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from src.ui.utils_ui import DraggableMixin
from datetime import datetime

class ProjectSettingsDialog(DraggableMixin, QDialog):
    settings_saved = Signal(dict) # Emite os dados atualizados do projeto

    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.participants = list(project_data.get("participantes", [])) # Cópia para edição
        self.has_changes = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(600, 500)
        self.setStyleSheet("""
            QDialog { background-color: #2D2D30; border: 1px solid #444; border-radius: 10px; }
            QLabel { color: #FFFDFF; }
            QLineEdit { 
                background-color: #3E3E42; 
                border: 1px solid #555; 
                border-radius: 4px; 
                padding: 5px; 
                color: white; 
            }
            QLineEdit:focus { border: 1px solid #007ACC; }
            QPushButton { border-radius: 4px; padding: 5px 10px; }
            QScrollArea { border: none; background: transparent; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header
        lbl_title = QLabel("Configurações do Projeto")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(lbl_title)

        # Nome do Projeto
        layout.addWidget(QLabel("Nome do projeto", objectName="lbl_subtitle"))
        self.input_project_name = QLineEdit()
        self.input_project_name.setText(project_data.get("infoProjeto", {}).get("nome", ""))
        self.input_project_name.textChanged.connect(self.on_change)
        layout.addWidget(self.input_project_name)

        layout.addSpacing(10)

        # Gerenciar Participantes
        lbl_part = QLabel("Gerenciar participantes")
        lbl_part.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_part)

        # Input Novo Participante
        add_layout = QHBoxLayout()
        self.input_new_participant = QLineEdit()
        self.input_new_participant.setPlaceholderText("Nome do aluno")
        
        btn_add = QPushButton("Adicionar")
        btn_add.setStyleSheet("background-color: #007ACC; color: white; font-weight: bold;")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_participant)
        
        add_layout.addWidget(self.input_new_participant)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)

        # Lista de Participantes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.participants_container = QWidget()
        self.participants_layout = QVBoxLayout(self.participants_container)
        self.participants_layout.setContentsMargins(0, 0, 0, 0)
        self.participants_layout.setSpacing(5)
        self.participants_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.participants_container)
        
        layout.addWidget(self.scroll_area)

        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #3E3E42; color: white; border: 1px solid #555;")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Salvar Alterações")
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #007ACC; color: white; font-weight: bold; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_changes)
        
        footer_layout.addWidget(btn_cancel)
        footer_layout.addWidget(self.btn_save)
        layout.addLayout(footer_layout)

        # Estilo extra para subtítulos
        self.findChild(QLabel, "lbl_subtitle").setStyleSheet("color: #AAA; font-size: 12px;")

        self.refresh_participants_list()

    def on_change(self):
        self.has_changes = True
        self.btn_save.setEnabled(True)

    def generate_new_id(self):
        """Encontra o menor ID natural disponível (p1, p2, p3...)"""
        existing_ids = set()
        for p in self.participants:
            # Extrai o número do ID (ex: "p1" -> 1)
            try:
                pid = int(p["id"].replace("p", ""))
                existing_ids.add(pid)
            except ValueError:
                continue
        
        new_id_num = 1
        while new_id_num in existing_ids:
            new_id_num += 1
            
        return f"p{new_id_num}"

    def add_participant(self):
        name = self.input_new_participant.text().strip()
        if not name:
            return

        new_id = self.generate_new_id()
        self.participants.append({"id": new_id, "nome": name})
        self.participants.sort(key=lambda x: int(x["id"].replace("p", ""))) # Mantém ordenado
        
        self.input_new_participant.clear()
        self.refresh_participants_list()
        self.on_change()

    def refresh_participants_list(self):
        # Limpa layout atual
        while self.participants_layout.count():
            child = self.participants_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for p in self.participants:
            item_widget = QFrame()
            item_widget.setStyleSheet("background-color: #333; border-radius: 5px;")
            item_widget.setFixedHeight(40)
            
            row_layout = QHBoxLayout(item_widget)
            row_layout.setContentsMargins(10, 0, 10, 0)
            
            # Nome (Editável mas parece label inicialmente)
            input_name = QLineEdit(p["nome"])
            input_name.setReadOnly(True)
            input_name.setStyleSheet("background: transparent; border: none; color: white;")
            
            # Botões
            btn_edit = QPushButton("✏️") # Placeholder
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("background: transparent; border: none;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            
            btn_delete = QPushButton("🗑️") # Placeholder
            btn_delete.setFixedSize(30, 30)
            btn_delete.setStyleSheet("background: transparent; border: none;")
            btn_delete.setCursor(Qt.PointingHandCursor)

            # Lógica de Edição Inline
            def enable_edit(inp=input_name, btn=btn_edit, part=p):
                inp.setReadOnly(False)
                inp.setFocus()
                inp.setStyleSheet("background-color: #252526; border: 1px solid #007ACC; border-radius: 4px;")
                # Move cursor para o final
                inp.setCursorPosition(len(inp.text()))
                
                # Muda ícone para check
                btn.setText("✅")
                btn.clicked.disconnect()
                btn.clicked.connect(lambda: save_edit(inp, btn, part))

            def save_edit(inp, btn, part):
                new_name = inp.text().strip()
                if new_name:
                    part["nome"] = new_name
                    self.on_change()
                else:
                    inp.setText(part["nome"]) # Reverte se vazio
                
                # Restaura estado
                inp.setReadOnly(True)
                inp.setStyleSheet("background: transparent; border: none; color: white;")
                btn.setText("✏️")
                btn.clicked.disconnect()
                btn.clicked.connect(lambda: enable_edit(inp, btn, part))

            btn_edit.clicked.connect(lambda checked=False, i=input_name, b=btn_edit, pt=p: enable_edit(i, b, pt))
            btn_delete.clicked.connect(lambda checked=False, pid=p["id"], pname=p["nome"]: self.delete_participant(pid, pname))

            row_layout.addWidget(input_name)
            row_layout.addStretch()
            row_layout.addWidget(btn_edit)
            row_layout.addWidget(btn_delete)
            
            self.participants_layout.addWidget(item_widget)

    def delete_participant(self, pid, pname):
        # Verifica uso em rotulações
        usage_count = 0
        for video in self.project_data.get("arquivosDeVideo", []):
            for rotulo in video.get("rotulacoes", []):
                if rotulo.get("idParticipante") == pid:
                    usage_count += 1
        
        if usage_count > 0:
            reply = QMessageBox.question(
                self, "Confirmar Exclusão",
                f"O participante {pname} está vinculado à {usage_count} rótulos no seu projeto atual.\n"
                "Se ele for excluído as rotulações ficarão sem participantes vinculados.\n"
                "Confirmar exclusão?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            
            # Remove vínculos
            self.remove_participant_links(pid)

        # Remove da lista
        self.participants = [p for p in self.participants if p["id"] != pid]
        self.refresh_participants_list()
        self.on_change()

    def remove_participant_links(self, pid):
        for video in self.project_data.get("arquivosDeVideo", []):
            for rotulo in video.get("rotulacoes", []):
                if rotulo.get("idParticipante") == pid:
                    rotulo["idParticipante"] = None # Ou "" dependendo do schema, usando None (null) por enquanto

    def save_changes(self):
        # Atualiza dados principais
        self.project_data["infoProjeto"]["nome"] = self.input_project_name.text()
        self.project_data["infoProjeto"]["dataModificacao"] = datetime.utcnow().isoformat() + "Z"
        self.project_data["participantes"] = self.participants
        
        self.settings_saved.emit(self.project_data)
        self.accept()
