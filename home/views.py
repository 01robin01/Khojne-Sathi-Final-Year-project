
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, Claim, Item, ItemImage
from PIL import Image
from django.contrib import messages
import imagehash
from django.contrib.auth.decorators import login_required, user_passes_test
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

# def search(request):
#     if request.method == 'POST':
#         query = request.POST.get("q", "")
#         img = request.FILES.get("img", None)
        
#         results = Item.objects.none()

#         if query:
#             results = Item.objects.filter(title__icontains=query, is_deleted=False)
#             print("Text Results:", results)

#         if img is not None:
#             print("Image uploaded for search.")
#             image = Image.open(img)
#             phash = imagehash.phash(image)
#             similar_images = ItemImage.objects.filter(perceptual_hash__startswith=str(phash)[:4]).select_related('item')
#             image_item_ids = [img_obj.item.id for img_obj in similar_images]
#             image_results = Item.objects.filter(id__in=image_item_ids, is_deleted=False)
#             results = results | image_results
#             print("Image Results:", image_results)

#         context = {
#             "query": query,
#             "matches": results.distinct(),
#             "categories": Category.objects.all(),
#             "img_searched": img is not None
#         }

#         return render(request, "search-page.html", context, status=201)

# def search(request):
    if request.method == 'POST':
        query = request.POST.get("q", "")
        img = request.FILES.get("img", None)

        results = Item.objects.none()

        if query:
            results = Item.objects.filter(title__icontains=query, is_deleted=False)

        if img is not None:
            image = Image.open(img)
            query_phash = imagehash.phash(image)

            # Fetch all hashes and compare with a threshold in Python
            all_images = ItemImage.objects.select_related('item').exclude(perceptual_hash__isnull=True).exclude(perceptual_hash__exact='')
            
            similar_item_ids = []
            for img_obj in all_images:
                try:
                    stored_hash = imagehash.hex_to_hash(img_obj.perceptual_hash)
                    # Hamming distance <= 10 means visually similar
                    if query_phash - stored_hash <= 10:
                        similar_item_ids.append(img_obj.item.id)
                except Exception as e:
                    print(f"Hash comparison error for image {img_obj.id}: {e}")
                    continue

            image_results = Item.objects.filter(id__in=similar_item_ids, is_deleted=False)
            results = results | image_results

        context = {
            "query": query,
            "matches": results.distinct(),
            "categories": Category.objects.all(),
            "img_searched": img is not None,
        }

        return render(request, "search-page.html", context, status=201)

