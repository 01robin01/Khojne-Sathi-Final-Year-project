from django.shortcuts import redirect, render


# Create your views here.
'''
class Item(models.Model):
    ITEM_TYPE_CHOICES = (
        ("lost", "Lost"),
        ("found", "Found"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("matched", "Matched"),
        ("resolved", "Resolved"),
        ("expired", "Expired"),
        ("withdrawn", "Withdrawn"),
    )

    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    reported_by = models.ForeignKey(
        User, related_name="reported_items", on_delete=models.CASCADE
    )

    # Ownership semantics
    claimed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="claimed_items",
        on_delete=models.SET_NULL,
    )

    # Location (structured)
    location_text = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Time semantics
    event_at = models.DateTimeField(help_text="When item was lost or found")
    reported_at = models.DateTimeField(default=timezone.now)

    is_sensitive = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    is_deleted = models.BooleanField(default=False)
    objects = ItemManager()
    admin_objects = models.Manager()  

    def __str__(self):
        return f"{self.item_type.upper()} - {self.title}"
    
    def delete(self,*args,**kwargs):
        self.is_deleted=True
        self.save()

    def restore(self,*args,**kwargs):
        self.is_deleted=False
        self.save()


# --------------------
# ITEM IMAGES
# --------------------
class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="items/")
    perceptual_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
'''
from home.models import Item, Category,ItemImage
from PIL import Image
import imagehash
from django.contrib import messages

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
            phash = imagehash.phash(Image.open(image))
            
            ItemImage.objects.create(item=item, image=image, perceptual_hash=str(phash))
            messages.success(request, 'Lost item reported successfully.')
        return redirect('my_lost_items')
    return render(request, 'report-lost.html')
