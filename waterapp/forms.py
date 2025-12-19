from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import WaterSource, IssueReport, RepairLog, WaterVendor

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

class AdminIssueReportForm(IssueReportForm):
    """Special form for Admins to mark issues as resolved."""
    class Meta(IssueReportForm.Meta):
        model = IssueReport
        fields = ['water_source', 'description', 'priority_level', 'is_resolved']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'is_resolved' in self.fields:
            self.fields['is_resolved'].widget.attrs.update({'class': 'form-check-input'})

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
        
        if 'password' in self.fields:
             self.fields['password'].help_text = '' 
        if 'val_1' in self.fields:
             self.fields['val_1'].help_text = ''
             
        for field_name in self.fields:
            self.fields[field_name].help_text = ''
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
            
            if field_name == 'username':
                self.fields[field_name].widget.attrs['autocomplete'] = 'username'
            elif field_name == 'email':
                self.fields[field_name].widget.attrs['autocomplete'] = 'email'
            elif field_name == 'first_name':
                self.fields[field_name].widget.attrs['autocomplete'] = 'given-name'
            elif field_name == 'last_name':
                self.fields[field_name].widget.attrs['autocomplete'] = 'family-name'
            
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
            
            if field == 'first_name':
                self.fields[field].widget.attrs['autocomplete'] = 'given-name'
            elif field == 'last_name':
                self.fields[field].widget.attrs['autocomplete'] = 'family-name'
            elif field == 'email':
                self.fields[field].widget.attrs['autocomplete'] = 'email'
            
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
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Your Name',
        'autocomplete': 'name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your Email Address',
        'autocomplete': 'email'
    }))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Type your message here...'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            

class VendorSignUpForm(forms.ModelForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    
    business_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Name (e.g. Super Water & Refill Ltd)'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (e.g. 0712...)'}))
    location_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location (e.g. Near Market)'}))
    price_per_20l = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price per 20L', 'min': '0', 'step': '1.0'}))

    class Meta:
        model = WaterVendor
        fields = ['business_name', 'phone_number', 'location_name', 'price_per_20l']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        vendor = super().save(commit=False)
        vendor.user = user
        vendor.is_verified = False
        if commit:
            vendor.save()
        return vendor
    
class VendorProfileEditForm(forms.ModelForm):
    """Form to allow vendors to edit their profile (including open/closed status)."""
    class Meta:
        model = WaterVendor
        fields = ['business_name', 'phone_number', 'location_name', 'price_per_20l', 'delivery_fee', 'is_open']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '254...'}),
            'location_name': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_20l': forms.NumberInput(attrs={'class': 'form-control'}),
            'delivery_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 2.5em; height: 1.5em;'}),
        }