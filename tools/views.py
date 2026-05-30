from django.shortcuts import render
from django.conf import settings
from django.core.files import File
from .models import ImageProcess
from .utils import compress_image, resize_image, convert_image, create_thumbnail, enhance_image, crop_image
from .filters import apply_filter
import os
import uuid
import zipfile
from PIL import Image

def save_processed_image(obj, output_path):
    with open(output_path, 'rb') as f:
        obj.processed_image.save(
            os.path.basename(output_path),
            File(f),
            save=False
        )


def update_stats(obj, input_path, output_path):
    original = os.path.getsize(input_path) / 1024
    new = os.path.getsize(output_path) / 1024

    obj.original_size = round(original, 2)
    obj.compressed_size = round(new, 2)

    if original > 0:
        obj.compression_percentage = round(
            ((original - new) / original) * 100, 2
        )
    else:
        obj.compression_percentage = 0

def compress_view(request):
    if request.method == 'POST':
        image = request.FILES['image']
        quality = int(request.POST.get('quality', 80))

        obj = ImageProcess(original_image=image)
        obj.save()

        input_path = obj.original_image.path

        output_path = compress_image(input_path, quality)

        save_processed_image(obj, output_path)
        update_stats(obj, input_path, output_path)

        obj.save()

        return render(request, 'tools/compress_result.html', {'obj': obj})

    return render(request, 'tools/compress.html')

def resize_view(request):
    if request.method == 'POST':
        image = request.FILES['image']
        mode = request.POST.get('mode')

        obj = ImageProcess(original_image=image)
        obj.save()

        input_path = obj.original_image.path

        # Safe open
        with Image.open(input_path) as img:
            original_width, original_height = img.size

        # Decide size
        if mode == "percentage":
            percentage = int(request.POST.get('percentage'))
            new_width = int(original_width * percentage / 100)
            new_height = int(original_height * percentage / 100)
        else:
            new_width = int(request.POST.get('width'))
            new_height = int(request.POST.get('height'))

        output_path = resize_image(input_path, new_width, new_height)

        save_processed_image(obj, output_path)
        update_stats(obj, input_path, output_path)

        obj.save()

        return render(request, 'tools/resize_result.html', {
            'obj': obj,
            'original_dim': f"{original_width} x {original_height}",
            'new_dim': f"{new_width} x {new_height}"
        })

    return render(request, 'tools/resize.html')

def convert_view(request):
    if request.method == 'POST':
        try:
            image = request.FILES.get('image')
            output_format = request.POST.get('format')

            if not image:
                return render(request, 'tools/convert.html', {
                    'error': 'No image uploaded'
                })

            obj = ImageProcess(original_image=image)
            obj.save()

            input_path = obj.original_image.path

            output_path = convert_image(input_path, output_format)

            save_processed_image(obj, output_path)
            update_stats(obj, input_path, output_path)

            obj.save()

            return render(request, 'tools/convert_result.html', {'obj': obj})

        except Exception as e:
            return render(request, 'tools/convert.html', {
                'error': str(e)
            })

    return render(request, 'tools/convert.html')

