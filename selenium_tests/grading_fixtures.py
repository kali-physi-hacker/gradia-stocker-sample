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
    stone_list = [
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=1,
            split_from=split,
            basic_carat=4,
            external_id="G0000001",
            carat_weight="0.008",
            color="F",
            basic_culet=CuletGrades.VERY_SMALL,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            grader_1=grader,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            girdle_min=GirdleGrades.THIN,
            girdle_max=GirdleGrades.THIN,
            girdle_grade=GirdleGrades.THIN,
            culet_size=CuletGrades.MEDIUM,
            total_depth=43,
            total_depth_grade=GeneralGrades.EXCELLENT,
            sheryl_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            cut_grade_est_table=GeneralGrades.EXCELLENT,
            sheryl_symmetry=GeneralGrades.GOOD,
            sarine_symmetry=GeneralGrades.GOOD,
            symmetry_grade=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size=43,
            table_size_grade=GeneralGrades.GOOD,
            crown_angle=23,
            crown_angle_grade=GeneralGrades.GOOD,
            pavilion_angle=54,
            pavilion_angle_grade=GeneralGrades.GOOD,
            star_length=24,
            star_length_grade=GeneralGrades.GOOD,
            lower_half=94,
            lower_half_grade=GeneralGrades.GOOD,
            girdle_thick=1,
            girdle_thick_grade=GeneralGrades.GOOD,
            crown_height=53,
            crown_height_grade=GeneralGrades.GOOD,
            pavilion_depth=23,
            pavilion_depth_grade=GeneralGrades.GOOD,
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
            internal_id=2,
            split_from=split,
            basic_carat=4,
            external_id="G0000002",
            carat_weight="0.009",
            color="G",
            basic_culet=CuletGrades.VERY_SMALL,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            grader_1=grader,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            girdle_min=GirdleGrades.THIN,
            girdle_max=GirdleGrades.THIN,
            girdle_grade=GirdleGrades.THIN,
            culet_size=CuletGrades.MEDIUM,
            total_depth=43,
            total_depth_grade=GeneralGrades.EXCELLENT,
            sheryl_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            cut_grade_est_table=GeneralGrades.EXCELLENT,
            sheryl_symmetry=GeneralGrades.GOOD,
            sarine_symmetry=GeneralGrades.GOOD,
            symmetry_grade=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size=43,
            table_size_grade=GeneralGrades.GOOD,
            crown_angle=23,
            crown_angle_grade=GeneralGrades.GOOD,
            pavilion_angle=54,
            pavilion_angle_grade=GeneralGrades.GOOD,
            star_length=24,
            star_length_grade=GeneralGrades.GOOD,
            lower_half=94,
            lower_half_grade=GeneralGrades.GOOD,
            girdle_thick=1,
            girdle_thick_grade=GeneralGrades.GOOD,
            crown_height=53,
            crown_height_grade=GeneralGrades.GOOD,
            pavilion_depth=23,
            pavilion_depth_grade=GeneralGrades.GOOD,
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
            internal_id=3,
            split_from=split,
            basic_carat=4,
            external_id="G0000003",
            carat_weight="0.089",
            color="F",
            basic_culet=CuletGrades.VERY_SMALL,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            grader_1=grader,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            girdle_min=GirdleGrades.THIN,
            girdle_max=GirdleGrades.THIN,
            girdle_grade=GirdleGrades.THIN,
            culet_size=CuletGrades.MEDIUM,
            total_depth=43,
            total_depth_grade=GeneralGrades.EXCELLENT,
            sheryl_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            cut_grade_est_table=GeneralGrades.EXCELLENT,
            sheryl_symmetry=GeneralGrades.GOOD,
            sarine_symmetry=GeneralGrades.GOOD,
            symmetry_grade=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size=43,
            table_size_grade=GeneralGrades.GOOD,
            crown_angle=23,
            crown_angle_grade=GeneralGrades.GOOD,
            pavilion_angle=54,
            pavilion_angle_grade=GeneralGrades.GOOD,
            star_length=24,
            star_length_grade=GeneralGrades.GOOD,
            lower_half=94,
            lower_half_grade=GeneralGrades.GOOD,
            girdle_thick=1,
            girdle_thick_grade=GeneralGrades.GOOD,
            crown_height=53,
            crown_height_grade=GeneralGrades.GOOD,
            pavilion_depth=23,
            pavilion_depth_grade=GeneralGrades.GOOD,
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
