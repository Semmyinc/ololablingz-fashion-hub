from django.contrib import admin
from .models import Category, Product, SimilarProduct, Variation, AboutTeamMember, AboutPerson, AboutSiteHeader, Client
from django.utils.html import format_html
import admin_thumbnails
# Register your models here.

admin.site.site_header = 'Ololablingz Administration'
# admin.site.site_title = 'Ololablingz'

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
    list_display = ('image', 'product_name', 'category', 'stock_level', 'promo', 'price', 'promo_price', 'modified_at', 'available')
    list_display_links = ['product_name']
    readonly_fields = ['created_at', 'modified_at']
    ordering = ['-modified_at']
    inlines = (SimilarProductInline,)

    
admin.site.register(Product, ProductAdmin)


    

admin.site.register(SimilarProduct)

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    # list_display_links = ['variation_category']
    list_editable = ['is_active']
    list_filter = ('product', 'variation_category', 'variation_value')
                   
admin.site.register(Variation, VariationAdmin)


admin.site.register(AboutSiteHeader)
admin.site.register(AboutPerson)
admin.site.register(AboutTeamMember)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'message')
    list_filter = ('name', 'email')

admin.site.register(Client, ClientAdmin)