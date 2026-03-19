
from django.urls import path
from django.shortcuts import render


urlpatterns = [
    path('items/',lambda request: render(request, 'my-lost-items.html'), name='my_lost_items'),
    path('report/',lambda request: render(request, 'report-lost.html'), name='report_lost'),
    
]
