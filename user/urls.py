from django.urls import path
from .views import *
from posapp import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', menu_view, name='menu'),# menu/
    path('my-orders/', my_orders, name='my_orders'),
    path('order/<int:order_id>/', order_detail_view, name='order_detail'),
    path('order_status/', order_status, name='order_status'),

    path('add_to_cart_guest/<int:menu_id>/', add_to_cart_guest, name='add_to_cart'),
    path('add_to_cart/<int:menu_id>/', add_to_cart, name='plus_to_cart'),
    path('decrease_quantity/<int:menu_id>/', decrease_quantity, name='decrease_quantity'),
    path('cart/', cart_view, name='cart'),
    path('cart/remove/<int:menu_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),

    path('login/', login_and_convert_cart, name='login'),

    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('check_points/', check_points, name='check_points'),
    # path('order_detail/<int:order_id>/', order_detail_view, name='oder_detail'),

    path('admin/', views.dashboard, name='dashboard'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
