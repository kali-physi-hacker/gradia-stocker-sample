from datetime import datetime

from django.shortcuts import render

# Create your views here.


def confirm_stones_checked(self, request, obj):
    if "_confirm_transfer" in request.POST:
        assert request.user == obj.to_user
        assert obj.confirmed_date is None
        obj.confirmed_date = datetime.now()
        obj.save()
    return super().response_change(request, obj)
