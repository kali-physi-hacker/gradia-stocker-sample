import sys
import unittest
import os
import csv

from django.conf import settings
from django.test import TestCase

from grading.models import Stone

# sys.path.append(".")
from grading.auto_grade.process_csv import auto_grade_stone

"""
    list of tests: (* done)
    test_generates_csv_in_correct_location *
    test_creates_correct_columns_in_the_correct_order *
    test_creates_correct_amount_of_rows *
    test_generate_correct_table_size_grade *
    test_generate_correct_crown_angle_grade *
    test_generate_correct_pavilion_angle_degree_grade *
    test_generate_correct_star_length_pct_grade *
    test_generate_correct_lower_half_pct_grade *
    test_generate_correct_girdle_thick_pct_grade *
    test_generate_correct_girdle_grade *
    test_generate_correct_crown_height_pct_grade *
    test_generate_correct_total_depth_pct_grade *
    test_generate_correct_gradia_cut *
    test_generate_corrent_est_table_cut_grade
    test_generate_correct_final_gradia_cut
    test_hand_graded_file
"""

"""
 'auto_table_size_rounded_grade',
 'auto_crown_angle_rounded_grade_grade',
 'auto_pavilion_angle_rounded_grade',
 'auto_star_length_rounded_grade',
 'auto_lower_half_rounded_grade',
 'auto_girdle_thick_rounded_grade',
 'auto_girdle_grade',
 'auto_crown_height_rounded_grade',
 'auto_total_depth_rounded_grade',
 'auto_individual_cut_grade_grade',
 'auto_est_table_cut_grade_grade',
 'auto_gradia_cut_grade_grade',
 'auto_final_sarine_cut_grade',
 'auto_final_gradia_cut_grade'
"""


