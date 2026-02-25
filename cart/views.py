from django.shortcuts import render, get_object_or_404, redirect
from product.models import Product, Variation
from cart.models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

# Assuming _cart_id function is defined elsewhere
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# def add_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     product_variation = []
    
#     if request.method == 'POST':
#         for item in request.POST:
#             key = item
#             value = request.POST[key]
    
#             try:
#                 variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                 product_variation.append(variation)
#                 # print(variation)
#             except Variation.DoesNotExist:
#                 pass

#     # for logged in user 
#     if request.user.is_authenticated:
#         # 1. Get current variations as a sorted list of IDs
#         current_var_ids = sorted([v.id for v in product_variation])

#         # 2. Get all existing cart items for this user and product
#         cart_items = CartItem.objects.filter(product=product, user=request.user)
        
#         existing_item = None
#         for item in cart_items:
#             # 3. Get existing variations as a sorted list of IDs
#             existing_var_ids = sorted([v.id for v in item.variations.all()])
            
#             # 4. Compare the ID lists
#             if existing_var_ids == current_var_ids:
#                 existing_item = item
#                 break
        
#         if existing_item:
#             existing_item.quantity += 1
#             existing_item.save()
#         else:
#             # Create new if no exact match found
#             item = CartItem.objects.create(product=product, quantity=1, user=request.user)
#             if product_variation:
#                 item.variations.add(*product_variation)
#             item.save()
                
#         # return redirect('cart_page')

    
        
#     # for guest user     
#     else:
#         try:
#             cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
#         except Cart.DoesNotExist:
#             cart = Cart.objects.create(cart_id=_cart_id(request))
#         cart.save()

#         does_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
#         if does_cart_item_exists:
#             cart_item = CartItem.objects.filter(product=product, cart=cart)
#             ex_var_list = []
#             id_list = []

#             for item in cart_item:
#                 existing_variation = item.variations.all()
#                 ex_var_list.append(list(existing_variation))
#                 id_list.append(item.id)

#             if product_variation in ex_var_list:
#                 # then increase the cart item quantity 
#                 indx = ex_var_list.index(product_variation)
#                 item_id = id_list[indx]
#                 item = CartItem.objects.get(product=product, id=item_id)
#                 item.quantity += 1
#                 item.save()

#             else:
#                 item = CartItem.objects.create(product=product, quantity=1, cart=cart)
#                 if len(product_variation) > 0:
#                     item.variations.clear()  
#                     item.variations.add(*product_variation)
#                 item.save()
          

#         else:
#             cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
#             if len(product_variation) > 0:
#                 cart_item.variations.clear()
#                 cart_item.variations.add(*product_variation)
#             cart_item.save()
#     return redirect('cart_page')

    # alternatively this code below for add_cart
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []
    
    # Check both POST (form) and GET (if you pass vars in URL, though POST is better)
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    # 1. Prepare current variations as a sorted list of IDs for comparison
    current_var_ids = sorted([v.id for v in product_variation])

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(product=product, cart=cart)

    # 2. Unified Grouping Logic
    existing_item = None
    for item in cart_items:
        existing_var_ids = sorted([v.id for v in item.variations.all()])
        if existing_var_ids == current_var_ids:
            existing_item = item
            break

    if existing_item:
        existing_item.quantity += 1
        existing_item.save()
    else:
        # 3. Create New Item
        if request.user.is_authenticated:
            item = CartItem.objects.create(product=product, quantity=1, user=request.user)
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        
        if len(product_variation) > 0:
            item.variations.add(*product_variation)
        item.save()

    return redirect('cart_page')    


def remove_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
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

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    cart_item.delete()
    return redirect('cart_page')
    
  
