from django.contrib import admin
from bookstore.models import Book,RequestBook,ProcureBook,Cart,Inventory,Sales, Vendor, Vendor_list
from datetime import datetime,timedelta
from rangefilter.filters import DateRangeFilter
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.db.models import Sum, F 



# admin.site.register(Book)
# admin.site.register(RequestBook)
admin.site.register(ProcureBook)
# admin.site.register(Cart)
# admin.site.register(Inventory)
# admin.site.register(Sales)
# admin.site.register(Vendor)
# admin.site.register(Vendor_list)


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('date', 'book','buyer_name', 'revenue', 'quantity')
    ordering= ('-date',)  # Hierarchical date-based navigation

    list_filter=(
        ("date",DateRangeFilter), 
        "book" 
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

class ThresholdFIlter(admin.SimpleListFilter):
    title= _("Threshold")
    parameter_name= "threshold"

    def lookups(self,request,model_admin):
        return[
            ("threshold",("Update threshold and Show books below threshold"))
        ]

    def queryset(self,request,queryset):
        if self.value()=="threshold":
            # Calculate the date range for the last two weeks
            two_weeks_ago = timezone.now() - timedelta(days=14)

            # Query to get the count of books sold in the last two weeks
            books_sold = Sales.objects.filter(
                date__gte=two_weeks_ago,
            ).values('book').annotate(total_sold=Sum('quantity'))

            # Dictionary to store the updated thresholds for each book
            updated_thresholds = {}

            for book_sold in books_sold:
                book_id = book_sold['book']
                total_sold = book_sold['total_sold']
                new_threshold = 20 + total_sold
                updated_thresholds[book_id] = new_threshold

            # Update the threshold for each book
            for book_id, new_threshold in updated_thresholds.items():
                Vendor_list.objects.filter(book_id=book_id).update(threshold=new_threshold)

            # Filter books below threshold
            books_below_threshold = Vendor_list.objects.filter(book__inventory__stock__lt=F('threshold'))

            return books_below_threshold

@admin.register(Vendor_list)
class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'vendor','threshold')
    list_filter= [ThresholdFIlter]

@admin.register(Vendor)
class RequestBookAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    
