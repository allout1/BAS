from django import template

register = template.Library()

@register.filter
def books_by_genre(books, genre):
    """
    Filter books by genre.
    """
    return [book for book in books if book.genre == genre]