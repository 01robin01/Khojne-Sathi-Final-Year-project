
from django.urls import path
from django.shortcuts import render
from .views import * 


urlpatterns = [
    path('items/',my_lost_items, name='my_lost_items'),
    path('report/',report_lost, name='report_lost'),
    
]
