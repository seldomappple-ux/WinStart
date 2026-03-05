from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "app_icon_source.png"
FALLBACK = ASSETS / "app_icon.png"
PNG_OUT = ASSETS / "app_icon.png"
ICO_OUT = ASSETS / "app_icon.ico"


def load_source() -> Image.Image:
    if SOURCE.exists():
        return Image.open(SOURCE).convert("RGBA")
    return Image.open(FALLBACK).convert("RGBA")


def make_square_canvas(img: Image.Image, size: int) -> Image.Image:
    fitted = img.copy()
    fitted.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2
    canvas.paste(fitted, (x, y), fitted)
    return canvas


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    source = load_source()
    png = make_square_canvas(source, 1024)
    png.save(PNG_OUT, "PNG")
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    frames = [make_square_canvas(source, size[0]) for size in sizes]
    frames[0].save(
        ICO_OUT,
        format="ICO",
        sizes=sizes,
        append_images=frames[1:],
    )
    print(PNG_OUT)
    print(ICO_OUT)


if __name__ == "__main__":
    main()
