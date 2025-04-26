from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Portfolio(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, blank=True, null=True)
    cash_balance = models.FloatField(default=0.0)  # ✅ Added Cash Balance

    def __str__(self):
        return f"{self.client.name}'s Portfolio"

class Stock(models.Model):
    id = models.BigAutoField(primary_key=True)
    parent_portfolio = models.ForeignKey(Portfolio, related_name="stocks", on_delete=models.CASCADE, null=True, blank=True)
    stock_symbol = models.CharField(max_length=100, null=True)
    stock_price = models.CharField(max_length=100, null=True, blank=True)
    stock_sector_performance = models.CharField(max_length=100, null=True, blank=True)
    stock_name = models.CharField(max_length=100, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.stock_name if self.stock_name else f"Stock {self.id}"
