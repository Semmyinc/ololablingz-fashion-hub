from django.db import models
from django.urls import reverse
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='uploads/category_picture', default='default.jpg')

    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural = 'Categories'

    def get_slug_url(self):
        return reverse('products_by_category', args=[self.slug])



class Product(models.Model):
    product_name = models.CharField(max_length=50)
    slug = models.SlugField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    promo = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    promo_price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='uploads/product_picture', default='default.jpg')
    available = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    stock_level = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.product_name
    

    def get_slug_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
class SimilarProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/similar_products')

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name_plural =' Similar Product'


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color', 'color'),
    ('size', 'size')
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=255, choices=variation_category_choice)
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return self.product
        return self.variation_value
    
    objects = VariationManager()

