# projects/utils.py foe hostinger
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

def optimize_image(image_field, max_size=(1200, 800), quality=85):
    """
    Optimize images for Hostinger hosting
    - Resize large images
    - Compress without losing quality
    - Convert to WebP for better performance
    """
    if not image_field:
        return
    
    img = Image.open(image_field)
    
    # Resize if too large
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save as optimized JPEG
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    # Create WebP version (optional - if you want to serve WebP)
    webp_output = BytesIO()
    img.save(webp_output, format='WEBP', quality=quality)
    webp_output.seek(0)
    
    return {
        'jpeg': ContentFile(output.read(), name=image_field.name),
        'webp': ContentFile(webp_output.read(), name=image_field.name.replace('.jpg', '.webp').replace('.jpeg', '.webp'))
    }