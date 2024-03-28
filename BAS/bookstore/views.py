from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from bookstore import views
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Book,Cart,Inventory, Sales, ProcureBook, RequestBook, Vendor_list
from django.core.mail import send_mail
from django.conf import settings
import re
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.contrib.admin.views.decorators import staff_member_required
# from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('search')  # Redirect to the homepage
        messages.error(request, 'Email or password is incorrect')    
    return render(request, 'registration/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Username is already taken')
                return render(request, 'registration/register.html')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                login(request, user)
                return redirect('search')  # Redirect to the homepage
        else:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/register.html')
    return render(request, 'registration/register.html')

#---HOME-PAGE---#
def index(request):
    return render(request,'index.html') # return the home page

#---LOG-OUT-OF-ADMIN-PAGE---#
def logout_view(request):
  logout(request) # remove any authenticated user
  response = redirect('home') # redirect to the index.html page
  response.delete_cookie('example_cookie') # delete  the cookie named example_cookie
  return response

#---SEARCH-BOOKS---#
def search(request):
    query = request.GET.get('query') # get query from the form
    search_type = request.GET.get('search_type') # get the query type i.e. by author or title

    all_books = Book.objects.all()
    shuffled_books = random.sample(list(all_books), len(all_books))
    
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
        normal=1 # normal is the parameter which decides whether normal page is to be shown or searched results
    # render the page search.html  with the list of searched book
    return render(request, 'search.html', {'books': books, 'request': request, 'genres':genres, 'all_books':shuffled_books,'normal':normal})

#---SEARCH-TITLE---#
def search_books(request):
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
@login_required
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
    cart, created = Cart.objects.get_or_create(user=request.user,book=book,defaults={'quantity': quantity})
    
    if created:
        cart.quantity = quantity
        cart.revenue = quantity*book.price
    else:
        if(cart.quantity+quantity>book.inventory.stock):
            messages.error(request, f"Less stock for {book.title}")
            return redirect(request.META.get('HTTP_REFERER', 'search'))
        cart.quantity += quantity
        cart.revenue += quantity*book.price
    cart.save() # save the book with quantity in the Cart
    # give a success message that the book is added to the cart and redirect to the previous page
    messages.success(request, f"{book.title} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'search'))

#---CART-PAGE---#
@login_required
def cart(request):
    carts = Cart.objects.filter(user=request.user)

    total_price = sum(cart.book.price * cart.quantity for cart in carts)

    context = {
        'cart': carts,
        'total_price': total_price
    }

    return render(request, 'cart.html', context)


#---REMOVE-BOOK-FROM-CART---#
@login_required
def remove_from_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    book = cart.book

    cart.delete()

    messages.success(request, f"{book.title} removed from your cart.")
    return redirect('cart')

#---CLEAR-THE-ENTIRE-CART---#
@login_required
def clear_cart_logout(request):
    user = request.user
    if not user.is_superuser:
        Cart.objects.filter(user=user).delete()
        user.delete()
    else:
        Cart.objects.filter(user=user).delete()
    logout(request)
    return redirect('home')

def start_shopping(request):
    logout(request)
    return redirect('home')

#---REQUEST-FOR-A-NEW-BOOK---#
@login_required
def procure(request):
    return render(request,'procurement.html')

@login_required
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
@login_required
def proceed_to_buy(request):
    cart = Cart.objects.filter(user=request.user)
    if request.method =='POST': # get the name of buyer, email and phone number from the form

        if not cart.exists():
            messages.error(request, "Your cart is empty or Transaction is over...")
            return redirect('cart')

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        for cart_item in cart:
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
        total_price = sum(cart_item.book.price * cart_item.quantity for cart_item in cart)
        # fill the bill content
        bill_email="\n"
        bill_date= timezone.now().date()
        bill_time= timezone.now().time()

        for cart_item in cart:
            bill_email+=f"{cart_item.book.title} X {cart_item.quantity} - ₹{cart_item.book.price * cart_item.quantity}\n"  #inside loop
            sales= Sales.objects.create(date=timezone.now(),book=cart_item.book,quantity=cart_item.quantity,revenue=cart_item.book.price * cart_item.quantity,buyer_name=name)
            sales.save()
        bill_email+=f"\nTotal: ₹{total_price}"# just outside loop

        #email sending procedure
        subject = 'Bill for your purchase'
        message = f'Hi {name}, thank you for buying.\nYour purchase is:\n{bill_email}\n\n Visit us Again'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )

        context = {
            'bill_content': bill_email,
            'bill_date': bill_date,
            'bill_time': bill_time,
            'buyer_name': name,
            'cart_items': cart,
            'total_price': total_price
        }
         # delete the cart
        cart.delete()
        return render(request, 'bill.html', context)
    else:
        return redirect('cart')

#---OPEN-BOOK_DETAILS-PAGE---#
def book_details(request,book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_details.html',{'book':book})

#---REQUEST-BOOK-IF-STOCK-OUT---#
@login_required
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

# @staff_member_required
# def book_threshold_page(request):
#     # Calculate the date range for the last two weeks
#     two_weeks_ago = timezone.now() - timedelta(days=14)
    
#     # Retrieve all books and calculate their threshold
#     books = Book.objects.all()
#     books_below_threshold = []

#     for book in books:
#         # vendor_list= Vendor_list.objects.get(book=book)
#         # Count the number of sales for the book in the last two weeks
#         sales_count = Sales.objects.filter(book=book, date__gte=two_weeks_ago).count()
#         # Calculate the threshold for the book
#         threshold = 20 + sales_count

#         try:
#         # Access the related Vendor_list
#             vendor_list = book.vendor_list  # This will return the related Vendor_list instance
#         except ObjectDoesNotExist:
#             # Handle the case where the related Vendor_list does not exist
#             Vendor_list.objects.create(book=book)  # or take appropriate action based on your application logic
#             vendor_list= book.vendor_list

#         vendor_list.threshold=threshold
#         # If the quantity is less than the threshold, add the book to the list
#         if book.inventory.stock < threshold:
#             books_below_threshold.append(book)

#     return render(request, 'book_threshold.html', {'books_below_threshold': books_below_threshold})