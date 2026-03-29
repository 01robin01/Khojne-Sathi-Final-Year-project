from django.urls import path
from django.shortcuts import render
from .views import * 

urlpatterns = [
     path('items/', my_found_items, name='my_found_items'),
     path('items/<int:item_id>/update/', update_item, name='update_found_item'),
    path('items/image/<int:image_id>/delete/', delete_item_image, name='delete_found_item_image'),
    path('report/', report_found, name='report_found'),
    

    

]
