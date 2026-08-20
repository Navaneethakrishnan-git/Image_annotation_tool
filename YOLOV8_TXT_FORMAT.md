# YOLOv8 TXT Annotation Format

This tool saves object-detection annotations as YOLO-compatible TXT files.

For each image:

    image001.jpg
    labels/image001.txt

Each annotation line is:

    class_id x_center y_center width height

All four coordinates are normalized between 0 and 1.

The tool writes exactly 9 decimal places.

Example:

    0 0.512345678 0.423456789 0.234567890 0.345678901
    1 0.723456789 0.612345678 0.123456789 0.234567890

No XML, JSON, CSV, or other annotation format is generated.
