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
}

# Caption templates: now only use {core_desc}, no extra connectivity slot
TEMPLATES = [
    "top-down {apt_word} {fp_word} showing {core_desc}, rendered as a clean black-and-white architectural drawing with {doors_phrase}{windows_phrase}",
    "{fp_word_cap} of a {apt_word} that contains {core_desc}, drawn in a monochrome architectural style with {doors_phrase}{windows_phrase}",
    "black-and-white {fp_word} of a {apt_word} featuring {core_desc}; the layout includes {doors_phrase}{windows_phrase}",
    "architectural {fp_word} of a {apt_word}, top-down view, with {core_desc} and {doors_phrase}{windows_phrase}",
]

# -------------------------
# Small helpers
# -------------------------
def plural_phrase(n: int, singular: str, plural: str | None = None):
    """Return '1 bedroom' or '2 bedrooms' etc."""
    if n <= 0:
        return ""
    if plural is None:
        plural = singular + "s"
    if n == 1:
        return f"1 {singular}"
    return f"{n} {plural}"

def join_non_empty(parts, sep=", "):
    return sep.join([p for p in parts if p])

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
            break

    return rooms

# -------------------------
# Connectivity detection (open kitchen ↔ living room) -> boolean
# -------------------------
def has_open_plan_kitchen(rooms):
    kitchen = [r for r in rooms if "kitchen" in r["type"]]
    living = [r for r in rooms if "living" in r["type"]]

    for k in kitchen:
        for l in living:
            if k["polygon"].touches(l["polygon"]):
                return True
    return False

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
        raw_type = r["type"]
        key = ROOM_MAPPING.get(raw_type)
        if key is not None and key in counts:
            counts[key] += 1

    return counts

# -------------------------
# Caption builder (RICH & NON-REPETITIVE)
# -------------------------
def build_caption(svg_path: Path):
    rooms = parse_rooms(svg_path)
    counts = aggregate_room_counts(rooms)

    # total bathrooms = normal + with shower
    total_bathrooms = counts["bathrooms"] + counts["bathrooms_shower"]

    # base phrases with counts
    bedroom_phrase = plural_phrase(counts["bedrooms"], "bedroom")
    bathroom_phrase = plural_phrase(total_bathrooms, "bathroom")

    # integrate "with shower" info directly into bathroom phrase
    if counts["bathrooms_shower"] > 0:
        shower_text = plural_phrase(
            counts["bathrooms_shower"],
            "one with shower",
            f"{counts['bathrooms_shower']} with shower"
        )
        # e.g. "2 bathrooms including one with shower"
        bathroom_phrase = f"{bathroom_phrase} including {shower_text}"

    kitchen_phrase  = plural_phrase(counts["kitchens"], "kitchen")
    living_phrase   = plural_phrase(counts["living_rooms"], "living room")
    corridor_phrase = plural_phrase(counts["corridors"], "corridor")
    outdoor_phrase  = plural_phrase(counts["outdoor"], "balcony or outdoor area")

    # open-plan handling: merge kitchen + living into ONE phrase with numbers
    open_plan = has_open_plan_kitchen(rooms)
    open_plan_phrase = ""
    if open_plan and counts["kitchens"] > 0 and counts["living_rooms"] > 0:
        open_plan_phrase = (
            plural_phrase(counts["kitchens"], "open-plan kitchen", "open-plan kitchens")
            + " connected to "
            + plural_phrase(counts["living_rooms"], "living room")
        )
        # remove separate kitchen/living phrases to avoid repetition
        kitchen_phrase = ""
        living_phrase = ""

    # build core description = list of non-empty phrases
    core_parts = [
        bedroom_phrase,
        bathroom_phrase,
        open_plan_phrase,
        kitchen_phrase,
        living_phrase,
        corridor_phrase,
        outdoor_phrase,
    ]
    core_desc = join_non_empty(core_parts, sep=", ")

    # doors / windows phrases
    doors, windows = count_doors_windows(svg_path)
    doors_phrase = plural_phrase(doors, "door")
    windows_phrase = plural_phrase(windows, "window")

    # for nicer language at the end
    if doors_phrase and windows_phrase:
        # "11 doors and 4 windows"
        windows_phrase = " and " + windows_phrase
    elif not doors_phrase and not windows_phrase:
        doors_phrase = "no specified openings"
        windows_phrase = ""

    # high-level synonyms for variety
    apt_word = random.choice(["apartment", "flat", "residential unit"])
    fp_word = random.choice(["floor plan", "layout", "blueprint"])
    fp_word_cap = fp_word.capitalize()

    template = random.choice(TEMPLATES)

    caption = template.format(
        apt_word=apt_word,
        fp_word=fp_word,
        fp_word_cap=fp_word_cap,
        core_desc=core_desc,
        doors_phrase=doors_phrase,
        windows_phrase=windows_phrase,
    )

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
    CAPTION_DIR = Path(r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\dataset\\captions2")

    generate_for_selected_images(IMAGE_DIR, SVG_ROOT, CAPTION_DIR)
