# type: ignore
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from .models import ContactMessage
from .forms import ContactForm

class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = '/contact/success/'
    
    def get_initial(self):
        """Auto-fill form ONLY when coming from Order Now button"""
        initial = super().get_initial()
        
        # Check if this is an order request (has service parameter)
        service_slug = self.request.GET.get('service')
        action = self.request.GET.get('action')
        
        # ONLY auto-fill if service parameter exists (coming from Order Now button)
        if service_slug and action == 'order':
            try:
                from services.models import Service
                service = Service.objects.get(slug=service_slug)
                
                # Map service name to choice value
                service_mapping = {
                    'autocad': 'autocad',
                    'illustrator': 'illustrator',
                    'blender': 'blender',
                    'photoshop': 'photoshop',
                    'office': 'office',
                    'python': 'python',
                    'django': 'django',
                    'flet': 'flet',
                    'pyside': 'pyside',
                }
                
                # Find matching service choice
                service_choice = 'other'
                for key, value in service_mapping.items():
                    if key in service.name.lower() or key in service.category.name.lower():
                        service_choice = value
                        break
                
                initial['service'] = service_choice
                initial['subject'] = f"ORDER: {service.name} Service"
                
                # Pre-filled message with service details
                message_template = f"""I am interested in ordering your {service.name} service.

Service Details:
- Name: {service.name}
- Price: ${service.price if service.price else 'Contact for pricing'}
- Category: {service.category.name if service.category else 'N/A'}
- Duration: {service.duration if service.duration else 'To be discussed'}

Please guide me with the next steps to proceed with this order.

Thank you!"""
                
                initial['message'] = message_template
                
                # Store in session to show notification
                self.request.session['auto_filled'] = True
                
            except Service.DoesNotExist:
                pass
        
        # Check for quote request (optional)
        elif service_slug and action == 'quote':
            try:
                from services.models import Service
                service = Service.objects.get(slug=service_slug)
                
                service_choice = 'other'
                for key, value in service_mapping.items():
                    if key in service.name.lower() or key in service.category.name.lower():
                        service_choice = value
                        break
                
                initial['service'] = service_choice
                initial['subject'] = f"QUOTE REQUEST: {service.name} Service"
                
                message_template = f"""I would like to request a quote for your {service.name} service.

Service: {service.name}
Category: {service.category.name if service.category else 'N/A'}

Please provide a detailed quote and estimated timeline.

Thank you!"""
                
                initial['message'] = message_template
                
            except Service.DoesNotExist:
                pass
        
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add flag to show auto-fill notification in template
        context['is_auto_filled'] = self.request.GET.get('action') == 'order' and self.request.GET.get('service')
        context['service_name'] = self.request.GET.get('service', '')
        
        return context
    
    def form_valid(self, form):
        # Save the form data to database
        contact = form.save()
        
        # Send email notification
        try:
            # Email to admin
            email_subject = f"New Contact Form Message: {contact.subject}"
            email_message = f"""
You have received a new message from your website contact form.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CUSTOMER DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Service Interested In: {contact.get_service_display()}
Submitted At: {contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MESSAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject: {contact.subject}

Message:
{contact.message}
            """
            
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            
            # Auto-reply to customer
            auto_reply_message = f"""
Dear {contact.name},

Thank you for contacting Anwaar Galaxy Glow!

We have received your {'order request' if 'ORDER' in contact.subject else 'inquiry'} regarding "{contact.get_service_display()}" and will respond within 24-48 hours.

Your Message Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject: {contact.subject}
Message: {contact.message[:200]}...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Our team will review your request and contact you soon at {contact.email}.

Thank you for choosing Anwaar Galaxy Glow!

Best regards,
Anwaar Galaxy Glow Team
{settings.SITE_URL}
            """
            
            send_mail(
                "Thank you for contacting Anwaar Galaxy Glow",
                auto_reply_message,
                settings.DEFAULT_FROM_EMAIL,
                [contact.email],
                fail_silently=True,
            )
            
            messages.success(self.request, 'Your message has been sent successfully! We will contact you soon.')
            
        except Exception as e:
            print(f"Email error: {e}")
            messages.warning(self.request, 'Your message was saved but we could not send a confirmation email.')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


def contact_success(request):
    return render(request, 'contact/success.html')