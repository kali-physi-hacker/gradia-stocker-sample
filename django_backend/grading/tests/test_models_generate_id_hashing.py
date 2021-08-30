from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError


from grading.models import Stone


class TestIDHashGeneration(TestCase):
    fixtures = ("data_migration/test_data.json",)

    def setUp(self):

        # Create some stone entries
        basic_grading_url = reverse("grading:upload_parcel_csv")
        csv_file = open("grading/tests/fixtures/sarine-01.csv", "r")
        self.client.login(username="graderuser", password="Passw0rd!")
        self.client.post(basic_grading_url, {"file": csv_file})

        self.stones = Stone.objects.all()  # Stones created

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
        self.assertEqual(hashed[0], "G")

    def test_basic_hashed_id_is_saved_to_stone(self):
        """
        Tests that the basic generated id is saved to stone (DB)
        :return:
        """

        stone = self.stones[0]
        stone.generate_basic_external_id()
        self.assertEqual(len(stone.external_id), 11)  # This is true for basic id
        self.assertIn("G", stone.external_id)
        self.assertIn("-B", stone.external_id)

    def test_triple_hashed_id_is_saved_to_stone(self):
        """
        Tests that the triple generated id is saved to stone (DB)
        :return:
        """
        stone = self.stones[0]
        stone.generate_triple_verified_external_id()
        self.assertEqual(len(stone.external_id), 9)  # This is true for triple id
        self.assertIn("G", stone.external_id)

    def test_basic_id_hashing_deterministic(self):
        """
        Tests that the same basic id hash is generated for the same stone
        :return:
        """
        for stone in self.stones:
            stone.generate_basic_external_id()
            hashed_1 = stone.external_id
            stone.generate_basic_external_id()
            hashed_2 = stone.external_id
            self.assertIn("-B", stone.external_id)
            self.assertEqual(hashed_1, hashed_2)

    def test_triple_verified_hashing_deterministic(self):
        """
        Test that same triple verified hash is generated for the same stone
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

        # Generate a basic external id some stone and clear back
        stone_1.generate_basic_external_id()
        stone_1_external_id = stone_1.external_id
        stone_1.external_id = None
        stone_1.save()

        # Assign saved hashed ID to stone_2
        stone_2.external_id = stone_1_external_id
        stone_2.save()

        with self.assertRaises(IntegrityError):
            stone_1.generate_basic_external_id()

        # Making sure that stone_2 stone_1 have different value for external_id
        self.assertNotEqual(stone_1.external_id, stone_2.external_id)

    def test_basic_hashing_hashes_with_the_correct_payload(self):
        pass

    def test_triple_hashing_hashes_with_the_correct_payload(self):
        pass
