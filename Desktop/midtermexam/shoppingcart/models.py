from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    pass

class Product(models.Model):
    product_name = models.CharField(max_length=256)
    description = models.CharField(max_length=64)
    img_url = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return f"{self.product_name}: {self.description}"

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_cart", null=True)

    def __str__(self):
        return f"{self.customer} Cart No. {self.id}"

class Cart_Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="corresponding_cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="selected_item")
    quantity = models.IntegerField(null=False, default=0)

    def computed_price(self):
        return f"{self.product.price * self.quantity}"
    def computed_weight(self):
        return f"{self.product.weight * self.quantity}"
    def __str__(self):
        return f"ID no. {self.id}: {self.product} x {self.quantity}"

class Shipping(models.Model):
    min_weight = models.FloatField()
    max_weight = models.FloatField()
    price = models.FloatField()

    def __str__(self):
        return f"Shipping Type No. {self.id}: MinWeight = {self.min_weight}, MaxWeight = {self.max_weight}, Price = {self.price}"

class Shipping_Details(models.Model):
    shipping_type = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name="shipping_reference")
    shipment_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_shipment")
    full_name = models.CharField(max_length=35)
    address1 = models.CharField(max_length=35)
    address2 = models.CharField(max_length=35, blank=True)
    address3 = models.CharField(max_length=35, blank=True)
    city = models.CharField(max_length=35)
    state = models.CharField(max_length=35)
    country = models.CharField(max_length=35, default="Philippines")

    def __str__(self):
        return f"Shipping Detail No {self.id}:{self.full_name}"

class Job_Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_owner")
    shipping_details = models.ForeignKey(Shipping_Details, on_delete=models.CASCADE, related_name="shipping_details")

    def __str__(self):
        return f"Order No {self.id}: {self.customer}'s parcel"

class Job_Items(models.Model):
    order_id = models.ForeignKey(Job_Order, on_delete=models.CASCADE, related_name="respective_order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="job_product")
    quantity = models.IntegerField()

    def computed_price(self):
        return f"{self.product.price * self.quantity}"
    def computed_weight(self):
        return f"{self.product.weight * self.quantity}"
    def __str__(self):
        return f"Job Order {self.order_id}: Item No. {self.id} x {self.quantity}"