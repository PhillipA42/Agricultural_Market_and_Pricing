from decimal import Decimal

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
    
    @property
    def get_total_quantity(self):
        return sum(int(item["quantity"]) for item in self.cart.values())
