from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Shape(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Rating(models.Model):
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], unique=True, default=3
    )

    def __str__(self):
        return str(self.value)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
    minimum_quantity = models.PositiveIntegerField(default=5)
    name = models.CharField(max_length=100)
    size = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000)])
    description = models.JSONField(default=dict)

    @property
    def discount_percent(self):
        if self.price > 0:
            return round((self.price - self.discount_price) / Decimal(self.price) * 100, 2)
        return 0

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.image.url
    

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_quantity = models.IntegerField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='order_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

