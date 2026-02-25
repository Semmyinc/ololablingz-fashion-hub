from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Category, SimilarProduct, Client, AboutPerson, AboutSiteHeader, AboutTeamMember
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
# Create your views here.

def home(request):
    products = Product.objects.all().filter(available=True)[:3]
    # return HttpResponse('Home Page')
    context = {'products':products}
    return render(request, 'product/index.html', context)

def about(request):
    context = {}
    return render(request, 'about.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        client = Client.objects.create(name=name, email=email, subject=subject, message=message)
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    
    context = {}
    return render(request, 'contact.html', context)

def products(request, category_slug=None):
    # fetch all products under a category 
    category = None
    products = None

    if category_slug != None:
        category = Category.objects.get(slug=category_slug)
        # category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

        # fetch all products 
    else:
        products = Product.objects.all().filter(available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {'products':paged_products, 'product_count':product_count}
    return render(request, 'product/products.html', context)


def product_detail(request, category_slug, product_slug):
    specific_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug, available=True)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=specific_product).exists()
    # return HttpResponse(in_cart)

    # category = Category.objects.get(slug=category_slug)
    related_products = Product.objects.filter(category__slug=category_slug, available=True).exclude(id=specific_product.id)
    # print(related_products)
    # exit()

    similar_products = SimilarProduct.objects.filter(product_id=specific_product.id)
    context = {'specific_product':specific_product, 'related_products':related_products, 'similar_products':similar_products, 'in_cart':in_cart}
    return render(request, 'product/product-detail.html', context)


def search(request):
    searched_items = None
    if request.method == 'POST':
        search = request.POST['search']
        searched_items = Product.objects.filter(Q(product_name__icontains=search)|
                                          
                                          Q(category__category_name__icontains=search)|
                                          Q(category__description__icontains=search)|
                                          Q(description__icontains=search)|
                                          Q(promo__icontains=search)|
                                          Q(available__icontains=search))
        # return HttpResponse(search)
        # exit()
        search_count = searched_items.count()
        if searched_items:
            messages.success(request, f'{search_count} products found!')
            context = {'searched_items':searched_items, 'search_count':search_count}
            return render(request, 'search.html', context)
        else:
            messages.warning(request, f'Found no match for your search. Please try again with a more specific word or phrase!')
            return redirect('search')
    else:
        context = {'searched_items':searched_items}
        return render(request, 'search.html', context)