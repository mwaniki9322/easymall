import uuid
from io import BytesIO

from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File


def crop_image(image, data):
    # Open the image using Pillow
    img = Image.open(image)

    # Crop image
    img = img.crop((
        data['x'], data['y'], data['w'] + data['x'], data['h'] + data['y']
    ))

    # Resize image
    img = img.resize((
        data['width'], data['height']), Image.ANTIALIAS
    )

    # Convert to rgb
    img = img.convert('RGB')

    # Save the resized image into the buffer in JPEG format
    buffer = BytesIO()
    img.save(buffer, format='JPEG')

    # Wrap the buffer in File object
    file_object = File(buffer)

    # Save the new resized file as usual, which will save to S3 using django-storages
    file_name = '{}.jpeg'.format(uuid.uuid4())
    image.save(file_name, file_object)


def validate_file_size(value):
    """
    Maximum upload file size is 10mb
    """
    filesize = value.size

    if filesize > settings.MAX_UPLOAD_SIZE * 1024 * 1024:
        raise ValidationError(f"You cannot upload file more than {settings.MAX_UPLOAD_SIZE}MB")
    else:
        return value
