from dataiku.connector import Connector
from quickbase_client import QuickBaseSession
from quickbase_commons import get_id_to_column_name, replace_id_with_column_names, RecordsLimit


class QuickBaseConnector(Connector):

    def __init__(self, config, plugin_config):
        Connector.__init__(self, config, plugin_config)

        self.session = QuickBaseSession(config)
        self.query_from = config.get("query_from")

    def get_read_schema(self):
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                      partition_id=None, records_limit=-1):
        limit = RecordsLimit(records_limit)
        query = {}
        if self.query_from:
            query["from"] = self.query_from

        number_of_records_to_skip = 0
        while self.session.has_more_data():
            if number_of_records_to_skip > 0:
                query["options"] = {"skip": number_of_records_to_skip}
            rows, fields, _ = self.session.post("https://api.quickbase.com/v1/records/query", json=query)
            id_to_column_name = get_id_to_column_name(fields)
            number_of_records_to_skip += len(rows)

            for row in rows:
                yield replace_id_with_column_names(id_to_column_name, row)
                if limit.is_reached():
                    return

    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                   partition_id=None):
        raise NotImplementedError

    def get_partitioning(self):
        raise NotImplementedError

    def list_partitions(self, partitioning):
        return []

    def partition_exists(self, partitioning, partition_id):
        raise NotImplementedError

    def get_records_count(self, partitioning=None, partition_id=None):
        raise NotImplementedError


class CustomDatasetWriter(object):
    def __init__(self):
        pass

    def write_row(self, row):
        """
        Row is a tuple with N + 1 elements matching the schema passed to get_writer.
        The last element is a dict of columns not found in the schema
        """
        raise NotImplementedError

    def close(self):
        pass
