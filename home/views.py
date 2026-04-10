
from django.shortcuts import redirect, render
from .models import Category, Item, ItemImage
from PIL import Image
from django.contrib import messages
import imagehash
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def is_admin(user):
    return user.is_staff or getattr(user, 'role', '') in ['admin', 'moderator']

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

@user_passes_test(is_admin)
def delete_item(request, id):
    item = Item.objects.filter(id=id).first()
    if item:
        item.delete()
        messages.success(request, 'Item deleted successfully.')
    else:
        messages.error(request, 'Item not found.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@user_passes_test(is_admin)
def delete_user(request, id):
    user = CustomUser.objects.filter(id=id).first()
    if user:
        user.delete()
        messages.success(request, 'User deleted successfully.')
    else:
        messages.error(request, 'User not found.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_users'))

@user_passes_test(is_admin)
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

@user_passes_test(is_admin)
def user_detail(request, id):
    from django.shortcuts import get_object_or_404
    user = get_object_or_404(CustomUser, id=id)
    context = {'user_obj': user}
    return render(request, 'admin-user-detail.html', context)

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = CustomUser.objects.filter(date_joined__gte=thirty_days_ago).count()

    total_lost = Item.objects.filter(item_type='lost', is_deleted=False).count()
    total_found = Item.objects.filter(item_type='found', is_deleted=False).count()
    total_returned = Item.objects.filter(status='resolved', is_deleted=False).count()

    # Base64 helper
    def get_graph():
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        return base64.b64encode(image_png).decode('utf-8')

    # 1. Bar Chart: Users per month
    users_by_month = CustomUser.objects.annotate(month=TruncMonth('date_joined')).values('month').annotate(total=Count('id')).order_by('month')
    months = [u['month'].strftime('%b %Y') if u['month'] else 'Unknown' for u in users_by_month]
    counts = [u['total'] for u in users_by_month]
    plt.figure(figsize=(8, 4))
    plt.bar(months, counts, color='skyblue')
    plt.title('Users Registered Per Month')
    plt.xlabel('Month')
    plt.ylabel('Users')
    plt.xticks(rotation=45)
    plt.tight_layout()
    bar_chart = get_graph()
    plt.close()

    # 2. Pie Chart: Active vs Inactive
    inactive_users = total_users - active_users
    plt.figure(figsize=(6, 6))
    plt.pie([active_users, inactive_users], labels=['Active', 'Inactive'], autopct='%1.1f%%', colors=['#28a745', '#dc3545'])
    plt.title('Active vs Inactive Users')
    plt.tight_layout()
    pie_chart = get_graph()
    plt.close()

    # 3. Line Chart: User growth over time (cumulative)
    cumulative_counts = []
    current_total = 0
    for count in counts:
        current_total += count
        cumulative_counts.append(current_total)
    
    plt.figure(figsize=(8, 4))
    plt.plot(months, cumulative_counts, marker='o', linestyle='-', color='indigo')
    plt.title('Cumulative User Growth')
    plt.xlabel('Month')
    plt.ylabel('Total Users')
    plt.xticks(rotation=45)
    plt.tight_layout()
    line_chart = get_graph()
    plt.close()

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'recent_users': recent_users,
        'total_lost': total_lost,
        'total_found': total_found,
        'total_returned': total_returned,
        'bar_chart': bar_chart,
        'pie_chart': pie_chart,
        'line_chart': line_chart,
    }
    return render(request, 'admin-dashboard.html', context)



@user_passes_test(is_admin)
def admin_lost(req):
    context = {
        'items': Item.objects.filter(item_type='lost', is_deleted=False)
    }
    return render(req,'admin-lost.html',context)

@user_passes_test(is_admin)
def admin_found(req):
    context = {
        'items': Item.objects.filter(item_type='found', is_deleted=False)
    }
    return render(req,'admin-found.html',context)

@user_passes_test(is_admin)
def admin_users(req):
    query = req.GET.get('q', '')
    status_filter = req.GET.get('status', 'all')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'suspended':
        users = users.filter(is_active=False)

    paginator = Paginator(users, 10) # 10 users per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    }
    return render(req,'admin-users.html',context)

@user_passes_test(is_admin)
def admin_claims(req):
    context = {
        'claims': Item.objects.filter(claimed_by__isnull=False, is_deleted=False)
    }
    return render(req,'admin-claims.html',context)