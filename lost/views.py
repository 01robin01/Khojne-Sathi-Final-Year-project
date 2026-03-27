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