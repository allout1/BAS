from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from bookstore import views
from django.db.models import Q
from django.utils import timezone
from .models import Book,Cart,Inventory, Sales, ProcureBook, RequestBook
from django.core.mail import send_mail
from django.conf import settings
import re
import random

# Create your views here.

#---HOME-PAGE---#
def index(request):
    return render(request,'index.html') # return the home page

#---SEARCH-BOOKS---#
def search(request):
    query = request.GET.get('query') # get query from the form
    all_books = Book.objects.all()
    books_list = list(all_books)
    shuffled_books = random.sample(list(all_books), len(all_books))
    
    search_type = request.GET.get('search_type')
    genres=['fiction','self-help','JEE','children']

    if query and search_type: # search for the book either by author name or title in the books table of db
        if search_type == 'author':
            books = search_authors(request)
        elif search_type == 'title':
            books = search_books(request)
        else:
            books = []
        normal = 0
    else: # if no query show the page with all the books
        books = []
        normal=1
    # render the page search.html  with the list of searched book
    return render(request, 'search.html', {'books': books, 'request': request, 'genres':genres, 'all_books':shuffled_books,'normal':normal})

#---SEARCH-TITLE---#
def search_books(request):
    print(Book.objects.all())
    query = str(request.GET.get('query')) # get query from the form
    query = query.replace(' ','')
    query = query.lower()
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('title')}
    else: 
        books = {}
    y = "[.*,-:()' ]*"
    result = list()
    for i in query:
        y += (i+  "[.*,-:()' ]*")
    for i in books:
        if(re.search(y,i.lower())):
            result.append(i)
    books = Book.objects.none()
    for i in result:
        r = Book.objects.filter(
            Q(title=i)
        )
        books = books.union(r)
    # render the page search.html  with the list of searched book
    return books

#---SEARCH-AUTHORS---#
def search_authors(request):
    query = str(request.GET.get('query')) # get query from the form
    query = query.replace('.',' ')
    query = query.replace(' ','')
    query = query.lower()
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('author')}
    else:
        books = {}
    y = "[.*,-:()' ]*"
    result = list()
    for i in query:
        y += (i+  "[.*,-:()' ]*")
    for i in books:
        if(re.search(y,i.lower())):
            result.append(i)
    books = Book.objects.none()
    for i in result:
        r = Book.objects.filter(
            Q(author=i)
        )
        books = books.union(r)
    # render the page search.html  with the list of searched book
    return books


