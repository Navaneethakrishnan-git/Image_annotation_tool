from pathlib import Path
from app.models.annotation import Annotation


class AnnotationManager:

    def __init__(self):
        self.annotations = []

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self):
        self.annotations.clear()

    # =========================================================
    # ADD
    # =========================================================

    def add(self, annotation: Annotation):
        self.annotations.append(annotation)

    # =========================================================
    # REMOVE
    # =========================================================

    def remove(self, index: int):
        if 0 <= index < len(self.annotations):
            self.annotations.pop(index)

    # =========================================================
    # GET LABEL PATH
    # =========================================================

    def get_label_path(self, image_path):
        """
        YOLOv8 labels are stored in a separate labels folder.

        Example:

        images/
            image001.jpg
            image002.jpg
            labels/
                image001.txt
                image002.txt
        """

        image_path = Path(image_path)

        labels_folder = image_path.parent / "labels"

        return labels_folder / f"{image_path.stem}.txt"

    # =========================================================
    # SAVE YOLO
    # =========================================================

    def save_yolo(self, image_path):
        """
        Save annotations in YOLOv8 TXT format.

        Format:

        class_id x_center y_center width height

        Example:

        0 0.523456789 0.412345678 0.120000000 0.250000000
        """

        label_path = self.get_label_path(image_path)

        # Create labels folder automatically
        label_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            label_path,
            "w",
            encoding="utf-8"
        ) as f:

            for ann in self.annotations:

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

        return label_path

    # =========================================================
    # LOAD YOLO
    # =========================================================

    def load_yolo(self, image_path):
        """
        Load YOLOv8 annotations from:

        image_folder/labels/image_name.txt
        """

        # Important:
        # Clear old image annotations first.
        self.clear()

        label_path = self.get_label_path(image_path)

        # No label file = image has no annotations
        if not label_path.exists():
            return

        try:

            lines = label_path.read_text(
                encoding="utf-8"
            ).splitlines()

        except Exception:
            return

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            # YOLOv8:
            # class x_center y_center width height

            if len(parts) != 5:
                continue

            try:

                cid = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])

                annotation = Annotation(
                    cid,
                    x,
                    y,
                    w,
                    h
                )

                self.annotations.append(
                    annotation
                )

            except (ValueError, TypeError):
                continue