def get_model_fields(model):
    return model._meta.fields


def get_field_names(fields):
    return [str(field).split(".")[2] for field in fields]
