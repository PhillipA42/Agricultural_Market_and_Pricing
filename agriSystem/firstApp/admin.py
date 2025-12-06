from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'in_stock', 'location', 'expiry_date', 'created_at')
    list_filter = ('seller', 'location', 'created_at', 'expiry_date')
    search_fields = ('name', 'description', 'seller__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
