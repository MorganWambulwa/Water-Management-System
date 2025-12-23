import threading
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
import csv 
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import WaterSource, IssueReport, RepairLog, WaterVendor, VendorClickLog, VendorReview, MpesaTransaction
from .mpesa_views import trigger_stk_push
from .forms import (
    IssueReportForm, 
    WaterSourceForm, 
    RepairLogForm, 
    SignUpForm, 
    ProfileUpdateForm, 
    VerificationRequestForm, 
    ContactForm, 
    VendorSignUpForm, 
    VendorProfileEditForm, 
    VendorReviewForm,
    VendorIssueReportForm
)

class EmailThread(threading.Thread):
    def __init__(self, subject, plain_message, recipient_emails, html_message):
        self.subject = subject
        self.plain_message = plain_message
        self.recipient_emails = recipient_emails
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.plain_message,
                settings.EMAIL_HOST_USER,
                self.recipient_emails,
                html_message=self.html_message,
                fail_silently=False
            )
            print(f"[SUCCESS] Email sent successfully to: {self.recipient_emails}")
        except Exception as e:
            print(f"[EMAIL FAILURE] Could not send email: {e}")

def notify_maintenance_team(request, report, source_name, source_type):
    staff_members = User.objects.filter(is_staff=True).exclude(email='')
    recipient_emails = [user.email for user in staff_members]

    if not recipient_emails:
        print("[WARNING] No staff members found with valid emails. Notification skipped.")
        return

    print(f"[INFO] Preparing to send email to {len(recipient_emails)} staff members.")

    context = {
        'source_name': source_name,
        'source_type': source_type,
        'priority': report.get_priority_level_display(),
        'reporter_name': report.reporter.username,
        'report_time': timezone.now().strftime('%Y-%m-%d %H:%M'),
        'description': report.description,
        'dashboard_url': request.build_absolute_uri('/dashboard/')
    }

    html_message = render_to_string('waterapp/issue_report_email.html', context)
    plain_message = strip_tags(html_message)

    subject = f"ACTION REQUIRED: {source_type} Issue at {source_name}"

    EmailThread(subject, plain_message, recipient_emails, html_message).start()

def index(request):
    total_sources = WaterSource.objects.count()
    open_issues = IssueReport.objects.filter(is_resolved=False).count()
    operational_sources = WaterSource.objects.filter(status='O').count()
    live_status_sources = WaterSource.objects.all().order_by('-last_updated')[:5]

    vendors = WaterVendor.objects.filter(is_verified=True)[:6]

    context = {
        'total_sources': total_sources,
        'open_issues': open_issues,
        'operational_sources': operational_sources,
        'live_status_sources': live_status_sources,
        'vendors': vendors, 
    }
    return render(request, 'waterapp/index.html', context)

