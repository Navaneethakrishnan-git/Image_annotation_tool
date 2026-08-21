from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBar, QToolButton


class AppToolbar(QToolBar):

    def __init__(self, parent=None):

        super().__init__("Tool Bar", parent)

        # =====================================================
        # TOOLBAR SETTINGS
        # =====================================================

        self.setMovable(False)
        self.setFloatable(False)

        # Vertical toolbar
        self.setOrientation(Qt.Vertical)

        # IMPORTANT:
        # Icon on top + text below
        self.setToolButtonStyle(
            Qt.ToolButtonTextUnderIcon
        )

        self.setIconSize(
            QSize(26, 26)
        )

        # =====================================================
        # ASSET PATH
        # =====================================================

        project_dir = Path(
            __file__
        ).resolve().parents[2]

        asset_dir = project_dir / "asset"

        def icon(name):

            path = asset_dir / name

            if path.exists():
                return QIcon(str(path))

            return QIcon()

        # =====================================================
        # TOOLBAR STYLE
        # =====================================================

        self.setStyleSheet("""
            QToolBar {
                background: #f5f5f5;

                border: none;
                border-right: 1px solid #d0d0d0;

                padding: 30px 3px 6px 3px;

                spacing: 3px;
            }

            QToolButton {

                width: 90px;
                height: 65px;

                padding: 3px;

                margin: 1px 0px;

                border: 1px solid transparent;

                border-radius: 6px;

                background: transparent;

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

                height: 6px;

                margin: 2px 4px;

                background: transparent;

                border: none;
            }
        """)

        # =====================================================
        # OPEN
        # =====================================================

        self.open_action = self.addAction(
            icon("open-file.png"),
            "Open"
        )

        self.open_action.setToolTip(
            "Open Folder"
        )

        # =====================================================
        # SAVE
        # =====================================================

        self.save_action = self.addAction(
            icon("save.png"),
            "Save"
        )

        self.save_action.setToolTip(
            "Save Annotation"
        )

        self.addSeparator()

        # =====================================================
        # PREVIOUS
        # =====================================================

        self.prev_action = self.addAction(
            icon("back-arrow.png"),
            "Previous"
        )

        self.prev_action.setToolTip(
            "Previous Image"
        )

        # =====================================================
        # NEXT
        # =====================================================

        self.next_action = self.addAction(
            icon("next_arrow.png"),
            "Next"
        )

        self.next_action.setToolTip(
            "Next Image"
        )

        self.addSeparator()

        # =====================================================
        # ZOOM OUT
        # =====================================================

        self.zoom_out_action = self.addAction(
            icon("zoom-out.png"),
            "Zoom Out"
        )

        self.zoom_out_action.setToolTip(
            "Zoom Out"
        )

        # =====================================================
        # RESET
        # =====================================================

        self.zoom_reset_action = self.addAction(
            icon("rotate.png"),
            "Reset"
        )

        self.zoom_reset_action.setToolTip(
            "Reset Zoom to 100%"
        )

        # =====================================================
        # ZOOM IN
        # =====================================================

        self.zoom_in_action = self.addAction(
            icon("zoom-in.png"),
            "Zoom In"
        )

        self.zoom_in_action.setToolTip(
            "Zoom In"
        )

        self.addSeparator()

        # =====================================================
        # IMPORT YAML
        # =====================================================

        self.import_class_action = self.addAction(
            icon("file.png"),
            "Import YAML"
        )

        self.import_class_action.setToolTip(
            "Import Classes YAML"
        )

        # =====================================================
        # FORMAT BUTTONS
        # =====================================================

        self._format_buttons()

    # =========================================================
    # FORMAT BUTTONS
    # =========================================================

    def _format_buttons(self):

        buttons = self.findChildren(
            QToolButton
        )

        for button in buttons:

            button.setFixedSize(
                90,
                65
            )

            button.setIconSize(
                QSize(26, 26)
            )

            # IMPORTANT
            # Icon ABOVE text
            button.setToolButtonStyle(
                Qt.ToolButtonTextUnderIcon
            )

            button.setAutoRaise(
                True
            )

            button.setFocusPolicy(
                Qt.NoFocus
            )

            button.setCursor(
                Qt.PointingHandCursor
            )