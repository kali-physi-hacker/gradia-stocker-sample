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
