from PySide6.QtCore import Qt, QRectF, Signal, QPointF, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QPen,
    QCursor,
)


class AnnotationCanvas(QWidget):
    box_created = Signal(float, float, float, float)
    box_changed = Signal(int, float, float, float, float, int)
    box_delete_requested = Signal(int)
    box_change_class_requested = Signal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(700, 500)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)


        self.pixmap = QPixmap()

        self.draw_enabled = False
        self.dragging = False

        # Mouse position used to draw a full-canvas crosshair
        # while Draw mode is active.
        self.mouse_pos = None

        self.start = QPointF()
        self.end = QPointF()

        # Each item:
        # (x, y, width, height, class_id)
        # x/y are normalized top-left coordinates.
        self.boxes = []

        self.current_box = None

        # Editing
        self.edit_index = -1
        self.edit_mode = None
        self.resize_handle = None
        self.drag_start = QPointF()
        self.original_box = None

        # Large corner handles make resizing easier.
        self.handle_size = 20
        self.handle_hit_size = 52

        # Image pan offset in screen pixels.
        self.pan_x = 0.0
        self.pan_y = 0.0

        # Pan state.
        self.panning = False
        self.pan_start = QPointF()
        self.pan_origin_x = 0.0
        self.pan_origin_y = 0.0
        self.zoom_factor = 1.0

        # Temporary instruction shown when the user tries to
        # draw without activating the Draw option.
        self.warning_text = ""
        self.warning_timer = QTimer(self)
        self.warning_timer.setSingleShot(True)
        self.warning_timer.timeout.connect(
            self._clear_warning
        )

    # =========================================================
    # DRAW WARNING
    # =========================================================

    def show_draw_warning(self):
        self.warning_text = "Please click the Draw option"
        self.warning_timer.start(3000)
        self.update()

    def _clear_warning(self):
        self.warning_text = ""
        self.update()

    # =========================================================
    # IMAGE
    # =========================================================

    def set_image(self, image_path):
        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():
            self.pixmap = QPixmap()
            self.update()
            return False

        self.pixmap = pixmap
        self.current_box = None
        self.edit_index = -1
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.edit_mode = None

        self.update()
        return True

    # =========================================================
    # BOXES
    # =========================================================

    def set_boxes(self, boxes):
        self.boxes = list(boxes)
        self.edit_index = -1
        self.edit_mode = None
        self.update()

    # =========================================================
    # DRAWING
    # =========================================================

    def enable_drawing(self, enabled=True):
        self.draw_enabled = bool(enabled)

        if self.draw_enabled:
            self.setFocus()

            # Hide the normal pointer and use our own visible + cursor.
            self.setCursor(Qt.BlankCursor)

            # Keep the real mouse position. Mouse tracking is enabled,
            # so the crosshair follows the cursor instead of staying
            # at the image center.
            if self.mouse_pos is None:
                self.mouse_pos = self.mapFromGlobal(
                    self.cursor().pos()
                )
        else:
            self.dragging = False
            self.current_box = None
            self.mouse_pos = None
            self.setCursor(Qt.ArrowCursor)

        self.update()


    # =========================================================
    # IMAGE RECT
    # =========================================================

    def _image_rect(self):

        if self.pixmap.isNull():
            return QRectF()

        if self.width() <= 0 or self.height() <= 0:
            return QRectF()

        fit_scale = min(
            self.width() / self.pixmap.width(),
            self.height() / self.pixmap.height()
        )

        scale = fit_scale * self.zoom_factor

        width = self.pixmap.width() * scale
        height = self.pixmap.height() * scale

        x = (self.width() - width) / 2 + self.pan_x
        y = (self.height() - height) / 2 + self.pan_y

        return QRectF(x, y, width, height)

    def zoom_in(self):
        self.zoom_factor = min(5.0, self.zoom_factor * 1.25)
        self.update()

    def zoom_out(self):
        self.zoom_factor = max(0.25, self.zoom_factor / 1.25)
        self.update()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    # =========================================================
    # SCREEN <-> NORMALIZED
    # =========================================================

    def _screen_to_normalized(self, point):
        rect = self._image_rect()

        if rect.isEmpty():
            return 0.0, 0.0

        x = (point.x() - rect.left()) / rect.width()
        y = (point.y() - rect.top()) / rect.height()

        return (
            max(0.0, min(1.0, x)),
            max(0.0, min(1.0, y))
        )

    def _normalized_to_screen(self, x, y):
        rect = self._image_rect()

        return QPointF(
            rect.left() + x * rect.width(),
            rect.top() + y * rect.height()
        )

    def _box_screen_rect(self, box):
        x, y, w, h, class_id = box

        rect = self._image_rect()

        return QRectF(
            rect.left() + x * rect.width(),
            rect.top() + y * rect.height(),
            w * rect.width(),
            h * rect.height()
        )

    # =========================================================
    # PAINT
    # =========================================================

    def paintEvent(self, event):

        painter = QPainter()

        try:
            if not painter.begin(self):
                return

            painter.setRenderHint(
                QPainter.SmoothPixmapTransform
            )

            painter.fillRect(
                self.rect(),
                QColor("#808080")
            )

            if self.pixmap.isNull():
                painter.setPen(Qt.white)
                painter.drawText(
                    self.rect(),
                    Qt.AlignCenter,
                    "Open an image folder"
                )
                return

            image_rect = self._image_rect()

            if image_rect.isEmpty():
                return

            # IMPORTANT: QRect is used for QPixmap drawing.
            painter.drawPixmap(
                image_rect.toRect(),
                self.pixmap
            )

            # Temporary instruction at the top of the image.
            if self.warning_text:
                font = painter.font()
                font.setBold(True)
                font.setPointSize(12)
                painter.setFont(font)

                text_width = (
                    painter.fontMetrics()
                    .horizontalAdvance(self.warning_text)
                    + 32
                )

                warning_rect = QRectF(
                    image_rect.left() + 10,
                    image_rect.top() + 10,
                    min(text_width, image_rect.width() - 20),
                    36
                )

                painter.fillRect(
                    warning_rect,
                    QColor("#333333")
                )

                painter.setPen(
                    QColor("#ffffff")
                )

                painter.drawText(
                    warning_rect,
                    Qt.AlignCenter,
                    self.warning_text
                )

            # Draw all boxes.
            for index, box in enumerate(self.boxes):

                x, y, w, h, class_id = box

                box_rect = self._box_screen_rect(box)

                # NG class = red, all other classes = green.
                # MainWindow can pass a special negative/NG class ID,
                # but the class name is drawn by MainWindow through set_class_names.
                class_name = ""
                if hasattr(self, "class_names"):
                    if 0 <= class_id < len(self.class_names):
                        class_name = self.class_names[class_id]

                is_ng = class_name.strip().lower() == "ng"

                if is_ng:
                    box_color = QColor("#ff2020")
                else:
                    box_color = QColor("#00ff66")

                # Editing does NOT change the class color.
                # NG remains red and other classes keep their normal color.
                painter.setPen(
                    QPen(
                        box_color,
                        3 if index == self.edit_index else 2
                    )
                )

                painter.drawRect(box_rect)

                # Class label above box.
                if class_name:
                    font = painter.font()
                    font.setBold(True)
                    font.setPointSize(10)
                    painter.setFont(font)

                    label_height = 22
                    label_width = max(
                        70,
                        painter.fontMetrics().horizontalAdvance(
                            class_name
                        ) + 12
                    )

                    label_x = box_rect.left()
                    label_y = box_rect.top() - label_height

                    if label_y < image_rect.top():
                        label_y = box_rect.top()

                    label_rect = QRectF(
                        label_x,
                        label_y,
                        label_width,
                        label_height
                    )

                    painter.fillRect(
                        label_rect,
                        box_color
                    )

                    painter.setPen(Qt.white)

                    painter.drawText(
                        label_rect,
                        Qt.AlignCenter,
                        class_name
                    )

                # Resize handles for selected box.
                if index == self.edit_index:
                    self._draw_handles(
                        painter,
                        box_rect,
                        box_color
                    )

            # Temporary drawing rectangle.
            if self.current_box:
                painter.setPen(
                    QPen(
                        QColor("#ffcc00"),
                        2,
                        Qt.DashLine
                    )
                )

                x1, y1, x2, y2 = self.current_box

                painter.drawRect(
                    QRectF(
                        min(x1, x2),
                        min(y1, y2),
                        abs(x2 - x1),
                        abs(y2 - y1)
                    )
                )

            # =====================================================
            # DRAW-MODE CROSSHAIR
            # =====================================================
            # When Draw mode is active, always show full horizontal and
            # vertical guide lines. The red + is exactly at their
            # intersection (the current mouse position).

            if (
                self.draw_enabled
                and self.mouse_pos is not None
                and image_rect.contains(self.mouse_pos)
            ):
                cross_x = self.mouse_pos.x()
                cross_y = self.mouse_pos.y()

                # Full horizontal guide line.
                painter.setPen(
                    QPen(
                        QColor("#ffffff"),
                        1,
                        Qt.SolidLine
                    )
                )
                painter.drawLine(
                    0,
                    int(cross_y),
                    self.width(),
                    int(cross_y)
                )

                # Full vertical guide line.
                painter.drawLine(
                    int(cross_x),
                    0,
                    int(cross_x),
                    self.height()
                )

                # Strong visible + marker at the exact intersection.
                painter.setPen(
                    QPen(
                        QColor("#ffffff"),
                        3,
                        Qt.SolidLine
                    )
                )

                plus_size = 8

                painter.drawLine(
                    int(cross_x - plus_size),
                    int(cross_y),
                    int(cross_x + plus_size),
                    int(cross_y)
                )

                painter.drawLine(
                    int(cross_x),
                    int(cross_y - plus_size),
                    int(cross_x),
                    int(cross_y + plus_size)
                )

        finally:
            if painter.isActive():
                painter.end()

    # =========================================================
    # RESIZE HANDLES
    # =========================================================

    def _draw_handles(self, painter, rect, color):

        painter.setBrush(QColor("#ffffff"))
        painter.setPen(
            QPen(color, 1)
        )

        size = self.handle_size

        points = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
        ]

        for handle_name, point in zip(
            ("tl", "tr", "bl", "br"),
            points
        ):
            # Highlight the handle currently being resized.
            if (
                self.edit_mode == "resize"
                and self.resize_handle == handle_name
            ):
                painter.setBrush(QColor("#ffff00"))
                painter.setPen(
                    QPen(
                        QColor("#ffffff"),
                        3
                    )
                )
                highlight_size = max(
                    self.handle_size + 8,
                    28
                )
            else:
                painter.setBrush(QColor("#ffffff"))
                painter.setPen(
                    QPen(color, 2)
                )
                highlight_size = self.handle_size

            painter.drawEllipse(
                QRectF(
                    point.x() - highlight_size / 2,
                    point.y() - highlight_size / 2,
                    highlight_size,
                    highlight_size
                )
            )

    def _get_resize_handle(self, point, rect):

        size = max(self.handle_hit_size, self.handle_size + 10)

        handles = {
            "tl": QRectF(
                rect.left() - size / 2,
                rect.top() - size / 2,
                size,
                size
            ),
            "tr": QRectF(
                rect.right() - size / 2,
                rect.top() - size / 2,
                size,
                size
            ),
            "bl": QRectF(
                rect.left() - size / 2,
                rect.bottom() - size / 2,
                size,
                size
            ),
            "br": QRectF(
                rect.right() - size / 2,
                rect.bottom() - size / 2,
                size,
                size
            ),
        }

        for name, handle_rect in handles.items():
            if handle_rect.contains(point):
                return name

        return None

    # =========================================================
    # FIND BOX
    # =========================================================

    def _find_box(self, point):

        # Check topmost boxes first.
        # Expand the box slightly so corner handles remain easy to select.
        for index in range(len(self.boxes) - 1, -1, -1):

            rect = self._box_screen_rect(
                self.boxes[index]
            )

            handle = self._get_resize_handle(
                point,
                rect
            )

            if handle:
                return index

            hit_rect = rect.adjusted(
                -8,
                -8,
                8,
                8
            )

            if hit_rect.contains(point):
                return index

        return -1

    # =========================================================
    # MOUSE PRESS
    # =========================================================
    def mousePressEvent(self, event):

        self.setFocus()

        if event.button() != Qt.LeftButton:
            return

        # If Draw mode is OFF, a click on empty image space at normal
        # zoom is treated as an attempt to draw. Show a temporary
        # instruction instead of creating a box.
        if not self.draw_enabled and self.zoom_factor <= 1.0:
            image_rect = self._image_rect()

            if image_rect.contains(event.position()):
                if self._find_box(event.position()) < 0:
                    self.show_draw_warning()
                    self.edit_index = -1
                    self.edit_mode = None
                    self.update()
                    return

        # Drawing mode has priority.
        if self.draw_enabled:

            rect = self._image_rect()

            if not rect.contains(event.position()):
                return

            self.dragging = True
            self.start = event.position()
            self.end = event.position()

            self.current_box = (
                self.start.x(),
                self.start.y(),
                self.end.x(),
                self.end.y()
            )

            return

        # First check if a box was clicked.
        index = self._find_box(event.position())

        if index >= 0:

            # Selecting/editing a box exits Draw mode.
            self.draw_enabled = False
            self.dragging = False
            self.current_box = None
            self.setCursor(Qt.ArrowCursor)

            self.edit_index = index

            box_rect = self._box_screen_rect(
                self.boxes[index]
            )

            handle = self._get_resize_handle(
                event.position(),
                box_rect
            )

            if handle:
                self.edit_mode = "resize"
                self.resize_handle = handle
                # Immediately repaint so the selected corner is highlighted.
                self.update()
            else:
                self.edit_mode = "move"
                self.resize_handle = None

            self.drag_start = event.position()
            self.original_box = list(
                self.boxes[index]
            )

            self.update()
            return

        # Empty image area: left-click + drag = PAN.
        if self.zoom_factor > 1.0:

            self.panning = True
            self.pan_start = event.position()
            self.pan_origin_x = self.pan_x
            self.pan_origin_y = self.pan_y

            self.setCursor(Qt.ClosedHandCursor)

            return

        # At fit zoom, simply deselect.
        self.draw_enabled = False
        self.dragging = False
        self.current_box = None
        self.edit_index = -1
        self.edit_mode = None
        self.setCursor(Qt.ArrowCursor)
        self.update()

    # =========================================================
    # MOUSE MOVE
    # =========================================================

    def mouseMoveEvent(self, event):

        # Track the mouse for the full-length Draw crosshair.
        if self.draw_enabled:
            # event.position() is in canvas/widget coordinates, which
            # keeps the guide lines exactly aligned with the mouse.
            self.mouse_pos = event.position().toPoint()
            self.update()

        # Pan image.
        if self.panning:

            dx = (
                event.position().x()
                - self.pan_start.x()
            )

            dy = (
                event.position().y()
                - self.pan_start.y()
            )

            self.pan_x = self.pan_origin_x + dx
            self.pan_y = self.pan_origin_y + dy

            self.update()

            return

        # Create new box.
        if self.draw_enabled and self.dragging:

            self.end = event.position()

            # Keep the starting + as the top-left corner.
            end_x = max(self.start.x(), self.end.x())
            end_y = max(self.start.y(), self.end.y())

            self.current_box = (
                self.start.x(),
                self.start.y(),
                end_x,
                end_y
            )

            self.update()

            return

        # Edit existing box.
        if self.edit_index < 0:
            return

        if self.edit_mode not in ("move", "resize"):
            return

        dx = (
            event.position().x()
            - self.drag_start.x()
        )

        dy = (
            event.position().y()
            - self.drag_start.y()
        )

        image_rect = self._image_rect()

        if image_rect.isEmpty():
            return

        dx_norm = dx / image_rect.width()
        dy_norm = dy / image_rect.height()

        old_x, old_y, old_w, old_h, class_id = (
            self.original_box
        )

        if self.edit_mode == "move":

            new_x = max(
                0.0,
                min(
                    1.0 - old_w,
                    old_x + dx_norm
                )
            )

            new_y = max(
                0.0,
                min(
                    1.0 - old_h,
                    old_y + dy_norm
                )
            )

            self.boxes[self.edit_index] = (
                new_x,
                new_y,
                old_w,
                old_h,
                class_id
            )

        else:

            left = old_x
            top = old_y
            right = old_x + old_w
            bottom = old_y + old_h

            if self.resize_handle == "tl":
                left += dx_norm
                top += dy_norm

            elif self.resize_handle == "tr":
                right += dx_norm
                top += dy_norm

            elif self.resize_handle == "bl":
                left += dx_norm
                bottom += dy_norm

            elif self.resize_handle == "br":
                right += dx_norm
                bottom += dy_norm

            left = max(0.0, min(1.0, left))
            top = max(0.0, min(1.0, top))
            right = max(0.0, min(1.0, right))
            bottom = max(0.0, min(1.0, bottom))

            min_size = 0.005

            if right - left < min_size:
                if self.resize_handle in ("tl", "bl"):
                    left = max(0.0, right - min_size)
                else:
                    right = min(1.0, left + min_size)

            if bottom - top < min_size:
                if self.resize_handle in ("tl", "tr"):
                    top = max(0.0, bottom - min_size)
                else:
                    bottom = min(1.0, top + min_size)

            self.boxes[self.edit_index] = (
                left,
                top,
                right - left,
                bottom - top,
                class_id
            )

        self.update()

    # =========================================================
    # MOUSE RELEASE
    # =========================================================

    def mouseReleaseEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        if self.panning:

            self.panning = False
            self.setCursor(
                Qt.CrossCursor
                if self.draw_enabled
                else Qt.ArrowCursor
            )

            return

        # New drawing.
        if self.draw_enabled and self.dragging:

            self.dragging = False
            self.end = event.position()

            rect = self._image_rect()

            if rect.isEmpty():
                return

            # The + cursor is the fixed top-left corner.
            # The box grows only right and down.
            x1 = max(
                rect.left(),
                min(self.start.x(), rect.right())
            )

            y1 = max(
                rect.top(),
                min(self.start.y(), rect.bottom())
            )

            x2 = min(
                rect.right(),
                max(self.start.x(), self.end.x())
            )

            y2 = min(
                rect.bottom(),
                max(self.start.y(), self.end.y())
            )

            if x2 - x1 < 5 or y2 - y1 < 5:

                self.draw_enabled = False
                self.dragging = False
                self.current_box = None
                self.mouse_pos = None
                self.setCursor(Qt.ArrowCursor)
                self.update()
                return

            nx1 = (x1 - rect.left()) / rect.width()
            ny1 = (y1 - rect.top()) / rect.height()
            nx2 = (x2 - rect.left()) / rect.width()
            ny2 = (y2 - rect.top()) / rect.height()

            self.box_created.emit(
                (nx1 + nx2) / 2,
                (ny1 + ny2) / 2,
                nx2 - nx1,
                ny2 - ny1
            )

            # One Draw click creates one box.
            # Return to normal cursor after creation.
            self.draw_enabled = False
            self.dragging = False
            self.current_box = None
            self.mouse_pos = None
            self.setCursor(Qt.ArrowCursor)

            self.update()
            return

        # Finish editing and synchronize the edited coordinates with
        # MainWindow / AnnotationManager. The canvas stores top-left
        # coordinates, while YOLO Annotation stores center coordinates.
        if self.edit_index >= 0:

            index = self.edit_index

            if 0 <= index < len(self.boxes):
                x, y, w, h, class_id = self.boxes[index]

                self.box_changed.emit(
                    index,
                    x,
                    y,
                    w,
                    h,
                    class_id
                )

            self.edit_mode = None
            self.resize_handle = None
            self.original_box = None

            self.update()

    # =========================================================
    # RIGHT CLICK ON BOX
    # =========================================================

    def contextMenuEvent(self, event):

        index = self._find_box(
            event.pos()
        )

        if index < 0:
            return

        self.edit_index = index
        self.update()

        menu = QMenu(self)

        change_class_action = menu.addAction(
            "Change Class"
        )

        delete_action = menu.addAction(
            "Delete Bounding Box"
        )

        action = menu.exec(
            self.mapToGlobal(event.pos())
        )

        if action == change_class_action:

            self.box_change_class_requested.emit(
                index
            )

        elif action == delete_action:

            self.box_delete_requested.emit(
                index
            )

    # =========================================================
    # CLASS NAMES
    # =========================================================

    def set_class_names(self, class_names):

        self.class_names = list(
            class_names
        )

        self.update()

    # =========================================================
    # CURSOR
    # =========================================================

    def update_cursor(self, position):

        if self.draw_enabled:
            self.setCursor(Qt.BlankCursor)
            return

        index = self._find_box(position)

        if index < 0:
            if self.zoom_factor > 1.0:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            return

        rect = self._box_screen_rect(
            self.boxes[index]
        )

        handle = self._get_resize_handle(
            position,
            rect
        )

        if handle in ("tl", "br"):
            self.setCursor(Qt.SizeFDiagCursor)

        elif handle in ("tr", "bl"):
            self.setCursor(Qt.SizeBDiagCursor)

        else:
            self.setCursor(Qt.SizeAllCursor)

    def mouseDoubleClickEvent(self, event):
        # Keep double-click available for normal selection/editing.
        if event.button() == Qt.LeftButton:
            self.edit_index = self._find_box(
                event.position()
            )
            self.update()

    def leaveEvent(self, event):
        if not self.dragging:
            self.setCursor(
                Qt.CrossCursor
                if self.draw_enabled
                else Qt.ArrowCursor
            )

        super().leaveEvent(event)