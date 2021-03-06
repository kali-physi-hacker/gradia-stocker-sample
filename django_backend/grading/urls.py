from django.urls import path

from . import views

urlpatterns = [
    path("return_to_vault/<int:pk>/", views.ReturnToVaultView.as_view(), name="return_to_vault"),
    path("confirm_received/<int:pk>/", views.ConfirmReceivedView.as_view(), name="confirm_received"),
    path("close_receipt/<int:pk>/", views.CloseReceiptView.as_view(), name="close_receipt"),
    path("close_parcel/<int:pk>/", views.CloseParcelView.as_view(), name="close_parcel"),
    path("upload/all/", views.AllUploadView.as_view(), name="upload_all"),
    path("upload/filenames", views.FileNameUploadView.as_view(), name="upload_filenames"),
    path("upload/sarine/", views.SarineUploadView.as_view(), name="sarine_data_upload_url"),
    path("upload/basic_grading/", views.BasicGradingUploadView.as_view(), name="basic_grading_data_upload_url"),
    path("upload/gia_adjusting/", views.GIAGradingAdjustView.as_view(), name="gia_adjusting_data_upload_url"),
    path("upload/", views.BasicGradingUploadView.as_view(), name="upload_parcel_csv"),
    path("gw_grading_data_upload_url/", views.GWGradingAdjustView.as_view(), name="gw_grading_data_upload_url"),
    path("upload/errors/", views.errors_page, name="errors_page"),
    path("gw_data_upload_url/", views.GWGradingUploadView.as_view(), name="gw_data_upload_url"),
    path("upload/gia_grading/", views.GIAGradingUploadView.as_view(), name="gia_grading_data_upload_url"),
    path("upload/macro_filename", views.MacroFileNameUpload.as_view(), name="macro_filename"),
    path("upload/nano_filename", views.NanoFileNameUpload.as_view(), name="nano_filename"),
]
