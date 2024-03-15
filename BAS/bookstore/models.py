from django.db import models

# Create your models here.
class Book(models.Model):
    title= models.CharField(max_length=50)
    author= models.CharField(max_length=50)
    publisher= models.CharField(max_length=50)
    price= models.DecimalField(max_digits=8, decimal_places=2)
    isbn= models.CharField(max_length=13,unique=True)
    image= models.ImageField(upload_to='static/images')

    def __str__(self):
        return self.title

class RequestBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    requested_by = models.CharField(max_length=50)
    date_of_request= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title}-{self.requested_by}"

class ProcureBook(models.Model):
    user_name= models.CharField(max_length=50)
    email= models.EmailField()
    phone_no= models.IntegerField()
    book_title= models.CharField(max_length=50)
    author_name= models.CharField(max_length=50)
    book_publisher= models.CharField(max_length=50)
    book_isbn= models.CharField(max_length=13,default="")

    def __str__(self):
        return f"{self.book_title}-{self.username}"

class Cart(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Inventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    stock = models.IntegerField()
    rack_number = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.book.title} - {self.stock}"

class Sales(models.Model):
    date= models.DateTimeField()
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    revenue= models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.book.title}"

