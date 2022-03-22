import sys
import unittest
import os
import csv
import pprint

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_LOG = os.path.join(BASE_DIR, "differences_log", "log.txt")

test_fields = "table_size_pct_grade,crown_angle_degree_grade,pavilion_angle_degree_grade,star_length_pct_grade,lower_half_pct_grade,girdle_thick_pct_grade,girdle_grade,individual_cut_grade,est_table_cut_grade,gradia_cut,final_gradia_cut,final_sarine_cut".split(
    ","
)


def check_differences_print_and_store_log(original_csv_path: str, computed_csv_path: str) -> None:
    return
    expected = []
    result = []
    with open(original_csv_path, "r") as input_file:
        input_reader = csv.DictReader(input_file)
        for row in input_reader:
            expected.append(row)
    with open(computed_csv_path, "r") as output_file:
        output_reader = csv.DictReader(output_file)
        for row in output_reader:
            result.append(row)

    logs = []
    rejected_stone = ["rej", "REJ"]
    for i, (expected_stone, result_stone) in enumerate(zip(expected, result)):
        if expected_stone["remarks"] in rejected_stone:
            continue
        for test_field in test_fields:
            if expected_stone[test_field] != result_stone[test_field]:
                logs.append(
                    dict(
                        test_field=test_field, computed=result_stone, hand_grading=expected_stone, line_number=i + 2
                    )
                )
    open(OUTPUT_LOG, "w").close()
    if logs:
        print(len(logs), "Differences Found:\n")
        for i, log in enumerate(logs, 1):
            internal_id = str(log["computed"]["internal_id"])
            line_number = str(log["line_number"])
            test_field = str(log["test_field"])
            computed_grading = str(log["computed"][test_field])
            hand_grading = str(log["hand_grading"][test_field])
            printlog(
                index=i,
                internal_id=internal_id,
                line_number=line_number,
                test_field=test_field,
                computed_grading=computed_grading,
                hand_grading=hand_grading,
            )
            writelog(
                output_log_file_path=OUTPUT_LOG,
                index=i,
                internal_id=internal_id,
                line_number=line_number,
                test_field=test_field,
                computed_grading=computed_grading,
                hand_grading=hand_grading,
            )
        print("...differences stored in log.txt")

    return len(logs)


def printlog(index, internal_id, line_number, test_field, computed_grading, hand_grading):
    print(index)
    print(
        "ID:          ",
        internal_id,
        "\n" "Line Number: ",
        line_number,
        "\n" "Field Name:  ",
        test_field,
        "\n" "Computed:    ",
        computed_grading,
        "\n" "Hand Graded: ",
        hand_grading,
        "\n",
    )


def writelog(output_log_file_path, index, internal_id, line_number, test_field, computed_grading, hand_grading):
    with open(output_log_file_path, "a", newline="") as log_file:
        log_file.write(str(index) + "\n")
        log_file.write("ID: " + internal_id + "\n")
        log_file.write("Line Number: " + line_number + "\n")
        log_file.write("Field Name: " + test_field + "\n")
        log_file.write("Computed: " + computed_grading + "\n")
        log_file.write("Hand Graded: " + hand_grading + "\n")
        log_file.write("\n")
