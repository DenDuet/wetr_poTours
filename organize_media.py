# -*- coding: utf-8 -*-
"""Скрипт: используемые медиа -> media/working/, остальное -> media/Мусор/"""
import os
import shutil
from pathlib import Path

MEDIA = Path(__file__).resolve().parent / "media"

# Все используемые пути (относительно media), из шаблонов и views
USED = [
    "mountain.mp4",
    "favicon.png",
    "test1/965-5762.png", "test1/965-5763.svg", "test1/965-5765.svg", "test1/965-5764.svg",
    "test1/I971-11654-1128-11013-831-4853.svg", "test1/I971-11654-1128-11013-831-4854.svg",
    "test1/I971-11655-831-4871-831-4865.svg", "test1/I971-11655-831-4871-831-4864.svg",
    "test1/origOf1icon.jpg", "test1/origOf2icon.jpg", "test1/origOf3icon.jpg",
    "test1/965-5790.png", "test1/965-5791.png", "test1/965-5792.png",
    "test1/20659480-uhd_3840_2160_24fps.mp4",
    "test1/I965-5797-449-1298-368-149.png", "test1/I965-5798-449-1298-368-149.png",
    "test1/965-5788.png",
    "lp/459-523.png", "lp/459-524.svg",
    "logo/icon.png",
    "footer/965-5972.png",
    "footer/I965-5974-476-1595.svg", "footer/I965-5974-476-1598.svg",
    "footer/I965-5974-476-1601.svg", "footer/I965-5974-476-1604.svg",
    "footer/I965-5974-476-1605.png",
    "video/final detail.mp4", "video/organisations_group.mp4",
    "hero/hero_organisations.jpg", "hero/kayak.jpg", "hero/balls.jpg", "hero/mount.jpg", "hero/mans.jpg",
    "figma-group-tours-page/202ef6f88b9e0536630c83b01ac794a18fa6d87b.png",
    "figma-group-tours-page/9f56211dc5d58e0c0d820adc91861c0d8824f195.png",
    "icons/time.png", "icons/cities.png", "icons/people.png", "icons/star.png", "icons/icon1.svg",
    "icons/card.png", "icons/king.png", "icons/exp.png",
    "tours/mountains-iceland.png", "tours/castle-europe.png",
]

WORKING = MEDIA / "working"
TRASH = MEDIA / "Мусор"
KEEP_TOPLEVEL = {"working", "Мусор", "catalog", "README.md"}  # не переносить в Мусор


def main():
    WORKING.mkdir(parents=True, exist_ok=True)
    TRASH.mkdir(parents=True, exist_ok=True)

    for rel in USED:
        src = MEDIA / rel
        if not src.exists():
            print("Skip (missing):", rel)
            continue
        dst = WORKING / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print("Copy:", rel)

    # Перенести всё, кроме working, Мусор, catalog и README, в Мусор
    for name in os.listdir(MEDIA):
        if name in KEEP_TOPLEVEL:
            continue
        path = MEDIA / name
        if not path.is_dir() and name != "README.md":
            dest = TRASH / name
            if path != dest:
                shutil.move(str(path), str(dest))
                print("Move to trash:", name)
            continue
        if path.is_dir() and name not in KEEP_TOPLEVEL:
            dest = TRASH / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(path), str(dest))
            print("Move to trash (dir):", name)

    print("Done.")


if __name__ == "__main__":
    main()
