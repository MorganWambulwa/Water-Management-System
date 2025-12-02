from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import WaterSource, IssueReport, RepairLog
from .forms import IssueReportForm, WaterSourceForm, RepairLogForm

def index(request):
    """
    Landing page: Renders the exact 'AquaConnect' dashboard shown in the screenshot.
    """
    # 1. The 3 main stats cards
    total_sources = WaterSource.objects.count()
    open_issues = IssueReport.objects.filter(is_resolved=False).count()
    operational_sources = WaterSource.objects.filter(status='O').count()

    # 2. The 'Live Network Status' list (Right side of Hero)
    # We fetch the last 3-5 sources to show recent status updates
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
    # Fixed: Changed 'reports' to 'issues' to match related_name in models.py
    sources = WaterSource.objects.all().annotate(
        num_open_issues=Count('issues', filter=Q(issues__is_resolved=False))
    )
    return render(request, 'waterapp/water_source_list.html', {'sources': sources})

def water_source_detail(request, pk):
    """Detailed view of a single water source."""
    source = get_object_or_404(WaterSource, pk=pk)
    # Fixed: Changed related_name access to match model
    open_issues = source.issues.filter(is_resolved=False)
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
            # Redirect to index to see the updated stats
            return redirect('index')
    else:
        form = IssueReportForm()
    return render(request, 'waterapp/issue_report_form.html', {'form': form})

# --- Administrator/Technician Views (Requires login) ---

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
            'lat': float(s.latitude),  # Convert Decimal to float for JSON
            'lon': float(s.longitude), 
            'status': s.get_status_display(),
            'color': s.status_color # Uses the property we added to the model
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
            
            # Auto-update status to Operational if repair is logged
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

from .forms import SignUpForm # Make sure to import the new form

def signup(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Redirect to login page after success
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def about(request):
    """Render the About page."""
    return render(request, 'waterapp/about.html')

def water_source_map(request):
    """Renders the map page."""
    return render(request, 'waterapp/water_source_map.html')

def water_source_map(request):
    """Renders the HTML page that contains the map."""
    return render(request, 'waterapp/water_source_map.html')