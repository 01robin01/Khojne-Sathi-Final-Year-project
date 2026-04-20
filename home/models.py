from django.db import models
from accounts.models import CustomUser as User
from django.utils import timezone
from django.urls import reverse
from .managers import ItemManager


# --------------------
# CATEGORY (HIERARCHICAL)
# --------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey( "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


# --------------------
# ITEM (BASE)
# --------------------
class Item(models.Model):
    ITEM_TYPE_CHOICES = (
        ("lost", "Lost"),
        ("found", "Found"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("matched", "Matched"),
        ("resolved", "Resolved"),
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

    def get_absolute_url(self):
        return reverse("item_details", kwargs={"id": self.pk})
    


# --------------------
# ITEM IMAGES
# --------------------
class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name="images", on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    image = models.ImageField(upload_to="items/")
    base64_image = models.TextField(blank=True)  # Store base64 version for sensitive images
    perceptual_hash = models.CharField(max_length=64, blank=True)   #Like Hashing but more visual where similar images result in similar hashes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.item.title}"

    def save(self,*args,**kwargs):
        if self.is_private and not self.base64_image:
            import base64
            from io import BytesIO
            from PIL import Image,ImageFilter

            img = Image.open(self.image)

            blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
            buffer = BytesIO()
            blurred.save(buffer, format="JPEG")
            encoded = base64.b64encode(buffer.getvalue()).decode()
            self.base64_image = encoded
        super().save(*args,**kwargs)

    def delete(self,*args,**kwargs):
        self.image.delete(save=False)
        super().delete(*args,**kwargs)

    


# --------------------
# MATCHES (CORE LOGIC)
# --------------------
class Match(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("claimed", "Claimed"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    lost_item = models.ForeignKey(
        Item, related_name="lost_matches", on_delete=models.CASCADE
    )
    found_item = models.ForeignKey(
        Item, related_name="found_matches", on_delete=models.CASCADE
    )

    score = models.FloatField(help_text="Match confidence score")
    criteria_snapshot = models.JSONField(help_text="Why this match was made")

    created_by_system = models.BooleanField(default=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lost_item", "found_item")


# --------------------
# CLAIM (DEPENDS ON MATCH)
# --------------------
# class Claim(models.Model):
#     STATUS_CHOICES = (
#         ("submitted", "Submitted"),
#         ("under_review", "Under Review"),
#         ("approved", "Approved"),
#         ("rejected", "Rejected"),
#     )
    

#     item = models.ForeignKey(Item, related_name="claims", on_delete=models.CASCADE)
#     claimant = models.ForeignKey(User, on_delete=models.CASCADE)

#     proof_text = models.TextField()
#     proof_files = models.FileField(upload_to="claims/", blank=True)

#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
#     admin_remarks = models.TextField(blank=True, default="")
#     reviewed_by = models.ForeignKey(
#         User,
#         null=True,
#         blank=True,
#         related_name="reviewed_claims",
#         on_delete=models.SET_NULL,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
class Claim(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    item = models.ForeignKey(Item, related_name="claims", on_delete=models.CASCADE)
    claimant = models.ForeignKey(User, on_delete=models.CASCADE)

    proof_text = models.TextField()
    proof_files = models.FileField(upload_to="claims/", blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_remarks = models.TextField(blank=True, default="")
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="reviewed_claims",
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)

# --------------------
# NOTIFICATIONS
# --------------------
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ("match", "Match"),
        ("claim", "Claim"),
        ("system", "System"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES
    )

    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField()

    is_read = models.BooleanField(default=False)
    dedupe_key = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]



PAYMENT_CHOICES = (
    ("khalti", "Khalti"),
    ("esewa", "eSewa"),
    ("bank_transfer", "Bank Transfer"),
)

payment_status_choices = (
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("failed", "Failed"),
)
class Donation(models.Model):
    donor = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_uuid = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, default="pending")

class Report(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    )

    item = models.ForeignKey(Item, related_name="reports", on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, related_name="reports", on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("item", "reported_by")  # one report per user per item

    def __str__(self):
        return f"Report #{self.id} - {self.item.title}"