"""
 # Set up the project  first
# Set up the firstApp
"""
"""
Register your app among the installed apps


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'firstApp',
    'django_daraja',
]
"""

"""
Go to the system's folder urls.py and include the path

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/firstApp/home/', permanent=False)),
    path('firstApp/', include('firstApp.urls')),  # Include your app URLs
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""

"""
Go to the settings.py and set the base dirctory to set the access o templates under 'DIRS'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

  # Add static URL to allow for the reading of the files in the static folder
  STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# Add mediae url to all the reading of media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
"""

"""
Into your app, go to views.py and add view functions

# Make the required imports

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .cart import Cart
from django.contrib.auth.decorators import login_required
from .models import Product, Profile, Order
from .forms import ProductForm, MpesaPaymentForm
from django.db.models import Sum
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django_daraja.mpesa.core import MpesaClient

# Allow home page to be displayed

def home(request):
    return render(request, 'home.html')

# Create a view for about page
 The user must login to view about page
@login_required
def about(request):
    return render(request, 'about.html')


Create view to view the products
User must login to view the products
# LISTING PRODUCTS
@login_required
def productsList(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

Create view to allow users to read more about a particular product
# PRODUCT DETAIL
@login_required
def productDetail(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product_detail.html', {'product': product})

Allow the product creation, user must login first to add products
# ADD PRODUCT
@login_required
def addProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('products')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

Create view for products update
# UPDATE PRODUCT
@login_required
def updateProduct(request, pk):
    product = Product.objects.get(id=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form, 'product': product})


Create the view to delete products
# DELETE PRODUCT
@login_required
def deleteProduct(request, pk):
    product = Product.objects.get(pk=pk, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('products')
    return render(request, 'delete_product.html', {'product': product})

# Create the view to add products to cart, user must login to add products to cart
@login_required
def addToCart(request, pk):
    product = Product.objects.get( id=pk)
    cart = Cart(request)
    cart.add(product)
    messages.success(request, f'{product.name} added to cart.')
    return redirect('products')
# Create view that allow users to view the products they have addded to cart
@login_required
def viewCart(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

# Create the view to allow removal of a product from cart
@login_required
def removeFromCart(request, pk):
    product = Product.objects.get(id=pk)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart')

# Create view to clear the entire cart
@login_required
def clearCart(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Cart cleared.')
    return redirect('cart')


# Allow for order to be created from cart

@login_required
def createOrderFromCart(request):
    cart = Cart(request)

    if not cart.items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    for product_id, item in cart.items.items():
        product = Product.objects.get(id=product_id)

        Order.objects.create(
            user=request.user,
            product=product,
            quantity=item["quantity"],
            total_price=Decimal(item["price"]) * int(item["quantity"]),
            is_paid=False
        )

    cart.clear()
    messages.success(request, "Order placed successfully. Proceed to payment.")
    return redirect("mpesa_payment")

# Create the view to allow user to register
# User registration
def registerUser(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        #Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'register.html')

        # Create username from email (auto)
        username = email.split('@')[0]

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=name
        )
        user.save()

        # Save phone number in Profile
        Profile.objects.create(
            user=user,
            phone=phone
        )

        #  Auto login after registration
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('home')

    return render(request, 'register.html')

# Create view that allow login and authentication to occur
# User login
def loginUser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with this email exists
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

        # Authenticate using username (Django default)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

# Create view to allow the user to logout if already loged in and wants to log out
# LOGOUT USER
def logoutUser(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('login')
    return render(request, 'logout.html')


# Create the views for admin dashboard
# ADMIN DASHBOARD
@staff_member_required
def adminDashboard(request):
    products = Product.objects.all()

    # BASIC COUNTS
    total_products = products.count()
    total_orders = Order.objects.count()

    # PAID & PENDING
    paid_orders = Order.objects.filter(is_paid=True)
    pending_orders = Order.objects.filter(is_paid=False)

    total_paid_orders = paid_orders.count()
    total_pending_orders = pending_orders.count()

    # TOTAL SALES (SAFE DECIMAL)
    total_sales = paid_orders.aggregate(
        total=Sum('total_price')
    )['total'] or Decimal('0.00')

    # DELIVERY STATUS
    on_delivery_products = Product.objects.filter(on_delivery=True).count()
    not_on_delivery_products = Product.objects.filter(on_delivery=False).count()

    # TOTAL STOCK VALUE (SAFE — USE PROPERTY, NOT ANNOTATE)
    total_stock_value = sum(
        (p.total_value for p in products),
        Decimal('0.00')
    )

    context = {
        'products': products,
        'total_products': total_products,
        'total_orders': total_orders,

        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        'total_paid_orders': total_paid_orders,
        'total_pending_orders': total_pending_orders,

        'total_sales': total_sales,

        'on_delivery_products': on_delivery_products,
        'not_on_delivery_products': not_on_delivery_products,

        'total_stock_value': total_stock_value,
    }

    return render(request, 'admin_dashboard.html', context)

# Create the views that allow payment to take place
# Initiate payment
@login_required
def mpesaPayment(request):
    unpaid_orders = Order.objects.filter(user=request.user, is_paid=False)
    total_amount = unpaid_orders.aggregate(total=Sum("total_price"))["total"] or Decimal("0.00")

    if total_amount <= 0:
        messages.warning(request, "You have no unpaid orders.")
        return redirect("cart")

    if request.method == "POST":
        form = MpesaPaymentForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]

            cl = MpesaClient()
            cl.stk_push(
                phone_number,
                int(total_amount),
                "AgriMarket Kisii",
                "Product Purchase",
                "https://api.darajambili.com/express-payment"
            )

            return redirect("success")
    else:
        form = MpesaPaymentForm()

    return render(request, "prompt_payment.html", {"form": form, "total": total_amount})


def successPayment(request):
    return render(request, "success.html")

"""


"""
# Go to settings.py and add this part for mpesa payment

from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()  # reads variables from a .env file and sets them in os.environ

# ========= MPESA=========

# The Mpesa environment to use
# Possible values: sandbox, production

MPESA_ENVIRONMENT = 'sandbox'

# Credentials for the daraja app

MPESA_CONSUMER_KEY = os.getenv('CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')

#Shortcode to use for transactions. For sandbox  use the Shortcode 1 provided on test credentials page

MPESA_SHORTCODE = 'mpesa_shortcode'

# Shortcode to use for Lipa na MPESA Online (MPESA Express) transactions
# This is only used on sandbox, do not set this variable in production
# For sandbox use the Lipa na MPESA Online Shorcode provided on test credentials page

MPESA_EXPRESS_SHORTCODE = os.getenv('BUSINESS_SHORT_CODE')

# Type of shortcode
# Possible values:
# - paybill (For Paybill)
# - till_number (For Buy Goods Till Number)

MPESA_SHORTCODE_TYPE = 'paybill'

# Lipa na MPESA Online passkey
# Sandbox passkey is available on test credentials page
# Production passkey is sent via email once you go live

MPESA_PASSKEY = os.getenv('MPESA_PASS_KEY')

# Username for initiator (to be used in B2C, B2B, AccountBalance and TransactionStatusQuery Transactions)

MPESA_INITIATOR_USERNAME = 'initiator_username'

# Plaintext password for initiator (to be used in B2C, B2B, AccountBalance and TransactionStatusQuery Transactions)

MPESA_INITIATOR_SECURITY_CREDENTIAL = 'initiator_security_credential'
"""



"""
# Go to your app and create a urls.py file
Inside it, set the paths for your system

from django.urls import path
from firstApp import views



urlpatterns = [
    path('products/', views.productsList, name='products'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('product/<int:pk>/', views.productDetail, name='product_detail'),
    path('add/', views.addProduct, name='add_product'),
    path('update/<int:pk>/', views.updateProduct, name='update_product'),
    path('delete/<int:pk>/', views.deleteProduct, name='delete_product'),
    path('cart/', views.viewCart, name='cart'),
    path('cart/add/<int:pk>/', views.addToCart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.removeFromCart, name='remove_from_cart'),
    path('cart/clear/', views.clearCart, name='clear_cart'),
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('admin-dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('payment/', views.mpesaPayment, name='mpesa_payment'),
    path('success-payment/', views.successPayment, name='success'),
    path("create-order/", views.createOrderFromCart, name="create_order_from_cart"),

] 

"""

"""
# Go to models.py file that is inside your app
 # make the required imports

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

# Create a class Product, this class allows us to create a table in our database called product 
# This allows for: 
 
# Assign products to sellers
# Store product name, price, image, stock, and location
# Track expiry dates for agricultural goods
# Monitor delivery status
# Automatically store when a product was created 

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    detailed_description = models.TextField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    
    in_stock = models.PositiveIntegerField()
    
    expiry_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    image = models.ImageField(upload_to='product_images/')

    #DELIVERY STATUS
    on_delivery = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.price * Decimal(self.in_stock)

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

# Create a model profile, this will allow you to:
  
 # Add extra user data without modifying Django’s User model
 # Easily store and manage phone numbers
 # Keep authentication (login) separate from personal data 
 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

# Create a model called order, this will allow you to:  
# Know who ordered
# Know what product was ordered
# Track quantity and total cost
# Track when the order was made
# Track payment status
# Display clean order names in Admin 

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

"""

"""
# Inside your app create a file called forms.py
# Make the imports
from django import forms
from .models import Product

 # Create a productform, this will perform these:

# Displays a styled product upload form
# Uses a calendar for expiry date
# Accepts text, numbers, and images
# Saves data directly into the Product model
# Improves user experience with Bootstrap
# Supports both product creation & editing 

 class ProductForm(forms.ModelForm):
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Product
        fields = ['name', 'description','detailed_description', 'price', 'location', 'in_stock', 'expiry_date', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detailed_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# create a form  for payment
# secure mpesa payment

class MpesaPaymentForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '2547XXXXXXXX'
        })
    )
"""

"""
# in your app, the file admin.py create a configuration for product model

from django.contrib import admin
from .models import Product

# This setup as admin will allow you to:

# See all important product details in one table
# Filter products easily by seller, location, and dates
# Quickly search for products
# Automatically sort by newest
# Protect the creation date from being edited 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'in_stock', 'location', 'expiry_date', 'created_at')
    list_filter = ('seller', 'location', 'created_at', 'expiry_date')
    search_fields = ('name', 'description', 'seller__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

"""

"""
# in your app create a cart.py file
# This is a shopping system
from decimal import Decimal

# Create a class Cart, this class allow you to:

# Add items
# Increase quantity
# Remove items
# Clear all items
# Store cart per user
# Persist across pages
# Calculate total price accurately


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]["quantity"] += quantity
        else:
            self.cart[product_id] = {
                "name": product.name,
                "price": str(product.price),
                "quantity": quantity
            }
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True

    @property
    def items(self):
        """Return the cart dictionary"""
        return self.cart

    @property
    def get_total_price(self):
        return sum(Decimal(item["price"]) * int(item["quantity"]) for item in self.cart.values())

"""

"""
# crfeate a file inside your app and name it context_processors.py
# inside it, add this

from .cart import Cart

def cart(request):
    return {"cart": Cart(request)}

# This will enable for cart to count the number of products added

# update your views.py under addToCart to this

@login_required
def addToCart(request, pk):
    product = Product.objects.get( id=pk)
    cart = Cart(request)
    cart.add(product, quantity=1)
    messages.success(request, f'{product.name} added to cart.')
    return redirect('products')

# inside your settings.py under TEMPLATES, update it to this

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'firstApp.context_processors.cart',
            ],
        },
    },
]

# Inside your cart.py add this section

 @property
    def get_total_quantity(self):
        return sum(int(item["quantity"]) for item in self.cart.values())

# Now this will enable the cart to update products
"""