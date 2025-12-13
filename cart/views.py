from django.shortcuts import render, get_object_or_404, redirect
from product.models import Product, Variation
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
    
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
    
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
                # print(variation)
            except:
                pass
        # color = request.POST['color']
        # size = request.POST['size']
        # print(color,size)
    # return HttpResponse(f'{color} and {size}')
    # exit()
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    does_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if does_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            # then increase the cart item quantity 
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()

        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                
                item.variations.add(*product_variation)
            
            item.save()

    else:
        cart_item = CartItem.objects.create(product = product, quantity = 1, cart = cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('cart_page')

    # try:
    #     cart_item = CartItem.objects.get(product=product, cart=cart)
    #     # check if product_variation list is empty or not 
    #     if len(product_variation) > 0:
    #         cart_item.variations.clear()
    #         for item in product_variation:
    #             cart_item.variations.add(item)
    #     cart_item.quantity += 1
    #     cart_item.save()
        
    # except CartItem.DoesNotExist:
    #     cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
    #     if len(product_variation) > 0:
    #         cart_item.variations.clear()
    #         for item in product_variation:
    #             cart_item.variations.add(item)
    #     cart_item.save()

    # # retur zn HttpResponse(cart_item.product)
    # # exit()
    # return redirect('cart_page')

def remove_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)

    
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart_page')

def remove_cart_item(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
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
        
    context = {'cart_items':cart_items, 'quantity':quantity, 'total':total, 'tax':tax, 'grand_total':grand_total}
    return render(request, 'cart/cart.html', context)


