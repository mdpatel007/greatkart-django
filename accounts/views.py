from django.shortcuts import render
from accounts.models import Banner
from store.models import Product

# Create your views here.
def home(request):
    banners = Banner.objects.filter(is_active=True)
    products = Product.objects.all().filter(is_available=True)

    print("!!! BANNERS FUNCTION CALLED !!!")
    
    context = {
        'banners': banners,
        'products': products,
    }
    return render(request, 'home.html', context)