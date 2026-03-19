from django.urls import path
from django.shortcuts import render

urlpatterns = [
    path('items/',lambda request: render(request, 'my-found-items.html'), name='my_found_items'),
    path('report/',lambda request: render(request, 'report-found.html'), name='report_found'),
    

    

]
