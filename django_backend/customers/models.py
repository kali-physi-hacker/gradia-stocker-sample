from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Entity(models.Model):
    class Relationship(models.TextChoices):
        SUPPLIER = "S", "Supplier"
        CUSTOMER = "C", "Customer"

    name = models.CharField(max_length=255)
    address = models.TextField()
    remarks = models.TextField()
    phone = models.CharField(max_length=11)
    email = models.CharField(max_length=255)
    relationship = models.CharField(max_length=1, choices=Relationship.choices)

    def customer_code(self):
        return None

    def __str__(self):
        return self.name


class AuthorizedPersonnel(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    position = models.CharField(max_length=11)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=11)
    hkid = models.CharField(max_length=10)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.entity} - {self.position})"


class Consignment(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    receipt_number = models.CharField(max_length=15)
    intake_date = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(null=True, blank=True)
    intake_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="consignment_intake")
    release_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="consignment_release", null=True, blank=True
    )

    def __str__(self):
        return "consignment " + self.receipt_number


class Parcel(models.Model):
    ### upon intake
    consignment = models.ForeignKey(Consignment, on_delete=models.PROTECT)
    name = models.CharField(max_length=15)
    code = models.CharField(max_length=15)
    reference_price_per_carat = models.PositiveIntegerField()
    total_carats = models.DecimalField(max_digits=5, decimal_places=3)
    total_pieces = models.IntegerField()

    ### upon release
    rejected_carats = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    rejected_pieces = models.IntegerField(null=True, blank=True)
    basic_graded_carats = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    basic_graded_pieces = models.IntegerField(null=True, blank=True)
    triple_verified_carats = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    triple_verified_pieces = models.IntegerField(null=True, blank=True)
    total_price_paid = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"parcel {self.name} ({self.total_carats}ct, {self.total_pieces}pcs, {self.consignment})"
