# -*- coding: utf-8 -*-
"""
Готовит картинки для antonkim.com из исходного выреза.

Исходник — вырез головы на прозрачном фоне (1080×1080, субъект прижат к краям).
Скрипт обрезает по альфе, вписывает голову в квадрат так, чтобы она красиво
села в круг (CSS рисует круг сам), и раскладывает по размерам.

    python make_photo.py [путь_к_исходнику]

Без аргумента ищет antonkim-2.png на рабочем столе текущего пользователя.
"""

import sys
from pathlib import Path

from PIL import Image

DEFAULT_SRC = Path.home() / "Desktop" / "antonkim-2.png"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
OUT = Path(__file__).resolve().parent / "img"

# Кадрирование снято с референса Антона (photo_2024-03-16_08-32-52.jpg, 640×640):
# голова занимает 0.864 высоты кадра, её центр — чуть правее и выше середины.
MASTER = 1024
HEAD_HEIGHT = 0.864
HEAD_CX = 0.537
HEAD_CY = 0.484

# Фавиконке нужно заполнить крошечный квадрат, поэтому там своё кадрирование.
FAVICON_HEIGHT = 0.94


def compose(height_ratio, cx=0.5, cy=0.5, size=MASTER):
    """Вырез, вписанный в прозрачный квадрат: заданная высота головы и центр."""
    src = Image.open(SRC).convert("RGBA")
    head = src.crop(src.getchannel("A").getbbox())
    h = round(size * height_ratio)
    head = head.resize((round(head.width * h / head.height), h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(head, (round(size * cx - head.width / 2),
                        round(size * cy - head.height / 2)), head)
    return canvas


def main():
    if not SRC.exists():
        sys.exit(f"Не нашёл исходник: {SRC}")
    OUT.mkdir(exist_ok=True)
    master = compose(HEAD_HEIGHT, HEAD_CX, HEAD_CY)
    for size in (256, 512):
        master.resize((size, size), Image.LANCZOS).save(
            OUT / f"photo-{size}.webp", quality=82, method=6)

    fav = compose(FAVICON_HEIGHT)
    for size in (32, 180):
        fav.resize((size, size), Image.LANCZOS).save(
            OUT / f"favicon-{size}.png", optimize=True)

    for f in sorted(OUT.iterdir()):
        print(f"{f.name:<20} {f.stat().st_size / 1024:.0f} КБ")


if __name__ == "__main__":
    main()
