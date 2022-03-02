import os
import sys

from django.conf import settings 

from grading.auto_grade.cut_grade_estimation_table_generation_tool.core.table_ds_generator import TableDSGenerator

GRADE_PARA = {
    "table_size_rounded": [52, 62, 50, 66, 47, 69, 44, 72],
    "crown_angle_rounded": [31.5, 36.5, 26.5, 38.5, 22.0, 40.0, 20.0, 41.5],
    "pavilion_angle_rounded": [40.6, 41.8, 39.8, 42.4, 38.8, 43.0, 37.4, 44],
    "star_length_rounded": [45, 65, 40, 70, 0, 100, 0, 100],
    "lower_half_rounded": [70, 85, 65, 90, 0, 100, 0, 100],
    "girdle_thickness_rounded": [2.5, 4.5, 2.5, 5.5, 2.5, 7.5, 2.5, 10.5],
    "crown_height_rounded": [12.5, 17.0, 10.5, 18.0, 9.0, 19.5, 7.0, 21.0],
    "total_depth_rounded": [57.5, 63.0, 56.0, 64.5, 53.0, 66.5, 51.9, 70.9],
}


def grade_table_size_pct(stone_dict: dict) -> dict:
    # auto_table_size_rounded_grade
    stone_dict["auto_table_size_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["table_size_rounded"], parameters=GRADE_PARA["table_size_rounded"]
    )
    return stone_dict


def grade_crown_angle_degree(stone_dict: dict) -> dict:
    # auto_crown_angle_rounded_grade_grade
    stone_dict["auto_crown_angle_rounded_grade_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["crown_angle_rounded"], parameters=GRADE_PARA["crown_angle_rounded"]
    )
    return stone_dict


def grade_pavilion_angle_degree(stone_dict: dict) -> dict:
    # auto_pavilion_angle_rounded_grade
    stone_dict["auto_pavilion_angle_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["pavilion_angle_rounded"], parameters=GRADE_PARA["pavilion_angle_rounded"]
    )
    return stone_dict


def grade_star_length_pct(stone_dict: dict) -> dict:
    # auto_star_length_rounded_grade
    stone_dict["auto_star_length_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["star_length_rounded"], parameters=GRADE_PARA["star_length_rounded"]
    )
    return stone_dict


def grade_lower_half_pct(stone_dict: dict) -> dict:
    # auto_lower_half_rounded_grade
    stone_dict["auto_lower_half_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["lower_half_rounded"], parameters=GRADE_PARA["lower_half_rounded"]
    )
    return stone_dict


def grade_girdle_thick_pct(stone_dict: dict) -> dict:
    # auto_girdle_thick_rounded_grade
    stone_dict["auto_girdle_thick_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["girdle_thickness_rounded"], parameters=GRADE_PARA["girdle_thickness_rounded"]
    )
    return stone_dict


def grade_girdle(stone_dict: dict) -> dict:
    # auto_girdle_grade
    stone_dict["auto_girdle_grade"] = grade_with_girlde_description(
        g_min=stone_dict["girdle_min_grade"], g_max=stone_dict["girdle_max_grade"]
    )
    return stone_dict


def grade_crown_height_pct(stone_dict: dict) -> dict:
    # auto_crown_height_rounded_grade
    stone_dict["auto_crown_height_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["crown_height_rounded"], parameters=GRADE_PARA["crown_height_rounded"]
    )
    return stone_dict


def grade_total_depth_pct(stone_dict: dict) -> dict:
    # auto_total_depth_rounded_grade
    stone_dict["auto_total_depth_rounded_grade"] = grade_with_range_parameters(
        stone_data=stone_dict["total_depth_rounded"], parameters=GRADE_PARA["total_depth_rounded"]
    )
    return stone_dict


def grade_individual_cut_grade(stone_dict: dict) -> dict:
    # auto_individual_cut_grade_grade
    stone_data_list = [
        # prioritized using hand graded
        stone_dict["table_size_dev_grade"],
        stone_dict["crown_angle_dev_grade"],
        stone_dict["pavilion_angle_dev_grade"],
        stone_dict["star_length_dev_grade"],
        stone_dict["lower_half_dev_grade"],
        stone_dict["girdle_thick_dev_grade"],
        stone_dict["auto_girdle_grade"], # from auto grading
        stone_dict["crown_height_dev_grade"],
        stone_dict["auto_total_depth_rounded_grade"], # from auto grading
    ]
    result = grade_with_list_return_lowest_grade(stone_data_list=stone_data_list)
    stone_dict["auto_individual_cut_grade_grade"] = result
    return stone_dict


def grade_est_table_cut_grade(stone_dict: dict) -> dict:
    # auto_est_table_cut_grade_grade
    stone_dict["auto_est_table_cut_grade_grade"] = grade_with_cut_grade_estimation_table(
        table_size_pct=stone_dict["table_size_rounded"],
        crown_angle_degree=stone_dict["crown_angle_rounded"],
        pavilion_angle_degree=stone_dict["pavilion_angle_rounded"],
    )
    return stone_dict


def grade_gradia_cut_grade(stone_dict: dict) -> dict:
    # auto_gradia_cut_grade_grade
    stone_dict["auto_gradia_cut_grade_grade"] = grade_with_list_return_lowest_grade(
        stone_data_list=[stone_dict["auto_individual_cut_grade_grade"], stone_dict["auto_est_table_cut_grade_grade"]]
    )
    return stone_dict


