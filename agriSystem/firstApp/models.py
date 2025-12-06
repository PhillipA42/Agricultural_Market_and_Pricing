from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    
    in_stock = models.PositiveIntegerField()
    
    expiry_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    image = models.ImageField(upload_to='product_images/')

    #DELIVERY STATUS
    on_delivery = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.price * Decimal(self.in_stock)

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"