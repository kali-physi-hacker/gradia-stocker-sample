import sys

from .settings import *

DEBUG = True
ALLOWED_HOSTS.append("localhost")


DATABASES["default"]["ENGINE"] = "django.db.backends.sqlite3"
DATABASES["default"]["NAME"] = "db.sqlite3"
del DATABASES["default"]["OPTIONS"]
if "--keepdb" in sys.argv:
    DATABASES["default"]["TEST"] = {"NAME": "/dev/shm/gradia-test-db.sqlite3"}
