from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy


class ClassRow(QFrame):
    draw_clicked = Signal(int)
    delete_clicked = Signal(int)
    selected = Signal(int)

    def __init__(self, index, name, parent=None):
        super().__init__(parent)
        self.index = index

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(5)

        self.label = QLabel(name)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label.setToolTip(name)

        self.draw_btn = QPushButton("✏")
        self.draw_btn.setToolTip("Draw Bounding Box")
        self.draw_btn.setFixedSize(30, 28)

        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setToolTip("Delete Class")
        self.delete_btn.setFixedSize(30, 28)

        layout.addWidget(self.label)
        layout.addWidget(self.draw_btn)
        layout.addWidget(self.delete_btn)

        self.draw_btn.clicked.connect(lambda: self.draw_clicked.emit(self.index))
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))

        self.label.mousePressEvent = lambda event: self.selected.emit(self.index)

        self.set_selected(False)

    def set_selected(self, value):
        if value:
            self.setStyleSheet("""
                QFrame { background: #dbeafe; border-radius: 5px; }
                QLabel { font-weight: bold; color: #111827; }
                QPushButton { background: white; border: 1px solid #9ca3af; border-radius: 4px; }
                QPushButton:hover { background: #eeeeee; }
            """)
        else:
            self.setStyleSheet("""
                QFrame { background: transparent; }
                QPushButton { background: #f8f8f8; border: 1px solid #d1d5db; border-radius: 4px; }
                QPushButton:hover { background: #eeeeee; }
            """)


class ClassPanel(QWidget):
    draw_requested = Signal(int)
    delete_requested = Signal(int)
    selected_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.selected_index = -1

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        self.main_layout.addStretch()

    def clear(self):
        for row in self.rows:
            row.deleteLater()
        self.rows.clear()
        self.selected_index = -1

    def set_classes(self, classes):
        self.clear()

        self.main_layout.takeAt(self.main_layout.count() - 1)

        for index, name in enumerate(classes):
            row = ClassRow(index, name, self)

            row.selected.connect(self.select_class)
            row.draw_clicked.connect(self._draw)
            row.delete_clicked.connect(self._delete)

            self.main_layout.addWidget(row)
            self.rows.append(row)

        self.main_layout.addStretch()

    def select_class(self, index):
        self.selected_index = index

        for i, row in enumerate(self.rows):
            row.set_selected(i == index)

        self.selected_changed.emit(index)

    def _draw(self, index):
        self.select_class(index)
        self.draw_requested.emit(index)

    def _delete(self, index):
        self.select_class(index)
        self.delete_requested.emit(index)

    def selected_class(self):
        return self.selected_index
