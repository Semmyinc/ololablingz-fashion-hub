from django.shortcuts import render, redirect, get_object_or_404
from users.models import Users
from product.models import Product, Category
from payment.models import Order
from .forms import UserForm, ProductForm, CategoryForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
# Dashboard Order History Section 

def dashboard_transactions(request):
    context = {}
    return render(request, 'dashboard/dashboard_transactions.html', context)

def dashboard_receivedorders(request):
    context = {}
    return render(request, 'dashboard/dashboard_receivedorders.html', context)

def dashboard_orderhistory(request):
    orders = Order.objects.all()
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    order_count = orders.count()
    context = {'orders':paged_orders, 'order_count':order_count}
    return render(request, 'dashboard/dashboard_orderhistory.html', context)

def dashboard_orderdetail(request, pk):
    context = {}
    return render(request, 'dashboard/dashboard_orderdetail.html', context)

# Dashboard Statistics section 
def dashboard(request):
    products = Product.objects.all()
    product_count = products.count()
    categories = Category.objects.all()
    category_count = categories.count
    users = Users.objects.all()
    user_count = users.count()
    orders = Order.objects.all()
    order_count = orders.count()
    context = {'products':products, 'product_count':product_count, 'categories':categories, 'category_count':category_count, 'users':users, 'user_count':user_count, 'orders':orders, 'order_count':order_count}
    return render(request, 'dashboard/dashboard.html', context)

def dashboard_categories(request):
    # categories = Category.objects.all()
    context = {}
    # context = {'categories':categories}
    return render(request, 'dashboard/dashboard_categories.html', context)

def dashboard_products(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'dashboard/dashboard_products.html', context)

def dashboard_users(request):
    users = Users.objects.all()
    context = {'users':users}
    return render(request, 'dashboard/dashboard_users.html', context)

# Dashboard Category CRUD section
def dashboard_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['category_name']
            form.save()
            messages.success(request, f'{name} has just been added t product list')
            return redirect('dashboard_products')
        messages.errors(request, f'Form not processed due to the errors below. Please amend and try again.')
    
    form = CategoryForm()
    context = {'form':form}
    return render(request, 'dashboard/dashboard_add_category.html', context)

def dashboard_edit_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            name = form.cleaned_data['category_name']
            form.save()
            messages.success(request, f'{name} has just been updated on the category list')
            return redirect('dashboard_categories')
        messages.error(request, f'Form not processed due to the errors below. Please amend and try again.')

    form = CategoryForm(instance=category)
    context = {'form':form}
    return render(request, 'dashboard/dashboard_edit_category.html', context)

def dashboard_delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category deleted successfully')
        return redirect('dashboard_categories')
    
    context = {'category':category}
    return render(request, 'dashboard/dashboard_delete_category.html', context)


# Dashboard Product CRUD section 
def dashboard_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['product_name']
            form.save()
            messages.success(request, f'{name} has just been added t product list')
            return redirect('dashboard_products')
        messages.errors(request, f'Form not processed due to the errors below. Please amend and try again.')

    form = ProductForm()
    context = {'form':form}
    return render(request, 'dashboard/dashboard_add_product.html', context)

def dashboard_edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            name = form.cleaned_data['product_name']
            form.save()
            messages.success(request, f'{name} has just been updated on the product list')
            return redirect('dashboard_products')
        messages.error(request, f'Form not processed due to the errors below. Please amend and try again.')
    form = ProductForm(instance=product)
    context = {'form':form}
    return render(request, 'dashboard/dashboard_edit_product.html', context)

def dashboard_delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Product deleted successfully')
        return redirect('dashboard_products')
    
    context = {'product':product}
    return render(request, 'dashboard/dashboard_delete_product.html', context)

# Dashboard User CRUD section 
def dashboard_add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            form.save()
            messages.success(request, f'Account has just been created for {first_name} {last_name}')
            return redirect('dashboard_users')
        messages.errors(request, f'Form not processed due to the errors below. Please amend and try again.')
        
    form = UserForm()   
    context = {'form':form}
    return render(request, 'dashboard/dashboard_add_user.html', context)

def dashboard_edit_user(request, pk):
    user = get_object_or_404(Users, id=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            form.save()
            messages.success(request, f'Account has just been updatedfor {first_name} {last_name}')
            return redirect('dashboard_users')
        messages.errors(request, f'Form not processed due to the errors below. Please amend and try again.')
    
    form = UserForm(instance=user)   
    context = {'form':form}
    return render(request, 'dashboard/dashboard_edit_user.html', context)


def dashboard_delete_user(request, pk):
    user = get_object_or_404(Users, id=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Account deleted successfully')
        return redirect('dashboard_users')
    
    context = {'user':user}
    return render(request, 'dashboard/dashboard_delete_user.html', context)