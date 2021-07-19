from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("ToS", views.tos_view, name="ToS"),
    path("create", views.create, name="create"),
    path("user_listings", views.own_listings, name="my_listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.filtered_view, name="filtered"),
    path("listings/<int:listing_id>", views.listing_view, name="listing"),
    path("claim_item/<str:item_name>", views.email_view, name="email")
]
