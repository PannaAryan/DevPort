import os
import uuid
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import io


class ImageHandler:
    """Enhanced image handling utility for DevPort"""
    
    def __init__(self):
        self.max_size = (800, 800)  # Maximum dimensions for uploaded images
        self.thumbnail_size = (200, 200)  # Thumbnail dimensions
        self.quality = 85  # JPEG quality
        self.allowed_formats = ['JPEG', 'PNG', 'WEBP']
    
    def process_profile_picture(self, image_file, user_id):
        """Process and optimize profile picture"""
        try:
            # Open and process the image
            img = Image.open(image_file)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Resize while maintaining aspect ratio
            img.thumbnail(self.max_size, Image.Resampling.LANCZOS)
            
            # Create a square crop from center
            img = self._center_crop_square(img)
            
            # Generate unique filename
            filename = f"profile_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
            
            # Save optimized image
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.read(), name=filename)
            
        except Exception as e:
            print(f"Error processing profile picture: {e}")
            return None
    
    def process_project_image(self, image_file, project_name):
        """Process and optimize project image"""
        try:
            # Open and process the image
            img = Image.open(image_file)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Resize while maintaining aspect ratio
            img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            
            # Generate unique filename
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            filename = f"project_{safe_name}_{uuid.uuid4().hex[:8]}.jpg"
            
            # Save optimized image
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.read(), name=filename)
            
        except Exception as e:
            print(f"Error processing project image: {e}")
            return None
    
    def _center_crop_square(self, img):
        """Crop image to square from center"""
        width, height = img.size
        
        # Determine the size of the square (minimum dimension)
        size = min(width, height)
        
        # Calculate crop box
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        return img.crop((left, top, right, bottom))
    
    def create_thumbnail(self, image_path):
        """Create thumbnail from existing image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Create thumbnail
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Generate thumbnail filename
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                thumb_filename = f"{base_name}_thumb.jpg"
                
                # Save thumbnail
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=self.quality, optimize=True)
                output.seek(0)
                
                return ContentFile(output.read(), name=thumb_filename)
                
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def validate_image(self, image_file):
        """Validate uploaded image"""
        try:
            # Check file size (max 10MB)
            if image_file.size > 10 * 1024 * 1024:
                return False, "Image file too large. Maximum size is 10MB."
            
            # Try to open and verify it's a valid image
            img = Image.open(image_file)
            img.verify()
            
            # Check format
            if img.format not in self.allowed_formats:
                return False, f"Unsupported image format. Allowed formats: {', '.join(self.allowed_formats)}"
            
            # Reset file pointer after verify()
            image_file.seek(0)
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def get_image_info(self, image_file):
        """Get image information"""
        try:
            img = Image.open(image_file)
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
            }
        except Exception as e:
            return None
    
    def cleanup_old_images(self, user_id, keep_recent=5):
        """Clean up old profile images for a user"""
        try:
            # This would implement cleanup logic for old images
            # For now, we'll just pass as it requires more complex file management
            pass
        except Exception as e:
            print(f"Error cleaning up old images: {e}")


# Global instance
image_handler = ImageHandler()

