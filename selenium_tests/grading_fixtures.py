import pytest
from customers.models import Entity
from grading.models import (
    ClarityGrades,
    ColorGrades,
    CuletGrades,
    FluorescenceGrades,
    GeneralGrades,
    GirdleGrades,
    Parcel,
    Receipt,
    Split,
    Stone,
)
from ownerships.models import ParcelTransfer, StoneTransfer

from stonegrading.models import Inclusion
from stonegrading.grades import Inclusions


@pytest.fixture
def receipt(django_user_model, erp, admin_user):
    return receipt_setup(django_user_model, admin_user)


# have this separate non-fixture function
# so that we can call it to setup non pytest data
def receipt_setup(django_user_model, admin_user):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
        code="VK-0001",
        intake_by=admin_user,
    )

    created_receipt_2 = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
        code="VK-0002",
        intake_by=admin_user,
    )

    parcel = Parcel.objects.create(
        receipt=created_receipt,
        gradia_parcel_code="123456789",
        customer_parcel_code="cust-parcel-1",
        total_carats=2,
        total_pieces=2,
        reference_price_per_carat=1,
    )
    parcel_2 = Parcel.objects.create(
        receipt=created_receipt_2,
        gradia_parcel_code="parcel1",
        customer_parcel_code="cust-parcel-2",
        total_carats=6,
        total_pieces=8,
        reference_price_per_carat=3,
    )

    # the parcel is received by admin user and put into the vault
    ParcelTransfer.objects.create(
        item=parcel,
        from_user=admin_user,
        to_user=django_user_model.objects.get(username="vault"),
        created_by=admin_user,
    )

    ParcelTransfer.objects.create(
        item=parcel_2,
        from_user=admin_user,
        to_user=django_user_model.objects.get(username="vault"),
        created_by=admin_user,
    )
    # vault confirms it has received this parcel
    ParcelTransfer.confirm_received(parcel)
    created_receipt.parcel_set.add(parcel)
    ParcelTransfer.confirm_received(parcel_2)
    created_receipt.parcel_set.add(parcel_2)
    return created_receipt


@pytest.fixture
def stones(django_user_model, receipt, data_entry_clerk, grader, receptionist):
    return stones_setup(django_user_model, receipt, data_entry_clerk, grader, receptionist)


