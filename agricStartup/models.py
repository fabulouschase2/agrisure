from django.db import models
from django.contrib.auth.models import AbstractUser

class Farmer(AbstractUser):
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    farm_size = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.username

class Crop(models.Model):
    name = models.CharField(max_length=50)
    average_yield_per_hectare = models.FloatField()
    market_price_per_ton = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class FarmInput(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    farm_size = models.FloatField()
    input_cost = models.FloatField()
    season_duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.username} - {self.crop.name}"

class LoanRequest(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    amount_requested = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ('approved', 'Approved'),
        ('conditional', 'Conditional'),
        ('rejected', 'Rejected')
    ])
    risk_level = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.username} - {self.status}"