import argparse
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz


def _load_pixmap(image_path: Path, shrink_factor: int = 0) -> "fitz.Pixmap":
    pix = fitz.Pixmap(str(image_path))
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.colorspace != fitz.csRGB:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    if shrink_factor:
        pix.shrink(shrink_factor)
    return pix


def _pdf_bytes_from_jpeg(jpeg_bytes: bytes, width: int, height: int) -> bytes:
    doc = fitz.open()
    try:
        page = doc.new_page(width=width, height=height)
        page.insert_image(fitz.Rect(0, 0, width, height), stream=jpeg_bytes)
        return doc.tobytes(garbage=4, deflate=True)
    finally:
        doc.close()


def _compressed_pdf_bytes(
    image_path: Path,
    target_mb: float | None,
    jpeg_quality: int | None,
) -> tuple[bytes, int, int]:
    target_bytes = int(target_mb * 1024 * 1024) if target_mb else None
    qualities = [jpeg_quality] if jpeg_quality else [92, 85, 75, 65, 55, 45, 35, 25]

    best: tuple[bytes, int, int] | None = None
    for shrink_factor in range(0, 3):
        pix = _load_pixmap(image_path, shrink_factor)
        for quality in qualities:
            jpeg_bytes = pix.tobytes("jpeg", jpg_quality=quality)
            pdf_bytes = _pdf_bytes_from_jpeg(jpeg_bytes, pix.width, pix.height)
            candidate = (pdf_bytes, quality, shrink_factor)
            if best is None or len(pdf_bytes) < len(best[0]):
                best = candidate
            if target_bytes is None or len(pdf_bytes) <= target_bytes:
                return candidate

    if best is None:
        raise RuntimeError("Failed to create compressed PDF bytes.")
    return best


def image_to_pdf(
    image_path: Path,
    output_path: Path | None = None,
    target_mb: float | None = None,
    jpeg_quality: int | None = None,
) -> Path:
    image_path = image_path.expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")
    if not image_path.is_file():
        raise ValueError(f"Input path is not a file: {image_path}")

    output_path = output_path or image_path.with_suffix(".pdf")
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if target_mb or jpeg_quality:
        pdf_bytes, quality, shrink_factor = _compressed_pdf_bytes(image_path, target_mb, jpeg_quality)
        output_path.write_bytes(pdf_bytes)
        print(f"Compressed with JPEG quality={quality}, shrink_factor={shrink_factor}")
    else:
        pix = fitz.Pixmap(str(image_path))
        width, height = pix.width, pix.height
        pix = None

        doc = fitz.open()
        try:
            page = doc.new_page(width=width, height=height)
            page.insert_image(fitz.Rect(0, 0, width, height), filename=str(image_path))
            doc.save(str(output_path))
        finally:
            doc.close()

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert one image into a one-page PDF.")
    parser.add_argument("image", help="Input image path, for example D:\\tmp\\scan.png")
    parser.add_argument("--output", help="Output PDF path. Defaults to the image path with .pdf extension.")
    parser.add_argument("--target-mb", type=float, help="Try to keep the PDF under this size by JPEG compression.")
    parser.add_argument("--jpeg-quality", type=int, choices=range(1, 101), metavar="1-100", help="Use a fixed JPEG quality.")
    args = parser.parse_args()

    output = image_to_pdf(
        Path(args.image),
        Path(args.output) if args.output else None,
        args.target_mb,
        args.jpeg_quality,
    )
    print(f"Wrote PDF: {output}")


if __name__ == "__main__":
    main()
