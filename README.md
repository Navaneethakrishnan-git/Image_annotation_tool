# Annotation Tool

A simple YOLO-format image annotation tool.

## Workflow

1. Open an image folder.
2. Add a class.
3. Select a class.
4. Right-click the selected class and choose **Draw Bounding Box**.
5. Draw the box on the image.
6. Click **Save**.
7. Only after saving can you move to another image.
8. Right-click a class to add/delete classes or enable drawing.

The rectangle drawing option is intentionally NOT present in the toolbar.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Or run `run.bat`.

## label format

Labels are saved as:

`class_id center_x center_y width height`

Coordinates are normalized between 0 and 1.


## Image loading

The tool supports JPG, JPEG, PNG, BMP, WebP, TIFF and TIF files.
The selected folder is searched recursively.

If an image cannot be loaded, the application shows an Image Error message
with the exact file path.
