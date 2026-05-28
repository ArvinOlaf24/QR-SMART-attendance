import requests
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/reverse-geocode")
def reverse_geocode():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng are required"}), 400

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "json", "lat": lat, "lon": lng},
            headers={"User-Agent": "TrackAS-Flask/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        return jsonify({"display_name": response.json().get("display_name", "Unknown location")})
    except requests.RequestException:
        return jsonify({"display_name": "Unknown location"})
