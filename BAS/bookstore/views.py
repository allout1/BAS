from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from bookstore import views
from django.db.models import Q
from django.utils import timezone
from .models import Book,Cart,Inventory, Sales, ProcureBook
import re
import datetime

# Create your views here.

#---HOME-PAGE---#
def index(request):
    return render(request,'index.html') # return the home page
#---SEARCH-BOOKS---#
def search(request):
    query = request.GET.get('query') # get query from the form
    all_books= Book.objects.all()
    search_type = request.GET.get('search_type')

    if query and search_type: # search for the book either by author name or title in the books table of db
        if search_type == 'author':
            books = search_authors(request)
        elif search_type == 'title':
            books = search_books(request)
        else:
            books = []
        normal = 0
    else:
        books = []
        normal=1
    # render the page search.html  with the list of searched book
    return render(request, 'search.html', {'books': books, 'request': request, 'genres':['fiction','self-help','JEE'], 'all_books':all_books,'normal':normal})
#---SEARCH-TITLE---#
def search_books(request):
    print(Book.objects.all())
    query = str(request.GET.get('query')) # get query from the form
    query = query.lower()
    query = query.split(' ')
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('title')}
    else: 
        books = {}
    y = "[.*,-:() ]*"
    result = list()
    for i in query:
        y += (i+  "[.*,-:() ]*")
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
    query = query.lower()
    query = query.split(' ')
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('author')}
    else:
        books = {}
    y = "[.*,-:() ]*"
    result = list()
    for i in query:
        y += (i+  "[.*,-:() ]*")
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
        book.quantity -= quantity
    else:
        cart.quantity += quantity
        book.quantity -= quantity
    cart.save() # save the book with quantity in the Cart
    book.save()
    # give a success message that the book is added to the cart and redirect to the previous page
    messages.success(request, f"{book.title} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'search'))

#---CART-PAGE---#
def cart(request):
    cart = Cart.objects.all()
    print(cart)
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
                return HttpResponse("Insufficient stock for some items. Please try again.")
        
        # find the total price
        total_price = sum(cart_item.book.price * cart_item.quantity for cart_item in cart_items)
        # fill the bill content
        bill_content = f"Buyer Name: {name}<br>Email: {email}<br>Phone Number: {phone}<br><br>Items:<br>"
        for cart_item in cart_items:
            bill_content += f"{cart_item.book.title} - {cart_item.quantity} - {cart_item.book.price * cart_item.quantity}<br>"
            sales= Sales.objects.create(date=timezone.now(),book=cart_item.book,quantity=cart_item.quantity,revenue=cart_item.book.price * cart_item.quantity)
            sales.save()
        bill_content += f"<br>Total: ${total_price}"

        # delete the cart
        Cart.objects.all().delete()

        # Return the generated bill
        return HttpResponse(bill_content)
    else:
        return HttpResponse("Invalid request method.")
#---THRESHOLD--CALCULATION---#   
def threshold(request):
    today = datetime.date.today()
    two_weeks_ago = today-datetime.timedelta(days = 14)
    books = Sales.objects.filter(date__gte= two_weeks_ago,date__lte = today)
    sales = dict()
    for i in books:
        sales[i.book.isbn] = 0
    for i in books:
        sales[i.book.isbn] += i.quantity
    threshold = dict()
    for i in sales:
        proc_time = 20
        threshold[Book.objects.filter(Q(isbn = i))] = sales[i] + proc_time
    return render(request, 'threshold.html', {'threshold': threshold})
    



