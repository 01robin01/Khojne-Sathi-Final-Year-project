from django.urls import path, include
from django.shortcuts import render
from .views import * 
# from django.contrib import admin

urlpatterns = [
    path('',index, name='landing_page'),
    path('search/',search, name='search_page'),
    path('item-details/<int:id>/',item_details, name='item_details'),
    path('admin-dashboard/',admin_dashboard, name='admin_dashboard'),
    path('dashboard/',dashboard, name='user_dashboard'),
    path('admin-lost/',admin_lost, name='admin_lost'),  
    path('admin-found/',admin_found, name='admin_found'),
    path('admin-users/',admin_users, name='admin_users'),
    path('admin-claims/',admin_claims, name='admin_claims'),
    
    path('admin-delete-item/<int:id>/', delete_item, name='delete_item'),
    path('admin-delete-user/<int:id>/', delete_user, name='delete_user'),
    path('admin-suspend-user/<int:id>/', suspend_user, name='suspend_user'),
    path('admin-user-detail/<int:id>/', user_detail, name='user_detail'),
]