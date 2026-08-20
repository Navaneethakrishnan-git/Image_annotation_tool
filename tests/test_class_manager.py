from app.core.class_manager import ClassManager

def test_add_class():
    cm = ClassManager()
    assert cm.add_class("car")
    assert not cm.add_class("car")
    assert cm.classes == ["car"]
