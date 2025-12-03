from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

class DraggableMixin:
    """
    Mixin para tornar uma janela Frameless arrastável.
    IMPORTANTE: Deve ser a PRIMEIRA classe na herança.
    Ex: class MinhaJanela(DraggableMixin, QWidget):
    """
    def mousePressEvent(self, event: QMouseEvent):
        # Permite arrastar apenas com o botão esquerdo
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPosition().toPoint()
            event.accept() # Diz ao sistema: "Eu cuido disso, não passe adiante"
        else:
            # Se a classe pai tiver o método, chama ele
            super_method = getattr(super(), 'mousePressEvent', None)
            if super_method:
                super_method(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if hasattr(self, '_old_pos') and event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super_method = getattr(super(), 'mouseMoveEvent', None)
            if super_method:
                super_method(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if hasattr(self, '_old_pos'):
            del self._old_pos
            event.accept()
        else:
            super_method = getattr(super(), 'mouseReleaseEvent', None)
            if super_method:
                super_method(event)