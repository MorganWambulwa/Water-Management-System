from django import forms
from django.core.exceptions import ValidationError  # Required for raising errors
from .models import WaterSource, IssueReport, RepairLog
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class WaterSourceForm(forms.ModelForm):
    """Form for administrators to create/edit a WaterSource."""
    class Meta:
        model = WaterSource
        # Added 'is_verified' to control the badge feature
        fields = ['name', 'source_type', 'latitude', 'longitude', 'status', 'is_verified', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply generic styling to all fields for a cleaner UI
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': field.title()})
            if field == 'is_verified':
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})

class IssueReportForm(forms.ModelForm):
    """Form for residents to report an issue."""
    class Meta:
        model = IssueReport
        fields = ['water_source', 'description', 'priority_level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue (e.g., No water flow, Broken handle...)'}),
            # UI Validation: Prevent user from clicking down past 1
            'priority_level': forms.NumberInput(attrs={'min': '1', 'max': '5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_priority_level(self):
        """Backend Validation: Ensure priority is positive."""
        priority = self.cleaned_data.get('priority_level')
        if priority is not None and priority < 1:
            raise ValidationError("Priority level must be 1 or higher.")
        return priority

class RepairLogForm(forms.ModelForm):
    """Form for technicians to log a repair."""
    class Meta:
        model = RepairLog
        fields = ['work_done', 'cost']
        widgets = {
            'work_done': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Details of repair work completed...'}),
            # UI Validation: Prevent negative cost in browser
            'cost': forms.NumberInput(attrs={'min': '0', 'step': '1.00',}),
            'class': 'no-spinners',
                # 1. Block keys: Stop user from typing minus, e, or using arrows
                'onkeydown': "if(['ArrowUp', 'ArrowDown', '-', 'e'].includes(event.key)) { event.preventDefault(); }",
                # 2. Block Paste/Input: If a negative value gets in (e.g. paste), remove it immediately
                'oninput': "validity.valid||(value='');"
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            existing_class = self.fields[field].widget.attrs.get('class', '')
            self.fields[field].widget.attrs.update({'class': existing_class + ' form-control'})

    def clean_cost(self):
        """Backend Validation: Ensure cost is not negative."""
        cost = self.cleaned_data.get('cost')
        if cost is not None and cost < 0:
            raise ValidationError("Repair cost cannot be negative.")
        return cost

class SignUpForm(UserCreationForm):
    """Form for new users to register."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removes the '150 characters or fewer' help text
        self.fields['username'].help_text = ''
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
class AdminRepairLogForm(RepairLogForm):
    """Special form for Admin panel that includes ALL fields."""
    class Meta(RepairLogForm.Meta):
        # This tells Django: "Use the validation from the parent, but show ALL fields"
        fields = '__all__'