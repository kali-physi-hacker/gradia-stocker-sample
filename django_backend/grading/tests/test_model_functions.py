from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from grading.models import Stone
from grading.forms import (
    SarineUploadForm,
    BasicUploadForm,
    GWGradingUploadForm,
    GIAUploadForm,
    GWAdjustingUploadForm,
    GIAAdjustingUploadForm,
)

from ownerships.models import StoneTransfer


User = get_user_model()


class StoneModelTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.grader = User.objects.get(username="tanly")
        self.split_user = User.objects.get(username="split")
        self.goldway_user = User.objects.get(username="goldway")
        self.gia_user = User.objects.get(username="gia")
        self.vault_manager = User.objects.get(username="vault")

        self.stone_ids = (1, 5, 6)

    def transfer_stones(self, to_user, from_user):
        """
        Transfer stones
        :param to_user:
        :param from_user:
        :return:
        """
        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            StoneTransfer.initiate_transfer(item=stone, from_user=from_user, to_user=to_user, created_by=self.grader)
            StoneTransfer.confirm_received(item=stone)

    def upload_sarine_grading_results(self):
        """
        Uploads sarine data
        :return:
        """
        with open("grading/tests/fixtures/sarine-01.csv", "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read())

        form = SarineUploadForm(data={}, files={"file": uploaded_file}, user=self.grader)
        self.assertTrue(form.is_valid())
        form.save()

    def upload_basic_grading_results(self):
        """
        Upload basic grading results
        :return:
        """
        with open("grading/tests/fixtures/basic-01.csv", "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read())

        form = BasicUploadForm(data={}, files={"file": uploaded_file}, user=self.grader)
        self.assertTrue(form.is_valid())
        form.save()

    def upload_goldway_grading_results(self):
        """
        Upload goldway grading results
        :return:
        """
        with open("grading/tests/fixtures/gold_way-01.csv", "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read())

        form = GWGradingUploadForm(data={}, files={"file": uploaded_file}, user=self.grader)
        self.transfer_stones(from_user=self.split_user, to_user=self.goldway_user)
        self.assertTrue(form.is_valid())
        form.save()

    def upload_goldway_adjusting_grading_results(self):
        """
        Upload goldway adjusting grading results
        :return:
        """
        with open("grading/tests/fixtures/gw_adjust.csv", "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read())

        form = GWAdjustingUploadForm(data={}, files={"file": uploaded_file})
        self.assertTrue(form.is_valid())
        form.save()

    def upload_gia_grading_results(self):
        """
        Upload gia grading results
        :return:
        """
        with open("grading/tests/fixtures/gia.csv", "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read())

        form = GIAUploadForm(data={}, files={"file": uploaded_file}, user=self.grader)

        self.transfer_stones(from_user=self.vault_manager, to_user=self.gia_user)
        self.assertTrue(form.is_valid())
        form.save()

    def upload_gia_adjusting_grading_results(self):
        """
        Upload gia adjusting grading results
        :return:
        """
        with open("grading/tests/fixtures/gia_adjusting.csv", "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read())

        form = GIAAdjustingUploadForm(
            data={},
            files={"file": uploaded_file},
        )

        self.assertTrue(form.is_valid())
        form.save()

    def test_is_sarine_grading_complete(self):
        """
        Tests that is_sarine_grading_complete returns True
        :return:
        """
        self.upload_sarine_grading_results()
        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertTrue(stone.is_sarine_grading_complete)

    def test_is_basic_grading_complete(self):
        """
        Tests that is_basic_grading_complete returns True if basic grading results
        have been uploaded and returns False otherwise
        :return:
        """
        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.is_basic_grading_complete)

        self.upload_basic_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertTrue(stone.is_basic_grading_complete)

    def test_is_goldway_grading_complete(self):
        """
        Tests that is_goldway_grading_complete returns True if goldway grading results
        have been uploaded and returns False otherwise
        :return:
        """
        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.is_goldway_grading_complete)

        self.upload_goldway_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertTrue(stone.is_goldway_grading_complete)

    def test_is_goldway_grading_complete_returns_false(self):
        """
        Tests that is_goldway_grading_complete returns False if
        stone has been transferred to goldway but has not completed
        goldway grading
        :return:
        """
        self.upload_sarine_grading_results()

        stones = [Stone.objects.get(internal_id=internal_id) for internal_id in self.stone_ids]

        for stone in stones:
            self.assertFalse(stone.is_goldway_grading_complete)

        vault = User.objects.get(username="vault")
        split = User.objects.get(username="split")
        goldway = User.objects.get(username="goldway")
        tanly = User.objects.get(username="tanly")

        # transfer to vault
        for stone in stones:
            StoneTransfer.initiate_transfer(item=stone, from_user=split, to_user=vault, created_by=tanly)
            StoneTransfer.confirm_received(item=stone)

        # transfer to goldway
        for stone in stones:
            StoneTransfer.initiate_transfer(item=stone, from_user=vault, to_user=goldway, created_by=tanly)

        # check that is_grading_complete should still be False
        for stone in stones:
            self.assertFalse(stone.is_goldway_grading_complete)

    def test_is_gia_grading_complete_returns_false(self):
        """
        Test that is_gia_grading_complete return False if
        stone has been transferred to gia but has not completed
        gia grading
        :return:
        """
        self.upload_sarine_grading_results()

        stones = [Stone.objects.get(internal_id=internal_id) for internal_id in self.stone_ids]

        for stone in stones:
            self.assertFalse(stone.is_goldway_grading_complete)

        gia = User.objects.get(username="gia")
        vault = User.objects.get(username="vault")
        tanly = User.objects.get(username="tanly")

        self.upload_goldway_grading_results()

        # transfer to gia
        for stone in stones:
            StoneTransfer.initiate_transfer(item=stone, from_user=vault, to_user=gia, created_by=tanly)
            StoneTransfer.confirm_received(item=stone)

        # be sure is_gia_grading_complete is still False
        for stone in stones:
            self.assertFalse(stone.is_gia_grading_complete)

    def test_is_goldway_adjusting_grading_complete(self):
        """
        Tests that is_goldway_adjusting_complete returns True if goldway adjusting results
        have been uploaded and returns False otherwise
        :return:
        """
        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.is_goldway_adjusting_grading_complete)

        self.upload_goldway_adjusting_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertTrue(stone.is_goldway_adjusting_grading_complete)

    def test_is_gia_grading_complete(self):
        """
        Tests that is_gia_grading_complete returns True if gia grading results
        have been uploaded and returns False otherwise
        :return:
        """
        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.is_gia_grading_complete)

        self.upload_goldway_grading_results()
        self.upload_gia_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertTrue(stone.is_gia_grading_complete)

    def test_is_gia_adjusting_grading_complete(self):
        """
        Tests that is_gia_adjusting_grading_complete returns True if gia adjusting results
        have been uploaded and returns False otherwise
        :return:
        """
        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.is_gia_adjusting_grading_complete)

        self.upload_goldway_grading_results()
        self.upload_gia_grading_results()
        self.upload_gia_adjusting_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertTrue(stone.is_gia_adjusting_grading_complete)

    def test_macro_image_uploaded_returns_false_if_no_macro_filename(self):
        """
        Tests that macro_filename_upload returns false if macro_filename has not been uploaded
        """
        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.macro_image_uploaded)

    def test_nano_image_uploaded_returns_false_if_no_nano_filename(self):
        """
        Tests that nano_filename_upload returns false if nano_filename has not been uploaded
        """

        self.upload_sarine_grading_results()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            self.assertFalse(stone.nano_image_uploaded)

    def test_macro_image_uploaded_returns_true_if_there_is_macro_filename(self):
        """
        Tests that macro_filename_upload returns true if macro_filename has been uploaded
        """

        self.upload_sarine_grading_results()

        filenames = ["G30204352_macro", "Gb46e9350_macro", "G02da2347_macro"]
        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            for filename in filenames:
                stone.macro_filename = filename
            self.assertTrue(stone.macro_image_uploaded)

    def test_nano_image_uploaded_returns_true_if_there_is_nano_filename(self):
        """
        Tests that nano_filename_upload returns true if nano_filename has been uploaded
        """

        self.upload_sarine_grading_results()

        filenames = ["G30204352_nano", "Gb46e9350_nano", "G02da2347_nano"]
        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            for filename in filenames:
                stone.macro_filename = filename
            self.assertTrue(stone.macro_image_uploaded)
