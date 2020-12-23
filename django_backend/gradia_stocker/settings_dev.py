import sys

from .settings import *

DEBUG = True
ALLOWED_HOSTS.append("localhost")


# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())
SECRET_KEY = "52633epecmm==%kw1-ls&u7z48+x6on#a!41+1xsuv%!iv14i*"

DATABASES["default"]["ENGINE"] = "django.db.backends.sqlite3"
DATABASES["default"]["NAME"] = "db.sqlite3"
del DATABASES["default"]["OPTIONS"]
if "--keepdb" in sys.argv:
    DATABASES["default"]["TEST"] = {"NAME": "/dev/shm/gradia-test-db.sqlite3"}
