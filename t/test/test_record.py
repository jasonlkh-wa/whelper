import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from record import create_record_type, Record
from whelper import printls

SampleClass = create_record_type({"a": int, "b": str})
sample_instance = SampleClass(a=1, b="2")


# Testing creation of record type with correct input
def test_create_record_type_success():
    assert issubclass(SampleClass, Record)
    assert isinstance(sample_instance, Record)


def test_record_type_attributes_and_method():
    expect_keys = {"a", "b", "set_a", "set_b"}
    assert set(sample_instance.__dict__.keys()) == expect_keys


# Testing creation of record type with type enforcement
def test_create_record_type_with_wrong_type():
    try:
        SampleClass(a="A", b="2")
    except TypeError:
        assert True
        return None
    printls("Expected TypeError not raised")
    assert False


def test_record_repr():
    assert (
        str(SampleClass(a=1, b="2"))
        == """_Record = {
    a: 1,
    b: 2
}"""
    )


def test_block_direct_assignment():
    try:
        sample_instance.a = "A"
    except AttributeError:
        assert True
        return None
    printls(
        "Expected AttributeError not raised, the class should block direct assignment"
    )
    assert False


def test_set_attribute():
    sample_instance = SampleClass(a=1, b="2")
    sample_instance.set_a(3)
    assert sample_instance.a == 3


def test_set_attribute_with_wrong_type():
    error = sample_instance.set_a("b")

    assert isinstance(error, TypeError)
    assert str(error) == "Expected <class 'int'> for b, got <class 'str'>"
