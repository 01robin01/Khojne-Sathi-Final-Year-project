from django.urls import path
from django.shortcuts import render
from .views import * 

urlpatterns = [
     path('items/', my_found_items, name='my_found_items'),
    path('report/', report_found, name='report_found'),
    

    

]
