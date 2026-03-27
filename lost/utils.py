from django.core.exceptions import ValidationError

def validate_image_size(image):
    if image.size > 10 * 1024 * 1024:
        raise ValidationError("Max image size is 10MB")