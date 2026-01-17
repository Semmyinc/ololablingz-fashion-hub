from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name='checkout'),
    path("create_order/", views.create_order, name='create_order'),
    path("payments/", views.payments, name='payments'),
    path("charge/", views.charge, name='charge'),
    path('paystack_checkout/<int:order_id>/', views.paystack_checkout, name='paystack_checkout'),
    path('paystack_webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('payment_success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment_failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
    path('stripe_checkout/<int:order_id>/', views.stripe_checkout, name='stripe_checkout'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    # https://unoverpowered-kayce-chidingly.ngrok-free.dev/stripe/webhook
    path("order_complete/<str:order_number>", views.order_complete, name='order_complete'),
]