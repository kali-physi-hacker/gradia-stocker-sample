import os
import numpy as np

class TableDSGenerator:

    # Table Size, Crown Angle, Pav. Angle
    # -> Grade

    def __init__(self, table_file_path):

        if os.stat(table_file_path).st_size == 0:
            raise Exception(table_file_path.split('/')[-1]+' is empty.')

        self.table_file_path = table_file_path

        self.table_size = None
        self.input_grades = None

        self.standard_grades = {
            "e": "EX",
            "v": "VG",
            "g": "GD",
            "f": "FR",
            "p": "PR",
        }

        self.crown_angle_ranges = np.array([float("{:.1f}".format(angle)) for angle in np.arange(22.0, 40.0, 0.5)])
        self.pavilion_angle_ranges = np.array([float("{:.1f}".format(angle)) for angle in np.arange(38.8, 43.0, 0.2)])

        self.get_input_grades()

        self.pavilion_angle_map_dict = {}
        self.crown_angle_map_dict = {}
        self.map_angles_to_integers()

        self.table = []
        self.generate_table()


    def get_input_grades(self):
        """
        Open file and initialize grades
        :return:
        """
        with open(self.table_file_path, 'r') as table_file:
            self.input_grades = list([line.strip() for line in table_file.readlines()])

    def map_angles_to_integers(self):
        """
        Map both crown_angles and pavilion_angles to integers to be used in get_grades
        :return:
        """
        for index in range(len(self.input_grades[0])-1):
            self.crown_angle_map_dict[self.crown_angle_ranges[index]] = index

        for index in range(len(self.input_grades)-1):
            self.pavilion_angle_map_dict[self.pavilion_angle_ranges[index]] = index


    def generate_table(self):
        """
        Generates and returns a list which contain multiple table DS (matrix) using input data
        :return:
        """
        for row in self.input_grades:
            self.table.append([self.standard_grades.get(column) for column in row])


    def get_grade(self ,crown_angle, pavilion_angle):
        """
        Return the grade given the table size, crown_angle and the pavilion_angle
        :param table_size:
        :param crown_angle:
        :param pavilion_angle:
        :return:
        """
        if crown_angle not in self.crown_angle_ranges:
            raise ValueError(f"{crown_angle} specified is invalid")

        if pavilion_angle not in self.pavilion_angle_ranges:
            raise ValueError(f"{pavilion_angle} specified is invalid")
        
        grade = self.table[self.pavilion_angle_map_dict[pavilion_angle]][self.crown_angle_map_dict[crown_angle]]
        return grade
