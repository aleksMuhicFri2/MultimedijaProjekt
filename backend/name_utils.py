import re
import unicodedata

def normalize_name(name: str):
    if not name:
        return None

    # Take only first part if multilingual
    name = name.split("/")[0]

    # Remove accents
    name = "".join(
        c for c in unicodedata.normalize("NFD", name)
        if unicodedata.category(c) != "Mn"
    )

    name = name.lower().strip()

    # Normalize hyphens & spaces
    name = re.sub(r"\s*-\s*", "-", name)
    name = re.sub(r"\s+", " ", name)

    return name