class AutoGradeTest(TestCase):
    def setUp(self):
        self.input_file_path = os.path.join(
            settings.BASE_DIR, "grading", "auto_grade", "tests", "test_input_file.csv"
        )
        stone_list = self.convert_csv_to_list(self.input_file_path)

        self.auto_graded_list = []
        for stone_data in stone_list:
            graded_stone = auto_grade_stone(stone_data)
            self.auto_graded_list.append(graded_stone)

    def convert_csv_to_list(self, csv_file):
        """
        Upload basic and sarine
        :returns:
        """
        with open(csv_file, "r") as file:
            reader = csv.DictReader(file)
            return list(reader)

    def test_generate_correct_table_size_grade(self):
        """
        Test to check if table size is generated correctly
        input: 58 output: EX
        input: 52 output: EX
        input: 51 output: VG
        input: 47 output: GD
        input: 30 output: PR
        input: 69 output: GD
        """
        expected_outputs = ["EX", "EX", "VG", "GD", "PR", "GD"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["table_size_pct_grade"], expected_output)

    def test_generate_correct_crown_angle_grade(self):
        """
        Test to check if crown angle degree grade is generated correctly
        input: 32 output: EX
        input: 31.5 output: EX
        input: 30 output: VG
        input: 22.0 output: GD
        input: 40.1 output: FR
        input: 60.5 output: PR
        """
        expected_outputs = ["EX", "EX", "VG", "GD", "FR", "PR"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["crown_angle_degree_grade"], expected_output)

    def test_generate_correct_pavilion_angle_degree_grade(self):
        """
        Test to check if pavilion angle degree grade is generated correctly
        input: 40.8 output: EX
        input: 40.6 output: EX
        input: 42.4 output: VG
        input: 42.9 output: GD
        input: 37.4 output: FR
        input: 37.3 output: PR
        """
        expected_outputs = ["EX", "EX", "VG", "GD", "FR", "PR"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["pavilion_angle_degree_grade"], expected_output)

    def test_generate_correct_star_length_pct_grade(self):
        """
        input           output
        45              EX
        50              EX
        40              VG
        70              VG
        30              GD
        80              GD
        """
        expected_outputs = ["EX", "EX", "VG", "VG", "GD", "GD"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["star_length_pct_grade"], expected_output)

    def test_generate_correct_lower_half_pct_grade(self):
        """
        input           output
        80              EX
        75              EX
        65              VG
        90              VG
        50              GD
        100             GD
        """
        expected_outputs = ["EX", "EX", "VG", "VG", "GD", "GD"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["lower_half_pct_grade"], expected_output)

    def test_generate_correct_girdle_thick_pct_grade(self):
        """
        input           output
        2.5             EX
        4.5             EX
        5.5             VG
        7.5             GD
        10.4            FR
        2               PR
        """
        expected_outputs = ["EX", "EX", "VG", "GD", "FR", "PR"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["girdle_thick_pct_grade"], expected_output)

    def test_generate_correct_girdle_grade(self):
        """
        input(min/thin) input(max/thick)  output
        ETN             ETN to VTN        GD
        MED             MED               EX
        ETK             ETK               FR
        THN             STK               EX
        MED             THK               VG
        THK             VTK               GD
        """
        expected_outputs = ["GD", "EX", "FR", "EX", "VG", "GD"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["girdle_grade"], expected_output)

    def test_generate_correct_crown_height_pct_grade(self):
        """
        input       output
        14          EX
        12.5        EX
        17          EX
        12          VG
        18          VG
        18.5        GD
        """
        expected_outputs = ["EX", "EX", "EX", "VG", "VG", "GD"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["crown_height_pct_grade"], expected_output)

    def test_generate_correct_total_depth_pct_grade(self):
        """
        input       output
        60.9        EX
        58.1        EX
        56.0        VG
        53.2        GD
        51.9        FR
        78.5        PR
        """
        expected_outputs = ["EX", "EX", "VG", "GD", "FR", "PR"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["total_depth_pct_grade"], expected_output)

    def test_generate_correct_individual_cut_grade(self):
        """
        Test if program correctly return the gradia_cut
        (lowest grade within list of grades)
        input:
            [table_size_grade: VG,
            crown_grade: VG,
            pav_grade: VG,
            star_length_grade: VG,
            lower_half_grade: VG,
            girdle_thickness: VG,
            girdle_grade: VG,
            crown_height: VG,
            total_depth: GD]
        output: 'GD'
        """
        expected_outputs = ["GD", "EX", "FR", "GD", "PR", "PR"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["individual_cut_grade"], expected_output)

    def test_generate_correct_est_table_cut_grade(self):
        """
        input                           output
        table_size  crown   pav         grade
        58          32      40.8        VG
        52          31.5    40.6        VG
        51          30      42.4        VG
        47          x       x           '' (table size overflow)
        30          x       x           '' (table size overflow)
        69          x       x           '' (table size overflow)
        """
        expected_outputs = ["VG", "VG", "VG", "", "", ""]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["est_table_cut_grade"], expected_output)

    def test_generate_correct_gradia_cut(self):
        """
        check if return the lower grade between individual_cut_grade and est_table_cut_grade.
        """
        expected_outputs = ["GD", "VG", "FR", "", "", ""]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["gradia_cut"], expected_output)

    def test_generate_correct_final_sarine_cut(self):
        """
        check if return a downgraded sraine cut grade if the sarine_symmetry or basic_final_polish is 2 grade lower
        input:
            [sarine_cut: EX,
            basic_final_polish: VG,
            sarine_symmetry: GD]
        output: 'VG'
        """
        expected_outputs = ["EX", "VG", "GD", "FR", "PR", "GD"]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["final_sarine_cut"], expected_output)

    def test_generate_correct_final_gradia_cut(self):
        """
        check if return a downgraded gradia cut grade if the basic_final_polish or sarine_symmetry is 2 grade lower
        input:
            [gradia_cut: EX,
            basic_final_polish: VG,
            sarine_symmetry: GD]
        output: 'VG'
        """
        expected_outputs = ["GD", "VG", "FR", "", "", ""]
        for row, expected_output in zip(self.auto_graded_list, expected_outputs):
            self.assertEqual(row["final_gradia_cut"], expected_output)

    # def test_generate_correct_check_result(self):
    #     """
    #     check if return the number of differences is 0 (Should not have differences)
    #     """
    #     self.assertEqual(self.number_of_differences, 0)
