from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase

from ownerships.forms import GWStoneTransferForm
from grading.forms import SarineUploadForm, BasicUploadForm

User = get_user_model()


class GWStoneTransferFormTest(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.gw_file = open("ownerships/tests/resources/gw.csv", "rb")

        self.goldway_user = User.objects.create_user(username="goldway", password="goldway")
        self.user = created_by_user = User.objects.get(username="kary")

    def do_initial_uploads(self):
        # Do Sarine upload
        sarine_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        form = SarineUploadForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(sarine_file.name, sarine_file.read())}
        )
        form.is_valid()
        form.save()

        # Do basic upload
        basic_file = open("grading/tests/fixtures/basic-01.csv", "rb")
        form = BasicUploadForm(
            data={},
            files={"file": SimpleUploadedFile(basic_file.name, basic_file.read())},
        )
        form.is_valid()
        form.save()

    def test_form_is_valid_if_valid_csv_file(self):
        """
        Tests that form is valid if all stone ids in the csv file exist
        :returns:  ===> convention in python ==> snake_case
        """
        self.do_initial_uploads()

        form = GWStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.gw_file.name, self.gw_file.read())}
        )

        # import pdb; pdb.set_trace()
        self.assertTrue(form.is_valid())

        stone_transfers = form.save()

        # Check here that stones have been transferred to gw
        for transfer in stone_transfers:
            current_owner = transfer.item.stonetransfer_set.last().to_user
            self.assertEqual(current_owner, self.goldway_user)

        self.assertEqual(len(stone_transfers), 3)

    def test_form_invalid_if_invalid_csv_file(self):
        """
        Tests that form is not valid there is invalid stone id in the csv file
        :returns:
        """
        form = GWStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.gw_file.name, self.gw_file.read())}
        )

        self.assertFalse(form.is_valid())

        ids = (1, 5, 6)
        for id, (_, error) in zip(ids, form.csv_errors.items()):
            self.assertEqual(error["internal_id"][0], f"Stone With ID `{id}` does not exist")
