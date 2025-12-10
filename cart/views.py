from django.shortcuts import render, get_object_or_404, redirect
from product.models import Product
from cart.models import Cart, CartItem
from django.http import HttpResponse
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        cart_item.save()

    # return HttpResponse(cart_item.product)
    # exit()
    return redirect('cart_page')

def remove_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_page')

def remove_cart_item(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_page')
    

    # cart = Cart.objects.get(cart_id=_cart_id(request))
    # if not cart:
    #     cart = Cart.objects.create(cart_id=_cart_id(request))
    # cart.save()

    # cart_item = CartItem.objects.get(product=product, cart=cart)
    # cart_item.quantity += 1
    # cart_item.save()
    # if not cart_item:
    #     cart_item.objects.create(product=product, cart=cart, quantity=1)
    #     cart_item.save()

    #     return HttpResponse(cart_item.product)
    #     exit()




def cart_page(request, quantity=0, total=0, cart_items=None):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    

    for cart_item in cart_items:
        quantity += cart_item.quantity
        if cart_item.product.promo:
            total += (cart_item.product.promo_price)*cart_item.quantity
        else:
            total += (cart_item.product.price)*cart_item.quantity
        
    tax = (5 * total)/100

    grand_total = total + tax
        
    context = {'cart_items':cart_items, 'quantity':quantity, 'total':total, 'tax':tax, 'grand_total':grand_total}
    return render(request, 'cart/cart.html', context)


