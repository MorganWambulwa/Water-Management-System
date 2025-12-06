from django import forms
from django.core.exceptions import ValidationError
from .models import WaterSource, IssueReport, RepairLog
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class WaterSourceForm(forms.ModelForm):
    """Form for users to create/edit a WaterSource (No verification access)."""
    class Meta:
        model = WaterSource
        fields = ['name', 'source_type', 'latitude', 'longitude', 'status', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': field.title()})

class AdminWaterSourceForm(WaterSourceForm):
    """Special form for Admins that allows verifying sources."""
    class Meta(WaterSourceForm.Meta):
        fields = ['name', 'source_type', 'latitude', 'longitude', 'status', 'is_verified', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'is_verified' in self.fields:
            self.fields['is_verified'].widget.attrs.update({'class': 'form-check-input'})

class IssueReportForm(forms.ModelForm):
    """Form for residents to report an issue."""
    class Meta:
        model = IssueReport
        fields = ['water_source', 'description', 'priority_level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue (e.g., No water flow, Broken handle...)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class RepairLogForm(forms.ModelForm):
    """Form for technicians to log a repair."""
    class Meta:
        model = RepairLog
        fields = ['work_done', 'cost']
        widgets = {
            'work_done': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Details of repair work completed...'}),
            'cost': forms.NumberInput(attrs={'min': '0', 'step': '1.00', 'class': 'no-spinners'}),
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
        self.fields['username'].help_text = ''
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
class AdminRepairLogForm(RepairLogForm):
    """Special form for Admin panel that includes ALL fields."""
    class Meta(RepairLogForm.Meta):
        fields = '__all__'
        
class ProfileUpdateForm(forms.ModelForm):
    """Form to allow users to update their profile info."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
class VerificationRequestForm(forms.Form):
    """Form for users to request verification of their source."""
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4, 
        'placeholder': 'Please provide details proving this source is legitimate (e.g. "I am the facility manager", "Located at main gate")...'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ContactForm(forms.Form):
    """General contact form for users/guests."""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email Address'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'How can we help you?'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})