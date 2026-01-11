from django import forms
from .models import Order 
class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'phone', 'email', 'address', 'city', 'state', 'country', 'order_note')

# class PaypalPaymentsForm(forms.Form):
#     def render(self, *args, **kwargs):
#         if not args and not kwargs:
#             return format_html
#                 <form action='{0}' method='post'>"""
#                 {1}
#                 <input type='image' src='2', name='submit' alt='buy it now'>
#                 </form>
#                 """,
#             self.get_login_url()
#             self.as_p()
#             self.get_image()
#         else:
#             pass