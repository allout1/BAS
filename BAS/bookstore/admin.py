from django.contrib import admin
from bookstore.models import Book,RequestBook,ProcureBook,Cart,Inventory,Sales, Vendor, Vendor_list


admin.site.register(Book)
admin.site.register(RequestBook)
admin.site.register(ProcureBook)
admin.site.register(Cart)
admin.site.register(Inventory)
admin.site.register(Sales)
admin.site.register(Vendor)
admin.site.register(Vendor_list)

