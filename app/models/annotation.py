from dataclasses import dataclass

@dataclass
class Annotation:
    class_id: int
    x: float
    y: float
    width: float
    height: float

    def to_yolo(self) -> str:
        return (
            f"{self.class_id} "
            f"{self.x:.6f} {self.y:.6f} "
            f"{self.width:.6f} {self.height:.6f}"
        )
