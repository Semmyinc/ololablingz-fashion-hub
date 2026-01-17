from django.shortcuts import render, redirect
from cart.views import _cart_id
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponse, JsonResponse
from .forms import CreateOrderForm
from .models import Order, Payment, OrderItem, OrderHistory
import datetime
import stripe
from django.conf import settings
from django.contrib import messages
from product.models import Product
from users.models import Users
# from .models import OrderHistory
# for paystack set-up
import uuid
from django.urls import reverse
from .paystack import check_out
from django.views.decorators.csrf import csrf_exempt
import hashlib
import hmac
import json
import requests

# email to user 
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# from paypal.standard.forms import PaypalPaymentsForm
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

def create_order(request, total=0, quantity=0):
    # if cart_item count <= 0, redirect to products page 
    cart_items = CartItem.objects.filter(user=request.user)
    cart_item_count = cart_items.count()

    tax= 0
    grand_total = 0

    for cart_item in cart_items:
        if cart_item.product.promo:
            total += cart_item.product.promo_price * cart_item.quantity
        else:
            total += cart_item.product.price * cart_item.quantity
            
        quantity += cart_item.quantity
    tax = (5 * total)/100
    grand_total = total + tax


    if cart_item_count <= 0:
        return redirect('products')
    
    else:
        if request.method == 'POST':
            form = CreateOrderForm(request.POST or None)
            if form.is_valid():
                data = Order()
                data.user = request.user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address = form.cleaned_data['address']
                data.city = form.cleaned_data['city']
                data.state = form.cleaned_data['state']
                data.country = form.cleaned_data['country']
                data.order_note = form.cleaned_data['order_note']
                data.tax = tax
                data.order_total = grand_total
                data.ip = request.META.get('REMOTE_ADDR') #to generate user's ip address 
                data.save()
                
                #generate order code
                yr = int(datetime.date.today().strftime('%Y'))
                m  = int(datetime.date.today().strftime('%m'))
                dt = int(datetime.date.today().strftime('%d'))

                d = datetime.date(yr,m,dt)
                current_date = d.strftime("%Y%m%d")
                order_number = f'{current_date}{str(data.id)}'
                data.order_number = order_number
                data.save()

                order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=False)

                # cart_item = CartItem.objects.get(user=request.user)
                for item in cart_items:
                    order_item = OrderItem()
                    order_item.order_id = order.id 
                    order_item.user_id = request.user.id
                    # order_item.payment = payment
                    order_item.quantity = item.quantity
                    if item.product.promo:
                        order_item.price = item.product.promo_price
                    else: 
                        order_item.price = item.product.price
                    order_item.product_id = item.product.id
                    # order_item.is_ordered = True      
                    order_item.save()

                    # copy variations (many-to-many)
                    # cart_item = CartItem.objects.get(id=item.id)
                    # product_variation = cart_item.variations.all()
                    # order_item = OrderItem.objects.get(id=order_item.id)
                    # order_item.variation.set(product_variation)
                    order_item.variation.set(item.variations.all())
                    order_item.save()

                context = {'order':order, 'tax':tax, 'total':total, 'grand_total':grand_total, 'cart_items':cart_items}
                # return redirect('checkout')
                return render(request, 'payment/payments.html', context)
            else:
                return redirect('checkout')

# def payment_free(request):
#     order 
#     order_number
#     payment_id
#     order_item 

#     context = {}
#     return render(request, 'payment/order_complete.html', context)

