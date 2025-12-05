from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from .models import WaterSource, IssueReport, RepairLog
from .forms import IssueReportForm, WaterSourceForm, RepairLogForm, SignUpForm, ProfileUpdateForm, VerificationRequestForm, ContactForm


def index(request):
    """Landing page: Renders the public dashboard."""
    total_sources = WaterSource.objects.count()
    open_issues = IssueReport.objects.filter(is_resolved=False).count()
    operational_sources = WaterSource.objects.filter(status='O').count()
    live_status_sources = WaterSource.objects.all().order_by('-last_updated')[:5]

    context = {
        'total_sources': total_sources,
        'open_issues': open_issues,
        'operational_sources': operational_sources,
        'live_status_sources': live_status_sources,
    }
    return render(request, 'waterapp/index.html', context)

def about(request):
    """Render the About page."""
    return render(request, 'waterapp/about.html')

def signup(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def water_source_list(request):
    """List of all water sources for public viewing."""
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
    """Renders the map page."""
    return render(request, 'waterapp/water_source_map.html')

def water_source_map_data(request):
    """JSON API endpoint for the map."""
    sources = WaterSource.objects.all()
    data = [
        {
            'id': s.pk, 
            'name': s.name, 
            'lat': float(s.latitude),
            'lon': float(s.longitude), 
            'status': s.get_status_display(),
            'color': s.status_color
        } 
        for s in sources
    ]
    return JsonResponse(data, safe=False)

def water_source_detail(request, pk):
    """Detailed view of a single water source."""
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
    """Allows a resident to submit a new issue report."""
    if request.method == 'POST':
        form = IssueReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user 
            report.save()
            return redirect('index')
    else:
        form = IssueReportForm()
    return render(request, 'waterapp/issue_report_form.html', {'form': form})

@login_required
def dashboard(request):
    """Internal dashboard for admins/technicians."""
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

@login_required
def profile(request):
    """Handles the user profile view and updates."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'waterapp/profile.html', {'form': form})

@login_required
def water_source_create_update(request, pk=None):
    """Handles both creation and updating of a WaterSource."""
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
    """Deletes a water source after confirmation."""
    source = get_object_or_404(WaterSource, pk=pk)
    
    if source.created_by != request.user and not request.user.is_superuser:
        raise PermissionDenied("You do not have permission to delete this source.")

    if request.method == 'POST':
        source.delete()
        return redirect('water_source_list')
    return render(request, 'waterapp/water_source_confirm_delete.html', {'source': source})

@login_required
def request_verification(request, pk):
    """Allows the creator to request verification via email."""
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
            try:
                send_mail(
                    subject,
                    email_body,
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, "Verification request sent successfully!")
            except Exception as e:
                messages.error(request, f"Failed to send email. Error: {str(e)}")
                
            return redirect('water_source_detail', pk=pk)
    else:
        form = VerificationRequestForm(initial={'subject': f"Verify: {source.name}"})

    return render(request, 'waterapp/verification_request.html', {'form': form, 'source': source})

@login_required
def repair_log_create(request, source_pk):
    """Allows a technician to log a repair."""
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
    """Toggles the 'is_resolved' status."""
    issue = get_object_or_404(IssueReport, pk=pk)
    if request.method == 'POST':
        issue.is_resolved = not issue.is_resolved
        issue.save()
    return redirect('dashboard')

def contact(request):
    """Renders the Contact page and handles message submission."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = f"Contact Form: {form.cleaned_data['subject']}"
            message = f"""
            You have received a new message from the WaterConnect website.
            
            Name: {form.cleaned_data['name']}
            Email: {form.cleaned_data['email']}
            
            Message:
            {form.cleaned_data['message']}
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, "Thank you! Your message has been sent.")
                return redirect('contact')
            except Exception as e:
                messages.error(request, "Failed to send message. Please try again later.")
    else:
        form = ContactForm()

    return render(request, 'waterapp/contact.html', {'form': form})


def legal_page(request, page_type):
    """Renders the Privacy, Terms, and Cookie policies."""
    content = {
        'privacy': {
            'title': 'Privacy Policy', 'updated': 'Last Updated: December 2025',
            'body': """<p>At WaterConnect, we are committed to protecting your personal information...</p>
                       <h5 class='mt-4 fw-bold'>1. Information We Collect</h5><ul><li>Personal Data...</li></ul>"""
        },
        'terms': {
            'title': 'Terms of Service', 'updated': 'Last Updated: December 2025',
            'body': """<p>Welcome to WaterConnect...</p>"""
        },
        'cookies': {
            'title': 'Cookie Policy', 'updated': 'Last Updated: December 2025',
            'body': """<p>This Cookie Policy explains how WaterConnect uses cookies...</p>"""
        }
    }
    data = content.get(page_type)
    return render(request, 'waterapp/legal_page.html', {'data': data})