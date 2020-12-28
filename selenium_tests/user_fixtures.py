from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import pytest


@pytest.fixture
def erp(django_user_model):
    erp_setup(django_user_model)


@pytest.fixture
def grader(django_user_model, erp):
    return user_setup(django_user_model, "grader")


@pytest.fixture
def receptionist(django_user_model, erp):
    return user_setup(django_user_model, "receptionist")


@pytest.fixture
def buyer(django_user_model, erp):
    return user_setup(django_user_model, "buyer")


@pytest.fixture
def data_entry_clerk(django_user_model, erp):
    return user_setup(django_user_model, "data_entry")


@pytest.fixture
def vault_manager(django_user_model, erp):
    return user_setup(django_user_model, "vault_manager")


# have this separate non-fixture function
# so that we can call it to setup non pytest data
def user_setup(django_user_model, group_name):
    email = group_name + "@test.com"
    username = group_name
    password = group_name + "password"

    user = django_user_model.objects.create_user(username, email=email, password=password, is_staff=True)
    group = Group.objects.get(name=group_name)
    user.groups.add(group)

    # add an extra field so we can later login with user.password
    user.raw_password = password
    return user


# have this separate non-fixture function
# so that we can call it to setup non pytest data
def erp_setup(django_user_model):
    # for the erp to work, there are some users and group permissions that we need
    django_user_model.objects.create_user("vault")
    django_user_model.objects.create_user("split")
    django_user_model.objects.create_user("goldway")
    django_user_model.objects.create_user("gia")

    # create permission groups
    grader_group = Group.objects.create(name="grader")
    grader_group.permissions.add(
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
    )

    receptionist_group = Group.objects.create(name="receptionist")
    receptionist_group.permissions.add(
        Permission.objects.get(
            codename="view_entity", content_type=ContentType.objects.get(app_label="customers", model="entity")
        ),
        Permission.objects.get(
            codename="add_entity", content_type=ContentType.objects.get(app_label="customers", model="entity")
        ),
        Permission.objects.get(
            codename="view_receipt", content_type=ContentType.objects.get(app_label="grading", model="receipt")
        ),
        Permission.objects.get(
            codename="add_receipt", content_type=ContentType.objects.get(app_label="grading", model="receipt")
        ),
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
    )

    buyer_group = Group.objects.create(name="buyer")
    buyer_group.permissions.add(
        Permission.objects.get(
            codename="view_seller", content_type=ContentType.objects.get(app_label="purchases", model="seller")
        ),
        Permission.objects.get(
            codename="add_seller", content_type=ContentType.objects.get(app_label="purchases", model="seller")
        ),
        Permission.objects.get(
            codename="view_receipt", content_type=ContentType.objects.get(app_label="purchases", model="receipt")
        ),
        Permission.objects.get(
            codename="add_receipt", content_type=ContentType.objects.get(app_label="purchases", model="receipt")
        ),
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="purchases", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="purchases", model="parcel")
        ),
        Permission.objects.get(
            codename="change_parcel", content_type=ContentType.objects.get(app_label="purchases", model="parcel")
        ),
    )
    data_entry_group = Group.objects.create(name="data_entry")
    data_entry_group.permissions.add(
        Permission.objects.get(
            codename="view_split", content_type=ContentType.objects.get(app_label="grading", model="split")
        ),
        Permission.objects.get(
            codename="add_split", content_type=ContentType.objects.get(app_label="grading", model="split")
        ),
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="view_stone", content_type=ContentType.objects.get(app_label="grading", model="stone")
        ),
        Permission.objects.get(
            codename="add_stone", content_type=ContentType.objects.get(app_label="grading", model="stone")
        ),
    )
    vault_manager_group = Group.objects.create(name="vault_manager")
    vault_manager_group.permissions.add(
        Permission.objects.get(
            codename="view_split", content_type=ContentType.objects.get(app_label="grading", model="split")
        ),
        Permission.objects.get(
            codename="add_split", content_type=ContentType.objects.get(app_label="grading", model="split")
        ),
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="view_goldwayverification",
            content_type=ContentType.objects.get(app_label="grading", model="goldwayverification"),
        ),
        Permission.objects.get(
            codename="view_giaverification",
            content_type=ContentType.objects.get(app_label="grading", model="giaverification"),
        ),
        Permission.objects.get(
            codename="view_parceltransfer",
            content_type=ContentType.objects.get(app_label="ownerships", model="parceltransfer"),
        ),
        Permission.objects.get(
            codename="add_parceltransfer",
            content_type=ContentType.objects.get(app_label="ownerships", model="parceltransfer"),
        ),
    )
