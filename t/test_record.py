from . import create_record_type


def test_create_record_type_success():
    # Testing creation of record type with correct input
    assert create_record_type({"a": int, "b": str})


def test_create_record_type_with_type_enforced():
    # Testing creation of record type with type enforcement
    Type = create_record_type({"a": int, "b": str})
    try:
        Type(a="A", b="2")
    except TypeError:
        assert True
        return None
    print("Expected TypeError not raised")
    assert False


def test_create_record_type_without_type_enforced():
    Type = create_record_type({"a": int, "b": str}, type_enforced=False)
    assert Type(a="A", b="2")


def test_create_record_type_print():
    Type = create_record_type({"a": int, "b": str})
    assert (
        str(Type(a=1, b="2"))
        == """Record = {
    a: <class 'int'>,
    b: <class 'str'>
    }"""
    )
