import os
import csv

from .grading_modules.all_grading_calculations import *

all_grading_calculations = [
    grade_table_size_pct,
    grade_crown_angle_degree,
    grade_pavilion_angle_degree,
    grade_star_length_pct,
    grade_lower_half_pct,
    grade_girdle_thick_pct,
    grade_girdle,
    grade_crown_height_pct,
    grade_total_depth_pct,
    grade_individual_cut_grade,
    grade_est_table_cut_grade,
    grade_gradia_cut_grade,
    grade_final_sarine_cut,
    grade_final_gradia_cut,
]


def auto_grade_stone(stone_dict):
    for calculation in all_grading_calculations:

        stone_dict.update(calculation(stone_dict=stone_dict))

    return stone_dict
