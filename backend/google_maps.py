import os
import googlemaps

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_MAPS_API_KEY not set")

gmaps = googlemaps.Client(key=API_KEY)