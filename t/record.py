from whelper import printls


def create_record_type(record: dict[str, type], type_enforced=True):
    doc_string = ",\n\t".join([f"{k}: {type_t}" for k, type_t in record.items()])

    class Record:
        __doc__ = f"""{doc_string}"""

        def __init__(self, **kwargs):
            self.record = record
            if type_enforced:
                self._init_with_type_enforced(**kwargs)
            else:
                for k, type_t in record.items():
                    setattr(self, k, kwargs[k])

        def _init_with_type_enforced(self, **kwargs):
            if not record.keys() == kwargs.keys():
                raise TypeError(f"expected:\n{record.keys()}\n\ngot:\n{kwargs.keys()}")
            for k, type_t in record.items():
                if isinstance(type_t, set):
                    if kwargs[k] in type_t:
                        setattr(self, k, kwargs[k])
                    else:
                        raise TypeError(
                            f"Value [{kwargs[k]}] is not one of the variants:\n\n{type_t}"
                        )
                elif isinstance(kwargs[k], type_t):
                    setattr(self, k, kwargs[k])
                else:
                    try:
                        setattr(self, k, type_t(kwargs[k]))
                    except ValueError:
                        printls(f"Expected {type_t} for {k}, got {type(kwargs[k])}")
                        raise TypeError("Unexpected field type")

        def __str__(self):
            class_name = self.__class__.__name__
            return f"{class_name} = {{\n\t{doc_string}\n\t}}".expandtabs(4)

    return Record
