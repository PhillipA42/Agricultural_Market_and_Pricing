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

# Create your views here.

def home(request):
    return render(request, 'home.html')
@login_required
def about(request):
    return render(request, 'about.html')

# LISTING PRODUCTS
@login_required
def productsList(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

# PRODUCT DETAIL
@login_required
def productDetail(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product_detail.html', {'product': product})

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

# DELETE PRODUCT
@login_required
def deleteProduct(request, pk):
    product = Product.objects.get(pk=pk, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('products')
    return render(request, 'delete_product.html', {'product': product})

# Add products to cart
@login_required
def addToCart(request, pk):
    product = Product.objects.get( id=pk)
    cart = Cart(request)
    cart.add(product, quantity=1)
    messages.success(request, f'{product.name} added to cart.')
    return redirect('products')

# view rour cart
@login_required
def viewCart(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def removeFromCart(request, pk):
    product = Product.objects.get(id=pk)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart')

@login_required
def clearCart(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Cart cleared.')
    return redirect('cart')

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

# LOGOUT USER
def logoutUser(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('login')
    return render(request, 'logout.html')


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

