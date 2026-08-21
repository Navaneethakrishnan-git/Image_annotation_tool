from pathlib import Path
import yaml


class ClassManager:
    """
    Manages annotation classes.

    YAML format:

        nc: 2
        names: ['human', 'tyer-count2']
    """

    def __init__(self):
        self.classes = []
        self.yaml_path = None

    # =========================================================
    # YAML - LOAD
    # =========================================================

    def load_yaml(self, yaml_path):

        self.yaml_path = Path(yaml_path)

        if not self.yaml_path.exists():
            self.classes = []
            return

        try:

            with open(
                self.yaml_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = yaml.safe_load(file) or {}

            names = data.get(
                "names",
                []
            )

            # Support:
            #
            # names:
            #   0: human
            #   1: car
            #
            if isinstance(names, dict):

                names = [
                    names[key]
                    for key in sorted(
                        names,
                        key=lambda value:
                            int(value)
                            if str(value).isdigit()
                            else str(value)
                    )
                ]

            self.classes = [
                str(name).strip()
                for name in names
                if str(name).strip()
            ]

        except Exception as error:

            print(
                f"Error loading classes.yaml: {error}"
            )

            self.classes = []

    # =========================================================
    # YAML - SAVE
    # =========================================================

    def save_yaml(self, yaml_path=None):

        if yaml_path is not None:

            self.yaml_path = Path(
                yaml_path
            )

        if self.yaml_path is None:
            return

        self.yaml_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # YOLO dataset YAML format
        data = {
            "nc": len(self.classes),
            "names": self.classes
        }

        with open(
            self.yaml_path,
            "w",
            encoding="utf-8"
        ) as file:

            # default_flow_style=True makes:
            #
            # names: ['human', 'car']
            #
            # instead of:
            #
            # names:
            # - human
            # - car

            yaml.safe_dump(
                data,
                file,
                sort_keys=False,
                default_flow_style=True,
                allow_unicode=True
            )

    # =========================================================
    # ADD CLASS
    # =========================================================

    def add_class(self, name):

        name = str(name).strip()

        if not name:
            return False

        if name in self.classes:
            return False

        self.classes.append(name)

        # Automatically update YAML
        self.save_yaml()

        return True

    # =========================================================
    # ADD CLASS - ALIAS
    # =========================================================

    def add(self, name):

        name = str(name).strip()

        if not name:
            return -1

        if name in self.classes:

            return self.classes.index(
                name
            )

        self.classes.append(name)

        self.save_yaml()

        return len(self.classes) - 1

    # =========================================================
    # DELETE CLASS
    # =========================================================

    def delete_class(self, index):

        if (
            index < 0
            or index >= len(self.classes)
        ):
            return False

        self.classes.pop(index)

        # Automatically update YAML
        self.save_yaml()

        return True

    # =========================================================
    # DELETE CLASS - ALIAS
    # =========================================================

    def remove(self, index):

        return self.delete_class(
            index
        )

    # =========================================================
    # CLASS INDEX
    # =========================================================

    def index(self, name):

        try:

            return self.classes.index(
                name
            )

        except ValueError:

            return -1

    # =========================================================
    # GET CLASS NAME
    # =========================================================

    def get_class_name(self, class_id):

        if (
            0 <= class_id
            < len(self.classes)
        ):

            return self.classes[
                class_id
            ]

        return ""

    # =========================================================
    # GET CLASS ID
    # =========================================================

    def get_class_id(self, name):

        return self.index(
            name
        )

    # =========================================================
    # OLD LOAD COMPATIBILITY
    # =========================================================

    def load(self, file_path):

        path = Path(
            file_path
        )

        if path.suffix.lower() in (
            ".yaml",
            ".yml"
        ):

            self.load_yaml(
                path
            )

            return

        if not path.exists():

            self.classes = []

            return

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            self.classes = [
                line.strip()
                for line in file
                if line.strip()
            ]

    # =========================================================
    # OLD SAVE COMPATIBILITY
    # =========================================================

    def save(self, file_path):

        path = Path(
            file_path
        )

        if path.suffix.lower() in (
            ".yaml",
            ".yml"
        ):

            self.save_yaml(
                path
            )

            return

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            for name in self.classes:

                file.write(
                    f"{name}\n"
                )