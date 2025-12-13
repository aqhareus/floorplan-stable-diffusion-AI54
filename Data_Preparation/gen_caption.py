import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from pathlib import Path
import random

SVG_NS = {"svg": "http://www.w3.org/2000/svg"}

TEMPLATES = [
    "floor plan drawing of an apartment with {bedrooms} bedrooms and {bathrooms} bathrooms{connectivity}, top-down architectural blueprint",
    "top-down apartment floor plan showing {bedrooms} bedrooms, {bathrooms} bathrooms and a kitchen{connectivity}",
    "black and white 2D architectural floor plan of an apartment with {bedrooms} bedrooms and {bathrooms} bathrooms{connectivity}",
    "apartment layout floor plan, top view, including {bedrooms} bedrooms, {bathrooms} bathrooms and corridors{connectivity}",
]

def parse_rooms(svg_path: Path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    rooms = []

    for g in root.findall(".//svg:g", SVG_NS):
        cls = g.attrib.get("class", "")
        if not cls.startswith("Space "):
            continue

        room_type = cls.replace("Space ", "").lower()

        for poly in g.findall(".//svg:polygon", SVG_NS):
            points = poly.attrib.get("points")
            if not points:
                continue

            coords = [tuple(map(float, p.split(","))) for p in points.split()]
            polygon = Polygon(coords)

            rooms.append({
                "type": room_type,
                "polygon": polygon
            })
            break

    return rooms

def detect_connectivity(rooms):
    kitchen = [r for r in rooms if "kitchen" in r["type"]]
    living = [r for r in rooms if "living" in r["type"]]

    for k in kitchen:
        for l in living:
            if k["polygon"].touches(l["polygon"]):
                return ", open kitchen connected to living room"

    return ""

def count_doors_windows(svg_path: Path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    doors = 0
    windows = 0

    for g in root.findall(".//svg:g", SVG_NS):
        cls = g.attrib.get("class", "").lower()
        if "door" in cls:
            doors += 1
        if "window" in cls:
            windows += 1

    return doors, windows

def build_caption(svg_path: Path):
    rooms = parse_rooms(svg_path)

    bedrooms = sum(1 for r in rooms if "bedroom" in r["type"])
    bathrooms = sum(1 for r in rooms if "bath" in r["type"])

    connectivity = detect_connectivity(rooms)
    doors, windows = count_doors_windows(svg_path)

    template = random.choice(TEMPLATES)

    caption = template.format(
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        connectivity=connectivity
    )

    if doors > 0 or windows > 0:
        caption += f", {doors} doors and {windows} windows"

    return caption

# -------------------------
# MAIN: generate captions only for selected PNGs
# -------------------------
def generate_for_selected_images(
    image_dir: Path,
    svg_root: Path,
    caption_dir: Path
):
    caption_dir.mkdir(parents=True, exist_ok=True)

    png_files = sorted(image_dir.glob("*.png"))

    print(f"Found {len(png_files)} selected images")

    for png in png_files:
        plan_id = png.stem  # "17" from "17.png"
        svg_path = svg_root / plan_id / "model.svg"

        if not svg_path.exists():
            print(f"[WARNING] SVG not found for {plan_id}, skipping")
            continue

        caption = build_caption(svg_path)
        out_file = caption_dir / f"{plan_id}.txt"
        out_file.write_text(caption, encoding="utf-8")

        print(f"✓ {plan_id}.png → {plan_id}.txt")

if __name__ == "__main__":
    IMAGE_DIR = Path(r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\dataset\\images")
    SVG_ROOT = Path(r"D:\\Documents\\UTBM\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\high_quality")
    CAPTION_DIR = Path(r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\dataset\\captions")

    generate_for_selected_images(IMAGE_DIR, SVG_ROOT, CAPTION_DIR)