def payments(order_id, user_id, payment_id, payment_method, amount_paid, status):
    order = Order.objects.get(id=order_id, is_ordered=False)
    user = Users.objects.get(id=user_id)

    # Prevent duplicate processing
    if Payment.objects.filter(payment_id=payment_id).exists():
        return

    payment = Payment.objects.create(
        user=user,
        payment_id=payment_id,
        payment_method=payment_method,
        amount_paid=amount_paid,
        status=status,
    )

    order.payment = payment
    order.is_ordered = True
    order.save()
    # print(order)
    # cart_items = CartItem.objects.filter(user=request.user)

    order_items = OrderItem.objects.filter(order=order)
    # print(order_items)
    for order_item in order_items:
        order_item.payment = payment
        order_item.is_ordered = True
        order_item.save()
    # print(order_items)

        # reduce stock
        product = Product.objects.get(id=order_item.product_id)     
        product.stock_level -= order_item.quantity
        product.save()

    # delete cart items 
        cart_items = CartItem.objects.filter(product=product, is_active=True)
        print(cart_items)
        cart_items.delete()
    # for item in cart_items:
    #     order_item = OrderItem.objects.create(
    #         order=order,
    #         user=user,
    #         payment=payment,
    #         product=item.product,
    #         quantity=item.quantity,
    #         price=item.product.price,
    #         is_ordered=True,
    #     )
        # order_item = OrderItem()
        # order_item.order_id = order.id 
        # order_item.user_id = user.id
        # order_item.payment = payment
        # order_item.quantity = item.quantity 
        # order_item.price = item.product.price 
        # order_item.product_id = item.product.id
        # order_item.is_ordered = True      
        # order_item.save()

        # copy variations (many-to-many)
        # cart_item = CartItem.objects.filter(id=item.id)
        # product_variation = cart_item.variations.all()
        # order_item = OrderItem.objects.filter(id=order_item.id)
        # order_item.variation.set(product_variation)
    #     order_item.variation.set(item.variations.all())
    #     order_item.save()

    #     
    # 

    # # Optional: order history
    # OrderHistory.objects.create(
    #     user=user,
    #     order=order,
    #     order_status=True
    # )

    # Send confirmation email
    mail_subject = 'Thank you for your order!'
    message = render_to_string('payment/order_recieved_email.html', {
        'user': user,
        'order': order,
    })
    EmailMessage(mail_subject, message, to=[order.user.email]).send()


    
    # return payment, order
    return redirect('order_complete')

def order_complete(request, order_number):
    grand_total = 0
    tax = 0
    subtotal = 0
    order = Order.objects.get(is_ordered=True, user=request.user, order_number=order_number)
    order_number = order.order_number
    payment = order.payment
    payment_id = payment.payment_id
    order_items = OrderItem.objects.filter(order_id=order.id, is_ordered=True)
    for item in order_items:
        subtotal += (item.price * item.quantity)

    context={'order':order, 'order_items':order_items, 'subtotal':subtotal, 'payment_id':payment_id, 'order_number':order_number}
    return render(request, 'payment/order_complete.html', context)

def charge(request, total=0, quantity=0):
    cart_items = CartItem.objects.filter(user=request.user)
    tax= 0
    grand_total = 0

    for cart_item in cart_items:
        if cart_item.product.promo:
            total += cart_item.product.promo_price * cart_item.quantity
        else:
            total += cart_item.product.price * cart_item.quantity
            
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount={{grand_total}},
            currency='ngn',
            description='Payment Gateway',
            source=request.POST['stripeToken']
        )
    context = {}
    return render(request, 'payment/charge.html', context)


def paystack_payment_verify(request, order_id):
    pass
#     order = Order.objects.get(id=order_id)
#     reference = request.GET.get('reference', '')
#     if reference:
#         headers = {
#             'Authorization':f'Bearer {settings.PAYSTACK_SECRET_KEY}',
#             'Content_Type':'Application/json'
#         }

#         response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
#         response_data = response.json()

#         if response.data['status']:
#             if response.data['data']['status'] == 'success':


@login_required(login_url='login')
def paystack_checkout(request, order_id):
    order = Order.objects.get(id=order_id)
    # product = Product.objects.get(id=product_id)
    purchase_id = f"purchase_{uuid.uuid4()}"
    order_number = order.order_number

    # /payment-success/2/
    payment_success_url = reverse('payment_success', kwargs={'order_id': order_id})
    # http://domain.com/payment-success/2/ 
    callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

    checkout_data = {
        "email": request.user.email,
        "amount": (order.order_total) * 100,  # in kobo (₦2500)
        "currency": "NGN",
        "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
        "reference": purchase_id, # generated by developer
        "callback_url": callback_url,
        "metadata": {
            "order_id": order_id,
            "user_id": request.user.id,
            "purchase_id": purchase_id,
            'order_number': order_number
        },
        # "label": f"Checkout For {order.first_name} {order.last_name}"
        "label": f"Checkout For {order.full_name}"
    }

    status, check_out_session_url_or_error_message = check_out(checkout_data)

    if status:
        return redirect(check_out_session_url_or_error_message)
    else:
        messages.error(request, check_out_session_url_or_error_message)
        return redirect('create_order')
    