def search(request):
    if request.method == 'POST':
        query = request.POST.get("q", "")
        img = request.FILES.get("img", None)
        
        results = Item.objects.none()

        if query:
            results = Item.objects.filter(title__icontains=query, is_deleted=False)

        if img is not None:
            image = Image.open(img)
            query_phash = imagehash.phash(image, hash_size=16)
            
            all_images = ItemImage.objects.select_related('item').exclude(
                perceptual_hash__isnull=True
            ).exclude(
                perceptual_hash__exact=''
            )
            
            similar_item_ids = []
            for img_obj in all_images:
                try:
                    stored_hash = imagehash.hex_to_hash(img_obj.perceptual_hash)
                    if query_phash - stored_hash <= 20:
                        similar_item_ids.append(img_obj.item.id)
                except Exception as e:
                    print(f"Hash comparison error for image {img_obj.id}: {e}")
                    continue

            image_results = Item.objects.filter(id__in=similar_item_ids, is_deleted=False)
            results = results | image_results

        context = {
            "query": query,
            "matches": results.distinct(),
            "categories": Category.objects.all(),
            "img_searched": img is not None,
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

@user_passes_test(is_admin)
def admin_claim_detail(req, id):
    item = Item.objects.filter(id=id).first()
    return render(req, 'admin-claim.html', {'claim': item})

@user_passes_test(is_admin)
def process_claim(req, id):
    messages.success(req, 'Claim processed.')
    return redirect(req.META.get('HTTP_REFERER', 'admin_claims'))

@user_passes_test(is_admin)
def item_reports(req):
    return render(req, 'list-reports.html', {'reports': []})

@user_passes_test(is_admin)
def report_detail(req):
    # Dummy object wrapper to prevent template crashes when accessing item.title etc.
    class DummyReport:
        id = req.GET.get('id', req.GET.get('item_id', '0'))
        status = 'Pending'
        created_at = timezone.now()
        reason = 'Violation of terms.'
        
        class DummyItem:
            title = 'Sample Item'
            category = 'General'
            location = 'Kathmandu'
            item_type = 'found'
            description = 'Sample description.'
            
            class DummyUser:
                id = 1
                first_name = 'Test'
                last_name = 'User'
                username = 'testuser'
                email = 'test@example.com'
                
            reported_by = DummyUser()
            
        item = DummyItem()
        reported_by = DummyItem.DummyUser()

    report = DummyReport() if (req.GET.get('id') or req.GET.get('item_id')) else None
    return render(req, 'reports.html', {'report': report})

@user_passes_test(is_admin)
def delete_report(req, id):
    messages.success(req, 'Report deleted successfully.')
    return redirect(req.META.get('HTTP_REFERER', 'item_reports'))

from .models import Donation
import uuid
def donate(req):
    if req.method == 'POST':
        amount = req.POST.get('amount')
        donor = req.POST.get('name')
        donation = Donation.objects.create(
            donor=donor,
            amount=amount,
            total_amount=amount,  # Assuming no extra charges for simplicity
            transaction_uuid=str(uuid.uuid4()),
            code="EPAYTEST",
            payment_method="esewa",
            )
        return redirect('donation_confirm', transaction_uuid=donation.transaction_uuid)
    return render(req,'donate.html')

from django_esewa import EsewaPayment

def donation_confirm(req, transaction_uuid):
    order = Donation.objects.filter(transaction_uuid=transaction_uuid).first()
    payment = EsewaPayment(
        product_code=order.code,
        success_url=f"http://localhost:8000/donate/success/{order.transaction_uuid}/",
        failure_url=f"http://localhost:8000/donate/failure/{order.transaction_uuid}/",
        amount=order.amount,
        tax_amount=order.tax_amount,
        total_amount=order.total_amount,
        product_delivery_charge=order.delivery_charge,
        product_service_charge=order.service_charge,
        transaction_uuid=order.transaction_uuid,
        )
    signature = payment.create_signature() #Saves the signature as well as return it
    
    context = {
            'form':payment.generate_form(),
            'amount': order.total_amount,
        }
    return render(req, 'confirm_donation.html',context)

def donation_success(req, transaction_uuid):
    req.GET.get('data')
    order = Donation.objects.filter(transaction_uuid=transaction_uuid).first()
    payment = EsewaPayment(
        product_code=order.code,
        success_url=f"http://localhost:8000/donate/success/{order.transaction_uuid}/",
        failure_url=f"http://localhost:8000/donate/failure/{order.transaction_uuid}/",
        amount=order.amount,
        tax_amount=order.tax_amount,
        total_amount=order.total_amount,
        product_delivery_charge=order.delivery_charge,
        product_service_charge=order.service_charge,
        transaction_uuid=order.transaction_uuid,
        )

    if payment.is_completed(dev=True):
        order.payment_status = 'completed'
        order.save()
    else: 
        return redirect('donation_failure', transaction_uuid=transaction_uuid)
    return render(req, 'donation_success.html', {'transaction_uuid': transaction_uuid})

def donation_failure(req, transaction_uuid):
    donation = Donation.objects.filter(transaction_uuid=transaction_uuid).first()
    if donation:
        donation.payment_status = 'failed'
        donation.save()
    return render(req, 'donation_failure.html', {'transaction_uuid': transaction_uuid})


from home.models import Report

@login_required
def report_detail(request):
    item_id = request.GET.get('item_id')
    item = get_object_or_404(Item, id=item_id) if item_id else None

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        item_id_post = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id_post)

        if not reason:
            messages.error(request, "Please provide a reason for the report.")
            return redirect(f"{request.path}?item_id={item_id_post}")

        if Report.objects.filter(item=item, reported_by=request.user).exists():
            messages.warning(request, "You have already reported this item.")
            return redirect("item_details", id=item.id)

        Report.objects.create(
            item=item,
            reported_by=request.user,
            reason=reason
        )
        messages.success(request, "Report submitted successfully.")
        return redirect("item_details", id=item.id)

    return render(request, "report_detail.html", {"item": item})


