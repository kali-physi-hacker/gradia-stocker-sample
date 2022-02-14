import os
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
import pandas as pd
from ownerships.models import StoneTransfer

from ownerships.forms import GWStoneTransferForm, GiaStoneTransferForm, ExternalStoneTransferForm
from grading.forms import SarineUploadForm, BasicUploadForm
from grading.models import GoldwayVerification, Stone

User = get_user_model()


class p(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.gw_file = open("ownerships/tests/resources/G048RV.csv", "rb")

        self.goldway_user = User.objects.get(username="goldway")
        self.user = User.objects.get(username="kary")

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
            user=self.user,
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
            current_owner = StoneTransfer.most_recent_transfer(item=transfer.item).to_user
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

    def test_form_contains_invoice_number(self):
        self.do_initial_uploads()

        stone_ids = (1, 5, 6)

        form = GWStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.gw_file.name, self.gw_file.read())}
        )
        self.assertTrue(form.is_valid())
        form.save()

        invoice_number = Path("ownerships/tests/resources/G048RV.csv").stem

        expected_goldway_verification = GoldwayVerification.objects.get(invoice_number=invoice_number)

        for stone_id in stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            invoice_number_gw = stone.gw_verification.invoice_number

            self.assertTrue(invoice_number_gw, str())
            self.assertEqual(invoice_number_gw, expected_goldway_verification.invoice_number)

    def test_invoice_number_upload_twice_errors(self):
        """
        Tests that when a csv with a particular invoice number is uploaded twice
        :returns:
        """
        self.do_initial_uploads()
        form = GWStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.gw_file.name, self.gw_file.read())}
        )

        self.assertTrue(form.is_valid())
        form.save()

        gw_file = open("ownerships/tests/resources/G048RV.csv", "rb")
        form = GWStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(gw_file.name, gw_file.read())}
        )
        self.assertFalse(form.is_valid())
        invoice_number = Path("ownerships/tests/resources/G048RV.csv").stem
        self.assertEqual(
            form.errors["file"][0],
            f"Stones with this {invoice_number} invoice number has already been transferred to goldway",
        )


class GiaTransferFormTest(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.gia_file = open("ownerships/tests/resources/gia.csv", "rb")
        self.user = User.objects.get(username="kary")
        self.gia_user = User.objects.get(username="gia")
        self.stone_ids = (1, 5, 6)

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
            user=self.user,
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

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            stone.gw_verification = GoldwayVerification.objects.create(invoice_number=stone_id)
            stone.save()

        form = GiaStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.gia_file.name, self.gia_file.read())}
        )

        self.assertTrue(form.is_valid())

        stone_transfers = form.save()

        # Check here that stones have been transferred to gia
        for transfer in stone_transfers:
            current_owner = StoneTransfer.most_recent_transfer(item=transfer.item).to_user
            self.assertEqual(current_owner, self.gia_user)

        self.assertEqual(len(stone_transfers), 3)

    def test_form_invalid_if_invalid_csv_file(self):
        """
        Tests that form is not valid there is invalid stone id in the csv file
        :returns:
        """
        form = GiaStoneTransferForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.gia_file.name, self.gia_file.read())}
        )

        self.assertFalse(form.is_valid())

        ids = (1, 5, 6)
        for id, (_, error) in zip(ids, form.csv_errors.items()):
            self.assertEqual(error["internal_id"][0], f"Stone With ID `{id}` does not exist")


class ExternalStoneTransferFormTest(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.gia_file = open("ownerships/tests/resources/gia.csv", "rb")
        self.user = User.objects.get(username="kary")
        self.gia_user = User.objects.get(username="gia")

        self.customer = User.objects.create(username="Test")

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
            user=self.user,
            files={"file": SimpleUploadedFile(basic_file.name, basic_file.read())},
        )
        form.is_valid()
        form.save()

    def test_form_is_valid_if_valid_csv_file(self):
        """
        Tests that form is valid if valid csv
        :returns:
        """
        self.do_initial_uploads()
        form = ExternalStoneTransferForm(
            data={"customer": self.customer.pk},
            user=self.user,
            files={"file": SimpleUploadedFile(self.gia_file.name, self.gia_file.read())},
        )
        self.assertTrue(form.is_valid())

        stone_transfers = form.save()

        for transfer in stone_transfers:
            current_owner = StoneTransfer.most_recent_transfer(item=transfer.item).to_user
            self.assertEqual(current_owner, self.customer)

    def test_form_invalid_if_invalid_csv_file(self):
        """
        Tests that  form is invalid if there is/are invalid stone ids in the csv file
        """
        form = ExternalStoneTransferForm(
            data={"customer": self.customer.pk},
            user=self.user,
            files={"file": SimpleUploadedFile(self.gia_file.name, self.gia_file.read())},
        )

        self.assertFalse(form.is_valid())

        ids = (1, 5, 6)
        for id, (_, error) in zip(ids, form.csv_errors.items()):
            self.assertEqual(error["internal_id"][0], f"Stone With ID `{id}` does not exist")
