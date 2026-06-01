# type: ignore
from django import forms
from django.core.validators import MinLengthValidator
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = [
            'client_name', 'client_email', 'client_role', 'company', 'location',
            'testimonial', 'rating', 'project', 'client_image'
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Doe',
                'required': True
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com',
                'help_text': 'We won\'t share your email publicly'
            }),
            'client_role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CEO, Manager, Business Owner'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company Name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'testimonial': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your experience working with us...',
                'required': True
            }),
            'rating': forms.RadioSelect(choices=[
                (5, 'Excellent - 5 Stars'),
                (4, 'Very Good - 4 Stars'),
                (3, 'Good - 3 Stars'),
                (2, 'Fair - 2 Stars'),
                (1, 'Poor - 1 Star'),
            ]),
            'project': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title of Project/Service/Blog you like'
            }),
            'client_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'client_name': 'Your Full Name *',
            'client_email': 'Email Address *',
            'client_role': 'Your Job Title',
            'company': 'Company Name',
            'location': 'Your Location',
            'testimonial': 'Your Testimonial *',
            'rating': 'Your Rating *',
            'project': 'Project/Service/Blog Tile or Name',
            'client_image': 'Your Photo (Optional)',
        }
        help_texts = {
            'client_email': 'We\'ll only use this to verify your testimonial',
            'client_image': 'Upload a professional photo (max 2MB)',
        }
    
    def clean_client_image(self):
        image = self.cleaned_data.get('client_image')
        if image:
            # Validate image size (max 2MB)
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Image file too large (max 2MB)')
            
            # Validate image type
            if not image.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
                raise forms.ValidationError('Only JPEG and PNG images are allowed')
        return image
    
    def clean_testimonial(self):
        testimonial = self.cleaned_data.get('testimonial')
        if len(testimonial) < 20:
            raise forms.ValidationError('Please provide at least 20 characters')
        return testimonial

class TestimonialAdminForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
        }