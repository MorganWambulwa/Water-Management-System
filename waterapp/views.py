from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import WaterSource, IssueReport, RepairLog
from .forms import IssueReportForm, WaterSourceForm, RepairLogForm
from django.shortcuts import render
from .forms import SignUpForm
from .forms import ProfileUpdateForm 
from django.contrib import messages


def index(request):
    """
    Landing page: Renders the exact 'WaterConnect' dashboard shown in the screenshot.
    """
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

def issue_report_create(request):
    """Allows a resident to submit a new issue report."""
    if request.method == 'POST':
        form = IssueReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.user.is_authenticated:
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

def water_source_map_data(request):
    """
    JSON API endpoint for the map. 
    Fixed: Accesses .latitude and .longitude fields directly (not GeoDjango PointField).
    """
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
            form.save()
            return redirect('water_source_list')
    else:
        form = WaterSourceForm(instance=source)
    
    return render(request, 'waterapp/water_source_form.html', {'form': form, 'source': source})

@login_required
def water_source_delete(request, pk):
    """Deletes a water source after confirmation."""
    source = get_object_or_404(WaterSource, pk=pk)
    if request.method == 'POST':
        source.delete()
        return redirect('water_source_list')
    return render(request, 'waterapp/water_source_confirm_delete.html', {'source': source})

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

def about(request):
    """Render the About page."""
    return render(request, 'waterapp/about.html')

def water_source_map(request):
    """Renders the map page."""
    return render(request, 'waterapp/water_source_map.html')



def legal_page(request, page_type):
    """Renders the Privacy, Terms, and Cookie policies with detailed content."""
    
    content = {
        'privacy': {
            'title': 'Privacy Policy',
            'updated': 'Last Updated: December 2025',
            'body': """
                <p>At WaterConnect, we are committed to protecting your personal information and your right to privacy. This policy explains what information we collect and how we use it.</p>
                
                <h5 class="mt-4 fw-bold">1. Information We Collect</h5>
                <p>We collect personal information that you voluntarily provide to us when you register on the website, express an interest in obtaining information about us or our products and services, or otherwise when you contact us.</p>
                <ul>
                    <li><strong>Personal Data:</strong> Username, email address, and phone number (if provided).</li>
                    <li><strong>Usage Data:</strong> Information about how you interact with our platform, such as the water sources you view or report.</li>
                    <li><strong>Location Data:</strong> When you use our map features, we may request access to your location to show nearby water sources.</li>
                </ul>

                <h5 class="mt-4 fw-bold">2. How We Use Your Information</h5>
                <p>We use the information we collect or receive:</p>
                <ul>
                    <li>To facilitate account creation and logon processes.</li>
                    <li>To send administrative information to you (e.g., updates on reported issues).</li>
                    <li>To protect our Services (e.g., fraud monitoring and prevention).</li>
                </ul>

                <h5 class="mt-4 fw-bold">3. Sharing Your Information</h5>
                <p>We do not share, sell, rent or trade your information with third parties for their promotional purposes. We may share data with local water authorities solely for the purpose of resolving maintenance issues you have reported.</p>
            """
        },
        'terms': {
            'title': 'Terms of Service',
            'updated': 'Last Updated: December 2025',
            'body': """
                <p>Welcome to WaterConnect. By accessing our website, you agree to be bound by these Terms of Service. If you do not agree with any part of these terms, you may not use our platform.</p>

                <h5 class="mt-4 fw-bold">1. Use of the Platform</h5>
                <p>You agree to use WaterConnect only for lawful purposes. You are prohibited from:</p>
                <ul>
                    <li>Submitting false or misleading reports about water sources.</li>
                    <li>Attempting to interfere with the proper working of the site (e.g., hacking or spamming).</li>
                    <li>Using the contact information of technicians for harassment or non-official purposes.</li>
                </ul>

                <h5 class="mt-4 fw-bold">2. User Accounts</h5>
                <p>You are responsible for maintaining the confidentiality of your account and password. You agree to accept responsibility for all activities that occur under your account.</p>

                <h5 class="mt-4 fw-bold">3. Disclaimer</h5>
                <p>WaterConnect provides data on water sources "as is." While we strive for accuracy, we cannot guarantee the real-time availability or quality of water at any specific source, as conditions may change rapidly.</p>
                
                <h5 class="mt-4 fw-bold">4. Termination</h5>
                <p>We reserve the right to suspend or terminate your account at our sole discretion, without notice, for conduct that we believe violates these Terms of Service or is harmful to other users.</p>
            """
        },
        'cookies': {
            'title': 'Cookie Policy',
            'updated': 'Last Updated: December 2025',
            'body': """
                <p>This Cookie Policy explains how WaterConnect uses cookies and similar technologies to recognize you when you visit our website.</p>

                <h5 class="mt-4 fw-bold">1. What are Cookies?</h5>
                <p>Cookies are small data files that are placed on your computer or mobile device when you visit a website. They are widely used to make websites work more efficiently and to provide reporting information.</p>

                <h5 class="mt-4 fw-bold">2. How We Use Cookies</h5>
                <ul>
                    <li><strong>Essential Cookies:</strong> These are strictly necessary for the website to function (e.g., allowing you to log in and access secure areas).</li>
                    <li><strong>Functionality Cookies:</strong> These are used to recognize you when you return to our website, enabling us to personalize content for you.</li>
                    <li><strong>Analytics Cookies:</strong> We use these to collect information about how visitors use our website, helping us improve the user experience.</li>
                </ul>

                <h5 class="mt-4 fw-bold">3. Managing Cookies</h5>
                <p>You have the right to decide whether to accept or reject cookies. You can set or amend your web browser controls to accept or refuse cookies. If you choose to reject cookies, you may still use our website, though your access to some functionality may be restricted.</p>
            """
        }
    }
    
    data = content.get(page_type)
    return render(request, 'waterapp/legal_page.html', {'data': data})