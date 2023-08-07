def get_id_to_column_name(fields):
    id_to_column_name = {}
    for field in fields:
        field_id = "{}".format(field.get("id"))
        field_label = field.get("label")
        id_to_column_name[field_id] = field_label
    return id_to_column_name


def replace_id_with_column_names(id_to_column_name, row):
    row_with_column_names = {}
    for field in row:
        column_name = id_to_column_name.get(field, field)
        row_with_column_names[column_name] = extract_value(row.get(field))
    return row_with_column_names


def extract_value(record):
    return record.get("value", record)


class RecordsLimit():
    def __init__(self, records_limit=-1):
        self.has_no_limit = (records_limit == -1)
        self.records_limit = records_limit
        self.counter = 0

    def is_reached(self):
        if self.has_no_limit:
            return False
        self.counter += 1
        return self.counter > self.records_limit
