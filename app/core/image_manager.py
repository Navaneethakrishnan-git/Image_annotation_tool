from pathlib import Path

SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

class ImageManager:
    def __init__(self):
        self.images = []
        self.index = -1
        self.folder = None

    def load_folder(self, folder):
        self.folder = Path(folder).resolve()

        # Search the selected folder and its subfolders.
        self.images = sorted(
            [
                p for p in self.folder.rglob("*")
                if p.is_file() and p.suffix.lower() in SUPPORTED
            ],
            key=lambda p: str(p).lower()
        )

        self.index = 0 if self.images else -1

    @property
    def current(self):
        if 0 <= self.index < len(self.images):
            return self.images[self.index]
        return None

    def next(self):
        if self.index + 1 < len(self.images):
            self.index += 1
            return self.current
        return None

    def previous(self):
        if self.index > 0:
            self.index -= 1
            return self.current
        return None
