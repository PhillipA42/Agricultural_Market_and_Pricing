from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, product):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'name': product.name,
                'price': str(product.price),  # store as string for session
                'quantity': 1
            }
        else:
            self.cart[product_id]['quantity'] += 1

        self.save()

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]

        self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def items(self):
        return self.cart.items()

    def get_total_price(self):
        total = Decimal('0.00')

        for item in self.cart.values():
            price = Decimal(item['price'])
            quantity = item['quantity']
            total += price * quantity

        return total