def batch_view(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        operation = request.POST.get('operation')
        quality = int(request.POST.get('quality', 80))
        output_format = request.POST.get('format')

        processed_files = []

        for image in images:
            obj = ImageProcess(original_image=image)
            obj.save()

            input_path = obj.original_image.path

            if operation == "compress":
                output_path = compress_image(input_path, quality)

            elif operation == "convert":
                output_path = convert_image(input_path, output_format)

            else:
                continue

            save_processed_image(obj, output_path)
            update_stats(obj, input_path, output_path)

            obj.save()
            processed_files.append(output_path)

        # Create ZIP
        zip_filename = f"batch_{uuid.uuid4().hex}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, 'processed', zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in processed_files:
                zipf.write(file, os.path.basename(file))

        return render(request, 'tools/batch_result.html', {
            'files': processed_files,
            'zip_file': f"media/processed/{zip_filename}"
        })

    return render(request, 'tools/batch.html')

def thumbnail_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')

        # Optional size input (default 300x300)
        width = request.POST.get('width')
        height = request.POST.get('height')

        try:
            width = int(width) if width else 300
            height = int(height) if height else 300
        except:
            width, height = 300, 300

        obj = ImageProcess(original_image=image)
        obj.save()

        input_path = obj.original_image.path

        original_size = os.path.getsize(input_path) / 1024

        output_path = create_thumbnail(input_path, (width, height))

        new_size = os.path.getsize(output_path) / 1024

        with open(output_path, 'rb') as f:
            obj.processed_image.save(
                os.path.basename(output_path),
                File(f),
                save=False
            )

        obj.original_size = round(original_size, 2)
        obj.compressed_size = round(new_size, 2)

        if original_size > 0:
            obj.compression_percentage = round(
                ((original_size - new_size) / original_size) * 100, 2
            )
        else:
            obj.compression_percentage = 0

        obj.save()

        return render(request, 'tools/thumbnail_result.html', {
            'obj': obj,
            'thumb_size': f"{width} x {height}"
        })

    return render(request, 'tools/thumbnail.html')

def crop_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        ratio = request.POST.get('ratio')

        obj = ImageProcess(original_image=image)
        obj.save()

        input_path = obj.original_image.path

        original_size = os.path.getsize(input_path) / 1024

        # Crop
        output_path = crop_image(input_path, ratio)

        new_size = os.path.getsize(output_path) / 1024

        # Save processed image
        with open(output_path, 'rb') as f:
            obj.processed_image.save(
                os.path.basename(output_path),
                File(f),
                save=False
            )

        obj.original_size = round(original_size, 2)
        obj.compressed_size = round(new_size, 2)
        obj.compression_percentage = round(
            ((original_size - new_size) / original_size) * 100, 2
        )

        obj.save()

        return render(request, 'tools/crop_result.html', {
            'obj': obj,
            'ratio': ratio
        })

    return render(request, 'tools/crop.html')

def enhance_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')

        brightness = float(request.POST.get('brightness', 1.0))
        contrast = float(request.POST.get('contrast', 1.0))
        color = float(request.POST.get('color', 1.0))
        sharpness=float(request.POST.get('sharpness', 1.0))

        obj = ImageProcess(original_image=image)
        obj.save()

        input_path = obj.original_image.path

        original_size = os.path.getsize(input_path) / 1024

        # Enhance
        output_path = enhance_image(input_path, brightness, contrast, color, sharpness)

        new_size = os.path.getsize(output_path) / 1024

        # Save processed image
        with open(output_path, 'rb') as f:
            obj.processed_image.save(
                os.path.basename(output_path),
                File(f),
                save=False
            )

        obj.original_size = round(original_size, 2)
        obj.compressed_size = round(new_size, 2)

        if original_size > 0:
            obj.compression_percentage = round(
                ((original_size - new_size) / original_size) * 100, 2
            )
        else:
            obj.compression_percentage = 0

        obj.save()

        return render(request, 'tools/enhance_result.html', {
            'obj': obj,
            'brightness': brightness,
            'contrast': contrast
        })

    return render(request, 'tools/enhance.html')

def filter_view(request):
    if request.method == 'POST':
        image = request.FILES['image']
        filter_name = request.POST.get('filter')

        # Save original
        obj = ImageProcess(original_image=image)
        obj.save()

        input_path = obj.original_image.path

        # Apply filter
        output_path = apply_filter(input_path, filter_name)

        # Save processed image
        with open(output_path, 'rb') as f:
            obj.processed_image.save(
                os.path.basename(output_path),
                File(f),
                save=False
            )

        # Stats
        original_size = os.path.getsize(input_path) / 1024
        new_size = os.path.getsize(output_path) / 1024

        obj.original_size = round(original_size, 2)
        obj.compressed_size = round(new_size, 2)
        obj.compression_percentage = round(
            ((original_size - new_size) / original_size) * 100, 2
        )

        obj.save()

        return render(request, 'tools/filter_result.html', {
            'obj': obj,
            'filter_used': filter_name.capitalize()
        })

    return render(request, 'tools/filter.html')