from PIL import Image, ImageEnhance
import os
from .utils import generate_filename, get_output_path, ensure_rgb

def apply_original(img):
    return img


def apply_fresh(img):
    img = ImageEnhance.Brightness(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    return img


def apply_night(img):
    img = ImageEnhance.Brightness(img).enhance(0.7)
    return img


def apply_city(img):
    img = ImageEnhance.Contrast(img).enhance(1.5)
    return img


def apply_clear(img):
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    return img


def apply_island(img):
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    return img


def apply_mountain(img):
    img = ImageEnhance.Color(img).enhance(0.8)
    img = ImageEnhance.Brightness(img).enhance(1.05)
    return img


def apply_mono(img):
    return img.convert("L").convert("RGB")


def apply_vintage(img):
    width, height = img.size
    pixels = img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = pixels[px, py]

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            pixels[px, py] = (
                min(255, tr),
                min(255, tg),
                min(255, tb)
            )

    return img


# ================================
# 🔹 Filter Mapping
# ================================

FILTER_MAP = {
    "original": apply_original,
    "fresh": apply_fresh,
    "night": apply_night,
    "city": apply_city,
    "clear": apply_clear,
    "island": apply_island,
    "mountain": apply_mountain,
    "mono": apply_mono,
    "vintage": apply_vintage,
}


# ================================
# 🔹 Main Filter Engine
# ================================

def apply_filter(input_path, filter_name):
    """
    Apply selected filter to image and return output path
    """

    if filter_name not in FILTER_MAP:
        raise ValueError(f"Unsupported filter: {filter_name}")

    filename = generate_filename(f"{filter_name}", "jpg")
    output_path = get_output_path(filename)

    with Image.open(input_path) as img:
        img = ensure_rgb(img)

        # Apply filter
        filter_function = FILTER_MAP[filter_name]
        processed_img = filter_function(img)

        # Save safely
        processed_img.save(output_path, "JPEG", optimize=True, quality=90)

    return output_path