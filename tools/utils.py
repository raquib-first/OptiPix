import os
import uuid
from PIL import Image, ImageEnhance
from django.conf import settings

# Helpers
def generate_filename(prefix, ext):
    return f"{prefix}_{uuid.uuid4().hex}.{ext}"


def get_output_path(filename):
    output_dir = os.path.join(settings.MEDIA_ROOT, "processed")
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def ensure_rgb(img):
    if img.mode in ("RGBA", "P"):
        return img.convert("RGB")
    return img


def get_size(path):
    return os.path.getsize(path) / 1024


def calc_percentage(original, new):
    if original == 0:
        return 0
    return ((original - new) / original) * 100


# Core Operations
def compress_image(input_path, quality=80):
    filename = generate_filename("compressed", "jpg")
    output_path = get_output_path(filename)

    with Image.open(input_path) as img:
        img = ensure_rgb(img)
        img.save(output_path, "JPEG", quality=quality, optimize=True)

    return output_path


def resize_image(input_path, width, height):
    filename = generate_filename("resized", "jpg")
    output_path = get_output_path(filename)

    with Image.open(input_path) as img:
        img = ensure_rgb(img)
        resized = img.resize((width, height))
        resized.save(output_path, "JPEG", quality=95,subsampling=0)
        # resized.save(output_path, "PNG")

    return output_path


def convert_image(input_path, output_format):
    ext = output_format.lower()
    filename = generate_filename("converted", ext)
    output_path = get_output_path(filename)

    with Image.open(input_path) as img:
        img = ensure_rgb(img)
        img.save(output_path, output_format.upper())

    return output_path

def create_thumbnail(input_path, size=(300, 300)):
    try:
        filename = generate_filename("thumb", "jpg")
        output_path = get_output_path(filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with Image.open(input_path) as img:
            img = ensure_rgb(img)

            img.thumbnail(size)

            img.save(
                output_path,
                "JPEG",
                quality=85,
                optimize=True
            )
        return output_path

    except Exception as e:
        raise RuntimeError(f"Thumbnail generation failed: {str(e)}")

def crop_image(input_path, aspect_ratio):
    try:
        # Parse ratio
        w_ratio, h_ratio = map(int, aspect_ratio.split(":"))

        filename = generate_filename("crop", "jpg")
        output_path = get_output_path(filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with Image.open(input_path) as img:
            img = ensure_rgb(img)

            width, height = img.size
            target_ratio = w_ratio / h_ratio
            current_ratio = width / height

            if current_ratio > target_ratio:
                # Crop width
                new_width = int(height * target_ratio)
                new_height = height
            else:
                # Crop height
                new_width = width
                new_height = int(width / target_ratio)

            # Center crop coordinates
            left = (width - new_width) // 2
            top = (height - new_height) // 2
            right = left + new_width
            bottom = top + new_height

            cropped = img.crop((left, top, right, bottom))

            cropped.save(output_path, "JPEG", quality=90, optimize=True)

        return output_path

    except Exception as e:
        raise RuntimeError(f"Crop failed: {str(e)}")

def enhance_image(input_path, brightness=1.0, contrast=1.0, color=1.0, sharpness=1.0):
    try:
        filename = generate_filename("enhanced", "jpg")
        output_path = get_output_path(filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with Image.open(input_path) as img:
            img = ensure_rgb(img)

            # Apply brightness
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)

            # Apply contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

            # Apply color
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(color)

            # Apply sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness )

            img.save(output_path, "JPEG", quality=90, optimize=True)

        return output_path

    except Exception as e:
        raise RuntimeError(f"Enhancement failed: {str(e)}")