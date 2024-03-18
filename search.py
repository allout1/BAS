#---SEARCH-BOOKS---#
def search(request):
    q1 = search_authors(request)
    q2 = search_books(request)
    books = q1.union(q2)
    return render(request, 'search.html', {'books': books, 'request': request})
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
    y = ".*"
    result = list()
    for i in query:
        y += (i+  ".*")
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
    query = query.replace(' ','')
    query = query.replace('.','')
    query = query.lower()
    if query: # search for the book either by author name or title in the books table of db
        books = {str(book[0]) for book in Book.objects.values_list('author')}
    else:
        books = {}
    y = ".*"
    result = list()
    for i in query:
        y += (i+  ".*")
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
