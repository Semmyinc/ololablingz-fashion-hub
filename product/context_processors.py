from .models import Category, Product
from django.shortcuts import get_object_or_404
def category_menu_links(request):
    links = Category.objects.all()
    # return dict(links=links) this works as well
    # context = {'links':links}
    # return context this works as well
    return {'links':links}


# pages involved - product views, here-context processors and the navbar.html

# def specific_product_link(request, category_slug, product_slug ):
#     link = specific_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
#     return dict(link=link)
