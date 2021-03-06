from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError


from grading.models import Stone


class TestIDHashGeneration(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):

        # Create some stone entries
        basic_grading_url = reverse("grading:upload_parcel_csv")
        csv_file = open("grading/tests/fixtures/sarine-01.csv", "r")
        self.client.login(username="graderuser", password="Passw0rd!")
        self.client.post(basic_grading_url, {"file": csv_file})

        stone = Stone.objects.first()
        new_stone = stone
        new_stone.id = 4
        new_stone.internal_id = 3
        new_stone.basic_color_final = "D"
        new_stone.basic_polish_final = "F"
        new_stone.save()

        self.stones = Stone.objects.all()  # Stones created

    def test_triple_verified_external_id_generation_valid_format(self):
        """
        Tests that the format of the generated ID is in Triple Format
        1. length == 9
        2. should start with a G
        :returns:
        """
        stone = self.stones[0]
        # test if stone does not have any pre-existing external_id
        self.assertEqual(stone.external_id, None)
        stone.generate_triple_verified_external_id()
        external_id = stone.external_id
        self.assertEqual(len(external_id), 9)
        self.assertEqual(external_id[0], "G")

    def test_that_triple_external_part_is_not_the_same_for_next_stone(self):
        # test that for two different stones the external part of their id would not be the same
        # triple external_id part
        stone = self.stones[0]
        stone2 = self.stones[1]
        stone.generate_triple_verified_external_id()
        stone2.generate_triple_verified_external_id()
        self.assertNotEqual(stone.external_id[:-3], stone2.external_id[:-3])

    def test_that_basic_external_part_is_not_the_same_for_next_stone(self):
        # test that for two different stones the external part of their id would not be the same
        # basic external_id part
        stone = self.stones[0]
        stone2 = self.stones[1]
        stone.generate_basic_external_id()
        stone2.generate_basic_external_id()
        self.assertNotEqual(stone.external_id[:-5], stone2.external_id[:-5])

    def test_triple_verified_external_id_generation_is_deterministic(self):
        """
        Tests that triple verified external_id generation is the same no matter when it
        is generated
        :returns:
        """
        stone = self.stones[0]
        stone.generate_triple_verified_external_id()
        external_id = stone.external_id
        stone.external_id = None
        stone.save()

        stone.generate_triple_verified_external_id()

        self.assertEqual(stone.external_id, external_id)

    def test_triple_verified_external_id_generation_raises_error_if_exists(self):
        stone = self.stones[0]
        stone.generate_triple_verified_external_id()
        external_id = stone.external_id
        stone.external_id = None
        stone.save()

        new_stone = self.stones[1]
        new_stone.external_id = external_id
        new_stone.save()

        with self.assertRaises(IntegrityError):
            stone.generate_triple_verified_external_id()

    def test_basic_external_id_generation_valid_format(self):
        """
        Tests that the format of the generated ID is of the following ID
        1. length = 9
        2. should start with GB
        :returns:
        """
        stone = self.stones[0]
        stone.generate_basic_external_id()
        external_id = stone.external_id

        self.assertEqual(len(external_id), 11)
        self.assertEqual(external_id[0], "G")
        self.assertEqual(external_id[9:], "-B")

    def test_basic_external_id_generation_is_deterministic(self):
        """
        Tests that basic external_id generation is the same no matter when it
        is generated
        :returns:
        """
        stone = self.stones[0]
        stone.generate_basic_external_id()
        external_id = stone.external_id

        stone.external_id = None
        stone.save()

        stone.generate_basic_external_id()

        self.assertEqual(stone.external_id, external_id)

    def test_basic_external_id_generation_raises_error_if_exists(self):
        stone = self.stones[0]
        stone.generate_basic_external_id()
        external_id = stone.external_id
        stone.external_id = None
        stone.save()

        new_stone = self.stones[1]
        new_stone.external_id = external_id
        new_stone.save()

        with self.assertRaises(IntegrityError):
            stone.generate_basic_external_id()