def grade_final_sarine_cut(stone_dict: dict) -> dict:
    # auto_final_sarine_cut_grade_grade
    stone_dict["auto_final_sarine_cut_grade"] = grade_determind_if_cut_needs_downgrade_with_two_parameter(
        cut=stone_dict["sarine_cut_pre_polish_symmetry"], para1=stone_dict["sarine_symmetry"], para2=stone_dict["basic_polish_final"]
    )
    return stone_dict


def grade_final_gradia_cut(stone_dict: dict) -> dict:
    # auto_final_gradia_cut_grade
    # stone_dict["sarine_symmetry"] = convert_long_grade_to_short(stone_dict["sarine_symmetry"])
    stone_dict["auto_final_gradia_cut_grade"] = grade_determind_if_cut_needs_downgrade_with_two_parameter(
        cut=stone_dict["auto_gradia_cut_grade_grade"], para1=stone_dict["basic_polish_final"], para2=stone_dict["sarine_symmetry"]
    )
    return stone_dict


def grade_with_range_parameters(stone_data: str, parameters: list) -> str:
    if not stone_data:
        return ""
    stone_data = float(stone_data)
    if parameters[0] <= stone_data <= parameters[1]:
        return "EX"
    elif parameters[2] <= stone_data <= parameters[3]:
        return "VG"
    elif parameters[4] <= stone_data <= parameters[5]:
        return "GD"
    elif parameters[6] <= stone_data <= parameters[7]:
        return "FR"
    elif 0 <= stone_data <= 100:
        return "PR"


def grade_with_girlde_description(g_min: str, g_max: str) -> str:
    if not g_min or not g_max:
        return ""
    if g_min == "ETN to VTN":
        g_min = "ETN"
    if g_max == "ETN to VTN":
        g_max = "ETN"
    g_dict = {}
    g_dict["ETN"] = {
        "ETN": "GD",
        "VTN": "VG",
        "THN": "VG",
        "MED": "VG",
        "STK": "VG",
        "THK": "VG",
        "VTK": "GD",
        "ETK": "FR",
    }
    g_dict["VTN"] = {"VTN": "VG", "THN": "VG", "MED": "VG", "STK": "VG", "THK": "VG", "VTK": "GD", "ETK": "FR"}
    g_dict["THN"] = {"THN": "EX", "MED": "EX", "STK": "EX", "THK": "VG", "VTK": "GD", "ETK": "FR"}
    g_dict["MED"] = {"MED": "EX", "STK": "EX", "THK": "VG", "VTK": "GD", "ETK": "FR"}
    g_dict["STK"] = {"STK": "EX", "THK": "VG", "VTK": "GD", "ETK": "FR"}
    g_dict["THK"] = {"THK": "VG", "VTK": "GD", "ETK": "FR"}
    g_dict["VTK"] = {"VTK": "GD", "ETK": "FR"}
    g_dict["ETK"] = {"ETK": "FR"}
    return g_dict[g_min][g_max]


def grade_with_list_return_lowest_grade(stone_data_list: list) -> str:
    standard_grade = ["PR", "FR", "GD", "VG", "EX"]
    lowest = standard_grade.index("EX")
    for grade in stone_data_list:
        if grade not in standard_grade:
            return ""
        index = standard_grade.index(grade)
        if index < lowest:
            lowest = index
    return standard_grade[lowest]


def grade_with_cut_grade_estimation_table(
    table_size_pct: str, crown_angle_degree: str, pavilion_angle_degree: str
) -> str:
    if table_size_pct == "" or not 50 <= int(table_size_pct) <= 67:
        return ""

    table_data_path = os.path.join(settings.BASE_DIR, "grading", "auto_grade", "cut_grade_estimation_table_generation_tool", "core", "all_grade_tables", f"{table_size_pct}.txt")
    # table_data_path = os.path.join(
    #     "cut_grade_estimation_table_generation_tool", "core", "all_grade_tables", table_size_pct + ".txt"
    # )
    table = TableDSGenerator(table_file_path=table_data_path)
    if not table:
        return ""
    return table.get_grade(float(crown_angle_degree), float(pavilion_angle_degree))


def grade_determind_if_cut_needs_downgrade_with_two_parameter(cut: str, para1: str, para2: str) -> dict:
    # Assume all input are in short forms
    cut = cut[:2]
    para1 = para1[:2]
    para2 = para2[:2]
    standard_grade = ["PR", "FR", "GD", "VG", "EX"]
    print(cut, para1, para2)
    if cut not in standard_grade or para1 not in standard_grade or para2 not in standard_grade:
        print("EMPTY")
        return ""
    cut_index, para1_index, para2_index = (
        standard_grade.index(cut),
        standard_grade.index(para1) + 1,
        standard_grade.index(para2) + 1,
    )
    if para1_index < cut_index or para2_index < cut_index:
        return standard_grade[para1_index] if para2_index > para1_index else standard_grade[para2_index]
    return standard_grade[cut_index]

def convert_long_grade_to_short(long):
    if long == "Poor":
        return "PR"
    if long == "Fair":
        return "FR"
    if long == "Good":
        return "GD"
    if long == "Very Good":
        return "VG"
    if long == "Excellent":
        return "EX"