from django.core.management.base import BaseCommand
from firstApp.models import Product
from django.utils.text import slugify

# 100 sample agricultural products with real images
PRODUCTS = [
    {"name": "Fresh Maize (50kg)", "price": "2000.00", "image_url": "https://images.unsplash.com/photo-1582500228826-bf9cd5dc44ef", "is_popular": True},
    {"name": "Irish Potatoes (50kg)", "price": "3500.00", "image_url": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce", "is_popular": True},
    {"name": "Tomatoes (crate)", "price": "600.00", "image_url": "https://images.unsplash.com/photo-1589927986089-35812388d1f4", "is_popular": True},
    {"name": "Onions (bag)", "price": "900.00", "image_url": "https://images.unsplash.com/photo-1617196031501-bf2ab16f0f27", "is_popular": False},
    {"name": "Cow Milk (litre)", "price": "80.00", "image_url": "https://images.unsplash.com/photo-1590080872499-8b5f42981e45", "is_popular": True},
    {"name": "Carrots (bag)", "price": "500.00", "image_url": "https://images.unsplash.com/photo-1601089196994-f568c7a2d8a3", "is_popular": False},
    {"name": "Cabbages (head)", "price": "300.00", "image_url": "https://images.unsplash.com/photo-1582515073490-d54791cd7a86", "is_popular": False},
    {"name": "Apples (crate)", "price": "1500.00", "image_url": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce", "is_popular": True},
    {"name": "Bananas (bunch)", "price": "200.00", "image_url": "https://images.unsplash.com/photo-1574226516831-e1dff420e40f", "is_popular": True},
    {"name": "Watermelon (whole)", "price": "400.00", "image_url": "https://images.unsplash.com/photo-1592928303384-4ec25a7314b4", "is_popular": False},
    {"name": "Mangoes (crate)", "price": "1200.00", "image_url": "https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2", "is_popular": True},
    {"name": "Oranges (crate)", "price": "1000.00", "image_url": "https://images.unsplash.com/photo-1607746882042-944635dfe10e", "is_popular": True},
    {"name": "Strawberries (box)", "price": "800.00", "image_url": "https://images.unsplash.com/photo-1587049352849-bb2e38a9f3c8", "is_popular": False},
    {"name": "Blueberries (box)", "price": "900.00", "image_url": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce", "is_popular": False},
    {"name": "Eggs (dozen)", "price": "180.00", "image_url": "https://images.unsplash.com/photo-1589927986089-35812388d1f4", "is_popular": True},
    {"name": "Chicken (whole)", "price": "1200.00", "image_url": "https://images.unsplash.com/photo-1604908177524-fcd9f6d6e167", "is_popular": True},
    {"name": "Goat Meat (kg)", "price": "950.00", "image_url": "https://images.unsplash.com/photo-1603030634455-78c066d7eb95", "is_popular": True},
    {"name": "Beef (kg)", "price": "1100.00", "image_url": "https://images.unsplash.com/photo-1603030634455-78c066d7eb95", "is_popular": True},
    {"name": "Fish (kg)", "price": "800.00", "image_url": "https://images.unsplash.com/photo-1567598508487-f3db0f08e9f5", "is_popular": True},
    {"name": "Honey (jar)", "price": "500.00", "image_url": "https://images.unsplash.com/photo-1592928303384-4ec25a7314b4", "is_popular": False},
    # ... continue to 100 products ...
]

# Generate more automatically to reach 100 products
for i in range(21, 101):
    PRODUCTS.append({
        "name": f"Agri Product {i}",
        "price": f"{100+i*10:.2f}",
        "image_url": f"https://source.unsplash.com/600x400/?agriculture,food,{i}",
        "is_popular": i % 2 == 0
    })

class Command(BaseCommand):
    help = 'Seed the database with 100 sample agricultural products'

    def handle(self, *args, **kwargs):
        created_count = 0
        for item in PRODUCTS:
            slug = slugify(item['name'])
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'price': item.get('price', '0.00'),
                    'image_url': item.get('image_url', ''),
                    'is_popular': item.get('is_popular', False),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {product.name}'))
        self.stdout.write(self.style.SUCCESS(f'Done. Created {created_count} new products.'))
