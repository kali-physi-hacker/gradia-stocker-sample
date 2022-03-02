import sys
import unittest
import os

import numpy as np
# Parent Module Import Setup
sys.path.append(".")
print(sys.path)
from ..core.table_ds_generator import TableDSGenerator


class TableDSGeneratorTest(unittest.TestCase):
    def setUp(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        table_5_path = os.path.join(BASE_DIR, "test_grade_tables", "5.txt")
        table_3_path = os.path.join(BASE_DIR, "test_grade_tables", "3.txt")
        self.table_5 = TableDSGenerator(table_file_path=table_5_path)
        self.table_3 = TableDSGenerator(table_file_path=table_3_path)
        self.table_file_path = os.path.join("tests", "test_grade_tables")

    def test_table_generates_ds_given_valid_input_file(self):
        """
        Tests that `get_grade` generates expected ds (table) with given
        valid input file
        :return:
        """

        calculated_grade = self.table_5.get_grade(35.0, 38.8)
        calculated_grade_2 = self.table_5.get_grade(34.0, 39.0)
        calculated_grade_3 = self.table_3.get_grade(28.5, 39.0)
        calculated_grade_4 = self.table_3.get_grade(34.0, 38.8)
        calculated_grade_5 = self.table_3.get_grade(34.5, 38.8)

        expected_grade = "GD"
        expected_grade_3 = "FR"

        self.assertEqual(calculated_grade, expected_grade)
        self.assertEqual(calculated_grade_2, expected_grade)
        self.assertEqual(calculated_grade_3, expected_grade_3)
        self.assertEqual(calculated_grade_4, expected_grade_3)
        self.assertEqual(calculated_grade_5, expected_grade)


    def test_table_raises_value_error_if_invalid_angles(self):
        """
        Tests that `get_grade` raises value error if invalid angles are supplied as arguments
        :return:
        """
        with self.assertRaises(ValueError):
            self.table_3.get_grade(999, 240)
            self.table_3.get_grade(22.0, 38.8)
            self.table_3.get_grade(40.0, 43.0)
            
    def test_empty_table_raises_error(self):
        with self.assertRaises(Exception):
            table_1_path = os.path.join(BASE_DIR, "test_grade_tables", "1.txt")
            self.table_1 = TableDSGenerator(table_file_path=table_1_path)
    # Jason you can try working on more test cases. Just try thinking of possible edges (happy / sad cases)


if __name__ == "__main__":
    unittest.main()
