from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, Category, SimilarProduct
# Create your views here.

def home(request):
    products = Product.objects.all().filter(available=True)[:3]
    # return HttpResponse('Home Page')
    context = {'products':products}
    return render(request, 'product/index.html', context)

def products(request, category_slug=None):
    # fetch all products under a category 
    category = None
    products = None

    if category_slug != None:
        category = Category.objects.get(slug=category_slug)
        # category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, available=True)
        product_count = products.count()

        # fetch all products 
    else:
        products = Product.objects.all().filter(available=True)
        product_count = products.count()

    context = {'products':products, 'product_count':product_count}
    return render(request, 'product/products.html', context)


def product_detail(request, category_slug, product_slug):
    specific_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug, available=True)

    # category = Category.objects.get(slug=category_slug)
    related_products = Product.objects.filter(category__slug=category_slug, available=True).exclude(id=specific_product.id)
    # print(related_products)
    # exit()

    similar_products = SimilarProduct.objects.filter(product_id=specific_product.id)
    context = {'specific_product':specific_product, 'related_products':related_products, 'similar_products':similar_products }
    return render(request, 'product/product-detail.html', context)