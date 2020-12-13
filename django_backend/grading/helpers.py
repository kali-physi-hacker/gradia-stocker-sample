def get_stone_fields(model):
    fields = model._meta.fields
    return [str(field).split(".")[2] for field in fields]


def column_tuple_to_value_tuple_dict_map(column, values):
    assert len(column) == len(values), "Column tuple must be of the same length as Values"

    dict_map = {}

    for index, col in enumerate(column):
        dict_map[col] = values[index]

    return dict_map


def get_field_names_snake_case(model):
    """
    Return a tuple of field names of a model in snake case
    :param model:
    :return:
    """
    fields = (field.verbose_name for field in model._meta.fields)
    fields_snake_case = tuple("_".join(field.split(" ")) for field in fields)
    return fields_snake_case
