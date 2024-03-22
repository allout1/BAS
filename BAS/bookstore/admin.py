from django.contrib import admin
from bookstore.models import Book,RequestBook,ProcureBook,Cart,Inventory,Sales, Vendor, Vendor_list
from datetime import datetime

from rangefilter.filters import DateRangeFilter

# admin.site.register(Book)
# admin.site.register(RequestBook)
admin.site.register(ProcureBook)
admin.site.register(Cart)
# admin.site.register(Inventory)
# admin.site.register(Sales)
# admin.site.register(Vendor)
# admin.site.register(Vendor_list)


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('date', 'book', 'revenue', 'quantity')
    ordering= ('-date',)  # Hierarchical date-based navigation

    list_filter=(
        ("date",DateRangeFilter),    
    )

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'publisher','price')
    ordering= ('title',)  # Hierarchical date-based navigation
    search_fields= ('title','author','isbn','publisher','genre')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'stock', 'rack_number')
    ordering= ('rack_number',)  # Hierarchical date-based navigation

@admin.register(RequestBook)
class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('date_of_request', 'book', 'requested_by', 'quantity')
    ordering= ('date_of_request',)  # Hierarchical date-based navigation
    search_fields= ('requested_by',)

@admin.register(Vendor_list)
class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'vendor')

@admin.register(Vendor)
class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    