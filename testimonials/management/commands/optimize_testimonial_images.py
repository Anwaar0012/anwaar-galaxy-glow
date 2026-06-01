# testimonials/management/commands/optimize_testimonial_images.py
from django.core.management.base import BaseCommand
from django.core.files.images import get_image_dimensions
from PIL import Image
import os
from testimonials.models import Testimonial

class Command(BaseCommand):
    help = 'Optimize testimonial images for performance'

    def handle(self, *args, **options):
        testimonials = Testimonial.objects.exclude(client_image='')
        
        for testimonial in testimonials:
            if testimonial.client_image:
                img_path = testimonial.client_image.path
                
                # Get image dimensions
                width, height = get_image_dimensions(testimonial.client_image)
                
                # Resize if too large
                if width > 400 or height > 400:
                    img = Image.open(img_path)
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    
                    # Optimize for web
                    img.save(img_path, optimize=True, quality=85)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Optimized image for {testimonial.client_name}')
                    )
        
        self.stdout.write(self.style.SUCCESS('All images optimized!'))