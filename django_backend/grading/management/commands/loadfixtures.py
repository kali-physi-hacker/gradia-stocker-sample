from django.core.management.base import BaseCommand
from django.core.management import call_command

from stonegrading.fixtures import inclusion_fixtures


class Command(BaseCommand):
    help = "Load fixture in the db"

    def handle(self, *args, **kwargs):
        """
        Load user fixture and inclusion fixtures in the db
        :param args:
        :param kwargs:
        :returns:
        """
        # Load user fixtures
        call_command("loaddata", "deploy_fixtures.json")  # ==> python manage.py loaddata deploy_fixtures.json()

        # Load inclusions
        try:
            inclusion_fixtures()  # Creates inclusions in the db
        except:
            pass

        # Show success message
        self.stdout.write(self.style.SUCCESS("Fixtures loaded successfully"))
