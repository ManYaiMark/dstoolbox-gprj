from django.urls import path,include
from .views import *
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', views.dashboard, name='dashboard'),
    path('admin/rewards/', views.reward_dashboard, name="reward"),
    path('create-reward/', views.create_reward, name='create_reward'),
    path('toggle-reward/<int:reward_id>/', views.toggle_reward, name='toggle_reward'),
    path('delete-reward/<int:reward_id>/', views.delete_reward, name='delete_reward'),
    path('admin/manage_menu/', views.manage_menu, name='manage_menu'),
    path('manage_menu/', views.manage_menu, name='manage_menu'),
    path('admin/menu/add/', views.add_menu, name='add_menu'),
    path('admin/menu/delete/<int:id>/', views.delete_menu, name='delete_menu'),
    path('admin/menu/edit/<int:id>/', views.edit_menu, name='edit_menu'),
    path('admin/orders/', order_list, name='admin_orders'),
    path('',include('user.urls')), 
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

