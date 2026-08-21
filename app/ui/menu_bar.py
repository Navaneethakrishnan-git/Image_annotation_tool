from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenuBar


class AppMenuBar(QMenuBar):
    """
    Top horizontal menu bar.

    Menus:
        File
        Navigation
        View
        Classes
    """

    open_folder_requested = Signal()
    save_requested = Signal()

    previous_requested = Signal()
    next_requested = Signal()

    zoom_out_requested = Signal()
    zoom_reset_requested = Signal()
    zoom_in_requested = Signal()

    import_yaml_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setNativeMenuBar(False)

        self.setStyleSheet("""
            QMenuBar {
                background: #f5f5f5;
                border-bottom: 1px solid #d0d0d0;
                padding: 2px 6px;
                spacing: 4px;
            }

            QMenuBar::item {
                padding: 6px 12px;
                margin: 1px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background: #e5e7eb;
            }

            QMenuBar::item:pressed {
                background: #d1d5db;
            }

            QMenu {
                background: white;
                border: 1px solid #d1d5db;
                padding: 4px;
            }

            QMenu::item {
                padding: 7px 25px 7px 12px;
                border-radius: 3px;
            }

            QMenu::item:selected {
                background: #e5e7eb;
            }
        """)

        # =====================================================
        # FILE
        # =====================================================

        file_menu = self.addMenu("File")

        open_action = file_menu.addAction(
            "Open Folder"
        )

        save_action = file_menu.addAction(
            "Save"
        )

        open_action.triggered.connect(
            self.open_folder_requested.emit
        )

        save_action.triggered.connect(
            self.save_requested.emit
        )

        # =====================================================
        # NAVIGATION
        # =====================================================

        navigation_menu = self.addMenu(
            "Navigation"
        )

        previous_action = navigation_menu.addAction(
            "Previous"
        )

        next_action = navigation_menu.addAction(
            "Next"
        )

        previous_action.triggered.connect(
            self.previous_requested.emit
        )

        next_action.triggered.connect(
            self.next_requested.emit
        )

        # =====================================================
        # VIEW
        # =====================================================

        view_menu = self.addMenu("View")

        zoom_out_action = view_menu.addAction(
            "Zoom Out"
        )

        zoom_reset_action = view_menu.addAction(
            "100% Reset"
        )

        zoom_in_action = view_menu.addAction(
            "Zoom In"
        )

        zoom_out_action.triggered.connect(
            self.zoom_out_requested.emit
        )

        zoom_reset_action.triggered.connect(
            self.zoom_reset_requested.emit
        )

        zoom_in_action.triggered.connect(
            self.zoom_in_requested.emit
        )

        # =====================================================
        # CLASSES
        # =====================================================

        classes_menu = self.addMenu(
            "Classes"
        )

        import_yaml_action = classes_menu.addAction(
            "Import Classes YAML"
        )

        import_yaml_action.triggered.connect(
            self.import_yaml_requested.emit
        )