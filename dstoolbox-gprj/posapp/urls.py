from django.urls import path,include
from .views import *
from . import views


urlpatterns = [
    path('admin/', views.dashboard, name='dashboard'),
    path('admin/rewards/', views.reward_dashboard, name="reward"),
    path('create-reward/', views.create_reward, name='create_reward'),
    path('toggle-reward/<int:reward_id>/', views.toggle_reward, name='toggle_reward'),
    path('delete-reward/<int:reward_id>/', views.delete_reward, name='delete_reward'),
    path('',include('user.urls')), 
]

