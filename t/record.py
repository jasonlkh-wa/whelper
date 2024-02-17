from whelper import raisels
import types


class Record:
    pass


# CR: add set_* method, and change all field to _field
def create_record_type(
    record: dict[str, type | set],
    type_caster_dict: dict | None = None,
):
    doc_string = ",\n\t".join([f"{k}: {type_t}" for k, type_t in record.items()])

    class _Record(Record):
        __doc__ = f"""{doc_string}"""
        RECORD = record
        TYPE_CASTER_DICT = type_caster_dict if type_caster_dict is not None else dict()

        def __init__(self, **kwargs):
            self._init_with_type_enforced(**kwargs)

        def __setattr__(self, name, value, allowed=False):
            # To block any assignment after [__init__]
            if not allowed:
                raisels(
                    AttributeError,
                    "Direct attribute asisgnment is not allowed\n"
                    "Use setter methods or create a new record instead",
                )

            # set [set_*] method
            if name.startswith("set_") and name.removeprefix("set_") in self.RECORD:
                super().__setattr__(name, value)
                return None

            try:
                type_t = self.RECORD[name]
            except KeyError:
                # RECORD and TYPE_CASTER_DICT should not be set after initialized
                raisels(
                    AttributeError,
                    f"Attribute [{name}] is not found in {self.RECORD}",
                )

            # If type_t is a set of values, set the attribute if [value] is in [type_t]
            if isinstance(type_t, set):
                if value in type_t:
                    super().__setattr__(name, value)
                    return None
                else:
                    return TypeError(
                        f"Value [{value}] is not one of the variants:\n\n{type_t}"
                    )

            # Set the attribute if [value] matches [type_t]
            if isinstance(value, type_t):
                super().__setattr__(name, value)
                return None

            # Try to convert [value] to [type_t] and set the attribute
            try:
                super().__setattr__(
                    name,
                    self.TYPE_CASTER_DICT.get(name, type_t)(value),
                )
                return None
            except (TypeError, ValueError):
                return TypeError(f"Expected {type_t} for {value}, got {type(value)}")

        def setattr(self, name, value):
            return self.__setattr__(name, value, allowed=True)

        def create_set_methods(self, name):
            def set_method(self, value):
                return self.setattr(name, value)

            # CR-someday: this is forcing python to recognize it as method
            # think of an alternative way
            return types.MethodType(set_method, self)

        def _init_with_type_enforced(self, **kwargs):
            if not self.RECORD.keys() == kwargs.keys():
                raisels(
                    TypeError,
                    f"Expected:\n{self.RECORD.keys()}\n\ngot:\n{kwargs.keys()}",
                )
            for name, value in kwargs.items():
                error = self.setattr(name, value)
                if error is not None:
                    raisels(type(error), str(error))
                print(name)
                self.setattr(f"set_{name}", self.create_set_methods(name))

        def to_dict(self):
            return {k: getattr(self, k) for k in self.RECORD.keys()}

        def __repr__(self):
            class_name = self.__class__.__name__
            body = ",\n\t".join(
                [f"{k}: {getattr(self, k)}" for k in self.RECORD.keys()]
            )
            return f"{class_name} = {{\n\t{body}\n}}".expandtabs(4)

    return _Record
