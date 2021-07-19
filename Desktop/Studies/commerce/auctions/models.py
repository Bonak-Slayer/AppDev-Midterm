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
    image_file = models.ImageField(upload_to='images/')
    availability = models.BooleanField()
    item_lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_lister')
    item_category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    watchlist = models.ManyToManyField(User, blank=True, related_name='watch_list')

    def __str__(self):
        return f"Listing {self.id}: {self.item_name}, listed by {self.item_lister}"

    def short_desc(self):
        if self.description.__len__() > 25:
            return f"{self.description[0:24]}..."
        else:
            return self.description

    def short_title(self):
        if self.item_name.__len__() > 30:
            return f"{self.item_name[0:29]}..."
        else:
            return self.item_name

    def short_lister(self):
        if self.item_lister.username.__len__() > 15:
            return f"{self.item_lister.username[0:14]}"
        else:
            return self.item_lister.username

class Bid(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    is_maximum = models.BooleanField()

    def __str__(self):
        return f"Bidder: {self.bidder} Value: PHP{self.value}"

class Comment(models.Model):
    text = models.CharField(max_length=300)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.commenter} commented: {self.text}"

class Auctioned_Items(models.Model):
    auctioned_item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    new_owner = models.ForeignKey(Bid, on_delete=models.CASCADE)

    def __str__(self):
        return f"The item {self.auctioned_item.item_name}, listed by {self.auctioned_item.item_lister}, " \
            f"has been successfully auctioned off to {self.new_owner.bidder}"