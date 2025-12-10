from django.db import models
from product.models import Product
# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        if self.product.promo:
            return self.product.promo_price * self.quantity
        else:
            return self.product.price * self.quantity


    def __str__(self):
        return self.product.product_name