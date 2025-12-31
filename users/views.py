from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import Users
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from cart.models import Cart, CartItem
from cart.views import _cart_id
import requests 

# for verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# Create your views here.


def register(request):
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            # if username != None:
            #     username = form.cleaned_data['username']
            # else:
            # username = email.split('@')[0]
            
            user = Users.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=username)
            user.phone = phone
            # messages.success(request, f'Congrats {username} ! Account created successfully.')
            user.save()

            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Account activation Notification'
            message = render_to_string('users/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, f'Thank you for registering. Verification mail has been sent to your email for confirmation.')
            return redirect('/users/login/?command=verification&email='+email)
        # else:
        #     messages.info(request, f'Error while filling form. Please try again')
        #     return redirect('register')

    else:
        form = SignUpForm()
        
    context = {'form':form}
    return render(request, 'users/register.html', context)


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        if user != None:
            
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                does_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if does_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    
                    # getting the product variations by cart_id 
                    product_variation = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # get the existing cart items from the user to access his product variations 
                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id_list = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)
                    
                    # if product_variation in ex_var_list:
                    #     index = ex_var_list.index(product_variation)
                    #     item_id = id_list[index]
                    #     item = CartItem.objects.get(id=item_id)
                    #     item.quantity += 1
                    #     item.user = user
                    #     item.save()
                    
                    # else:
                    #     cart_items = CartItem.objects.filter(cart=cart)
                    #     for item in cart_items:
                    #         item.user = user
                    #         item.save()
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user = user
                            item.save()
            except:
                pass

            login(request, user)
            messages.success(request, f'Welcome! Glad to have you back')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
           

                print('query: ', query)
                # query:  next=/payment/checkout/
                print('_________')
                params = dict(x.split('=') for x in query.split('&'))
                print('params: ', params)
                # params:  {'next': '/payment/checkout/'}
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
                
            except:
                return redirect('dashboard')
        else:
            # messages.info(request, f'Invalid login credentials. Please check and try again.')
            return redirect('login')
    
    context = {}
    return render(request, 'users/login.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, f'You just logged out. See you around!')
    return redirect('login')


def activate(request, uidb64, token):
    # return HttpResponse('ok')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Users._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None

    if user != None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f'congrats! Account successfully verified and activated')
        return redirect('login')
    
    else:
        messages.info(request, f'Invalid Activation Link')
        return redirect('register')
    
def dashboard(request):

    context = {}
    return render(request, 'users/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        # check if mail is in database
        if Users.objects.filter(email=email).exists:
            user = Users.objects.get(email__iexact=email)

            # reset password email
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Notification'
            message = render_to_string('users/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send() 

            messages.success(request, f'Password reset link has been sent to your email.')
            return redirect('login')
        else:
            messages.warning(request, f'Email does not exist in our database. Please check and try again')
            return redirect('forgot_password')   
    context = {}
    return render(request, 'users/forgot_password.html', context)


def reset_password_validation(request, uidb64, token):
    # return HttpResponse('ok')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Users._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None

    if user != None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, f'Please reset your password')
        return redirect('reset_password')
    else:
        messages.warning(request, f'Password reset link has expired. please try again')
        return redirect('forgot_password')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Users.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, f'Password Reset Completed')
            return redirect('login')
        else:
            messages.success(request, f'Passwords mis-match. Please try again')
            return redirect('reset_password')
    else:
        return render(request, 'users/reset_password.html')