from django.urls import path, include
from django.shortcuts import render
# from django.contrib import admin

urlpatterns = [
    path('',lambda request: render(request, 'index.html'), name='landing_page'),
    path('admin-dashboard/',lambda request: render(request, 'admin-dashboard.html'), name='admin_dashboard'),
    path('dashboard/',lambda request: render(request, 'dashboard.html'), name='user_dashboard'),
    path('admin-lost/',lambda request: render(request, 'admin-lost.html'), name='admin_lost'),  
    path('admin-found/',lambda request: render(request, 'admin-found.html'), name='admin_found'),
    path('admin-users/',lambda request: render(request, 'admin-users.html'), name='admin_users'),
    path('admin-claims/',lambda request: render(request, 'admin-claims.html'), name='admin_claims'),
    
    # path('admin/', admin.site.urls),
    # path('accounts/', include('allauth.urls')),
    
    
]
