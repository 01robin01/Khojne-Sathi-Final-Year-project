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
    path('admin-delete-item/<int:id>/', delete_item, name='delete_item'),
    path('admin-delete-user/<int:id>/', delete_user, name='delete_user'),
    path('admin-suspend-user/<int:id>/', suspend_user, name='suspend_user'),
    path('admin-user-detail/<int:id>/', user_detail, name='user_detail'),

    # Claims & Reports dummy routes
    path('admin-claims/',admin_claims, name='admin_claims'),
    path('admin-claim/<int:id>/', admin_claim_detail, name='admin_claim'),
    path('process-claim/<int:id>/', process_claim, name='process_claim'),
    path('delete-claim/<int:id>/', delete_claim, name='delete_claim'),
    path('item-reports/', item_reports, name='item_reports'),
    path('reports/', report_detail, name='report_detail'),
    path('delete-report/<int:id>/', delete_report, name='delete_report'),
    path('admin-report/<int:id>/', admin_report_detail, name='admin_report_detail'),
    
    #Donations 
    path('donate/',donate,name="donate"),
    path('donate/confirm/<str:transaction_uuid>/',donation_confirm,name="donation_confirm"),
    path('donate/success/<str:transaction_uuid>/',donation_success,name="donation_success"),
    path('donate/failure/<str:transaction_uuid>/',donation_failure,name="donation_failure"),
]