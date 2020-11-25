from django.urls import path

from . import views

urlpatterns = [
    path(
        "close_receipt/<int:pk>/",
        views.CloseReceiptView.as_view(),
        name="close_receipt",
    )
]
