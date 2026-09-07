#!/usr/bin/env python3
"""Create Chrome Web Store promotional images from the theme artwork."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "store-assets" / "final"
MASTER = ROOT / "store-assets" / "source" / "promo-master-generated.png"
THEME_BG = ROOT / "images" / "new-tab-background.png"
ICON = ROOT / "images" / "icon-128.png"

DEEP = (14, 13, 20)
BASE = (25, 23, 36)
SURFACE = (31, 29, 46)
OVERLAY = (38, 35, 58)
MUTED = (110, 106, 134)
SUBTLE = (144, 140, 170)
TEXT = (224, 222, 244)
LOVE = (235, 111, 146)
GOLD = (246, 193, 119)
ROSE = (235, 188, 186)
PINE = (49, 116, 143)
FOAM = (156, 207, 216)
IRIS = (196, 167, 231)

FONT_PATH = "/System/Library/Fonts/SFNS.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(FONT_PATH, size)
    if bold:
        try:
            face.set_variation_by_name("Bold")
        except (AttributeError, OSError):
            pass
    return face


def cover(image: Image.Image, size: tuple[int, int], focus_x: float = 0.5,
          focus_y: float = 0.5) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)),
                           Image.Resampling.LANCZOS)
    left = round((resized.width - target_w) * focus_x)
    top = round((resized.height - target_h) * focus_y)
    left = max(0, min(left, resized.width - target_w))
    top = max(0, min(top, resized.height - target_h))
    return resized.crop((left, top, left + target_w, top + target_h))


def left_fade(image: Image.Image, strength: int = 222, reach: float = 0.68) -> None:
    overlay = Image.new("RGBA", image.size, (*DEEP, 0))
    draw = ImageDraw.Draw(overlay)
    fade_width = int(image.width * reach)
    for x in range(fade_width):
        t = x / max(1, fade_width - 1)
        alpha = round(strength * (1 - t) ** 1.7)
        draw.line((x, 0, x, image.height), fill=(*DEEP, alpha))
    image.alpha_composite(overlay)


def letterspaced(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                 face: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
                 spacing: int) -> None:
    x, y = xy
    for character in text:
        draw.text((x, y), character, font=face, fill=fill)
        width = draw.textlength(character, font=face)
        x += round(width) + spacing


def make_marquee(master: Image.Image, icon: Image.Image) -> None:
    image = cover(master, (1400, 560), focus_x=0.5).convert("RGBA")
    left_fade(image, 236, .66)
    draw = ImageDraw.Draw(image)
    mark = icon.resize((78, 78), Image.Resampling.LANCZOS)
    image.alpha_composite(mark, (92, 76))
    letterspaced(draw, (188, 91), "ROSÉ PINE", font(22, True), ROSE, 4)
    draw.text((86, 183), "Afterglow", font=font(78, True), fill=TEXT)
    draw.text((91, 286), "A calmer Chrome, in full color.", font=font(27), fill=SUBTLE)
    draw.rounded_rectangle((90, 372, 326, 425), radius=26, fill=(*OVERLAY, 228),
                           outline=(*IRIS, 128), width=2)
    draw.text((122, 383), "DARK  •  QUIET  •  VIVID", font=font(15, True), fill=IRIS)
    image.convert("RGB").save(STORE / "promo-marquee-1400x560.png", optimize=True)


def make_small(master: Image.Image, icon: Image.Image) -> None:
    image = cover(master, (440, 280), focus_x=.60).convert("RGBA")
    left_fade(image, 238, .78)
    draw = ImageDraw.Draw(image)
    mark = icon.resize((58, 58), Image.Resampling.LANCZOS)
    image.alpha_composite(mark, (32, 37))
    letterspaced(draw, (101, 50), "ROSÉ PINE", font(14, True), ROSE, 2)
    draw.text((30, 117), "Afterglow", font=font(46, True), fill=TEXT)
    draw.text((33, 181), "A modern dark Chrome theme", font=font(17), fill=SUBTLE)
    image.convert("RGB").save(STORE / "promo-small-440x280.png", optimize=True)


def browser_chrome(image: Image.Image, title: str = "New Tab") -> None:
    draw = ImageDraw.Draw(image)
    tab_face = font(17, True)
    tab_right = min(image.width - 110,
                    112 + max(248, round(draw.textlength(title, font=tab_face)) + 96))
    draw.rectangle((0, 0, image.width, 61), fill=BASE)
    draw.ellipse((18, 19, 34, 35), fill=(255, 95, 87))
    draw.ellipse((42, 19, 58, 35), fill=(254, 188, 46))
    draw.ellipse((66, 19, 82, 35), fill=(40, 201, 64))
    draw.rounded_rectangle((112, 12, tab_right, 61), radius=15, fill=OVERLAY)
    draw.ellipse((132, 28, 142, 38), fill=IRIS)
    draw.text((157, 22), title, font=tab_face, fill=TEXT)
    draw.text((tab_right - 31, 21), "×", font=font(18), fill=SUBTLE)
    draw.text((tab_right + 26, 18), "+", font=font(24), fill=MUTED)

    draw.rectangle((0, 61, image.width, 139), fill=SURFACE)
    draw.text((24, 82), "‹", font=font(34), fill=SUBTLE)
    draw.text((66, 82), "›", font=font(34), fill=MUTED)
    draw.text((108, 83), "↻", font=font(25), fill=SUBTLE)
    draw.rounded_rectangle((158, 76, image.width - 84, 123), radius=24, fill=DEEP)
    draw.ellipse((181, 92, 195, 106), outline=FOAM, width=2)
    draw.text((211, 88), "Search the web", font=font(17), fill=SUBTLE)
    draw.ellipse((image.width - 58, 88, image.width - 38, 108), fill=OVERLAY,
                 outline=IRIS, width=2)


def make_screenshot_new_tab(theme: Image.Image) -> None:
    image = Image.new("RGB", (1280, 800), DEEP)
    page = cover(theme, (1280, 661), focus_x=.5)
    image.paste(page, (0, 139))
    browser_chrome(image)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((393, 329, 887, 389), radius=30, fill=(31, 29, 46, 244),
                           outline=(144, 140, 170, 100), width=2)
    draw.ellipse((422, 349, 438, 365), outline=FOAM, width=2)
    draw.text((458, 346), "Search or type a URL", font=font(18), fill=SUBTLE)
    image.save(STORE / "screenshot-01-new-tab-1280x800.png", optimize=True)


def make_screenshot_chrome(master: Image.Image) -> None:
    image = cover(master, (1280, 800), focus_x=.47).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (*DEEP, 156))
    image = Image.alpha_composite(image, overlay)
    browser = Image.new("RGB", (1088, 318), DEEP)
    browser_chrome(browser, "Active tab — easy to find")
    draw_browser = ImageDraw.Draw(browser)
    draw_browser.rounded_rectangle((0, 139, 1088, 318), radius=0, fill=DEEP)
    browser = browser.filter(ImageFilter.GaussianBlur(.15))
    shadow = Image.new("RGBA", (1128, 358), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((20, 20, 1108, 338), radius=24,
                                             fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(shadow, (76, 91))
    image.alpha_composite(browser.convert("RGBA"), (96, 111))

    draw = ImageDraw.Draw(image)
    draw.text((96, 515), "Dark, calm, cohesive.", font=font(48, True), fill=TEXT)
    draw.text((99, 582), "Readable tabs, a dark omnibox, and a unified toolbar.",
              font=font(22), fill=SUBTLE)
    draw.rounded_rectangle((99, 650, 337, 701), radius=25, fill=(*OVERLAY, 232),
                           outline=(*SUBTLE, 92), width=2)
    draw.text((127, 664), "WHITE BOOKMARK LABELS", font=font(14, True), fill=TEXT)
    image.convert("RGB").save(STORE / "screenshot-02-browser-chrome-1280x800.png",
                              optimize=True)


def main() -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    master = Image.open(MASTER).convert("RGB")
    master = ImageEnhance.Contrast(master).enhance(1.04)
    theme = Image.open(THEME_BG).convert("RGB")
    icon = Image.open(ICON).convert("RGBA")
    icon.save(STORE / "store-icon-128.png", optimize=True)
    make_marquee(master, icon)
    make_small(master, icon)
    make_screenshot_new_tab(theme)
    make_screenshot_chrome(master)
    print(f"Generated Chrome Web Store assets in {STORE}")


if __name__ == "__main__":
    main()
