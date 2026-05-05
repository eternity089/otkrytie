from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('contact', views.contact, name='contact'),
    path('product/<int:pk>', views.ProductDetail.as_view(), name='product'),
    path('cart', views.cart, name='cart'),
    path('orders', views.OrderListView.as_view(), name='orders'),
    path('get-addresses/', views.get_addresses, name='get_addresses'),
    path('set-address/', views.set_address, name='set_address'),
    path('set-city/', views.set_city, name='set_city'),
    path('catalog/<slug:slug>/', views.catalog, name='catalog'),
    path('about/', views.about, name='about'),
    path('delete_order/<pk>', views.delete_order, name='delete_order'),
    path('to_cart/<pk>', views.to_cart, name='to_cart'),
    path('remove_to_cart/<pk>', views.remove_to_cart, name='remove_to_cart'),
    path('get-cart-total/', views.get_cart_total, name='get_cart_total'),
    path('search/', views.search, name='search'),
]