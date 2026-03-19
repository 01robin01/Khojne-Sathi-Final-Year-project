from django.contrib import admin
from .models import Category, Item,ItemImage,Match,Claim,Notification 



admin.site.register(Category)
admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(Match)
admin.site.register(Claim)
admin.site.register(Notification)
# Register your models here.
