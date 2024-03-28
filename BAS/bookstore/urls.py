from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView, LogoutView
# app_name = "bookstore"

urlpatterns = [
    # home page
    path('',views.index,name='home'),
    # search page
    path('search/',views.search, name='search'),
    # add a book to cart
    path("add_to_cart/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    # book details page
    path('book_details/<int:book_id>/', views.book_details, name='book_details'),
    # cart page
    path("cart/", views.cart, name="cart"), 
    # remove a book from cart
    path("remove_from_cart/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    # empty the cart
    path('clear-cart/', views.clear_cart_logout, name='clear_cart_logout'),
    # procure a new book page
    path('procure/',views.procure,name='procure'),
    # send procurement request
    path('send-procure-request/', views.send_procure_request, name='send_procure_request'),
    # request a book having less stock
    path('request_book/<int:book_id>/',views.request_book,name='request_book'),
    # proceed to buy and generate bill
    path('proceed_to_buy/', views.proceed_to_buy, name='proceed_to_buy'),

    # path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('start_shopping',views.start_shopping,name='start_shopping'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
