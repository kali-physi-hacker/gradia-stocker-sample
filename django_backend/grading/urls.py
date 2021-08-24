from django.urls import path

from . import views


urlpatterns = [
    path("return_to_vault/<int:pk>/", views.ReturnToVaultView.as_view(), name="return_to_vault"),
    path("confirm_received/<int:pk>/", views.ConfirmReceivedView.as_view(), name="confirm_received"),
    path("close_receipt/<int:pk>/", views.CloseReceiptView.as_view(), name="close_receipt"),
    path("upload/sarine/", views.SarineUploadView.as_view(), name="sarine_data_upload_url"),
    path("upload/", views.UploadBasicParcelCSVFile.as_view(), name="upload_parcel_csv"),
]
