from django.contrib import admin
from django.urls import path, include
from . import views

# app_name = "bookstore"

urlpatterns = [
    path('',views.index,name='home'),
    path('search/',views.search, name='search'),
    path("cart/", views.cart, name="cart"),
    path("add_to_cart/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:book_id>/", views.remove_from_cart, name="remove_from_cart"),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('procure/',views.procure,name='procure'),
    path('proceed_to_buy/', views.proceed_to_buy, name='proceed_to_buy'),
    path('send-procure-request/', views.send_procure_request, name='send_procure_request'),
]