@login_required(login_url='login')   
def payment_success(request, order_id):
    subtotal = 0
    order = Order.objects.get(id=order_id, is_ordered=True)
    payment = order.payment 
    payment_id = payment.payment_id
    # payment = Payment.objects.get(payment_id=payment_id)  -- also valid

    order_items = OrderItem.objects.filter(order=order, payment=payment, is_ordered=True)
    subtotal = 0
    for order_item in order_items:
        
        # amount = order_item.price * order_item.quantity
        unit_price = order_item.price
        # if order_item.product.promo:
            
        #    order_item.amount = order_item.product.promo_price * order_item.quantity
        # else:
            
        #    order_item.amount = order_item.product.price * order_item.quantity

        order_item.amount = order_item.price * order_item.quantity
        subtotal += order_item.amount
        # order_item.save()
        
    context = {'order':order, 'order_items':order_items, 'payment_id':payment_id, 'payment':payment, 'unit_price':unit_price, 'subtotal':subtotal}
    return render(request, 'payment/payment_success.html', context)

# subtotal = 0
#     order = Order.objects.get(is_ordered=True, user=request.user, order_number=order_number)
#     order_number = order.order_number
#     payment = order.payment
#     payment_id = payment.payment_id
#     order_items = OrderItem.objects.filter(order_id=order.id, is_ordered=True)
#     for item in order_items:
#         subtotal += (item.price * item.quantity)

#     context={'order':order, 'order_items':order_items, 'subtotal':subtotal, 'payment_id':payment_id, 'order_number':order_number}

@login_required(login_url='login')
def payment_failed(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {'order':order}
    return render(request, 'payment/payment_failed.html', context)
    
@csrf_exempt
def paystack_webhook(request):
    secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    
    if signature == None:
        return HttpResponse(status=400)
    
    hash = hmac.new(secret, request.body, hashlib.sha512).hexdigest()
    if hash != signature:
        return HttpResponse(status=400)
    
    payload = json.loads(request.body)
    print(payload)
    if payload['event'] == 'charge.success':
        data = payload['data']
        metadata = data['metadata']
      
        try:
            payments(
                    order_id=metadata["order_id"],
                    user_id=metadata["user_id"],
                    payment_id=data["id"],
                    payment_method=data["channel"],
                    amount_paid=data["amount"] / 100,
                    status=data["status"]
            )
        except Exception as e:
            return HttpResponse(status=500)

    return HttpResponse(status=200)

# def process_paystack_payment(
#     order_id,
#     user_id,
#     payment_id,
#     payment_method,
#     amount_paid,
#     status
# ):
#     order = Order.objects.get(id=order_id, is_ordered=False)
#     user = Users.objects.get(id=user_id)

#     # Prevent duplicate processing
#     if Payment.objects.filter(payment_id=payment_id).exists():
#         return

#     payment = Payment.objects.create(
#         user=user,
#         payment_id=payment_id,
#         payment_method=payment_method,
#         amount_paid=amount_paid,
#         status=status,
#     )

#     order.payment = payment
#     order.is_ordered = True
#     order.save()

#     cart_items = CartItem.objects.filter(user=user)

#     for item in cart_items:
#         order_item = OrderItem.objects.create(
#             order=order,
#             user=user,
#             payment=payment,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price,
#             is_ordered=True,
#         )

#         # copy variations (many-to-many)
#         order_item.variations.set(item.variations.all())

#         # reduce stock
#         product = item.product
#         product.stock -= item.quantity
#         product.save()

#     cart_items.delete()

#     # Optional: order history
#     OrderHistory.objects.create(
#         user=user,
#         order=order,
#         order_status=True
#     )
    #     if webhook_post_data["event"] == "charge.success":
    #         payment_id = webhook_post_data['data']['id']
    #         payment_status = webhook_post_data['data']['status']
    #         payment_method = webhook_post_data['data']['channel']
    #         amount_paid = (webhook_post_data['data']['amount'])/100

    #         metadata = webhook_post_data["data"]["metadata"]

    #         order_id = metadata["order_id"]
    #         user_id = metadata["user_id"]
    #         purchase_id = metadata["purchase_id"]

    #         user = Users.objects.get(id=user_id)

    #         OrderHistory.objects.create(
    #             purchase_id = purchase_id,
    #             user = user,
    #             order_status = True,
    #             order = Order.objects.get(id=order_id)
    #         )

    #         # Payment.objects.create(
    #         #     user = user,
    #         #     payment_id = payment_id, 
    #         #     payment_method = payment_method,
    #         #     amount_paid = amount_paid,
    #         #     status = payment_status,
    #         # )

    #         # send mail to user or perfrom extra processing

    #         order = Order.objects.get(id=order_id)
    #         payment = Payment(user = user,
    #             payment_id = payment_id, 
    #             payment_method = payment_method,
    #             amount_paid = amount_paid,
    #             status = payment_status,)

    #         payment.save()
    #         order.payment = payment
    #         order.is_ordered = True
    #         order.save()

    #         # move cart_items to order_items table 
    #         cart_items = CartItem.objects.filter(user=request.user)
    #         for item in cart_items:
    #             orderitem = OrderItem()
    #             orderitem.order_id = order.id
    #             orderitem.user_id = request.user.id
    #             orderitem.payment = payment
    #             orderitem.product_id = item.product_id
    #             orderitem.quantity = item.quantity
    #             orderitem.price = item.product.price
    #             orderitem.is_ordered = True
    #             # variations can not be assigned directly as it is many to many field 
    #             orderitem.save()

    # return HttpResponse(status=200)    



# lets accept payment using stripe 
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='login')
def stripe_checkout(request, order_id):
    order = Order.objects.get(id=order_id)
    purchase_id = f"purchase_{uuid.uuid4()}"
    order_number = order.order_number

    callback_url = f"{request.scheme}://{request.get_host()}"

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data':{
                    'currency':'ngn',
                    'unit_amount':int(order.order_total * 100),
                    'product_data':{
                        'name':f'{order.first_name}',
                        # 'images':['']
                    },
                },
                'quantity':1,
            },
        ],
        metadata={
            'order_id':order_id,
            'user_email':request.user.email,
            'user_id':request.user.id,
            'purchase_id':purchase_id,
            'order_number':order_number
            # user = models.ForeignKey(Users, on_delete=models.CASCADE)
    # payment_id = models.CharField(max_length=100)
    # Payment_method = models.CharField(max_length=100)
    # # amount_paid = models.CharField(max_length=100) - amount_paid = order.order_total
    # status = models.CharField(max_length=100) - 'status':payment_status
    # created_at = models.DateTimeField(auto_now_add=True)
        },
        mode='payment',

        # success_url=callback_url + f'/payment/payment_success/{order_id}',
        # cancel_url=callback_url + f'/payment/create_order/{order_id}'
        success_url=f'{callback_url}/payment/payment_success/{order_id}', #wrote this myself from the commented above
        cancel_url=f'{callback_url}/payment/create_order/{order_id}', #wrote this myself from the commented above
    )

    return redirect(checkout_session.url)

