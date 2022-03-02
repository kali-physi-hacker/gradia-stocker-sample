import io

from django.test import TestCase
from django.core.management import call_command 

from grading.models import Stone 

"""
1. command (python manage.py auto_grade) works successfully
2. test that auto_grade is deterministic (i.e produces the same output when run multiple times)
"""

out = io.StringIO()
call_command("auto_grade", stdout=out)

# In our mind, when `python manage.py auto_grade` is called:
#  1. search for stones that have completed all the other grading stages
#  2. run the auto grade on them

# test for output after command is called 


class AutoGradeTest(TestCase):
    def setUp(self):
        pass 

    def test_command_auto_grades_successfully(self):
        """
        Tests that `auto_grade` command:
            1. auto grades successfully
            2. runs only one stones that have completed sarine and basic stages
        :returns:
        """
        
        pass 

    def test_auto_grade_is_deterministic(self):
        """
        Tests that `auto_grade` returns the same result when run multiple times
        :returns:
        """