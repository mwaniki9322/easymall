from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='admin_c'),
    path('users/', views.users_view, name='admin_users'),
    path('users/<int:pk>/', views.single_user_view, name='admin_single_user'),
    path('users/<int:pk>/change-password/', views.change_user_password_view, name='admin_change_user_password'),
    path('users/<int:pk>/delete/', views.delete_user_view, name='admin_delete_user'),

    path('products/', views.products_view, name='admin_products'),
    path('products/add/', views.AddProductView.as_view(), name='admin_add_product'),
    path('products/<str:slug>/manage/', views.ManageProductView.as_view(), name='admin_manage_product'),
    path('products/<str:slug>/delete/', views.delete_product_view, name='admin_delete_product'),
    path('delete-gallery-img/', views.delete_gallery_img_view, name='admin_delete_gallery_img'),

    path('payments/', views.payments_view, name='admin_payments'),

    path('orders/', views.orders_view, name='admin_orders'),
    path('orders/<int:pk>/', views.single_order_view, name='admin_single_order'),
    path('orders/<int:pk>/change-status/', views.change_order_status_view, name='admin_change_order_status'),
]