@csrf_exempt
def stripe_webhook(request):
    event = None
    payload = request.body
    secret = settings.STRIPE_WEBHOOK_SECRET
    signature = request.META['HTTP_STRIPE_SIGNATURE']

    if signature == None:
        return HttpResponse(status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    # if event != signature:
    #     return HttpResponse(status=400)
    
    print(event)

    if event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        metadata = session['metadata']

        order_id = metadata['order_id']
        user_email = metadata['user_email']
        user_id = metadata['user_id']
        # purchase_id = session['metadata']['purchase_id']
        
        order = Order.objects.get(id=order_id)
        user = Users.objects.get(id=user_id)
        # purchase_id = purchase_id
        OrderHistory.objects.create(order=order, user=user)

    elif event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session['metadata']


        try:
            payments(
                    order_id=metadata["order_id"],
                    user_id=metadata["user_id"],
                    payment_id=session["id"],
                    payment_method=session["payment_method_types"],
                    amount_paid=session["amount_total"] / 100,
                    status=session["payment_status"]
            )
        except Exception as e:
            return HttpResponse(status=500)

        # payment_id = session['id']
        # payment_method = session['payment_method_types']
        # amount_paid = int(session['amount_total'])/100
        # status = session['payment_status']
        # order_id = session['metadata']['order_id']
        # user_email = session['metadata']['user_email']
        # user_id = session['metadata']['user_id']
        # purchase_id = session['metadata']['purchase_id']
        # order_number =  session['metadata']['order_number']

        # order = Order.objects.get(id=order_id)
        # user = Users.objects.get(id=user_id)
        # purchase_id = purchase_id
        # order_number = order_number
        # OrderHistory.objects.create(order=order, user=user, purchase_id=purchase_id, order_status=True)

        # Payment.objects.create(
        #     user = user,
        #     payment_id = payment_id, 
        #     payment_method = payment_method,
        #     amount_paid = amount_paid,
        #     status = status,
        # )
    else:
        # print(Unhandled event type {}.format(event['type']))
        print(f"Unhandled {event['type']}")
    
    return  HttpResponse(status=200)






# let's accept payments using paypal
# def paypal_checkout(request, order_id):
#     order = Order.objects.get(id=order_id)

#     host = request.get_host()

#     paypal_checkout={
#         'business':settings.PAYPAL_RECEIVER_EMAIL, 
#         'amount':order.order_total,
#         'item_name':f'{order.first_name}-{order.order_number}',
#         'invoice':uuid.uuid4(),
#         'currency_code':'ngn',
#         'notify_url':f'http://{host}{reverse(paypal_ipn)}',
#         'return_url':f'http://{host}{reverse(payment_success, kwargs={'order_id':order_id})}',
#         'cancel_url':f'http://{host}{reverse(payment_failed, kwargs={'order_id':order_id})}',
#     }

#     paypal_payment = PaypalPaymentsForm(initials=paypal_checkout)


# chat gpt suggestions 

# def process_paystack_payment(
#     order_id,
#     user_id,
#     payment_id,
#     payment_method,
#     amount_paid,
#     status
# ):
#     order = Order.objects.get(id=order_id, is_ordered=False)
#     user = Users.objects.get(id=user_id)

#     # Prevent duplicate processing
#     if Payment.objects.filter(payment_id=payment_id).exists():
#         return

#     payment = Payment.objects.create(
#         user=user,
#         payment_id=payment_id,
#         payment_method=payment_method,
#         amount_paid=amount_paid,
#         status=status,
#     )

#     order.payment = payment
#     order.is_ordered = True
#     order.save()

#     cart_items = CartItem.objects.filter(user=user)

#     for item in cart_items:
#         order_item = OrderItem.objects.create(
#             order=order,
#             user=user,
#             payment=payment,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price,
#             is_ordered=True,
#         )

#         # copy variations (many-to-many)
#         order_item.variations.set(item.variations.all())

#         # reduce stock
#         product = item.product
#         product.stock -= item.quantity
#         product.save()

#     cart_items.delete()

#     # Optional: order history
#     OrderHistory.objects.create(
#         user=user,
#         order=order,
#         order_status=True
#     )

# @csrf_exempt
# def paystack_webhook(request):
#     secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
#     signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')

#     if signature is None:
#         return HttpResponse(status=400)

#     computed_hash = hmac.new(
#         secret,
#         request.body,
#         hashlib.sha512
#     ).hexdigest()

#     if computed_hash != signature:
#         return HttpResponse(status=400)

#     payload = json.loads(request.body)

#     if payload.get("event") == "charge.success":
#         data = payload["data"]
#         metadata = data.get("metadata", {})

#         try:
#             process_paystack_payment(
#                 order_id=metadata["order_id"],
#                 user_id=metadata["user_id"],
#                 payment_id=data["id"],
#                 payment_method=data["channel"],
#                 amount_paid=data["amount"] / 100,
#                 status=data["status"]
#             )
#         except Exception as e:
#             # log error here
#             return HttpResponse(status=500)

#     return HttpResponse(status=200)



# def process_successful_payment(order_number, payment_id, payment_method, status):
#     order = get_object_or_404(Order, order_number=order_number, is_ordered=False)

#     payment = Payment.objects.create(
#         user=order.user,
#         payment_id=payment_id,
#         payment_method=payment_method,
#         amount_paid=order.order_total,
#         status=status,
#     )

#     order.payment = payment
#     order.is_ordered = True
#     order.save()

#     cart_items = CartItem.objects.filter(user=order.user)

#     for item in cart_items:
#         order_product = OrderProduct.objects.create(
#             order=order,
#             payment=payment,
#             user=order.user,
#             product=item.product,
#             quantity=item.quantity,
#             product_price=item.product.price,
#             ordered=True,
#         )

#         order_product.variations.set(item.variations.all())

#         product = item.product
#         product.stock -= item.quantity
#         product.save()

#     cart_items.delete()

#     # Send confirmation email
#     mail_subject = 'Thank you for your order!'
#     message = render_to_string('orders/order_recieved_email.html', {
#         'user': order.user,
#         'order': order,
#     })
#     EmailMessage(mail_subject, message, to=[order.user.email]).send()

#     return payment

# how order number reaches webhook 
# Webhook → order_number → Order object
