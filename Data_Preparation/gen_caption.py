import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from pathlib import Path
import random

SVG_NS = {"svg": "http://www.w3.org/2000/svg"}

# Map raw room types (from SVG) to abstract categories
ROOM_MAPPING = {
    "bedroom": "bedrooms",
    "bath": "bathrooms",                  # normal bathroom
    "bath shower": "bathrooms_shower",    # bathroom with shower
    "kitchen": "kitchens",
    "livingroom": "living_rooms",
    "diningroom": "dining_rooms",
    "entry lobby": "corridors",
    "draughtlobby": "corridors",
    "corridor": "corridors",
    "hall": "corridors",
    "storage": "storage",
    "outdoor": "outdoor",
    # anything not here is ignored in counts
}

TEMPLATES = [
    "floor plan drawing of an apartment with {bedrooms} bedrooms and {bathrooms} bathrooms{connectivity}, top-down architectural blueprint",
    "top-down apartment floor plan showing {bedrooms} bedrooms and {bathrooms} bathrooms{connectivity}",
    "black and white 2D architectural floor plan of an apartment with {bedrooms} bedrooms and {bathrooms} bathrooms{connectivity}",
    "apartment layout floor plan, top view, with {bedrooms} bedrooms and {bathrooms} bathrooms{connectivity}",
]

# -------------------------
# Parse SVG and extract rooms
# -------------------------
def parse_rooms(svg_path: Path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    rooms = []

    for g in root.findall(".//svg:g", SVG_NS):
        cls = g.attrib.get("class", "")
        if not cls.startswith("Space "):
            continue

        # Raw type from SVG, e.g. "Bath", "Bath Shower", "Entry Lobby"
        room_type_raw = cls.replace("Space ", "").lower().strip()

        for poly in g.findall(".//svg:polygon", SVG_NS):
            points = poly.attrib.get("points")
            if not points:
                continue

            coords = [tuple(map(float, p.split(","))) for p in points.split()]
            polygon = Polygon(coords)

            rooms.append({
                "type": room_type_raw,
                "polygon": polygon,
            })
            break  # only first polygon per room group

    return rooms

# -------------------------
# Connectivity detection (open kitchen ↔ living room)
# -------------------------
def detect_connectivity(rooms):
    kitchen = [r for r in rooms if "kitchen" in r["type"]]
    living = [r for r in rooms if "living" in r["type"]]

    for k in kitchen:
        for l in living:
            if k["polygon"].touches(l["polygon"]):
                return ", open kitchen connected to living room"

    return ""

# -------------------------
# Door & window counting
# -------------------------
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

# -------------------------
# Aggregate room counts using ROOM_MAPPING
# -------------------------
def aggregate_room_counts(rooms):
    counts = {
        "bedrooms": 0,
        "bathrooms": 0,          # normal baths
        "bathrooms_shower": 0,   # baths with shower
        "kitchens": 0,
        "living_rooms": 0,
        "dining_rooms": 0,
        "corridors": 0,
        "storage": 0,
        "outdoor": 0,
    }

    for r in rooms:
        raw_type = r["type"]  # e.g. "bath", "bath shower", "entry lobby"
        key = ROOM_MAPPING.get(raw_type)
        if key is not None and key in counts:
            counts[key] += 1

    return counts

# -------------------------
# Caption builder
# -------------------------
def build_caption(svg_path: Path):
    rooms = parse_rooms(svg_path)
    counts = aggregate_room_counts(rooms)

    # total bathrooms = normal + with shower
    total_bathrooms = counts["bathrooms"] + counts["bathrooms_shower"]

    bedrooms = counts["bedrooms"]
    bathrooms = total_bathrooms

    connectivity = detect_connectivity(rooms)
    doors, windows = count_doors_windows(svg_path)

    template = random.choice(TEMPLATES)

    caption = template.format(
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        connectivity=connectivity
    )

    # Extra info about other spaces (only if present)
    extras = []
    if counts["kitchens"] > 0:
        extras.append("a kitchen")
    if counts["living_rooms"] > 0:
        extras.append("a living room")
    if counts["corridors"] > 0:
        extras.append("corridors")
    if counts["outdoor"] > 0:
        extras.append("a balcony or outdoor area")

    # Mention bathrooms with shower if any
    if counts["bathrooms_shower"] > 0:
        if counts["bathrooms_shower"] == 1:
            extras.append("one bathroom with shower")
        else:
            extras.append(f"{counts['bathrooms_shower']} bathrooms with shower")

    if extras:
        extras_str = ", ".join(extras)
        caption += f", including {extras_str}"

    # Optional: doors & windows
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

        print(f"✓ {plan_id}.png → {plan_id}.txt :: {caption}")


if __name__ == "__main__":
    IMAGE_DIR = Path(r"D:\\Documents\\UTBM\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\dataset\\images")
    SVG_ROOT = Path(r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\high_quality")
    CAPTION_DIR = Path(r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\dataset\\captions")

    generate_for_selected_images(IMAGE_DIR, SVG_ROOT, CAPTION_DIR)