# have this separate non-fixture function
# so that we can call it to setup non pytest data
def stones_setup(django_user_model, receipt, data_entry_clerk, grader, receptionist):
    parcel = receipt.parcel_set.get(gradia_parcel_code="123456789")
    split = Split.objects.create(original_parcel=parcel, split_by=data_entry_clerk)
    # import pdb; pdb.set_trace()
    stone_list = [
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=67,
            grader_1=grader,
            split_from=split,
            basic_carat=4,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            basic_culet=CuletGrades.VERY_SMALL,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            table_size=43,
            crown_angle=23,
            pavilion_angle=54,
            star_length=24,
            lower_half=94,
            girdle_thick=1,
            girdle_min=1.84,
            girdle_max=3.32,
            girdle_grade=GirdleGrades.THIN,
            culet_size=0.85,
            crown_height=53,
            pavilion_depth=23,
            total_depth=43,
            table_size_pct=53,
            table_size_pct_grade=GeneralGrades.EXCELLENT,
            crown_angle_degree=38.3,
            crown_angle_degree_grade=GeneralGrades.GOOD,
            pavilion_angle_degree=41,
            pavilion_angle_degree_grade=GeneralGrades.EXCELLENT,
            star_length_pct=50,
            star_length_pct_grade=GeneralGrades.FAIR,
            lower_half_pct=70,
            lower_half_pct_grade=GeneralGrades.GOOD,
            girdle_thick_pct=4,
            girdle_thick_pct_grade=GeneralGrades.EXCELLENT,
            girdle_min_description=GirdleGrades.MEDIUM,
            culet_size_description=CuletGrades.MULTI_CHOICES[0][0],
            crown_height_pct=12.5,
            crown_height_pct_grade=GeneralGrades.EXCELLENT,
            pavilion_depth_pct=43,
            total_depth_pct=60.9,
            total_depth_pct_grade=GeneralGrades.POOR,
            parameter_cut_grade=GeneralGrades.VERY_GOOD,
            est_table_cut_grade=GeneralGrades.EXCELLENT,
            gradia_cut=GeneralGrades.GOOD,
            final_gradia_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            final_sarine_cut=GeneralGrades.EXCELLENT,
            sarine_symmetry=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size_dev=0.8,
            table_size_dev_grade=GeneralGrades.VERY_GOOD,
            crown_angle_dev=1,
            crown_angle_dev_grade=GeneralGrades.GOOD,
            pavilion_angle_dev=0.9,
            pavilion_angle_dev_grade=GeneralGrades.EXCELLENT,
            star_length_dev=7.2,
            star_length_dev_grade=GeneralGrades.GOOD,
            lower_half_dev=2.9,
            lower_half_dev_grade=GeneralGrades.EXCELLENT,
            girdle_thick_dev=1.1,
            girdle_thick_dev_grade=GeneralGrades.EXCELLENT,
            crown_height_dev=0.8,
            crown_height_dev_grade=GeneralGrades.GOOD,
            pavilion_depth_dev=0.8,
            pavilion_depth_dev_grade=GeneralGrades.EXCELLENT,
            misalignment=1,
            misalignment_grade=GeneralGrades.GOOD,
            table_edge_var=1,
            table_edge_var_grade=GeneralGrades.GOOD,
            table_off_center=1,
            table_off_center_grade=GeneralGrades.GOOD,
            culet_off_center=1,
            culet_off_center_grade=GeneralGrades.GOOD,
            table_off_culet=1,
            table_off_culet_grade=GeneralGrades.GOOD,
            star_angle=1,
            star_angle_grade=GeneralGrades.GOOD,
            upper_half_angle=1,
            upper_half_angle_grade=GeneralGrades.GOOD,
            lower_half_angle=1,
            lower_half_angle_grade=GeneralGrades.GOOD,
        ),
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=68,
            grader_1=grader,
            split_from=split,
            basic_carat=4,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            basic_culet=CuletGrades.VERY_SMALL,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            table_size=43,
            crown_angle=23,
            pavilion_angle=54,
            star_length=24,
            lower_half=94,
            girdle_thick=1,
            girdle_min=1.84,
            girdle_max=3.32,
            girdle_grade=GirdleGrades.THIN,
            culet_size=0.85,
            crown_height=53,
            pavilion_depth=23,
            total_depth=43,
            table_size_pct=53,
            table_size_pct_grade=GeneralGrades.EXCELLENT,
            crown_angle_degree=38.3,
            crown_angle_degree_grade=GeneralGrades.GOOD,
            pavilion_angle_degree=41,
            pavilion_angle_degree_grade=GeneralGrades.EXCELLENT,
            star_length_pct=50,
            star_length_pct_grade=GeneralGrades.FAIR,
            lower_half_pct=70,
            lower_half_pct_grade=GeneralGrades.GOOD,
            girdle_thick_pct=4,
            girdle_thick_pct_grade=GeneralGrades.EXCELLENT,
            girdle_min_description=GirdleGrades.MEDIUM,
            culet_size_description=CuletGrades.MULTI_CHOICES[0][0],
            crown_height_pct=12.5,
            crown_height_pct_grade=GeneralGrades.EXCELLENT,
            pavilion_depth_pct=43,
            total_depth_pct=60.9,
            total_depth_pct_grade=GeneralGrades.POOR,
            parameter_cut_grade=GeneralGrades.VERY_GOOD,
            est_table_cut_grade=GeneralGrades.EXCELLENT,
            gradia_cut=GeneralGrades.GOOD,
            final_gradia_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            final_sarine_cut=GeneralGrades.EXCELLENT,
            sarine_symmetry=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size_dev=0.8,
            table_size_dev_grade=GeneralGrades.VERY_GOOD,
            crown_angle_dev=1,
            crown_angle_dev_grade=GeneralGrades.GOOD,
            pavilion_angle_dev=0.9,
            pavilion_angle_dev_grade=GeneralGrades.EXCELLENT,
            star_length_dev=7.2,
            star_length_dev_grade=GeneralGrades.GOOD,
            lower_half_dev=2.9,
            lower_half_dev_grade=GeneralGrades.EXCELLENT,
            girdle_thick_dev=1.1,
            girdle_thick_dev_grade=GeneralGrades.EXCELLENT,
            crown_height_dev=0.8,
            crown_height_dev_grade=GeneralGrades.GOOD,
            pavilion_depth_dev=0.8,
            pavilion_depth_dev_grade=GeneralGrades.EXCELLENT,
            misalignment=1,
            misalignment_grade=GeneralGrades.GOOD,
            table_edge_var=1,
            table_edge_var_grade=GeneralGrades.GOOD,
            table_off_center=1,
            table_off_center_grade=GeneralGrades.GOOD,
            culet_off_center=1,
            culet_off_center_grade=GeneralGrades.GOOD,
            table_off_culet=1,
            table_off_culet_grade=GeneralGrades.GOOD,
            star_angle=1,
            star_angle_grade=GeneralGrades.GOOD,
            upper_half_angle=1,
            upper_half_angle_grade=GeneralGrades.GOOD,
            lower_half_angle=1,
            lower_half_angle_grade=GeneralGrades.GOOD,
        ),
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=69,
            grader_1=grader,
            split_from=split,
            basic_carat=4,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            basic_culet=CuletGrades.VERY_SMALL,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            table_size=43,
            crown_angle=23,
            pavilion_angle=54,
            star_length=24,
            lower_half=94,
            girdle_thick=1,
            girdle_min=1.84,
            girdle_max=3.32,
            girdle_grade=GirdleGrades.THIN,
            culet_size=0.85,
            crown_height=53,
            pavilion_depth=23,
            total_depth=43,
            table_size_pct=53,
            table_size_pct_grade=GeneralGrades.EXCELLENT,
            crown_angle_degree=38.3,
            crown_angle_degree_grade=GeneralGrades.GOOD,
            pavilion_angle_degree=41,
            pavilion_angle_degree_grade=GeneralGrades.EXCELLENT,
            star_length_pct=50,
            star_length_pct_grade=GeneralGrades.FAIR,
            lower_half_pct=70,
            lower_half_pct_grade=GeneralGrades.GOOD,
            girdle_thick_pct=4,
            girdle_thick_pct_grade=GeneralGrades.EXCELLENT,
            girdle_min_description=GirdleGrades.MEDIUM,
            culet_size_description=CuletGrades.MULTI_CHOICES[0][0],
            crown_height_pct=12.5,
            crown_height_pct_grade=GeneralGrades.EXCELLENT,
            pavilion_depth_pct=43,
            total_depth_pct=60.9,
            total_depth_pct_grade=GeneralGrades.POOR,
            parameter_cut_grade=GeneralGrades.VERY_GOOD,
            est_table_cut_grade=GeneralGrades.EXCELLENT,
            gradia_cut=GeneralGrades.GOOD,
            final_gradia_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            final_sarine_cut=GeneralGrades.EXCELLENT,
            sarine_symmetry=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size_dev=0.8,
            table_size_dev_grade=GeneralGrades.VERY_GOOD,
            crown_angle_dev=1,
            crown_angle_dev_grade=GeneralGrades.GOOD,
            pavilion_angle_dev=0.9,
            pavilion_angle_dev_grade=GeneralGrades.EXCELLENT,
            star_length_dev=7.2,
            star_length_dev_grade=GeneralGrades.GOOD,
            lower_half_dev=2.9,
            lower_half_dev_grade=GeneralGrades.EXCELLENT,
            girdle_thick_dev=1.1,
            girdle_thick_dev_grade=GeneralGrades.EXCELLENT,
            crown_height_dev=0.8,
            crown_height_dev_grade=GeneralGrades.GOOD,
            pavilion_depth_dev=0.8,
            pavilion_depth_dev_grade=GeneralGrades.EXCELLENT,
            misalignment=1,
            misalignment_grade=GeneralGrades.GOOD,
            table_edge_var=1,
            table_edge_var_grade=GeneralGrades.GOOD,
            table_off_center=1,
            table_off_center_grade=GeneralGrades.GOOD,
            culet_off_center=1,
            culet_off_center_grade=GeneralGrades.GOOD,
            table_off_culet=1,
            table_off_culet_grade=GeneralGrades.GOOD,
            star_angle=1,
            star_angle_grade=GeneralGrades.GOOD,
            upper_half_angle=1,
            upper_half_angle_grade=GeneralGrades.GOOD,
            lower_half_angle=1,
            lower_half_angle_grade=GeneralGrades.GOOD,
        ),
    ]
    for s in stone_list:
        StoneTransfer.objects.create(
            item=s,
            from_user=receptionist,
            to_user=django_user_model.objects.get(username="vault"),
            created_by=receptionist,
        )
    return stone_list


@pytest.fixture
def inclusions():
    inclusions = (choice[0] for choice in Inclusions.CHOICES)

    for inclusion in inclusions:
        Inclusion.objects.create(inclusion=inclusion)
    return inclusions


@pytest.fixture
def parcel(admin_user):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
        code="VK-0011",
        intake_by=admin_user,
    )
    parcel = Parcel.objects.create(
        receipt=created_receipt,
        customer_parcel_code="VK01",
        total_carats="50.000",
        total_pieces=50,
        reference_price_per_carat=5,
        gradia_parcel_code="sarine-01"
    ) 
    return parcel 

@pytest.fixture
def invalid_parcel(admin_user):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
        code="VK-0012",
        intake_by=admin_user,
    )
    invalid_parcel = Parcel.objects.create(
        receipt=created_receipt,
        customer_parcel_code="VK04",
        total_carats="50.000",
        total_pieces=70,
        reference_price_per_carat=2,
        gradia_parcel_code="sarine-01-type"
    ) 
    return invalid_parcel 