def about(request):
    return render(request, 'waterapp/about.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def water_source_list(request):
    sources = WaterSource.objects.all()
    query = request.GET.get('q')
    if query:
        sources = sources.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    sources = sources.annotate(
        num_open_issues=Count('issues', filter=Q(issues__is_resolved=False))
    )
    return render(request, 'waterapp/water_source_list.html', {'sources': sources})

def water_source_map(request):
    return render(request, 'waterapp/water_source_map.html')

def water_source_map_data(request):
    sources = WaterSource.objects.all()
    
    vendors = WaterVendor.objects.filter(
        is_open=True, 
        is_verified=True
    ).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    data = []
    for s in sources:
        data.append({
            'type': 'source', 
            'id': s.pk,
            'name': s.name,
            'lat': float(s.latitude),
            'lon': float(s.longitude),
            'status': s.get_status_display(),
            'color': s.status_color
        })

    for v in vendors:
        data.append({
            'type': 'vendor',
            'id': v.pk,
            'name': v.business_name,
            'lat': float(v.latitude),
            'lon': float(v.longitude),
            'status': f"Selling @ KES {v.price_per_20l}/20L",
            'phone': v.whatsapp_number,
            'color': 'info'
        })
        
    return JsonResponse(data, safe=False)

def vendor_list(request):
    vendors = WaterVendor.objects.filter(is_open=True, is_verified=True)
    return render(request, 'waterapp/vendor_list.html', {'vendors': vendors})

def vendor_signup(request):
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Your account is pending approval from the Admin.")
            return redirect('index')
    else:
        form = VendorSignUpForm()
    return render(request, 'waterapp/vendor_signup.html', {'form': form})

def water_source_detail(request, pk):
    source = get_object_or_404(WaterSource.objects.prefetch_related('issues', 'repairs'), pk=pk)
    open_issues = [issue for issue in source.issues.all() if not issue.is_resolved]
    repair_history = source.repairs.all()
    
    context = {
        'source': source,
        'open_issues': open_issues,
        'repair_history': repair_history,
    }
    return render(request, 'waterapp/water_source_detail.html', context)

@login_required 
def issue_report_create(request):
    if request.method == 'POST':
        form = IssueReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user 
            report.save()
            notify_maintenance_team(
                request, 
                report, 
                report.water_source.name, 
                "Public Source"
            )

            messages.success(request, "Report submitted! Technicians have been notified.")
            return redirect('index')
    else:
        form = IssueReportForm()
    return render(request, 'waterapp/issue_report_form.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_staff:
        sources = WaterSource.objects.all().order_by('name')
        open_issues = IssueReport.objects.filter(is_resolved=False).order_by('-priority_level', '-reported_at')
        
        status_counts = WaterSource.objects.values('status').annotate(count=Count('status'))
        source_type_counts = WaterSource.objects.values('source_type').annotate(count=Count('source_type'))
        
        context = {
            'sources': sources,
            'open_issues': open_issues,
            'status_counts': list(status_counts),
            'source_type_counts': list(source_type_counts),
            'total_sources': sources.count(),
            'total_open_issues': open_issues.count(),
        }
        return render(request, 'waterapp/dashboard.html', context)
    
    elif hasattr(request.user, 'vendor_profile'):
        vendor = request.user.vendor_profile
        
        today = timezone.now().date()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        
        chart_labels = []
        chart_data = []
        
        for d in dates:
            chart_labels.append(d.strftime('%a')) 
            
            count = VendorClickLog.objects.filter(
                vendor=vendor,
                timestamp__date=d
            ).count()
            chart_data.append(count)

        context = {
            'vendor': vendor,
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'total_clicks_7days': sum(chart_data),
        }
        return render(request, 'waterapp/vendor_dashboard.html', context)

    else:
        user_issues = IssueReport.objects.filter(reporter=request.user).order_by('-reported_at')
        resolved_notifications = IssueReport.objects.filter(
            reporter=request.user, 
            is_resolved=True
        ).order_by('-reported_at')[:3]
        available_sources = WaterSource.objects.filter(status='O').order_by('-last_updated')[:3]
        
        context = {
            'user_issues': user_issues,
            'resolved_notifications': resolved_notifications,
            'available_sources': available_sources,
        }
        return render(request, 'waterapp/user_dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'waterapp/profile.html', {'form': form})

@login_required
def vendor_profile_edit(request):
    if not hasattr(request.user, 'vendor_profile'):
        raise PermissionDenied
    
    vendor = request.user.vendor_profile
    
    if request.method == 'POST':
        form = VendorProfileEditForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Business profile updated successfully!")
            return redirect('dashboard')
    else:
        form = VendorProfileEditForm(instance=vendor)
    
    return render(request, 'waterapp/vendor_profile_edit.html', {'form': form})

@login_required
def vendor_report_issue(request):
    if not hasattr(request.user, 'vendor_profile'):
        messages.error(request, "Only registered vendors can request repairs.")
        return redirect('index')

    vendor = request.user.vendor_profile

    if request.method == 'POST':
        form = VendorIssueReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.vendor = vendor 
            report.reporter = request.user
            report.save()
            
            notify_maintenance_team(
                request, 
                report, 
                vendor.business_name, 
                "Commercial Vendor"
            )

            messages.success(request, "Repair request submitted! Technicians have been notified.")
            return redirect('dashboard')
    else:
        form = VendorIssueReportForm()
    
    return render(request, 'waterapp/vendor_report_issue.html', {'form': form})

@login_required
def water_source_create_update(request, pk=None):
    if pk:
        source = get_object_or_404(WaterSource, pk=pk)
    else:
        source = None

    if request.method == 'POST':
        form = WaterSourceForm(request.POST, instance=source)
        if form.is_valid():
            new_source = form.save(commit=False)
            if not source:
                new_source.created_by = request.user
            new_source.save()
            return redirect('water_source_list')
    else:
        form = WaterSourceForm(instance=source)
    
    return render(request, 'waterapp/water_source_form.html', {'form': form, 'source': source})

@login_required
def water_source_delete(request, pk):
    source = get_object_or_404(WaterSource, pk=pk)
    
    if source.created_by != request.user and not request.user.is_superuser:
        raise PermissionDenied("You do not have permission to delete this source.")

    if request.method == 'POST':
        source.delete()
        return redirect('water_source_list')
    return render(request, 'waterapp/water_source_confirm_delete.html', {'source': source})

@login_required
def request_verification(request, pk):
    source = get_object_or_404(WaterSource, pk=pk)
    
    if source.created_by != request.user:
        messages.error(request, "You can only verify sources you created.")
        return redirect('water_source_detail', pk=pk)
    
    if source.is_verified:
        messages.info(request, "This source is already verified!")
        return redirect('water_source_detail', pk=pk)

    if request.method == 'POST':
        form = VerificationRequestForm(request.POST)
        if form.is_valid():
            subject = f"Verification Request: {source.name}"
            email_body = f"""
            Hello Admin,

            A user has requested verification for a water source.

            --- DETAILS ---
            Source Name: {source.name}
            Source ID: {source.id}
            Submitted By: {request.user.username} ({request.user.email})
            
            --- USER MESSAGE ---
            {form.cleaned_data['message']}
            
            --- ACTION ---
            Review this source in the admin panel:
            https://water-management-system-ouep.onrender.com/admin/waterapp/watersource/{source.pk}/change/
            """
            
            EmailThread(subject, email_body, [settings.EMAIL_HOST_USER], None).start()
            messages.success(request, "Verification request sent successfully!")
                
            return redirect('water_source_detail', pk=pk)
    else:
        form = VerificationRequestForm(initial={'subject': f"Verify: {source.name}"})

    return render(request, 'waterapp/verification_request.html', {'form': form, 'source': source})

@login_required
def repair_log_create(request, source_pk):
    source = get_object_or_404(WaterSource, pk=source_pk)
    if request.method == 'POST':
        form = RepairLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.water_source = source
            log.technician = request.user 
            log.save()
            
            source.status = 'O'
            source.save()
            
            return redirect('water_source_detail', pk=source_pk)
    else:
        form = RepairLogForm(initial={'water_source': source})

    return render(request, 'waterapp/repair_log_form.html', {'form': form, 'source': source})

@login_required
def issue_toggle_resolve(request, pk):
    issue = get_object_or_404(IssueReport, pk=pk)
    if request.method == 'POST':
        issue.is_resolved = not issue.is_resolved
        issue.save()
    return redirect('dashboard')

@login_required
def export_issues_csv(request):
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to access this page.")
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="open_issues_report.csv"'

    writer = csv.writer(response)

    writer.writerow(['ID', 'Source', 'Priority', 'Description', 'Reported At'])

    issues = IssueReport.objects.filter(is_resolved=False).select_related('water_source')
    
    for issue in issues:
        writer.writerow([
            issue.pk,
            issue.water_source.name,
            issue.priority_level,
            issue.description,
            issue.reported_at.strftime("%Y-%m-%d %H:%M")
        ])

    return response

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            context = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'subject': form.cleaned_data['subject'],
                'message': form.cleaned_data['message']
            }
            
            html_message = render_to_string('waterapp/contact_email.html', context)
            plain_message = strip_tags(html_message)
            
            subject = f"New Contact: {form.cleaned_data['subject']}"
            
            EmailThread(subject, plain_message, [settings.EMAIL_HOST_USER], html_message).start()

            messages.success(request, "Your message has been sent.")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'waterapp/contact.html', {'form': form})

def legal_page(request, page_type):
    h_style = "fw-bold text-dark mt-4 mb-3"
    p_style = "text-muted mb-3"
    ul_style = "text-muted mb-4"

    content = {
        'privacy': {
            'title': 'Privacy Policy',
            'updated': 'Last Updated: December 22, 2025',
            'body': f"""
                <p class="{p_style}">At WaterConnect, we prioritize the protection of your personal data. This policy outlines how we handle your information, particularly regarding our Water Vendor and M-Pesa payment services.</p>
                
                <h4 class="{h_style}">1. Information We Collect</h4>
                <ul class="{ul_style}">
                    <li><strong>Account Data:</strong> Username, email address and phone number.</li>
                    <li><strong>Transaction Data:</strong> M-Pesa transaction codes, amounts and timestamps.</li>
                    <li><strong>Location Data:</strong> GPS coordinates for water delivery and mapping services.</li>
                </ul>

                <h4 class="{h_style}">2. How We Share Data with Vendors</h4>
                <p class="{p_style}">WaterConnect acts as a bridge between you and independent Water Vendors. When you place an order:</p>
                <ul class="{ul_style}">
                    <li><strong>Phone Number:</strong> Your phone number is shared with the specific vendor you selected to facilitate delivery.</li>
                    <li><strong>Location:</strong> Your delivery location is shared with the vendor for logistics purposes.</li>
                </ul>
                <p class="{p_style}">We do not sell your personal data to third-party advertisers.</p>

                <h4 class="{h_style}">3. M-Pesa Payment Data</h4>
                <p class="{p_style}">Payments are processed securely via Safaricom's Daraja API. We store transaction records for account history and dispute resolution purposes only.</p>
            """
        },
        'terms': {
            'title': 'Terms of Service',
            'updated': 'Last Updated: December 22, 2025',
            'body': f"""
                <p class="{p_style}">Welcome to WaterConnect. By using our platform to locate water sources or order refills, you agree to these terms.</p>

                <h4 class="{h_style}">1. Platform Role & Liability</h4>
                <p class="{p_style}">WaterConnect is a technology platform that connects users with independent Water Vendors. We are <strong>not</strong> the seller of the water.</p>
                <ul class="{ul_style}">
                    <li><strong>Quality:</strong> While we verify vendors, we are not liable for the quality or safety of the water delivered by independent vendors.</li>
                    <li><strong>Delivery:</strong> Delivery times and fulfillment are the responsibility of the vendor.</li>
                </ul>

                <h4 class="{h_style}">2. M-Pesa Payments & Refunds</h4>
                <p class="{p_style}">All payments made via M-Pesa on WaterConnect are directed to the platform or the vendor as specified.</p>
                <ul class="{ul_style}">
                    <li><strong>Disputes:</strong> If a vendor fails to deliver after payment, please report the issue via your Dashboard within 24 hours.</li>
                    <li><strong>Refunds:</strong> Refunds are processed at the discretion of the admin after verifying the claim with the vendor. Reversals are subject to M-Pesa transaction fees.</li>
                </ul>

                <h4 class="{h_style}">3. User Conduct</h4>
                <p class="{p_style}">You agree not to submit false reports, harass vendors or attempt to bypass the platform's payment system for orders initiated here.</p>
            """
        },
        'cookies': {
            'title': 'Cookie Policy',
            'updated': 'Last Updated: December 22, 2025',
            'body': f"""
                <p class="{p_style}">We use cookies to improve your experience on WaterConnect.</p>

                <h4 class="{h_style}">1. Essential Cookies</h4>
                <p class="{p_style}">These are required for you to log in, view your dashboard and process M-Pesa payments securely.</p>

                <h4 class="{h_style}">2. Analytics</h4>
                <p class="{p_style}">We use anonymous cookies to understand how many users are viewing the map and vendor profiles to improve our services.</p>
            """
        }
    }
    
    data = content.get(page_type)
    if not data:
        data = content['privacy']
        
    return render(request, 'waterapp/legal_page.html', {'data': data})

def track_vendor_click(request, vendor_id):
    vendor = get_object_or_404(WaterVendor, pk=vendor_id)
    VendorClickLog.objects.create(vendor=vendor)
    return JsonResponse({'status': 'success'})

def vendor_public_profile(request, pk):
    vendor = get_object_or_404(WaterVendor, pk=pk)
    reviews = vendor.reviews.all()
    
    average_rating = 0
    if reviews.exists():
        total_stars = sum([r.rating for r in reviews])
        average_rating = round(total_stars / reviews.count(), 1)

    if request.method == 'POST' and request.user.is_authenticated:
        form = VendorReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.vendor = vendor
            review.author = request.user
            review.save()
            messages.success(request, "Your review has been posted!")
            return redirect('vendor_public_profile', pk=pk)
    else:
        form = VendorReviewForm()

    context = {
        'vendor': vendor,
        'reviews': reviews,
        'average_rating': average_rating,
        'form': form,
        'star_range': range(1, 6),
    }
    return render(request, 'waterapp/vendor_public_profile.html', context)


@login_required
def initiate_payment(request, vendor_id):
    vendor = get_object_or_404(WaterVendor, pk=vendor_id)
    
    if request.method == "POST":
        phone = request.POST.get('phone')
        custom_amount = request.POST.get('amount') 
        
        response = trigger_stk_push(
            phone_number=phone,
            amount=custom_amount,
            account_reference=f"Pay {vendor.business_name}",
            transaction_desc="Water Payment"
        )
        
        if response and response.response_code == "0":
            MpesaTransaction.objects.create(
                phone_number=phone,
                amount=custom_amount,
                vendor=vendor,
                status="Pending (STK Sent)",
                transaction_code=response.checkout_request_id
            )
            messages.success(request, f"STK Push sent to {phone}. Please enter your PIN!")
        else:
            error_msg = response.error_message if response else "Connection Failed"
            messages.error(request, f"M-Pesa Error: {error_msg}")
            
        return redirect('vendor_public_profile', pk=vendor_id)
    
    initial_phone = request.user.username if request.user.username.isdigit() else ""
    
    return render(request, 'waterapp/payment_form.html', {
        'vendor': vendor, 
        'user': request.user
    })


def donate(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        
        response = trigger_stk_push(
            phone_number=phone,
            amount=amount,
            account_reference="Donation",
            transaction_desc="Community Support"
        )
        
        if response and response.response_code == "0":
            MpesaTransaction.objects.create(
                phone_number=phone,
                amount=amount,
                status="Pending (STK Sent)",
                transaction_code=response.checkout_request_id
            )
            messages.success(request, f"Thank you! STK Push sent to {phone}.")
        else:
            error_msg = response.error_message if response else "Connection Failed"
            messages.error(request, f"Failed: {error_msg}")
            
        return redirect('index')

    return render(request, 'waterapp/donate.html')

@login_required
def transaction_history(request):
    user_phone = request.user.username
    
    transactions = MpesaTransaction.objects.filter(
        phone_number=user_phone
    ).order_by('-created_at')

    return render(request, 'waterapp/transaction_history.html', {
        'transactions': transactions
    })