from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError


from grading.models import Stone


class TestIDHashGeneration(TestCase):
    fixtures = (
        "grading/tests/fixtures/basic_grading_fixtures.json",
        "grading/tests/fixtures/default_users.json"
    )

    def setUp(self):

        # Create some stone entries
        basic_grading_url = reverse("grading:upload_parcel_csv")
        csv_file = open("grading/tests/fixtures/123456789.csv", "r")
        self.client.login(username="graderuser", password="Passw0rd!")
        self.client.post(basic_grading_url, {"file": csv_file})

        self.stones = Stone.objects.all()     # Stones created

    def test_generated_hashed_id_format_correct(self):
        """
        Tests that the format of the generated hash ID is of the format
        G9d8495d
        :return:
        """
        # Get a stone
        stone = self.stones[0]
        stone.generate_basic_external_id()
        hashed = stone.external_id
        self.assertEqual(hashed[0], 'G')

    def test_basic_hashed_id_is_saved_to_stone(self):
        """
        Tests that the generated id is saved to DB
        :return:
        """
        # If there were a last updated field? We could use that
        # But for now,
        # 1. Check that external_id is not empty and the available one is of the
        # correct format

        stone = self.stones[0]
        stone.generate_basic_external_id()
        self.assertEqual(len(stone.external_id), 11)   # This is true for basic id
        self.assertIn('G', stone.external_id)
        self.assertIn('-B', stone.external_id)

    def test_basic_id_hashing_deterministic(self):
        """
        Tests that the same id hash is generated for the same stone
        :return:
        """
        for stone in self.stones:
            stone.generate_basic_external_id()
            hashed_1 = stone.external_id
            stone.generate_basic_external_id()
            hashed_2 = stone.external_id
            self.assertIn('-B', stone.external_id)
            self.assertEqual(hashed_1, hashed_2)

    def test_triple_verified_hashed_id_generation(self):
        """
        Tests that the hashed id generated is of the format G12345678 (triple
        :return:
        """
        for stone in self.stones:
            stone.generate_triple_verified_external_id()
            hashed_1 = stone.external_id
            stone.generate_triple_verified_external_id()
            hashed_2 = stone.external_id
            self.assertEqual(hashed_1, hashed_2)

    def test_complain_loudly_if_collision(self):
        """
        Tests that loud complain is made (email) d
        :return:
        """
        stone_1 = self.stones[0]
        stone_2 = self.stones[1]

        # We assuming a collision has occurred during generation
        with self.assertRaises(IntegrityError):
            stone_1.generate_basic_external_id()
            stone_2.external_id = stone_1.external_id
            stone_2.save()
