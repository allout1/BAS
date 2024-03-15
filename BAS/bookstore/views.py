from django.shortcuts import render
from bookstore import views

# Create your views here.
def index(request):
    return render(request,'index.html')

def customer(request):
    return render(request,'user.html')