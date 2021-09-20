from django.urls import path

from . import views


urlpatterns = [
    path("return_to_vault/<int:pk>/", views.ReturnToVaultView.as_view(), name="return_to_vault"),
    path("confirm_received/<int:pk>/", views.ConfirmReceivedView.as_view(), name="confirm_received"),
    path("close_receipt/<int:pk>/", views.CloseReceiptView.as_view(), name="close_receipt"),
    path("upload/all/", views.AllUploadView.as_view(), name="upload_all"),
    path("upload/sarine/", views.SarineUploadView.as_view(), name="sarine_data_upload_url"),
    path("upload/basic_grading/", views.BasicGradingUploadView.as_view(), name="basic_grading_data_upload_url"),
    path("upload/", views.BasicGradingUploadView.as_view(), name="upload_parcel_csv"),
    path("upload/errors/", views.errors_page, name="errors_page"),
]
