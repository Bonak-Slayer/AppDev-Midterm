from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64)

    def __str__(self):
        return f"Category: {self.category_name}"

class Listing(models.Model):
    item_name = models.CharField(max_length=128)
    description = models.CharField(max_length=300)
    image_link = models.CharField(max_length=128, blank=True)
    availability = models.BooleanField()
    item_lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_lister')
    item_category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    watchlist = models.ManyToManyField(User, blank=True, related_name='watch_list')

    def __str__(self):
        return f"Listing {self.id}: {self.item_name}, listed by {self.item_lister}"

class Bid(models.Model):
    value = models.DecimalField(max_digits=6, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    is_maximum = models.BooleanField()

    def __str__(self):
        return f"Bidder: {self.bidder} Value: ${self.value}"

class Comment(models.Model):
    text = models.CharField(max_length=300)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.commenter} commented: {self.text}"
