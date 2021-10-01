from django.urls import path

from . import views

urlpatterns = [
    path("transfer/upload/all/", views.AllUploadView.as_view(), name="transfer_upload_all_url"),
    path("transfer/upload/goldway/", views.GoldwayTransferView.as_view(), name="goldway_transfer_upload_url"),
]
