from django.urls import path

from . import views

urlpatterns = [
    path("return_to_vault/<int:pk>/", views.ReturnToVaultView.as_view(), name="return_to_vault"),
    path("confirm_received/<int:pk>/", views.ConfirmReceivedView.as_view(), name="confirm_received"),
]