#---ADD-A-BOOK-TO-CART---#
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id) # get the book from the Book db using id
    quantity = request.POST.get('quantity') # get the quantity asked for
    if not quantity:
        messages.error(request, "Please enter a quantity.") # if no quantity is entered return to the previous searched page
        return redirect(request.META.get('HTTP_REFERER', 'search'))
    try:
        quantity = int(quantity)
    except ValueError: # if entered quantity is not a valid integer give error and return to previous page
        messages.error(request, "Invalid quantity.")
        return redirect(request.META.get('HTTP_REFERER', 'search'))

    # if book already present in cart get its instance else create a new instance
    cart, created = Cart.objects.get_or_create(book=book,defaults={'quantity': quantity})
    
    if created:
        cart.quantity = quantity
    else:
        if(cart.quantity+quantity>book.inventory.stock):
            messages.error(request, f"Less stock for {book.title}")
            return redirect(request.META.get('HTTP_REFERER', 'search'))
        cart.quantity += quantity
    cart.save() # save the book with quantity in the Cart
    # give a success message that the book is added to the cart and redirect to the previous page
    messages.success(request, f"{book.title} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'search'))

#---CART-PAGE---#
def cart(request):
    cart = Cart.objects.all()
    total_price=0
    for cart_item in cart: # find the total price of the cart
        total_price+=cart_item.book.price * cart_item.quantity
    # render the cart.html page with the total_price 
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

#---REMOVE-BOOK-FROM-CART---#
def remove_from_cart(request, book_id):
    # Get the cart item associated with the book_id
    cart_item = get_object_or_404(Cart, id=book_id)
    # Delete the cart item
    cart_item.delete()
    # Redirect the user to the cart page
    return redirect('cart')

#---CLEAR-THE-ENTIRE-CART---#
def clear_cart(request):
    Cart.objects.all().delete()
    return redirect('search')

#---REQUEST-FOR-A-NEW-BOOK---#
def procure(request):
    return render(request,'procurement.html')

def send_procure_request(request):
    if request.method == 'POST':
        # Get data from the request
        user_name = request.POST.get('user_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        book_title = request.POST.get('book_title')
        author_name = request.POST.get('author_name')
        book_publisher = request.POST.get('book_publisher')
        book_isbn = request.POST.get('book_isbn')
        genre = request.POST.get('genre')

        # Create and save the ProcureBook object
        procure_book = ProcureBook.objects.create(
            user_name=user_name,
            email=email,
            phone_no=phone_no,
            book_title=book_title,
            author_name=author_name,
            book_publisher=book_publisher,
            book_isbn=book_isbn,
            genre=genre
        )
        procure_book.save()
        messages.success(request, f"Request sent for {book_title} ")
        # Optionally, you can add a success message here
        return redirect('procure')  # Redirect to a success page after form submission

    # If the request method is not POST, render the procurement.html template
    return render(request, 'procurement.html')


#---MAKE-BILL-AND-REDUCE-INVENTORY---#
def proceed_to_buy(request):
    if request.method =='POST': # get the name of buyer, email and phone number from the form

        if not Cart.objects.exists():
            messages.error(request, "Your cart is empty or Transaction is over...")
            return redirect('cart')

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        cart_items = Cart.objects.all()
        for cart_item in cart_items:
            book = cart_item.book
            inventory = Inventory.objects.get(book=book)
            # if inventory stock is greater than or equal to asked quantity reduce the inventory
            if inventory.stock >= cart_item.quantity:
                inventory.stock -= cart_item.quantity
                inventory.save()
            else:
                # Handle insufficient stock situation
                messages.error(request,"Insufficient stock for some items. Please try again.")
                return redirect('cart')
        
        # find the total price
        total_price = sum(cart_item.book.price * cart_item.quantity for cart_item in cart_items)
        # fill the bill content
        bill_email="\n"
        bill_date= timezone.now().date()
        bill_time= timezone.now().time()
        bill_email+="Date: " + str(bill_date) + "\n"
        bill_email+="Time: " + str(bill_time) + "\n"

        for cart_item in cart_items:
            bill_email+=f"{cart_item.book.title} X {cart_item.quantity} - ₹{cart_item.book.price * cart_item.quantity}\n"  #inside loop
            sales= Sales.objects.create(date=timezone.now(),book=cart_item.book,quantity=cart_item.quantity,revenue=cart_item.book.price * cart_item.quantity)
            sales.save()
        bill_email+=f"\nTotal: ₹{total_price}"# just outside loop

        #email sending procedure
        subject = 'Bill for your purchase'
        message = f'Hi {name}, thank you for buying.\nYour purchase is:\n{bill_email}\n\n Visit us Again'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )

        # delete the cart
        Cart.objects.all().delete()

        context = {
            'bill_content': bill_email,
            'bill_date': bill_date,
            'bill_time': bill_time,
            'buyer_name': name,
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, 'bill.html', context)
    else:
        return redirect('cart')

def book_details(request,book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_details.html',{'book':book})


def request_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        requested_by = request.POST.get('name')
        email = request.POST.get('email')
        quantity = int(request.POST.get('quantity'))

        if quantity <= 0:
            return render(request, 'your_template.html', {'error_message': 'Invalid quantity. Please enter a positive number.'})

        if quantity <= book.inventory.stock:
            messages.error(request, f"The quantity of {quantity} can be bought with the existing stock !")
            # If the requested quantity is available in stock, handle as a regular purchase
            # You may want to add your purchase logic here
            pass
        else:
            # If the requested quantity exceeds the stock, create a request
            messages.success(request, f"Request sent for {book.title}")
            RequestBook.objects.create(date_of_request=timezone.now(),book=book, requested_by=requested_by, email=email, quantity=quantity).save()

    # Redirect back to the book detail page
    return redirect(request.META.get('HTTP_REFERER', 'book_details'))