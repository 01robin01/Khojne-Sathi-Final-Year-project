from django.conf import settings
from django.shortcuts import redirect, render


# Create your views here.

from home.models import Item, Category,ItemImage
from PIL import Image
import imagehash
from django.contrib import messages
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .utils import validate_image_size
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden


@login_required
def report_lost(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = Category.objects.get(id=request.POST.get('category'))
        location_text = request.POST.get('location_text')
        long = request.POST.get('longitude')
        lat = request.POST.get('latitude')
        is_sensitive = request.POST.get('is_sensitive') == 'on'
        event_at = request.POST.get('event_at')
        images = request.FILES.getlist('images')
        
        if len(images) > 10:
            messages.error(request, "You can only upload up to 10 images.")
            return redirect('report_lost')
        item = Item.objects.create(
            item_type='lost',
            title=title,
            description=description,
            category=category,
            reported_by=request.user,
            location_text=location_text,
            event_at=event_at,
            longitude=long,
            latitude=lat,
            is_sensitive=is_sensitive
            
        )

        for image in images:
            
            if image.size > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
                messages.error(
                    request,
                    f"{image.name} exceeds 2MB limit."
                     )
                continue

            try:
                img = Image.open(image)
                img = img.convert("RGB")  
                
                img.thumbnail(settings.MAX_RESOLUTION, Image.LANCZOS) # pyright: ignore[reportAttributeAccessIssue]
                
                img_io = BytesIO()
                img.save(img_io, format='JPEG', quality=90)
                img_io.seek(0)

                django_image = InMemoryUploadedFile(
                    img_io,
                    None,
                    image.name,
                    'image/jpeg',
                    img_io.getbuffer().nbytes,
                    None
                )


                phash = imagehash.phash(
                    Image.open(django_image),
                    hash_size=16
                )


                ItemImage.objects.create(
                    item=item,
                    perceptual_hash=str(phash)
                )
                
                
            except Exception:
                messages.error(
                    request,
                    f"{image.name} is not a valid image."
                )

        messages.success(
            request,
            'Lost item reported successfully.'
        )
        return redirect('my_lost_items')

        return render(request, 'report-lost.html')
    @login_required
    def my_lost_items(request):
        items = Item.objects.filter(
        reported_by=request.user,
        item_type='lost'
        ).order_by('-reported_at')
        paginator = Paginator(items, 3)  # Show 3 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj
        }
    return render(request, 'my-lost-items.html', context)


@login_required
def update_item(request, item_id):
    item = Item.objects.get(id=item_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        item.title = request.POST.get("title", item.title)
        item.description = request.POST.get("description", item.description)
        category_id = request.POST.get("category", item.category.id)
        item.category = Category.objects.get(id=category_id)

        item.location_text = request.POST.get("location_text", item.location_text)
        item.latitude = request.POST.get("latitude", item.latitude)
        item.longitude = request.POST.get("longitude", item.longitude)
        item.event_at = request.POST.get("event_at", item.event_at)
        item.is_sensitive = bool(request.POST.get("is_sensitive", item.is_sensitive))
        item.save()
        
        # Handle new image uploads
        images = request.FILES.getlist('images')
        
        existing_images_count = item.images.count()
        if existing_images_count + len(images) > 10:
            messages.error(request, f"You can only have up to 10 images per item. You currently have {existing_images_count} images.")
            return redirect("update_item", item_id=item.id)
            
        for image in images:
            if image.size > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
                messages.error(
                    request,
                    f"{image.name} exceeds limit."
                )
                continue

            try:
                img = Image.open(image)
                img = img.convert("RGB")
                img.thumbnail(settings.MAX_RESOLUTION, Image.LANCZOS)
                
                img_io = BytesIO()
                img.save(img_io, format='JPEG', quality=90)
                img_io.seek(0)

                django_image = InMemoryUploadedFile(
                    img_io, None, image.name, 'image/jpeg',
                    img_io.getbuffer().nbytes, None
                )
                
                phash = imagehash.phash(Image.open(django_image), hash_size=16)
                
                ItemImage.objects.create(
                    item=item,
                    image=django_image,
                    perceptual_hash=str(phash)
                )
            except Exception:
                messages.error(request, f"{image.name} is not a valid image.")
        
        messages.success(request, "Item updated successfully!")
        return redirect("my_lost_items")

    context = {
        "item": item,
        "categories": categories
    }

    return render(request, "report-lost.html", context)


@login_required
def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully!")
        return redirect("my_lost_items")

    context = {
        "item": item
    }
    return render(request, "confirm-delete.html", context)

@login_required
def delete_item_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(ItemImage, id=image_id)
        if image.item.reported_by != request.user:
            return HttpResponseForbidden("You are not allowed to delete this image.")
        
        item_id = image.item.id
        image.delete()
        messages.success(request, "Image deleted successfully!")
        return redirect("update_item", item_id=item_id)
    return redirect("my_lost_items")


@login_required
def lost_item_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    context = {
        "item": item
    }
    return render(request, "item-details.html", context)