from django.shortcuts import render
from cart.views import _cart_id
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required 
# Create your views here.

@login_required(login_url='login')
def checkout(request, quantity=0, total=0, cart_items=None):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
    tax = 0
    grand_total = 0
    for cart_item in cart_items:
        quantity += cart_item.quantity
        if cart_item.product.promo:
            total += (cart_item.product.promo_price)*cart_item.quantity
        else:
            total += (cart_item.product.price)*cart_item.quantity
        
    tax = (5 * total)/100
    grand_total = total + tax

    context = {'cart_items':cart_items, 'grand_total':grand_total, 'tax':tax, 'total':total, 'quantity':quantity}
    return render(request, 'payment/checkout.html', context)