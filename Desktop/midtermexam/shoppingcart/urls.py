from . import views
from django.urls import path

app_name = "Shop"
urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('register', views.register_view, name="register"),
    path('logout', views.logout_view, name="logout"),
    path('products/<int:product_id>', views.product_view, name="product_details"),
    path('cart', views.cart_view, name="cart"),
    path('shipping', views.shipping_view, name="shipping"),
    path('delete/<str:item_name>', views.delete_item, name="delete"),
    path('payment', views.payment_view, name="payment"),
    path('confirmation', views.confirmation_view, name="confirmation")
]