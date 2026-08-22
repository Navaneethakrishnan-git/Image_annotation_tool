from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtWidgets import QToolBar, QToolButton, QWidget


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

        # Icon ABOVE text
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

        # =====================================================
        # THEME-AWARE ICON FUNCTION
        # =====================================================

        def icon(name):

            path = asset_dir / name

            if not path.exists():

                print(
                    f"Icon not found: {path}"
                )

                return QIcon()

            pixmap = QPixmap(
                str(path)
            )

            if pixmap.isNull():

                print(
                    f"Unable to load icon: {path}"
                )

                return QIcon()

            # -------------------------------------------------
            # Get current system text color
            #
            # Light mode -> normally dark
            # Dark mode  -> normally light
            # -------------------------------------------------

            text_color = (
                self.palette()
                .windowText()
                .color()
            )

            # -------------------------------------------------
            # Create transparent pixmap
            # -------------------------------------------------

            tinted = QPixmap(
                pixmap.size()
            )

            tinted.fill(
                Qt.transparent
            )

            # -------------------------------------------------
            # Paint original image
            # -------------------------------------------------

            painter = QPainter(
                tinted
            )

            painter.drawPixmap(
                0,
                0,
                pixmap
            )

            # -------------------------------------------------
            # Replace icon color
            # Keep transparency
            # -------------------------------------------------

            painter.setCompositionMode(
                QPainter.CompositionMode_SourceIn
            )

            painter.fillRect(
                tinted.rect(),
                text_color
            )

            painter.end()

            return QIcon(
                tinted
            )

        # =====================================================
        # TOOLBAR STYLE
        # =====================================================

        self.setStyleSheet("""
            QToolBar {

                background: palette(window);

                color: palette(window-text);

                border: none;

                border-right:
                    1px solid palette(mid);

                padding:
                    90px 3px 6px 3px;

                spacing: 3px;
            }

            QToolButton {

                width: 90px;

                height: 65px;

                padding: 3px;

                margin: 1px 0px;

                border:
                    1px solid transparent;

                border-radius: 6px;

                background:
                    transparent;

                color:
                    palette(window-text);

                font-size: 10px;
            }

            QToolButton:hover {

                background:
                    palette(alternate-base);

                border:
                    1px solid palette(mid);

                color:
                    palette(window-text);
            }

            QToolButton:pressed {

                background:
                    palette(highlight);

                color:
                    palette(highlighted-text);
            }

            QToolButton:checked {

                background:
                    palette(highlight);

                color:
                    palette(highlighted-text);
            }

            QToolBar::separator {

                height: 6px;

                margin: 2px 4px;

                background:
                    transparent;

                border: none;
            }
        """)

        # =====================================================
        # OPEN
        # =====================================================

        top_space = QWidget()
        top_space.setFixedHeight(50)

        self.addWidget(top_space)

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
            icon("icons8-back-to-48.png"),
            "Previous"
        )

        self.prev_action.setToolTip(
            "Previous Image"
        )

        # =====================================================
        # NEXT
        # =====================================================

        self.next_action = self.addAction(
            icon("icons8-next-page-48.png"),
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