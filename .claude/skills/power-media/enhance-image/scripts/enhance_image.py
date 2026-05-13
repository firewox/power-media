import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


PRESETS = {
    "soft": {
        "contrast": 1.12,
        "sharpness": 1.35,
        "brightness": 1.0,
        "denoise": False,
    },
    "document": {
        "contrast": 1.22,
        "sharpness": 1.9,
        "brightness": 1.02,
        "denoise": False,
    },
    "strong": {
        "contrast": 1.35,
        "sharpness": 2.4,
        "brightness": 1.03,
        "denoise": False,
    },
}

SUPPORTED_OUTPUT_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


def _apply_unsharp_mask(image: Image.Image, amount: float) -> Image.Image:
    if amount <= 1:
        return image
    percent = int((amount - 1) * 140)
    return image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=percent, threshold=3))


def enhance_image(
    image_path: Path,
    output_path: Path | None = None,
    *,
    mode: str = "color",
    preset: str = "document",
    contrast: float | None = None,
    sharpness: float | None = None,
    brightness: float | None = None,
    denoise: bool | None = None,
    scale: float = 1.0,
    threshold: int = 185,
) -> Path:
    image_path = image_path.expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")
    if not image_path.is_file():
        raise ValueError(f"Input path is not a file: {image_path}")

    output_path = output_path or image_path.with_name(f"{image_path.stem}-enhanced.png")
    output_path = output_path.expanduser().resolve()
    if output_path.suffix.lower() not in SUPPORTED_OUTPUT_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_OUTPUT_EXTENSIONS))
        raise ValueError(f"Output path must include an image extension, for example .png. Supported: {supported}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if preset not in PRESETS:
        raise ValueError("preset must be one of: soft, document, strong")
    settings = PRESETS[preset]
    contrast = settings["contrast"] if contrast is None else contrast
    sharpness = settings["sharpness"] if sharpness is None else sharpness
    brightness = settings["brightness"] if brightness is None else brightness
    denoise = settings["denoise"] if denoise is None else denoise

    with Image.open(image_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")

    if scale <= 0:
        raise ValueError("scale must be greater than 0")
    if scale != 1.0:
        width = max(1, round(image.width * scale))
        height = max(1, round(image.height * scale))
        image = image.resize((width, height), Image.Resampling.LANCZOS)

    if denoise:
        image = image.filter(ImageFilter.MedianFilter(size=3))

    image = ImageEnhance.Brightness(image).enhance(brightness)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = _apply_unsharp_mask(image, sharpness)
    image = ImageEnhance.Sharpness(image).enhance(max(1.0, sharpness / 1.4))

    if mode == "grayscale":
        image = ImageOps.grayscale(image)
    elif mode == "bw":
        grayscale = ImageOps.grayscale(image)
        image = grayscale.point(lambda pixel: 255 if pixel >= threshold else 0, mode="1")
    elif mode == "color":
        pass
    else:
        raise ValueError("mode must be one of: color, grayscale, bw")

    image.save(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Enhance scanned documents and image clarity.")
    parser.add_argument("image", help="Input image path, for example D:\\tmp\\scan.png")
    parser.add_argument("--output", help="Output image path. Defaults to <image_stem>-enhanced.png")
    parser.add_argument("--mode", choices=["color", "grayscale", "bw"], default="color")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="document")
    parser.add_argument("--contrast", type=float)
    parser.add_argument("--sharpness", type=float)
    parser.add_argument("--brightness", type=float)
    parser.add_argument("--scale", type=float, default=1.0, help="Upscale factor, for example 2.0")
    parser.add_argument("--threshold", type=int, default=185, help="Black/white threshold for --mode bw")
    parser.add_argument("--denoise", action="store_true", help="Apply median denoise filter. Can soften text edges.")
    args = parser.parse_args()

    output = enhance_image(
        Path(args.image),
        Path(args.output) if args.output else None,
        mode=args.mode,
        preset=args.preset,
        contrast=args.contrast,
        sharpness=args.sharpness,
        brightness=args.brightness,
        denoise=args.denoise,
        scale=args.scale,
        threshold=args.threshold,
    )
    print(f"Wrote enhanced image: {output}")


if __name__ == "__main__":
    main()
