from django.contrib import admin
from .models import Category, Product, SimilarProduct
from django.utils.html import format_html
import admin_thumbnails
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border radius:50%;">'.format(object.image.url))
    thumbnail.short_description = 'Category Image'

    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('image', 'category_name', 'slug')
    list_display_links = ['category_name']
    

admin.site.register(Category, CategoryAdmin)

@admin_thumbnails.thumbnail('image')
class SimilarProductInline(admin.TabularInline):
    model = SimilarProduct
    extra = 1

    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border radius:50%;">'.format(object.image.url))
    thumbnail.short_description = 'Similar Product Image'


class ProductAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border radius:50%;">'.format(object.image.url))
    thumbnail.short_description = 'Product Image'
    
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ('image', 'product_name', 'slug', 'category', 'promo', 'price', 'promo_price')
    list_display_links = ['product_name']
    readonly_fields = ['created_at', 'modified_at']
    ordering = ['-modified_at']
    inlines = (SimilarProductInline,)

    
admin.site.register(Product, ProductAdmin)


    

admin.site.register(SimilarProduct)