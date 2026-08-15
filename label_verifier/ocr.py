from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

def preprocess_image(image: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(image).convert("L")
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    if max(img.size) < 1600:
        scale = 1600 / max(img.size)
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    return img.filter(ImageFilter.SHARPEN)

def extract_text(image: Image.Image) -> str:
    return pytesseract.image_to_string(preprocess_image(image), config="--psm 6")
