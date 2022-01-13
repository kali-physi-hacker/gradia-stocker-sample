from django.core.management import BaseCommand, CommandError
import csv

from grading.models import Stone


class Command(BaseCommand):
    description = "Management command to overwrite the external_ids of a bunch of stones"

    def add_arguments(self, parser):
        """
        Add arguments
        :param parser:
        :return:
        """
        parser.add_argument("-f", "--file", required=True, help="csv file path")

    def handle(self, *args, **options):
        """
        Overwrite the `external_id`s of a list of stones
        :param args:
        :param options:
        :return:
        """
        csv_file_path = options["file"].strip()
        try:
            csv_file = open(csv_file_path)
        except FileNotFoundError:
            raise CommandError(f"file path: {options['file']} does not exist")

        content = csv.reader(csv_file)
        header = [head.strip() for head in next(content)]

        assert "internal_id" in header, "`internal_id` is a required csv header"
        assert "external_id" in header, "`external_id` is a required csv header"

        rows = []
        for row in content:
            rows.append(row)

        internal_id_index = header.index("internal_id")
        external_id_index = header.index("external_id")

        data_dict = {row[internal_id_index]: row[external_id_index] for row in rows}

        invalid_internal_ids = []

        for internal_id in data_dict:
            try:
                Stone.objects.get(internal_id=internal_id)
            except Stone.DoesNotExist:
                invalid_internal_ids.append(internal_id)

        if len(invalid_internal_ids) > 0:
            raise CommandError(
                "Stones with the following internal_ids do not exist:\n" + "\n".join(invalid_internal_ids)
            )
        internal_id_external_id_map_list = []

        for internal_id, external_id in data_dict.items():
            stone = Stone.objects.get(internal_id=internal_id)
            stone.external_id = external_id
            stone.save()
            internal_id_external_id_map_list.append(f"{internal_id} ===> {external_id}")

        self.stdout.write(
            self.style.SUCCESS(
                "Stone external_id updated successfully:" + "\n".join(internal_id_external_id_map_list)
            )
        )
