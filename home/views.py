from django.shortcuts import render
from .models import Item,ItemImage

def index(request):
    items = Item.objects.all().order_by('-id')[:10]


    return render(request, 'Index.html', {'items': items})


