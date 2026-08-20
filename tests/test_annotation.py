from app.models.annotation import Annotation

def test_yolo_format():
    a = Annotation(1, 0.5, 0.5, 0.2, 0.3)
    assert a.to_yolo() == "1 0.500000 0.500000 0.200000 0.300000"
