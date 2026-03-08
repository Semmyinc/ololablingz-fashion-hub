from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path('dashboard_products', views.dashboard_products, name='dashboard_products'),
    path('dashboard_categories', views.dashboard_categories, name='dashboard_categories'),
    path('dashboard_users', views.dashboard_users, name='dashboard_users'),

    # paths for user dashboard users 
    path('dashboard_add_user', views.dashboard_add_user, name='dashboard_add_user'),
    path('dashboard_edit_user/<int:pk>', views.dashboard_edit_user, name='dashboard_edit_user'),
    path('dashboard_delete_user/<int:pk>', views.dashboard_delete_user, name='dashboard_delete_user'),

    # paths for user dashboard products
    path('dashboard_add_product', views.dashboard_add_product, name='dashboard_add_product'),
    path('dashboard_edit_product/<slug:slug>/', views.dashboard_edit_product, name='dashboard_edit_product'),
    path('dashboard_delete_product/<slug:slug>/', views.dashboard_delete_product, name='dashboard_delete_product'),

    # paths for user dashboard categories
    path('dashboard_add_category', views.dashboard_add_category, name='dashboard_add_category'),
    path('dashboard_edit_category/<slug:slug>/', views.dashboard_edit_category, name='dashboard_edit_category'),
    path('dashboard_delete_category/<slug:slug>/', views.dashboard_delete_category, name='dashboard_delete_category'),

    #paths for dashboard orders
    path('orderhistory/', views.dashboard_orderhistory, name='orderhistory'),
    path('orderdetail/<int:pk>/', views.dashboard_orderdetail, name='orderdetail'),
    path('receivedorders/', views.dashboard_receivedorders, name='receivedorders'),
    path('transactions/', views.dashboard_transactions, name='transactions')
]