def get_model_fields(model):
    return model._meta.fields


def get_field_names(fields):
    return [str(field).split(".")[2] for field in fields]


class CSVManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()
