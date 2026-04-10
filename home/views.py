
from django.shortcuts import redirect, render
from .models import Category, Item, ItemImage
from PIL import Image
from django.contrib import messages
import imagehash

def index(request):
    items = (
        Item.objects
        .prefetch_related('images')
        .order_by('-id')[:10]
    )

    context = {
        "items": items
    }

    return render(request, "Index.html", context)

def search(request):
    if request.method == 'POST':
        query = request.POST.get("q", "")
        img = request.FILES.get("img", None)
        
        results = Item.objects.none()

        if query:
            results = Item.objects.filter(title__icontains=query, is_deleted=False)
            print("Text Results:", results)

        if img is not None:
            print("Image uploaded for search.")
            image = Image.open(img)
            phash = imagehash.phash(image)
            similar_images = ItemImage.objects.filter(perceptual_hash__startswith=str(phash)[:4]).select_related('item')
            image_item_ids = [img_obj.item.id for img_obj in similar_images]
            image_results = Item.objects.filter(id__in=image_item_ids, is_deleted=False)
            results = results | image_results
            print("Image Results:", image_results)

        context = {
            "query": query,
            "matches": results.distinct(),
            "categories": Category.objects.all(),
            "img_searched": img is not None
        }

        return render(request, "search-page.html", context, status=201)



def item_details(req,id):
    context = {
        'item':Item.objects.get(id=id),
        'related_items': Item.objects.filter(category=Item.objects.get(id=id).category).exclude(id=id)[:5]
    }
    return render(req,'item-details.html',context)


def dashboard(request):
    lost_items = Item.objects.filter(item_type='lost', is_deleted=False)
    found_items = Item.objects.filter(item_type='found', is_deleted=False)
    context = {
        'lost_items': lost_items,
        'found_items': found_items
    }
    return render(request, 'dashboard.html',context)

from accounts.models import CustomUser

def delete_item(request, id):
    item = Item.objects.filter(id=id).first()
    if item:
        item.delete()
        messages.success(request, 'Item deleted successfully.')
    else:
        messages.error(request, 'Item not found.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

def delete_user(request, id):
    user = CustomUser.objects.filter(id=id).first()
    if user:
        user.delete()
        messages.success(request, 'User deleted successfully.')
    else:
        messages.error(request, 'User not found.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_users'))

def suspend_user(request, id):
    user = CustomUser.objects.filter(id=id).first()
    if user:
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "suspended"
        messages.success(request, f'User {status} successfully.')
    else:
        messages.error(request, 'User not found.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_users'))

def user_detail(request, id):
    user = CustomUser.objects.filter(id=id).first()
    context = {'user_obj': user}
    return render(request, 'admin-user-detail.html', context)



def admin_lost(req):
    context = {
        'items': Item.objects.filter(item_type='lost', is_deleted=False)
    }
    return render(req,'admin-lost.html',context)

def admin_found(req):
    context = {
        'items': Item.objects.filter(item_type='found', is_deleted=False)
    }
    return render(req,'admin-found.html',context)
def admin_users(req):
    context = {
        'users': CustomUser.objects.all()
    }
    return render(req,'admin-users.html',context)
def admin_claims(req):
    context = {
        'claims': Item.objects.filter(claimed_by__isnull=False, is_deleted=False)
    }
    return render(req,'admin-claims.html',context)