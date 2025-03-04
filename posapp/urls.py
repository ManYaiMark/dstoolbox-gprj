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
    path('accounts/login/', login_view, name='login'),
    path('admin/orders/', views.manage_orders, name='orders'), 
    path('admin/orders/<int:order_id>/detail/', detail_order, name='details'),   
    path('admin/update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin/update/<int:order_id>/', views.update_order, name='update_order'),
    path('admin/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('',include('user.urls')), 
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

