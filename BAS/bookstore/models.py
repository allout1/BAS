from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Book(models.Model):
    title= models.CharField(max_length=100)
    author= models.CharField(max_length=50)
    publisher= models.CharField(max_length=50)
    price= models.DecimalField(max_digits=8, decimal_places=2)
    isbn= models.CharField(max_length=13,unique=True)
    image= models.ImageField(upload_to='static/images',default='static/images/book.png')
    genre= models.CharField(max_length=50,default="")
    desc= models.CharField(max_length=1000,default="")

    def __str__(self):
        return self.title

@receiver(post_save, sender=Book)
def create_inventory(sender, instance, created, **kwargs):
    """
    Create an Inventory record when a new Book instance is created.
    """
    if created:
        Inventory.objects.create(book=instance, stock=0)
        Vendor_list.objects.create(book=instance)

class Inventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    rack_number = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.book.title} - {self.stock}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update corresponding Vendor_list stock
        try:
            vendor_list = Vendor_list.objects.get(book=self.book)
            vendor_list.stock = self.stock
            vendor_list.save()
        except Vendor_list.DoesNotExist:
            pass  # Handle the case where Vendor_list doesn't exist for this book


class RequestBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    requested_by = models.CharField(max_length=50)
    email= models.EmailField(default="")
    quantity= models.IntegerField(default=0)
    date_of_request= models.DateTimeField()

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
    genre= models.CharField(max_length=50,default="")

    def __str__(self):
        return f"{self.book_title}-{self.user_name}"

class Cart(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    revenue= models.DecimalField(max_digits=8, decimal_places=2,default=0)

    def __str__(self):
        return f"{self.book.title}-{self.quantity}"


class Sales(models.Model):
    date= models.DateTimeField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    revenue= models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.IntegerField(default=0)
    buyer_name= models.CharField(max_length=100,default="")

    def __str__(self):
        return f"{self.date} - {self.book.title}"

class Vendor(models.Model):
    name= models.CharField(max_length=100)
    email= models.EmailField()
    phone= models.IntegerField()
    address= models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Vendor_list(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    vendor= models.ForeignKey(Vendor,on_delete=models.CASCADE,null=True)
    threshold= models.IntegerField(default=20)
    stock= models.IntegerField(default=0)

    def __str__(self):
        return self.book.title
    




