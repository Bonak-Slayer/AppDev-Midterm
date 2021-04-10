from django.contrib import admin
from .models import User, Product, Cart, Cart_Item, Shipping, Shipping_Details, Job_Order, Job_Items
# Register your models here.
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Cart_Item)
admin.site.register(Shipping)
admin.site.register(Shipping_Details)
admin.site.register(Job_Order)
admin.site.register(Job_Items)