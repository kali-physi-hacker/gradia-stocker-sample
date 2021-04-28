[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=shield)](https://circleci.com/gh/gradia-exchange/GRADIA_stocker)

### usage
- to run tests:
- to record a screencast:
	1. change all comments to prints in your test file: 
       - linux: `sed -i 's/^\(\W*\)# \(.\+\)$/\1print(""" \2 """); import time; time.sleep(1)/g' file_name.py`
       - macOS: install the gnu-sed package: `brew install gnu-sed` then run the command `gsed -r 's/^\(\W*\)# \(.\+\)$/\1print(""" \2 """); import time; time.sleep(1)/g' file_name.py`
    2. disable headless in conftest: 
       - linux: `sed -i 's/chrome_options.add_argument("--headless")/# chrome_options.add_argument("--headless")/' conftest.py`
       - macOS: `gsed -r 's/chrome_options.add_argument("--headless")/# chrome_options.add_argument("--headless")/' conftest.py`
    3. run just your single test function: `pytest --capture=tee-sys -k test_grader_can_confirm_received_stones 3>&1 1>&2 2>&3  | tee descriptive-name.txt`
    4. make sure screenrecorder can see browser + last couple lines of terminal
    5. after all is done, revert the changes `git checkout test_admin_page_grader.py conftest.py`
	6. edit descriptive-name.txt and upload the mp4 and txt to the trello card
- to upload initial data:
    - `set -a; source ~/.env; set +a; ./manage.py shell`
    - `%run data_migration/populate_from_pytest_fixtures.py`

### basics
- special users: vault, split, admin


### questions
- kyc will be done in remarks. we will have a checklist
- would you ever return parts of a consignment? ie. one parcel out of 3


### todo:
- start transfer should have search and select like user select
    - cant tell if have confirmed stones or not
- splits- why does the more descriptive error not show up
- stones should have location and action to return to vault
- vaultmasters can also split even if they dont own the thing
- data entry needs to be able to split even if they dont own the thing
- make sure splits add up
- filter by user thing
- move receipts to customers


- backend to confirm stones
- backend to return stones to vault
- better error page for split (eg: not confirmed transfer yet, you are not the owner so you can't split)
- split parcel -> add. u can choose who the user who split the parcel is- instead it should just autosave as the logged in user


- make the 2. parcel info into an excel thing and have the return to vault button in the list view as well
- stone table view

- allow gary to confirm stones on vault's behalf

- make a way to create splits and add new packages as the child of the split
- make a way to create splits into stones
- when splitting -> the parent ownership gets expired
- permissions for creating split parcels

- generate stone ID
- make receipt ID and parcel ID unique. autogenerate them?

- allow select group to confirm GIA/goldway user receipts
- fix the search bar in the transfer thing


### done
- in the transfer thing. default to only showing their stuff
- parcel admin view has split parcels in it
- take out user / received by option from parcel. instead track ownership transfer

### not doing
- link parcel or split parcel to stone <- fixed by new splitting mechanism
