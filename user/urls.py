from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', menu_view, name='menu'),# menu/
    path('order/<int:order_id>/', order_detail_view, name='order_detail'),
    path('add_to_cart/<int:menu_id>/', add_to_cart, name='add_to_cart'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)