import yaml
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QDialog,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
)

from app.ui.annotation_canvas import AnnotationCanvas
from app.ui.class_panel import ClassPanel
from app.ui.toolbar import AppToolbar
from app.ui.menu_bar import AppMenuBar

from app.core.class_manager import ClassManager
from app.core.image_manager import ImageManager
from app.core.annotation_manager import AnnotationManager

from app.models.annotation import Annotation
from PySide6.QtGui import QShortcut, QKeySequence


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Image Annotation Tool"
        )

        # Application icon.
        icon_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "arinutpam_icon.ico"
        )

        if icon_path.exists():
            self.setWindowIcon(
                QIcon(str(icon_path))
            )

        self.resize(
            1500,
            850
        )

        # -----------------------------------------------------
        # MANAGERS
        # -----------------------------------------------------

        self.class_manager = ClassManager()
        self.image_manager = ImageManager()
        self.annotation_manager = AnnotationManager()

        self.dirty = False
        self.current_folder = None
        self.classes_yaml_path = None
        self.drawing_class = None

        # -----------------------------------------------------
        # LOAD EXISTING CLASSES
        # -----------------------------------------------------

        self.load_classes_yaml()

        # -----------------------------------------------------
        # TOOLBAR
        # -----------------------------------------------------

        self.toolbar = AppToolbar(self)

        # LEFT: vertical icon toolbar.
        self.addToolBar(
            Qt.LeftToolBarArea,
            self.toolbar
        )

        self.toolbar.open_action.triggered.connect(
            self.open_folder
        )

        self.toolbar.save_action.triggered.connect(
            self.save_current
        )

        self.toolbar.prev_action.triggered.connect(
            self.previous_image
        )

        self.toolbar.next_action.triggered.connect(
            self.next_image
        )

        # Draw Bounding Box from TOOLBAR.
        # No class is pre-selected, so the class dialog appears
        # after the box is completed.
        self.toolbar.draw_bounding_action.triggered.connect(
            lambda checked=False: self.start_drawing(None)
        )

        # -----------------------------------------------------
        # IMPORT CLASS YAML ACTION
        # -----------------------------------------------------

        self.toolbar.import_class_action.triggered.connect(
            self.import_classes_yaml
        )

        # =====================================================
        # TOP MENU BAR
        # =====================================================

        self.app_menu_bar = AppMenuBar(self)

        self.app_menu_bar.open_folder_requested.connect(
            self.open_folder
        )

        self.app_menu_bar.save_requested.connect(
            self.save_current
        )

        self.app_menu_bar.previous_requested.connect(
            self.previous_image
        )

        self.app_menu_bar.next_requested.connect(
            self.next_image
        )

        self.app_menu_bar.import_yaml_requested.connect(
            self.import_classes_yaml
        )

        self.setMenuBar(
            self.app_menu_bar
        )

        # -----------------------------------------------------
        # CENTRAL WIDGET
        # -----------------------------------------------------

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        # =====================================================
        # TOP INFORMATION BAR
        # =====================================================

        top_bar = QHBoxLayout()

        self.folder_label = QLabel(
            "Folder: Not selected"
        )

        self.image_count_label = QLabel(
            "Images: 0"
        )

        self.current_image_label = QLabel(
            "Image: 0 / 0"
        )

        self.image_name_label = QLabel(
            "No image"
        )

        top_bar.addWidget(
            self.folder_label
        )

        top_bar.addStretch()

        top_bar.addWidget(
            self.image_count_label
        )

        top_bar.addSpacing(
            20
        )

        top_bar.addWidget(
            self.current_image_label
        )

        top_bar.addSpacing(
            20
        )

        top_bar.addWidget(
            self.image_name_label
        )

        main_layout.addLayout(
            top_bar
        )

        # =====================================================
        # MAIN CONTENT AREA
        # =====================================================

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # =====================================================
        # LEFT / CENTER: IMAGE CANVAS
        # =====================================================

        self.canvas = AnnotationCanvas()

        self.toolbar.zoom_in_action.triggered.connect(
            self.canvas.zoom_in
        )

        self.toolbar.zoom_out_action.triggered.connect(
            self.canvas.zoom_out
        )

        self.toolbar.zoom_reset_action.triggered.connect(
            self.canvas.reset_zoom
        )

        # Menu bar zoom actions must be connected AFTER the canvas
        # has been created.
        self.app_menu_bar.zoom_out_requested.connect(
            self.canvas.zoom_out
        )

        self.app_menu_bar.zoom_reset_requested.connect(
            self.canvas.reset_zoom
        )

        self.app_menu_bar.zoom_in_requested.connect(
            self.canvas.zoom_in
        )

        self.canvas.box_created.connect(
            self.box_created
        )

        self.canvas.box_changed.connect(
            self.box_changed
        )

        self.canvas.box_delete_requested.connect(
            self.delete_bounding_box
        )

        self.canvas.box_change_class_requested.connect(
            self.change_bounding_box_class
        )

        # =====================================================
        # KEYBOARD SHORTCUTS
        # =====================================================

        self.previous_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.previous_shortcut.setContext(Qt.WindowShortcut)
        self.previous_shortcut.activated.connect(self.previous_image)

        self.next_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.next_shortcut.setContext(Qt.WindowShortcut)
        self.next_shortcut.activated.connect(self.next_image)

        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.delete_shortcut.setContext(Qt.WindowShortcut)
        self.delete_shortcut.activated.connect(self.delete_selected_box)

        self.zoom_in_shortcut = QShortcut(QKeySequence(Qt.Key_Plus), self)
        self.zoom_in_shortcut.setContext(Qt.WindowShortcut)
        self.zoom_in_shortcut.activated.connect(self.canvas.zoom_in)

        self.zoom_out_shortcut = QShortcut(QKeySequence(Qt.Key_Minus), self)
        self.zoom_out_shortcut.setContext(Qt.WindowShortcut)
        self.zoom_out_shortcut.activated.connect(self.canvas.zoom_out)

        self.zoom_reset_shortcut = QShortcut(QKeySequence(Qt.Key_0), self)
        self.zoom_reset_shortcut.setContext(Qt.WindowShortcut)
        self.zoom_reset_shortcut.activated.connect(self.canvas.reset_zoom)

            

        

        # Canvas occupies the main area.
        content_layout.addWidget(
            self.canvas,
            4
        )

        # =====================================================
        # RIGHT: CLASSES + IMAGES ONLY
        # =====================================================

        # One right-side container only.
        # Classes are on top and Images are below.
        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right_layout.setSpacing(8)

        # -----------------------------------------------------
        # CLASSES
        # -----------------------------------------------------

        class_group = QGroupBox(
            "Classes"
        )

        class_layout = QVBoxLayout(
            class_group
        )

        self.class_panel = ClassPanel()

        self.class_panel.setMinimumWidth(
            250
        )

        self.class_panel.delete_requested.connect(
            self.delete_class
        )

        # Draw from Class Panel:
        # the selected class is already known, so NO class popup
        # is shown after drawing.
        self.class_panel.draw_requested.connect(
            self.start_drawing
        )

        class_layout.addWidget(
            self.class_panel
        )

        add_class_button = QPushButton(
            "Add Class"
        )

        add_class_button.clicked.connect(
            self.add_class_dialog
        )

        class_layout.addWidget(
            add_class_button
        )

        right_layout.addWidget(
            class_group,
            1
        )

        # -----------------------------------------------------
        # IMAGES
        # -----------------------------------------------------

        image_group = QGroupBox(
            "Images"
        )

        image_layout = QVBoxLayout(
            image_group
        )

        self.image_list = QListWidget()

        self.image_list.setMinimumWidth(
            250
        )

        self.image_list.currentRowChanged.connect(
            self.image_list_clicked
        )

        image_layout.addWidget(
            self.image_list
        )

        right_layout.addWidget(
            image_group,
            1
        )

        # Add exactly ONE right panel.
        content_layout.addWidget(
            right_panel,
            1
        )

        # Add the complete content layout once.
        main_layout.addLayout(
            content_layout
        )

        # -----------------------------------------------------
        # INITIAL CLASS LIST
        # -----------------------------------------------------

        self.refresh_classes()

        self.statusBar().showMessage(
            "Open an image folder to start"
        )

    # =========================================================
    # OPEN IMAGE FOLDER
    # =========================================================

    def load_classes_yaml(self):
        if not self.current_folder:
            return

        yaml_path = Path(self.current_folder) / "classes.yaml"
        self.classes_yaml_path = yaml_path

        self.class_manager.load_yaml(yaml_path)
        self.refresh_classes()

    def import_classes_yaml(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Classes YAML",
            "",
            "YAML Files (*.yaml *.yml)"
        )
        if not file_path:
            return

        self.classes_yaml_path = Path(file_path)
        self.class_manager.load_yaml(file_path)
        self.refresh_classes()

    def open_folder(self):

        if not self.check_save_before_navigation():
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Image Folder"
        )

        if not folder:
            return

        self.current_folder = Path(folder)
        self.classes_yaml_path = self.current_folder / "classes.yaml"
        self.load_classes_yaml()

        if not folder:
            return

        self.image_manager.load_folder(
            folder
        )

        self.folder_label.setText(
            f"Folder: {folder}"
        )

        self.image_list.clear()

        # -----------------------------------------------------
        # NO IMAGES
        # -----------------------------------------------------

        if not self.image_manager.images:

            self.image_count_label.setText(
                "Images: 0"
            )

            self.current_image_label.setText(
                "Image: 0 / 0"
            )

            self.image_name_label.setText(
                "No image"
            )

            QMessageBox.warning(
                self,
                "No Images",
                "No supported images were found."
            )

            return

        # -----------------------------------------------------
        # ADD IMAGES TO LEFT PANEL
        # -----------------------------------------------------

        for index, image_path in enumerate(
            self.image_manager.images
        ):

            item = QListWidgetItem(
                f"{index + 1}. {image_path.name}"
            )

            item.setToolTip(
                str(image_path)
            )

            self.image_list.addItem(
                item
            )

        # Select first image
        self.image_list.setCurrentRow(
            self.image_manager.index
        )

        self.image_count_label.setText(
            f"Images: {len(self.image_manager.images)}"
        )

        self.load_current_image()

    # =========================================================
    # IMAGE LIST CLICK
    # =========================================================

    def image_list_clicked(self, row):

        if row < 0:
            return

        if row == self.image_manager.index:
            return

        if not self.check_save_before_navigation():
            # Restore previous selection
            self.image_list.blockSignals(True)

            self.image_list.setCurrentRow(
                self.image_manager.index
            )

            self.image_list.blockSignals(False)

            return

        self.image_manager.index = row

        self.load_current_image()

    # =========================================================
    # LOAD CURRENT IMAGE
    # =========================================================

    def load_current_image(self):

        image = self.image_manager.current

        if not image:
            return

        try:

            self.annotation_manager.load_yolo(
                image
            )

            self.dirty = False
            self.drawing_class = None

            self.canvas.enable_drawing(
                False
            )

            self.canvas.reset_zoom()

            loaded = self.canvas.set_image(
                image
            )

            if not loaded:

                QMessageBox.critical(
                    self,
                    "Image Error",
                    f"Could not display image:\n{image}"
                )

                return

            self.refresh_canvas()

            # -------------------------------------------------
            # TOP COUNTER
            # -------------------------------------------------

            current_number = (
                self.image_manager.index + 1
            )

            total = len(
                self.image_manager.images
            )

            self.current_image_label.setText(
                f"Image: {current_number} / {total}"
            )

            self.image_count_label.setText(
                f"Images: {total}"
            )

            self.image_name_label.setText(
                image.name
            )

            # -------------------------------------------------
            # SELECT IMAGE IN LEFT PANEL
            # -------------------------------------------------

            self.image_list.blockSignals(
                True
            )

            self.image_list.setCurrentRow(
                self.image_manager.index
            )

            self.image_list.blockSignals(
                False
            )

            self.statusBar().showMessage(
                f"Image {current_number}/{total}: {image.name}"
            )

            self.update_title()

        except Exception as exc:

            import traceback

            traceback.print_exc()

            QMessageBox.critical(
                self,
                "Image Error",
                f"Error loading image:\n\n"
                f"{image}\n\n"
                f"{type(exc).__name__}: {exc}"
            )

    # =========================================================
    # ADD CLASS
    # =========================================================

    def add_class_dialog(self):

        name, ok = QInputDialog.getText(
            self,
            "Add Class",
            "Class name:"
        )

        if ok and name.strip():

            self.add_class(
                name.strip()
            )

    def add_class(self, name):

        if not self.class_manager.add_class(
            name
        ):

            QMessageBox.warning(
                self,
                "Class",
                "Class already exists or is empty."
            )

            return

        self.refresh_classes()

        if self.classes_yaml_path:
            self.class_manager.save_yaml(
                self.classes_yaml_path
            )

    # =========================================================
    # DELETE CLASS
    # =========================================================

    def delete_class(self, index):

        if index < 0:
            return

        if index >= len(
            self.class_manager.classes
        ):
            return

        class_name = (
            self.class_manager.classes[index]
        )

        result = QMessageBox.question(
            self,
            "Delete Class",
            f"Delete class '{class_name}'?"
        )

        if result != QMessageBox.Yes:
            return

        self.class_manager.delete_class(
            index
        )

        self.refresh_classes()

        if self.classes_yaml_path:
            self.class_manager.save_yaml(
                self.classes_yaml_path
            )

    # =========================================================
    # IMPORT CLASSES FROM TXT
    # =========================================================

    def import_classes_txt(self):

        txt_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Class TXT File",
            "",
            "Text Files (*.txt)"
        )

        if not txt_file:
            return

        try:

            with open(
                txt_file,
                "r",
                encoding="utf-8"
            ) as file:

                lines = file.readlines()

            added = 0

            for line in lines:

                class_name = line.strip()

                # Ignore empty lines
                if not class_name:
                    continue

                # Ignore duplicate classes
                if class_name in self.class_manager.classes:
                    continue

                self.class_manager.classes.append(
                    class_name
                )

                added += 1

            self.refresh_classes()

            # Save imported classes as application's classes.txt
            self.class_manager.save(
                "classes.txt"
            )

            QMessageBox.information(
                self,
                "Import Classes",
                f"Imported {added} class(es)."
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Import Error",
                f"Could not read TXT file:\n\n{exc}"
            )

    # =========================================================
    # REFRESH CLASS LIST
    # =========================================================

    def refresh_classes(self):

        self.class_panel.set_classes(
            self.class_manager.classes
        )

        self.canvas.set_class_names(
            self.class_manager.classes
        )

    # =========================================================
    # START DRAWING
    # =========================================================

    def start_drawing(self, class_id=None):

        # class_id is:
        #   None -> started from toolbar -> show class popup
        #   int  -> started from Class Panel -> use that class directly
        self.drawing_class = class_id

        self.canvas.enable_drawing(
            True
        )

        if class_id is None:
            self.statusBar().showMessage(
                "Draw Bounding Box: click and drag on the image."
            )
        else:
            class_name = (
                self.class_manager.get_class_name(
                    class_id
                )
            )

            self.statusBar().showMessage(
                f"Drawing enabled: {class_name}"
            )

    # =========================================================
    # BOX CREATED
    # =========================================================

    def box_created(
        self,
        center_x,
        center_y,
        width,
        height
    ):

        # If drawing started from the Class Panel, the class is
        # already selected. Save immediately without a popup.
        if self.drawing_class is not None:

            class_id = self.drawing_class

        # If drawing started from the toolbar, ask for a class
        # only after the bounding box is completed.
        else:

            class_id = self.choose_class_for_box()

            if class_id is None:
                self.canvas.enable_drawing(False)
                self.drawing_class = None
                self.refresh_canvas()

                self.statusBar().showMessage(
                    "Bounding box cancelled. No class was selected."
                )

                return

        annotation = Annotation(
            class_id,
            center_x,
            center_y,
            width,
            height
        )

        self.annotation_manager.add(
            annotation
        )

        self.dirty = True

        self.canvas.enable_drawing(
            False
        )

        self.drawing_class = None

        self.refresh_canvas()

        class_name = self.class_manager.get_class_name(
            class_id
        )

        self.statusBar().showMessage(
            f"Bounding box added: {class_name}. Click Save."
        )

    # =========================================================
    # CHOOSE CLASS AFTER DRAWING
    # =========================================================

    def choose_class_for_box(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Class")
        dialog.setMinimumWidth(360)

        layout = QVBoxLayout(dialog)

        label = QLabel(
            "Choose a class for this bounding box:"
        )

        layout.addWidget(label)

        combo = QComboBox()
        combo.addItems(
            self.class_manager.classes
        )

        layout.addWidget(combo)

        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Class")
        cancel_button = QPushButton("Cancel")
        ok_button = QPushButton("Use Class")

        button_layout.addWidget(add_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        def add_class_from_dialog():

            before = list(
                self.class_manager.classes
            )

            self.add_class_dialog()

            after = self.class_manager.classes

            # Add only newly created classes to the combo.
            for name in after:
                if name not in before:
                    combo.addItem(name)
                    combo.setCurrentText(name)
                    break

        add_button.clicked.connect(
            add_class_from_dialog
        )

        cancel_button.clicked.connect(
            dialog.reject
        )

        ok_button.clicked.connect(
            dialog.accept
        )

        if not self.class_manager.classes:
            combo.setEnabled(False)
            ok_button.setEnabled(False)

        if dialog.exec() != QDialog.Accepted:
            return None

        if combo.currentIndex() < 0:
            return None

        return combo.currentIndex()

    # =========================================================
    # SYNCHRONIZE EDITED BOX
    # =========================================================

    def box_changed(
        self,
        index,
        top_left_x,
        top_left_y,
        width,
        height,
        class_id
    ):

        if index < 0 or index >= len(
            self.annotation_manager.annotations
        ):
            return

        annotation = (
            self.annotation_manager.annotations[index]
        )

        # Canvas uses normalized TOP-LEFT coordinates.
        # Annotation/YOLO uses normalized CENTER coordinates.
        annotation.x = top_left_x + (width / 2.0)
        annotation.y = top_left_y + (height / 2.0)
        annotation.width = width
        annotation.height = height
        annotation.class_id = class_id

        self.dirty = True

        self.statusBar().showMessage(
            "Bounding box adjusted. Click Save."
        )

    # =========================================================
    # DELETE SELECTED BOX FROM KEYBOARD
    # =========================================================

    def delete_selected_box(self):

        index = self.canvas.edit_index

        if index < 0:
            return

        if index >= len(self.annotation_manager.annotations):
            return

        self.delete_bounding_box(index)

    # =========================================================
    # DELETE BOUNDING BOX
    # =========================================================

    def delete_bounding_box(self, index):

        if index < 0:
            return

        if index >= len(
            self.annotation_manager.annotations
        ):
            return

        result = QMessageBox.question(
            self,
            "Delete Bounding Box",
            "Delete the selected bounding box?",
            QMessageBox.Yes | QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        self.annotation_manager.remove(
            index
        )

        self.dirty = True

        self.refresh_canvas()

        self.statusBar().showMessage(
            "Bounding box deleted. Click Save."
        )

    # =========================================================
    # CHANGE BOUNDING BOX CLASS
    # =========================================================

    def change_bounding_box_class(self, index):

        if index < 0:
            return

        if index >= len(
            self.annotation_manager.annotations
        ):
            return

        if not self.class_manager.classes:

            QMessageBox.warning(
                self,
                "No Classes",
                "Add or import a class first."
            )

            return

        class_name, ok = QInputDialog.getItem(
            self,
            "Change Class",
            "Select new class:",
            self.class_manager.classes,
            0,
            False
        )

        if not ok:
            return

        new_class_id = (
            self.class_manager.classes.index(
                class_name
            )
        )

        annotation = (
            self.annotation_manager.annotations[index]
        )

        annotation.class_id = new_class_id

        self.dirty = True

        self.refresh_canvas()

        self.statusBar().showMessage(
            f"Class changed to: {class_name}. Click Save."
        )

    # =========================================================
    # REFRESH CANVAS
    # =========================================================

    def refresh_canvas(self):

        boxes = []

        for annotation in (
            self.annotation_manager.annotations
        ):

            boxes.append(
                (
                    annotation.x - annotation.width / 2,
                    annotation.y - annotation.height / 2,
                    annotation.width,
                    annotation.height,
                    annotation.class_id
                )
            )

        self.canvas.set_class_names(
            self.class_manager.classes
        )

        self.canvas.set_boxes(
            boxes
        )

    # =========================================================
    # SAVE
    # =========================================================

    def save_current(self):

        current = self.image_manager.current

        if current is None:
            return

        image_path = Path(current)

        # YOLOv8 detection labels are stored separately
        # from images in a "labels" folder.
        labels_folder = image_path.parent / "labels"
        labels_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        label_path = (
            labels_folder /
            f"{image_path.stem}.txt"
        )

        # Save only YOLOv8 TXT detection format:
        #
        # class_id x_center y_center width height
        #
        # Coordinates are normalized to 0..1.
        # Exactly 9 decimal places are written.
        with open(
            label_path,
            "w",
            encoding="utf-8"
        ) as f:

            for ann in self.annotation_manager.annotations:

                class_id = int(ann.class_id)

                x = max(
                    0.0,
                    min(1.0, float(ann.x))
                )

                y = max(
                    0.0,
                    min(1.0, float(ann.y))
                )

                width = max(
                    0.0,
                    min(1.0, float(ann.width))
                )

                height = max(
                    0.0,
                    min(1.0, float(ann.height))
                )

                f.write(
                    f"{class_id} "
                    f"{x:.9f} "
                    f"{y:.9f} "
                    f"{width:.9f} "
                    f"{height:.9f}\n"
                )

        # Keep classes.yaml for the class list.
        yaml_path = image_path.parent / "classes.yaml"
        self.classes_yaml_path = yaml_path

        self.class_manager.save_yaml(
            yaml_path
        )

        self.dirty = False

        self.statusBar().showMessage(
            f"YOLOv8 label saved: {label_path}"
        )


    # =========================================================
    # SAVE CHECK
    # =========================================================

    def check_save_before_navigation(self):

        if not self.dirty:
            return True

        result = QMessageBox.warning(
            self,
            "Unsaved Changes",
            "You must save the current image before moving to another image.",
            QMessageBox.Save | QMessageBox.Cancel
        )

        if result == QMessageBox.Save:

            self.save_current()

            return not self.dirty

        return False

    # =========================================================
    # NEXT IMAGE
    # =========================================================

    def next_image(self):

        if not self.check_save_before_navigation():
            return

        if self.image_manager.next():

            self.load_current_image()

        else:

            QMessageBox.information(
                self,
                "Images",
                "This is the last image."
            )

    # =========================================================
    # PREVIOUS IMAGE
    # =========================================================

    def previous_image(self):

        if not self.check_save_before_navigation():
            return

        if self.image_manager.previous():

            self.load_current_image()

        else:

            QMessageBox.information(
                self,
                "Images",
                "This is the first image."
            )

    # =========================================================
    # WINDOW TITLE
    # =========================================================

    def update_title(self):
        # Keep the application title fixed.
        # Do not append the current image filename.
        self.setWindowTitle(
            "Image Annotation Tool"
        )


    # =========================================================
    # CLOSE
    # =========================================================

    def closeEvent(self, event):

        if self.check_save_before_navigation():

            event.accept()

        else:

            event.ignore()