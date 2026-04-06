from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .models import Item, ItemImage
 


def send_match_email(user, items):
    if not items or not user.email:
        return

    links = []
    for item in items:
        url = f"http://127.0.0.1:8000{reverse('item_details', args=[item.id])}"
        links.append(f"{item.title}: {url}")

    message = "We found possible matches for your item:\n\n"
    message += "\n".join(links)

    send_mail(
        subject="Potential Matches Found",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True
    )


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from decimal import Decimal
import math

# Helper for Distance Calculation (Haversine Formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    """Returns distance between two points in kilometers"""
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    R = 6371  # Earth radius in km
    lat1 = Decimal(lat1)
    lon1 = Decimal(lon1)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def hamming_distance(hash1, hash2):
    try:
        return bin(int(hash1, 16) ^ int(hash2, 16)).count('1')
    except (ValueError, TypeError):
        return 999

def find_intelligent_matches(current_item):
    """
    Finds matches based on:
    1. Opposite item type (Lost vs Found)
    2. Exact Category
    3. Location Proximity (within 10km) (Haversine Formula)
    4. Image Similarity (hamming distance of perceptual hashes)
    """
    # 1. Start with basic filters: Must be opposite type, same category, and active
    opposite_type = "found" if current_item.item_type == "lost" else "lost"
    
    potential_matches = Item.objects.filter(
        item_type=opposite_type,
        category=current_item.category,
        status="active",
        is_deleted=False
    ).exclude(id=current_item.id).prefetch_related('images')

    matched_ids = []

    for candidate in potential_matches:
        is_match = False
        
        # --- CRITERIA A: Location (If coordinates exist) ---
        if current_item.latitude and candidate.latitude:
            dist = calculate_distance(
                current_item.latitude, current_item.longitude,
                candidate.latitude, candidate.longitude
            )
            # Only consider it a match if within 10km (adjust as needed)
            if dist and dist <= getattr(settings, 'LOCATION_THRESHOLD_KM', 10):
                is_match = True
        
        # --- CRITERIA B: Image Hashing (If not already matched by location) ---
        if not is_match:
            current_hashes = current_item.images.values_list('perceptual_hash', flat=True)
            candidate_hashes = candidate.images.values_list('perceptual_hash', flat=True)
            
            for h1 in current_hashes:
                if is_match: break
                for h2 in candidate_hashes:
                    if h1 and h2 and hamming_distance(h1, h2) <= getattr(settings, 'IMAGE_HASH_THRESHOLD', 5):
                        is_match = True
                        break

        # --- CRITERIA C: Text Keyword fallback ---
        if not is_match and current_item.title.lower() in candidate.title.lower():
            is_match = True

        if is_match:
            matched_ids.append(candidate.id)

    return Item.objects.filter(id__in=matched_ids)[:10]

 


@receiver(post_save, sender=Item)
def match_on_item_update(sender, instance, created, **kwargs):
    
    if not created:
        return

    matches = find_intelligent_matches(instance)
    if matches.exists():
        send_match_email(instance.reported_by, matches)
        print(f"Intelligent match found {matches.count()} items for Item {instance.id}")