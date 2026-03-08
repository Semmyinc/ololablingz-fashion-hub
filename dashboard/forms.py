from django import forms
from users.models import Users
from product.models import Product, Category 

class UserForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'username', 'email', 'password')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description', 'image']