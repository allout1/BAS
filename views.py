#---SEARCH-AUTHORS---#
def search_author(request):
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
    print(books)
    # render the page search.html  with the list of searched book
    return render(request, 'search.html', {'books': books, 'request': request})
