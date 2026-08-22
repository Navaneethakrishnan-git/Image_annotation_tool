from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBar, QToolButton, QStyle


class AppToolbar(QToolBar):

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(False)
        self.setFloatable(False)
        self.setOrientation(Qt.Vertical)

        # Icon + text BELOW the icon.
        self.setToolButtonStyle(
            Qt.ToolButtonTextUnderIcon
        )

        self.setIconSize(QSize(24, 24))

        project_dir = Path(__file__).resolve().parents[2]
        asset_dir = project_dir / "asset"

        def icon(name):
            path = asset_dir / name
            if path.exists():
                return QIcon(str(path))
            return QIcon()

        # -----------------------------------------------------
        # COMPACT VERTICAL TOOLBAR
        # -----------------------------------------------------

        self.setStyleSheet("""
            QToolBar {
                background: #f5f5f5;
                border: none;
                border-right: 1px solid #d0d0d0;
                padding: 4px 2px;
                spacing: 0px;
            }

            QToolButton {
                width: 76px;
                height: 62px;

                padding: 2px 1px;
                margin: 1px 0px;

                border: 1px solid transparent;
                border-radius: 5px;

                background: transparent;
                color: #111827;

                font-size: 10px;
            }

            QToolButton:hover {
                background: #e8e8e8;
                border: 1px solid #d0d0d0;
            }

            QToolButton:pressed {
                background: #d8d8d8;
            }

            QToolBar::separator {
                height: 5px;
                margin: 1px 5px;
                background: transparent;
                border: none;
            }
        """)

        # -----------------------------------------------------
        # ACTIONS
        # -----------------------------------------------------

        self.open_action = self.addAction(
            icon("open-file.png"),
            "Open"
        )
        self.open_action.setToolTip("Open Folder")

        self.save_action = self.addAction(
            icon("save.png"),
            "Save"
        )

        # -----------------------------------------------------
        # DRAW BOUNDING BOX
        # -----------------------------------------------------

        self.draw_bounding_action = self.addAction(
            icon("bounding-box.png"),
            "Draw Box"
        )

        self.draw_bounding_action.setToolTip(
            "Draw Bounding Box"
        )

        self.addSeparator()

        self.prev_action = self.addAction(
            icon("icons8-back-to-48.png"),
            "Previous"
        )

        self.next_action = self.addAction(
            icon("icons8-next-page-48.png"),
            "Next"
        )

        self.addSeparator()

        self.zoom_out_action = self.addAction(
            icon("zoom-out.png"),
            "Zoom Out"
        )

        self.zoom_reset_action = self.addAction(
            icon("rotate.png"),
            "Reset"
        )
        self.zoom_reset_action.setToolTip(
            "Reset Zoom to 100%"
        )

        self.zoom_in_action = self.addAction(
            icon("zoom-in.png"),
            "Zoom In"
        )

        self.addSeparator()

        # No user icon was supplied for YAML import.
        # Use Qt's standard file icon as a fallback.
        yaml_icon = self.style().standardIcon(
            QStyle.SP_FileDialogDetailedView
        )

        self.import_class_action = self.addAction(
            yaml_icon,
            "Import YAML"
        )

        self.import_class_action.setToolTip(
            "Import Classes YAML"
        )

        self._format_buttons()

    # =========================================================
    # FORMAT
    # =========================================================

    def _format_buttons(self):

        for button in self.findChildren(QToolButton):

            button.setFixedSize(
                76,
                62
            )

            button.setIconSize(
                QSize(24, 24)
            )

            button.setToolButtonStyle(
                Qt.ToolButtonTextUnderIcon
            )

            button.setAutoRaise(True)

            button.setFocusPolicy(
                Qt.NoFocus
            )

            button.setCursor(
                Qt.PointingHandCursor
            )