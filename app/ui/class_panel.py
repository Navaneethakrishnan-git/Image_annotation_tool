from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)


class ClassRow(QFrame):
    draw_clicked = Signal(int)
    delete_clicked = Signal(int)
    selected = Signal(int)

    def __init__(self, index, name, parent=None):
        super().__init__(parent)

        self.index = index

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(6)

        # -----------------------------------------------------
        # CLASS NAME
        # -----------------------------------------------------

        self.label = QLabel(name)

        self.label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.label.setToolTip(name)
        self.label.setAlignment(
            Qt.AlignVCenter | Qt.AlignLeft
        )

        # -----------------------------------------------------
        # ICON PATHS
        # -----------------------------------------------------

        # Project structure:
        #
        # annotation_tool/
        #     asset/
        #         draw.png
        #         delete.png
        #
        # class_panel.py:
        #     app/ui/class_panel.py
        #
        # parents[2] -> annotation_tool

        project_dir = Path(
            __file__
        ).resolve().parents[2]

        asset_dir = project_dir / "asset"

        draw_icon_path = (
            asset_dir / "bounding-box.png"
        )

        delete_icon_path = (
            asset_dir / "delete.png"
        )

        # -----------------------------------------------------
        # DRAW BUTTON
        # -----------------------------------------------------

        self.draw_btn = QPushButton()

        self.draw_btn.setToolTip(
            "Draw Bounding Box"
        )

        self.draw_btn.setFixedSize(
            34,
            32
        )

        self.draw_btn.setIconSize(
            self.draw_btn.size() * 0.62
        )

        if draw_icon_path.exists():

            self.draw_btn.setIcon(
                QIcon(
                    str(draw_icon_path)
                )
            )

        else:

            # Fallback if icon file is missing.
            self.draw_btn.setText("✏")

        # -----------------------------------------------------
        # DELETE BUTTON
        # -----------------------------------------------------

        self.delete_btn = QPushButton()

        self.delete_btn.setToolTip(
            "Delete Class"
        )

        self.delete_btn.setFixedSize(
            34,
            32
        )

        self.delete_btn.setIconSize(
            self.delete_btn.size() * 0.62
        )

        if delete_icon_path.exists():

            self.delete_btn.setIcon(
                QIcon(
                    str(delete_icon_path)
                )
            )

        else:

            # Fallback if icon file is missing.
            self.delete_btn.setText("🗑")

        # -----------------------------------------------------
        # BUTTON STYLE
        # -----------------------------------------------------

        self.draw_btn.setStyleSheet("""
            QPushButton {
                background: #f8f8f8;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 3px;
            }

            QPushButton:hover {
                background: #eeeeee;
                border: 1px solid #9ca3af;
            }

            QPushButton:pressed {
                background: #dddddd;
            }
        """)

        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #f8f8f8;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 3px;
            }

            QPushButton:hover {
                background: #eeeeee;
                border: 1px solid #9ca3af;
            }

            QPushButton:pressed {
                background: #dddddd;
            }
        """)

        # -----------------------------------------------------
        # HORIZONTAL LAYOUT
        # -----------------------------------------------------

        # Class name + Draw icon + Delete icon
        # all remain on the SAME horizontal line.

        layout.addWidget(
            self.label,
            1
        )

        layout.addWidget(
            self.draw_btn,
            0
        )

        layout.addWidget(
            self.delete_btn,
            0
        )

        # -----------------------------------------------------
        # SIGNALS
        # -----------------------------------------------------

        self.draw_btn.clicked.connect(
            lambda: self.draw_clicked.emit(
                self.index
            )
        )

        self.delete_btn.clicked.connect(
            lambda: self.delete_clicked.emit(
                self.index
            )
        )

        self.label.mousePressEvent = (
            lambda event:
            self.selected.emit(
                self.index
            )
        )

        self.set_selected(False)

    # =========================================================
    # SELECTED STATE
    # =========================================================

    def set_selected(self, value):

        if value:

            self.setStyleSheet("""
                QFrame {
                    background: #dbeafe;
                    border-radius: 5px;
                }

                QLabel {
                    font-weight: bold;
                    color: #111827;
                }
            """)

        else:

            self.setStyleSheet("""
                QFrame {
                    background: transparent;
                }

                QLabel {
                    color: #111827;
                }
            """)


class ClassPanel(QWidget):

    draw_requested = Signal(int)
    delete_requested = Signal(int)
    selected_changed = Signal(int)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.rows = []
        self.selected_index = -1

        # Scrollable class list
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_widget = QWidget()

        self.main_layout = QVBoxLayout(
            self.scroll_widget
        )
        self.main_layout.setContentsMargins(
            0, 0, 0, 0
        )
        self.main_layout.setSpacing(2)
        self.main_layout.addStretch()

        self.scroll_area.setWidget(
            self.scroll_widget
        )

        outer_layout.addWidget(
            self.scroll_area
        )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self):

        for row in self.rows:

            row.deleteLater()

        self.rows.clear()
        self.selected_index = -1

    # =========================================================
    # SET CLASSES
    # =========================================================

    def set_classes(self, classes):

        self.clear()

        # Remove the old stretch.
        if self.main_layout.count() > 0:

            item = self.main_layout.takeAt(
                self.main_layout.count() - 1
            )

            if item.widget():
                item.widget().deleteLater()

        for index, name in enumerate(classes):

            row = ClassRow(
                index,
                name,
                self
            )

            row.selected.connect(
                self.select_class
            )

            row.draw_clicked.connect(
                self._draw
            )

            row.delete_clicked.connect(
                self._delete
            )

            self.main_layout.addWidget(
                row
            )

            self.rows.append(
                row
            )

        self.main_layout.addStretch()

    # =========================================================
    # SELECT CLASS
    # =========================================================

    def select_class(self, index):

        self.selected_index = index

        for i, row in enumerate(
            self.rows
        ):

            row.set_selected(
                i == index
            )

        self.selected_changed.emit(
            index
        )

    # =========================================================
    # DRAW
    # =========================================================

    def _draw(self, index):

        self.select_class(
            index
        )

        self.draw_requested.emit(
            index
        )

    # =========================================================
    # DELETE
    # =========================================================

    def _delete(self, index):

        self.select_class(
            index
        )

        self.delete_requested.emit(
            index
        )

    # =========================================================
    # SELECTED CLASS
    # =========================================================

    def selected_class(self):

        return self.selected_index