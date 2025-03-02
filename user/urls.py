from django.urls import path
from .views import *

urlpatterns = [
    path('', menu_view, name='menu'),# menu/
    path('order/<int:order_id>/', order_detail_view, name='order_detail'),
    path('add_to_cart/<int:menu_id>/', add_to_cart, name='add_to_cart'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]