#!/bin/bash


# to be run like this:
# ./data_migration/reset_testing_environment.sh

rm db.sqlite3
./manage.py migrate --settings='gradia_stocker.settings_dev'
./manage.py loaddata --settings='gradia_stocker.settings_dev' data_migration/old_data.json
./manage.py shell --settings='gradia_stocker.settings_dev'

# then from the ipython console
# %run data_migration/migration_script.py
