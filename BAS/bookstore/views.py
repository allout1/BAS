from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from bookstore import views
from django.db.models import Q
from .models import Book,Cart,Inventory

# Create your views here.
def index(request):
    return render(request,'index.html')

def search(request):
    query = request.GET.get('query')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    else:
        books = []
    return render(request, 'search.html', {'books': books, 'request': request})

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    quantity = request.POST.get('quantity')
    if not quantity:
        messages.error(request, "Please enter a quantity.")
        return redirect(request.META.get('HTTP_REFERER', 'search'))
    try:
        quantity = int(quantity)
    except ValueError:
        messages.error(request, "Invalid quantity.")
        return redirect(request.META.get('HTTP_REFERER', 'search'))
    cart, created = Cart.objects.get_or_create(book=book,defaults={'quantity': quantity})
    
    if created:
        cart.quantity = quantity
    else:
        cart.quantity += quantity
    cart.save()
    messages.success(request, f"{book.title} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'search'))

def cart(request):
    cart = Cart.objects.all()
    total_price=0
    for cart_item in cart:
        total_price+=cart_item.book.price * cart_item.quantity
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

def remove_from_cart(request):
    pass
