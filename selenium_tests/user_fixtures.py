from collections import namedtuple

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import pytest

from grading.models import Entity, Receipt, Split
from purchases.models import Seller
from grading.models import Parcel


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
            codename="view_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
        Permission.objects.get(
            codename="add_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
    )

    receptionist_group = Group.objects.create(name="receptionist")
    receptionist_group.permissions.add(
        Permission.objects.get(
            codename="view_entity",
            content_type=ContentType.objects.get(app_label="customers", model="entity"),
        ),
        Permission.objects.get(
            codename="add_entity",
            content_type=ContentType.objects.get(app_label="customers", model="entity"),
        ),
        Permission.objects.get(
            codename="view_receipt",
            content_type=ContentType.objects.get(app_label="grading", model="receipt"),
        ),
        Permission.objects.get(
            codename="add_receipt",
            content_type=ContentType.objects.get(app_label="grading", model="receipt"),
        ),
        Permission.objects.get(
            codename="view_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
        Permission.objects.get(
            codename="add_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
    )

    buyer_group = Group.objects.create(name="buyer")
    buyer_group.permissions.add(
        Permission.objects.get(
            codename="view_seller",
            content_type=ContentType.objects.get(app_label="purchases", model="seller"),
        ),
        Permission.objects.get(
            codename="add_seller",
            content_type=ContentType.objects.get(app_label="purchases", model="seller"),
        ),
        Permission.objects.get(
            codename="view_receipt",
            content_type=ContentType.objects.get(
                app_label="purchases", model="receipt"
            ),
        ),
        Permission.objects.get(
            codename="add_receipt",
            content_type=ContentType.objects.get(
                app_label="purchases", model="receipt"
            ),
        ),
        Permission.objects.get(
            codename="view_parcel",
            content_type=ContentType.objects.get(app_label="purchases", model="parcel"),
        ),
        Permission.objects.get(
            codename="add_parcel",
            content_type=ContentType.objects.get(app_label="purchases", model="parcel"),
        ),
        Permission.objects.get(
            codename="change_parcel",
            content_type=ContentType.objects.get(app_label="purchases", model="parcel"),
        ),
    )
    data_entry_group = Group.objects.create(name="data_entry")
    data_entry_group.permissions.add(
        Permission.objects.get(
            codename="view_split",
            content_type=ContentType.objects.get(app_label="grading", model="split"),
        ),
        Permission.objects.get(
            codename="add_split",
            content_type=ContentType.objects.get(app_label="grading", model="split"),
        ),
        Permission.objects.get(
            codename="view_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
        Permission.objects.get(
            codename="view_stone",
            content_type=ContentType.objects.get(app_label="grading", model="stone"),
        ),
        Permission.objects.get(
            codename="add_stone",
            content_type=ContentType.objects.get(app_label="grading", model="stone"),
        ),
    )
    vault_manager_group = Group.objects.create(name="vault_manager")
    vault_manager_group.permissions.add(
        Permission.objects.get(
            codename="view_split",
            content_type=ContentType.objects.get(app_label="grading", model="split"),
        ),
        Permission.objects.get(
            codename="add_split",
            content_type=ContentType.objects.get(app_label="grading", model="split"),
        ),
        Permission.objects.get(
            codename="view_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
        Permission.objects.get(
            codename="add_parcel",
            content_type=ContentType.objects.get(app_label="grading", model="parcel"),
        ),
        Permission.objects.get(
            codename="view_goldwayverification",
            content_type=ContentType.objects.get(
                app_label="grading", model="goldwayverification"
            ),
        ),
        Permission.objects.get(
            codename="view_giaverification",
            content_type=ContentType.objects.get(
                app_label="grading", model="giaverification"
            ),
        ),
        Permission.objects.get(
            codename="view_parceltransfer",
            content_type=ContentType.objects.get(
                app_label="ownerships", model="parceltransfer"
            ),
        ),
        Permission.objects.get(
            codename="add_parceltransfer",
            content_type=ContentType.objects.get(
                app_label="ownerships", model="parceltransfer"
            ),
        ),
    )


@pytest.fixture
def erp(django_user_model):
    # have this separate non-fixture function
    # so that we can call it to setup
    erp_setup(django_user_model)


UserData = namedtuple("User", ["username", "password"])


@pytest.fixture
def grader(django_user_model, erp):
    user_data = UserData(username="grader", password="graderpassword")
    user = django_user_model.objects.create_user(
        user_data.username,
        email=user_data.username,
        password=user_data.password,
        is_staff=True,
    )
    grader_group = Group.objects.get(name="grader")
    user.groups.add(grader_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def receptionist(django_user_model, erp):
    user_data = UserData(username="receptionist", password="receptionistpassword")
    user = django_user_model.objects.create_user(
        user_data.username,
        email=user_data.username,
        password=user_data.password,
        is_staff=True,
    )
    receptionist_group = Group.objects.get(name="receptionist")
    user.groups.add(receptionist_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def buyer(django_user_model, erp):
    user_data = UserData(username="buyer", password="buyerpassword")
    user = django_user_model.objects.create_user(
        user_data.username,
        email=user_data.username,
        password=user_data.password,
        is_staff=True,
    )
    buyer_group = Group.objects.get(name="buyer")
    user.groups.add(buyer_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def data_entry_clerk(django_user_model, erp):
    user_data = UserData(username="dataentry", password="dataentrypassword")
    user = django_user_model.objects.create_user(
        user_data.username,
        email=user_data.username,
        password=user_data.password,
        is_staff=True,
    )
    data_entry_group = Group.objects.get(name="data_entry")
    user.groups.add(data_entry_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def vault_manager(django_user_model, erp):
    user_data = UserData(username="vaultmanager", password="vaultmanagerpassword")
    user = django_user_model.objects.create_user(
        user_data.username,
        email=user_data.username,
        password=user_data.password,
        is_staff=True,
    )
    vault_manager_group = Group.objects.get(name="vault_manager")
    user.groups.add(vault_manager_group)

    user.raw_password = user_data.password
    return user
