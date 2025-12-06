from django.contrib import admin
from django.urls import path
from firstApp import views



urlpatterns = [
    path('index/', views.index, name='index'),
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
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('admin-dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('payment/', views.mpesaPayment, name='mpesa_payment'),


] 
