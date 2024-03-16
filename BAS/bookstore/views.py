from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from bookstore import views
from django.db.models import Q
from django.utils import timezone
from .models import Book,Cart,Inventory, Sales

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

def remove_from_cart(request, book_id):
    # Retrieve the cart item associated with the book_id
    cart_item = get_object_or_404(Cart, id=book_id)

    # Delete the cart item
    cart_item.delete()

    # Redirect the user to the cart page
    return redirect('cart')

def clear_cart(request):
    Cart.objects.all().delete()
    return redirect('search')

def procure(request):
    return render(request,'procurement.html')

def proceed_to_buy(request):
    if request.method =='POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        cart_items = Cart.objects.all()
        for cart_item in cart_items:
            book = cart_item.book
            inventory = Inventory.objects.get(book=book)
            if inventory.stock >= cart_item.quantity:
                inventory.stock -= cart_item.quantity
                inventory.save()
            else:
                # Handle insufficient stock situation
                return HttpResponse("Insufficient stock for some items. Please try again.")
        
        total_price = sum(cart_item.book.price * cart_item.quantity for cart_item in cart_items)
        bill_content = f"Buyer Name: {name}<br>Email: {email}<br>Phone Number: {phone}<br><br>Items:<br>"
        for cart_item in cart_items:
            bill_content += f"{cart_item.book.title} - {cart_item.quantity} - {cart_item.book.price * cart_item.quantity}<br>"
            sales= Sales.objects.create(date=timezone.now(),book=cart_item.book,quantity=cart_item.quantity,revenue=cart_item.book.price * cart_item.quantity)
            sales.save()
        bill_content += f"<br>Total: ${total_price}"

        Cart.objects.all().delete()

        # Return the generated bill
        return HttpResponse(bill_content)
    else:
        return HttpResponse("Invalid request method.")