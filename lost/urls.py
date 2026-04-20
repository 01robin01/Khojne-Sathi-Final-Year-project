
from django.urls import path
from django.shortcuts import render
from .views import * 


urlpatterns = [
    path('items/',my_lost_items, name='my_lost_items'),
    path('items/<int:item_id>/',lost_item_detail, name='view_item'),
    path('items/<int:item_id>/update/',update_item, name='update_item'),
    path('items/<int:item_id>/delete/',delete_item, name='delete_item'),
    path('items/image/<int:image_id>/delete/', delete_item_image, name='delete_item_image'),
    path('report/',report_lost, name='report_lost'),
     path('claim/<int:item_id>/', claim_item, name='claim_item'),
    
]