@login_required
def item_reports(request):
    reports = Report.objects.all().order_by('-created_at')
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "list-reports.html", {"reports": reports, "page_obj": page_obj})


@login_required
def delete_report(request, id):
    report = get_object_or_404(Report, id=id)
    if request.method == 'POST':
        report.delete()
        messages.success(request, "Report deleted successfully.")
        return redirect("item_reports")
    return redirect("item_reports")

@login_required
def admin_report_detail(request, id):
    report = get_object_or_404(Report, id=id)
    return render(request, "admin_report_detail.html", {"report": report})

# @login_required
# def admin_claims(request):
#     claims = Claim.objects.select_related('item', 'claimant').order_by('-created_at')

#     paginator = Paginator(claims, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'admin-claims.html', {
#         'claims': page_obj,
#         'page_obj': page_obj,
#     })


# @login_required
# def admin_claim_detail(request, id):
#     claim = get_object_or_404(
#         Claim.objects.select_related('item', 'claimant', 'reviewed_by', 'item__category'),
#         id=id
#     )
#     return render(request, 'admin-claim.html', {'claim': claim})


# @login_required
# def process_claim(request, id):
#     claim = get_object_or_404(Claim, id=id)

#     if request.method == 'POST':
#         action = request.POST.get('action')
#         admin_remarks = request.POST.get('admin_remarks', '').strip()

#         if action == 'delete':
#             claim.delete()
#             messages.success(request, 'Claim deleted.')
#             return redirect('admin_claims')

#         claim.admin_remarks = admin_remarks
#         claim.reviewed_by = request.user

#         if action == 'approve':
#             claim.status = 'approved'
#             claim.save()
#             messages.success(request, 'Claim approved successfully.')

#         elif action == 'reject':
#             claim.status = 'rejected'
#             claim.save()
#             messages.success(request, 'Claim rejected.')

#         else:
#             messages.error(request, 'Invalid action.')

#         return redirect('admin_claim', id=claim.id)

#     return redirect('admin_claim', id=claim.id)


# @login_required
# def delete_claim(request, id):


@login_required
def admin_claims(request):
    claims = Claim.objects.select_related('item', 'claimant').order_by('-created_at')

    paginator = Paginator(claims, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin-claims.html', {
        'claims': page_obj,
        'page_obj': page_obj,
    })


@login_required
def admin_claim_detail(request, id):
    claim = get_object_or_404(
        Claim.objects.select_related('item', 'claimant', 'reviewed_by', 'item__category'),
        id=id
    )
    return render(request, 'admin-claim.html', {'claim': claim})


@login_required
def process_claim(request, id):
    claim = get_object_or_404(Claim, id=id)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_remarks = request.POST.get('admin_remarks', '').strip()

        if action == 'delete':
            claim.delete()
            messages.success(request, 'Claim deleted.')
            return redirect('admin_claims')

        claim.admin_remarks = admin_remarks
        claim.reviewed_by = request.user

        if action == 'approve':
            claim.status = 'approved'
            claim.save()
            messages.success(request, 'Claim approved successfully.')

        elif action == 'reject':
            claim.status = 'rejected'
            claim.save()
            messages.success(request, 'Claim rejected.')

        else:
            messages.error(request, 'Invalid action.')

        return redirect('admin_claim', id=claim.id)

    return redirect('admin_claim', id=claim.id)

@login_required
def delete_claim(request, id):
    claim = get_object_or_404(Claim, id=id)
    if request.method == 'POST':
        claim.delete()
        messages.success(request, 'Claim deleted.')
    return redirect('admin_claims')
    claim = get_object_or_404(Claim, id=id)
    if request.method == 'POST':
        claim.delete()
        messages.success(request, 'Claim deleted.')
    return redirect('admin_claims')