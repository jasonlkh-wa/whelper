from whelper import raisels


class Record:
    pass


# CR: add set_* method, and change all field to _field
def create_record_type(
    record: dict[str, type | set],
    type_enforced=True,
    type_caster_dict: dict | None = None,
):
    doc_string = ",\n\t".join([f"{k}: {type_t}" for k, type_t in record.items()])

    class _Record(Record):
        __doc__ = f"""{doc_string}"""
        RECORD = record

        def __init__(self, **kwargs):
            if type_enforced:
                self.type_caster_dict = (
                    type_caster_dict if type_caster_dict is not None else dict()
                )

                self._init_with_type_enforced(**kwargs)
            else:
                for k in self.RECORD.keys():
                    setattr(self, k, kwargs[k])

        def _init_with_type_enforced(self, **kwargs):
            if not self.RECORD.keys() == kwargs.keys():
                raisels(
                    TypeError,
                    f"Expected:\n{self.RECORD.keys()}\n\ngot:\n{kwargs.keys()}",
                )
            for k, type_t in self.RECORD.items():
                if isinstance(type_t, set):
                    if kwargs[k] in type_t:
                        setattr(self, k, kwargs[k])
                    else:
                        raisels(
                            TypeError,
                            f"Value [{kwargs[k]}] is not one of the variants:\n\n{type_t}",
                        )

                elif isinstance(kwargs[k], type_t):
                    setattr(self, k, kwargs[k])

                else:
                    try:
                        setattr(
                            self, k, self.type_caster_dict.get(k, type_t)(kwargs[k])
                        )
                    except (TypeError, ValueError):
                        raisels(
                            TypeError,
                            f"Expected {type_t} for {k}, got {type(kwargs[k])}",
                        )

        def to_dict(self):
            return {k: getattr(self, k) for k in self.RECORD.keys()}

        def __repr__(self):
            class_name = self.__class__.__name__
            body = ",\n\t".join(
                [
                    f"{k}: {v}"
                    for k, v in self.__dict__.items()
                    if k not in {"type_caster_dict"}
                ]
            )
            return f"{class_name} = {{\n\t{body}\n}}".expandtabs(4)

    return _Record
