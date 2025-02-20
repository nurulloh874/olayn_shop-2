from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .models import Product, ProductCategory, User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from .models import Cart, CartItem

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Foydalanuvchining savatini olish yoki yaratish
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Mahsulotni savatga qo'shish
    cart.add_product(product)  # Bu yerda add_product metodi ishlatiladi
    
    return redirect('cart')  # Foydalanuvchini savat sahifasiga yo'naltirish


def base_page(request):
    products = Product.objects.all()
    categories = ProductCategory.objects.all()
    new_products = Product.objects.order_by('-id')[:5]

    # Foydalanuvchining savatini olish
    cart_products = Cart.objects.filter(user=request.user).first()
    cart_items = cart_products.items.all() if cart_products else []

    context = {
        'products': products,
        'categories': categories,
        'new_products': new_products,
        'cart_items': cart_items  # Savatdagi mahsulotlar
    }
    return render(request, 'base.html', context)


# Class based view
class HomePage(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        products = Product.objects.all()
        categories = ProductCategory.objects.all()
        new_products = Product.objects.order_by('-id')[:5]
        eng_qimmatlari = Product.objects.order_by('-price')[:8]
        context = {
            'products': products,
            'categories': categories,
            'new_products': new_products,
            'eng_qimmatlari': eng_qimmatlari
        }
        return context
        

def StorePage(request, c):
    # Kategoriya nomiga mos mahsulotlarni filtrlash
    products = Product.objects.filter(category__name=c)
    categories = ProductCategory.objects.all()

    context = {
        'products': products,
        'categories': categories
    }

    return render(request, 'store.html', context)


def ProductPage(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = ProductCategory.objects.all()

    context = {
        'product': product,
        'categories': categories
    }

    return render(request, 'product.html', context)


@login_required
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()  # Foydalanuvchining savatini olish
    if not cart:
        return render(request, 'checkout.html', {'error': 'Savatda mahsulotlar mavjud emas'})
    
    cart_items = cart.items.all()  # Savatdagi mahsulotlar
    total_price = cart.get_total_price()  # Savatdagi jami narx

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'checkout.html', context)


# Savatdagi mahsulotni olib tashlash uchun view
@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.filter(user=request.user).first()
    
    if cart:
        cart.remove_product(product)
    
    return redirect('cart_detail')


# Foydalanuvchini tizimga kirish

def login_view(request):  # username, password
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        print(user)
        
        if user is not None:
            login(request, user)
            print('User logged in')
            return render(request, 'index.html')
        else:
            print('User not found')
            return render(request, 'login.html')
    return render(request, 'login.html')



def register_view(request):  # full_name, username, email, telefon, password, confirm_password
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        telefon = request.POST.get('telefon')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = full_name
            user.save()
            return render(request, 'login.html')
        else:
            return render(request, 'register.html')
    return render(request, 'register.html')


# Tizimdan chiqish
def logout_view(request):
    logout(request)
    return redirect('home')


