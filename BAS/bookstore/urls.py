from django.contrib import admin
from django.urls import path, include
from . import views

# app_name = "bookstore"

urlpatterns = [
    path('',views.index,name='home'),
    path('search/',views.search, name='search'),
    path("cart/", views.cart, name="cart"),
    path("add_to_cart/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
]