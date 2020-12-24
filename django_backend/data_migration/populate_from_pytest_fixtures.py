import sys

from django.contrib.auth.models import User

sys.path.append("../selenium_tests")

from grading_fixtures import receipt_setup, stones_setup  # isort:skip
from user_fixtures import erp_setup, user_setup  # isort:skip


erp_setup(User)

grader = user_setup(User, "grader")
receptionist = user_setup(User, "receiptionist")
buyer = user_setup(User, "buyer")
data_entry = user_setup(User, "data_entry")
vault_manager = user_setup(User, "vault_manager")

receipt = receipt_setup(User, receptionist)
stones_setup(User, receipt, data_entry, grader, receptionist)
