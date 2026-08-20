from PySide6.QtWidgets import QToolBar


class AppToolbar(QToolBar):

    def __init__(self, parent=None):

        super().__init__("Main Toolbar", parent)

        self.open_action = self.addAction("Open Folder")
        self.save_action = self.addAction("Save")

        self.addSeparator()

        self.prev_action = self.addAction("← Previous")
        self.next_action = self.addAction("Next →")

        self.addSeparator()

        self.zoom_out_action = self.addAction("− Zoom Out")
        self.zoom_reset_action = self.addAction("100% Reset")
        self.zoom_in_action = self.addAction("+ Zoom In")