def cart_page(request, quantity=0, total=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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
        
    except ObjectDoesNotExist:
        pass

    context = {'cart_items':cart_items, 'quantity':quantity, 'total':total, 'tax':tax, 'grand_total':grand_total}
    return render(request, 'cart/cart.html', context)



# if request.user.is_authenticated:
    #     # Get all cart items for this user and product
    #     cart_items = CartItem.objects.filter(product=product, user=request.user)
        
    #     existing_item = None
        
    #     # Check if any existing item matches the current variations exactly
    #     for item in cart_items:
    #         existing_variations = list(item.variations.all())
    #         if existing_variations == product_variation:
    #             existing_item = item
    #             break
        
    #     if existing_item:
    #         # Match found: increase quantity
    #         existing_item.quantity += 1
    #         existing_item.save()
    #     else:
    #         # No match: create new item with variations
    #         item = CartItem.objects.create(product=product, quantity=1, user=request.user)
    #         if len(product_variation) > 0:
    #             item.variations.add(*product_variation)
    #         item.save()
            
    #     return redirect('cart_page')


    # if request.user.is_authenticated:     
    #     does_cart_item_exists = CartItem.objects.filter(product=product, user=request.user).exists()
    #     if does_cart_item_exists:
    #         cart_item = CartItem.objects.filter(product=product, user=request.user)
    #         ex_var_list = []
    #         id_list = []
    #         for item in cart_item:
    #             existing_variation = item.variations.all()
    #             ex_var_list.append(list(existing_variation))
    #             id_list.append(item.id)

    #         if product_variation in ex_var_list:
    #             # then increase the cart item quantity 
    #                 indx = ex_var_list.index(product_variation)
    #                 item_id = id_list[indx]
    #                 item = CartItem.objects.get(product=product, id=item_id)
    #                 item.quantity += 1
    #                 item.save()

    #         else:
    #              item = CartItem.objects.create(product=product, quantity=1, user=request.user)
    #              if len(product_variation) > 0:
    #                 item.variations.clear()
    #                 item.variations.add(*product_variation)
    #                 item.save()
                
    #     else:
    #         cart_item = CartItem.objects.create(product=product, quantity=1, user=request.user)
    #         if len(product_variation) > 0:
    #             cart_item.variations.clear()
    #             cart_item.variations.add(*product_variation)
    #         cart_item.save()
            
    #     return redirect('cart_page')


# Helper function to get or create a session ID for anonymous users
# def _cart_id(request):
#     cart_id = request.session.session_key
#     if not cart_id:
#         request.session.create()
#         cart_id = request.session.session_key
#     return cart_id

# def add_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     product_variation = []

#     if request.method == 'POST':
#         for item in request.POST:
#             key = item
#             value = request.POST[key]
#             try:
#                 variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                 product_variation.append(variation)
#             except ObjectDoesNotExist:
#                 pass

#     # For logged-in users
#     if request.user.is_authenticated:
#         # Code provided in the original snippet, completed below
#         does_cart_item_exists = CartItem.objects.filter(product=product, user=request.user).exists()
#         if does_cart_item_exists:
#             cart_items = CartItem.objects.filter(product=product, user=request.user)
#             ex_var_list = []
#             id_list = []
#             for item in cart_items:
#                 existing_variation = item.variations.all()
#                 ex_var_list.append(list(existing_variation))
#                 id_list.append(item.id)

#             if product_variation in ex_var_list:
#                 # Increase the cart item quantity
#                 index = ex_var_list.index(product_variation)
#                 item_id = id_list[index]
#                 item = CartItem.objects.get(product=product, id=item_id)
#                 item.quantity += 1
#                 item.save()

#             else:
#                 # Create a new cart item for the new variation combination
#                 item = CartItem.objects.create(
#                     product=product,
#                     quantity=1,
#                     user=request.user,
#                 )
#                 if len(product_variation) > 0:
#                     item.variations.clear()
#                     item.variations.add(*product_variation)
#                 item.save()
#         else:
#             cart_item = CartItem.objects.create(product=product, quantity=1, user=request.user)
#             if len(product_variation) > 0:
#                 cart_item.variations.clear()
#                 cart_item.variations.add(*product_variation)
#             cart_item.save()

#     # For guest users (anonymous)
#     else:
#         # Get or create the cart based on the session ID
#         try:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#         except Cart.DoesNotExist:
#             cart = Cart.objects.create(cart_id=_cart_id(request))
#         cart.save()

#         # Handle CartItem logic for guest users (similar to logged-in logic)
#         does_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
#         if does_cart_item_exists:
#             cart_items = CartItem.objects.filter(product=product, cart=cart)
#             ex_var_list = []
#             id_list = []
#             for item in cart_items:
#                 existing_variation = item.variations.all()
#                 ex_var_list.append(list(existing_variation))
#                 id_list.append(item.id)

#             if product_variation in ex_var_list:
#                 index = ex_var_list.index(product_variation)
#                 item_id = id_list[index] 
#                 item = CartItem.objects.get(product=product, id=item_id)
#                 item.quantity += 1
#                 item.save()
#             else:
#                 item = CartItem.objects.create(
#                     product=product,
#                     quantity=1,
#                     cart=cart,
#                 )
#                 if len(product_variation) > 0:
#                     item.variations.clear()
#                     item.variations.add(*product_variation)
#                 item.save()
#         else:
#             # Create a brand new cart item if it doesn't exist at all
#             cart_item = CartItem.objects.create(
#                 product=product,
#                 quantity=1,
#                 cart=cart,
#             )
#             if len(product_variation) > 0:
#                 cart_item.variations.clear()
#                 cart_item.variations.add(*product_variation)
#             cart_item.save()
            
#     # Redirect to the cart page after adding the item
#     return redirect('cart_page')


# def add_cart(request, product_id):
#     # Retrieve the product or return 404
#     product = get_object_or_404(Product, id=product_id)
#     product_variation = []

#     # Process POST request to collect variations
#     if request.method == 'POST':
#         for item_key in request.POST:
#             key = item_key
#             value = request.POST[key]
#             try:
#                 # Find the corresponding Variation object
#                 variation = Variation.objects.get(
#                     product=product,
#                     variation_category__iexact=key,
#                     variation_value__iexact=value
#                 )
#                 product_variation.append(variation)
#             except Variation.DoesNotExist:
#                 pass

#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(cart_id=_cart_id(request))
#     cart.save()

#     # Check if a CartItem with the exact product and variations already exists
#     # Use filter instead of exists() to get the queryset for logic below
#     cart_items_with_variations = CartItem.objects.filter(product=product, cart=cart)
    
#     item_found = False
    
#     # Iterate through existing cart items to find a match
#     for cart_item in cart_items_with_variations:
#         existing_variations = list(cart_item.variations.all())
        
#         # Check if the collected product_variation exactly matches the existing variations
#         if existing_variations == list(product_variation):
#             cart_item.quantity += 1
#             cart_item.save()
#             item_found = True
#             break # Exit loop once the matching item is updated

#     # If no matching item was found, create a new CartItem
#     if not item_found:
#         # The provided code missed the save() call here for the initial creation of cart_item
#         cart_item = CartItem.objects.create(
#             product=product, 
#             quantity=1, 
#             cart=cart
#         )
#         if len(product_variation) > 0:
#             # Add all collected variations to the new cart item
#             cart_item.variations.add(*product_variation)
#         cart_item.save()

#     # Redirect user after adding to cart
#     return redirect('cart_page')

# def add_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
    
#     product_variation = []
#     if request.method == 'POST':
#         for item in request.POST:
#             key = item
#             value = request.POST[key]

#             try:
#                 variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                 product_variation.append(variation)
#             except Variation.DoesNotExist:
#                 pass

#         try:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#         except Cart.DoesNotExist:
#             cart = Cart.objects.create(cart_id=_cart_id(request))
#         cart.save()    

#     cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
#     if cart_item_exists:
#         cart_items = CartItem.objects.filter(product=product, cart=cart)
#         ex_var_list = []
#         id_list = []

#         for prdt in cart_items:
#             existing_variation = prdt.variations.all()
#             ex_var_list.append(list(existing_variation))
#             id_list.append(prdt.id)

#         if product_variation in ex_var_list:
#             indx = ex_var_list.index(product_variation)
#             item_id = id_list[indx]
#             prod = CartItem.objects.get(product=product, id=item_id)
#             prod.quantity += 1
#             prod.save()

#         else:
#             # prod = CartItem.objects.create(product=product, quantity=1, cart=cart)
#             if len(product_variation) > 0:
#                 cart_items.variations.clear()
#                 for item in product_variation:
#                     cart_items.variations.add(item)
#                 # cart_items.variations.add(*product_variation)
#             cart_items.save()
#     else:
#         cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
#         if len(product_variation) > 0:
#             cart_item.variations.clear()
#             cart_item.variations.add(*product_variation)
#         cart_item.save()
        
#     return redirect('cart_page')