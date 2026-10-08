from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_LOCATION = {
    "lat": 23.6739,
    "lon": 86.9524,
    "city": "Asansol, West Bengal",
}

DEFAULT_STATIONS: List[Dict[str, Any]] = [
    {"name": "Asansol EV Hub", "address": "G.T. Road, Asansol", "city": "Asansol", "state": "West Bengal", "type": "DC Fast", "power_kw": 120, "amenities": "Parking, Restrooms, 24x7", "latitude": 23.6739, "longitude": 86.9524},
    {"name": "Durgapur ChargeX", "address": "City Centre, Durgapur", "city": "Durgapur", "state": "West Bengal", "type": "DC Fast", "power_kw": 100, "amenities": "Retail, Security", "latitude": 23.5204, "longitude": 87.3119},
    {"name": "Kolkata GreenStop", "address": "Salt Lake, Kolkata", "city": "Kolkata", "state": "West Bengal", "type": "DC Fast", "power_kw": 120, "amenities": "Retail, Restrooms", "latitude": 22.5726, "longitude": 88.3639},
    {"name": "Siliguri GreenLink", "address": "Hill Cart Road, Siliguri", "city": "Siliguri", "state": "West Bengal", "type": "Level 2", "power_kw": 55, "amenities": "Parking", "latitude": 26.7271, "longitude": 88.3953},
    {"name": "Patna ElectroRoute", "address": "Boring Road, Patna", "city": "Patna", "state": "Bihar", "type": "Level 2 + DC", "power_kw": 95, "amenities": "Parking, Wi‑Fi", "latitude": 25.5941, "longitude": 85.1376},
    {"name": "Ranchi PowerNest", "address": "Main Road, Ranchi", "city": "Ranchi", "state": "Jharkhand", "type": "Level 2 + DC", "power_kw": 70, "amenities": "Parking, Security", "latitude": 23.3441, "longitude": 85.3096},
    {"name": "Jamshedpur Chargedrive", "address": "Bistupur, Jamshedpur", "city": "Jamshedpur", "state": "Jharkhand", "type": "Level 2", "power_kw": 50, "amenities": "Parking, Café", "latitude": 22.8046, "longitude": 86.2029},
    {"name": "Bhubaneswar EV Bay", "address": "KIIT Road, Bhubaneswar", "city": "Bhubaneswar", "state": "Odisha", "type": "DC Fast", "power_kw": 110, "amenities": "Parking, Lounge", "latitude": 20.2961, "longitude": 85.8245},
    {"name": "Cuttack ChargeCore", "address": "Madhupatna, Cuttack", "city": "Cuttack", "state": "Odisha", "type": "Level 2", "power_kw": 45, "amenities": "Parking", "latitude": 20.4625, "longitude": 85.8830},
    {"name": "Guwahati Green Plug", "address": "Paltan Bazaar, Guwahati", "city": "Guwahati", "state": "Assam", "type": "Level 2", "power_kw": 60, "amenities": "Café, Parking", "latitude": 26.1445, "longitude": 91.7362},
    {"name": "Shillong EV Point", "address": "Police Bazar, Shillong", "city": "Shillong", "state": "Meghalaya", "type": "Level 2", "power_kw": 40, "amenities": "Parking", "latitude": 25.5788, "longitude": 91.8933},
    {"name": "Agartala ChargeHub", "address": "Lake Chowmuhani, Agartala", "city": "Agartala", "state": "Tripura", "type": "Level 2", "power_kw": 35, "amenities": "Parking", "latitude": 23.8315, "longitude": 91.2868},
    {"name": "Imphal Electric Stop", "address": "Thangal Bazar, Imphal", "city": "Imphal", "state": "Manipur", "type": "Level 2", "power_kw": 30, "amenities": "Parking", "latitude": 24.8170, "longitude": 93.9368},
    {"name": "Lucknow GridPoint", "address": "Hazratganj, Lucknow", "city": "Lucknow", "state": "Uttar Pradesh", "type": "DC Fast", "power_kw": 100, "amenities": "Cafe, Parking", "latitude": 26.8467, "longitude": 80.9462},
    {"name": "Kanpur VoltLane", "address": "Kalyanpur, Kanpur", "city": "Kanpur", "state": "Uttar Pradesh", "type": "Level 2", "power_kw": 50, "amenities": "Parking, Security", "latitude": 26.4499, "longitude": 80.3319},
    {"name": "Varanasi E-Connect", "address": "Assi Ghat, Varanasi", "city": "Varanasi", "state": "Uttar Pradesh", "type": "Level 2", "power_kw": 50, "amenities": "Parking, Wi‑Fi", "latitude": 25.3176, "longitude": 82.9739},
    {"name": "Agra EV Circuit", "address": "Taj Road, Agra", "city": "Agra", "state": "Uttar Pradesh", "type": "Level 2 + DC", "power_kw": 60, "amenities": "Parking, Wi‑Fi", "latitude": 27.1767, "longitude": 78.0081},
    {"name": "Prayagraj E-Flow", "address": "Civil Lines, Prayagraj", "city": "Prayagraj", "state": "Uttar Pradesh", "type": "Level 2", "power_kw": 45, "amenities": "Parking", "latitude": 25.4358, "longitude": 81.8463},
    {"name": "Delhi EV Corridor", "address": "Connaught Place, New Delhi", "city": "New Delhi", "state": "Delhi", "type": "Ultra Fast", "power_kw": 200, "amenities": "Retail, Lounge, 24x7", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Noida ChargeZone", "address": "Sector 62, Noida", "city": "Noida", "state": "Uttar Pradesh", "type": "DC Fast", "power_kw": 140, "amenities": "Parking, Lounge", "latitude": 28.5355, "longitude": 77.3910},
    {"name": "Gurugram Meridian Charge", "address": "Cyber Hub, Gurugram", "city": "Gurugram", "state": "Haryana", "type": "Ultra Fast", "power_kw": 180, "amenities": "Coffee, Lounge", "latitude": 28.4595, "longitude": 77.0266},
    {"name": "Chandigarh ChargePoint", "address": "Sector 17, Chandigarh", "city": "Chandigarh", "state": "Chandigarh", "type": "DC Fast", "power_kw": 100, "amenities": "Parking, Security", "latitude": 30.7333, "longitude": 76.7794},
    {"name": "Jaipur EV Station", "address": "Malviya Nagar, Jaipur", "city": "Jaipur", "state": "Rajasthan", "type": "Level 2 + DC", "power_kw": 90, "amenities": "Security, Parking", "latitude": 26.9124, "longitude": 75.7873},
    {"name": "Jodhpur EV Point", "address": "Ratanada, Jodhpur", "city": "Jodhpur", "state": "Rajasthan", "type": "Level 2 + DC", "power_kw": 80, "amenities": "Parking, Café", "latitude": 26.2389, "longitude": 73.0243},
    {"name": "Kota VoltPoint", "address": "Talwandi, Kota", "city": "Kota", "state": "Rajasthan", "type": "Level 2", "power_kw": 50, "amenities": "Parking, Restrooms", "latitude": 25.2138, "longitude": 75.8648},
    {"name": "Ahmedabad ChargeNest", "address": "Navrangpura, Ahmedabad", "city": "Ahmedabad", "state": "Gujarat", "type": "Level 2", "power_kw": 50, "amenities": "Parking", "latitude": 23.0225, "longitude": 72.5714},
    {"name": "Surat City Charge", "address": "Adajan, Surat", "city": "Surat", "state": "Gujarat", "type": "Level 2 + DC", "power_kw": 90, "amenities": "Parking, Restrooms", "latitude": 21.1702, "longitude": 72.8311},
    {"name": "Vadodara EV Lane", "address": "Alkapuri, Vadodara", "city": "Vadodara", "state": "Gujarat", "type": "DC Fast", "power_kw": 95, "amenities": "Parking, Café", "latitude": 22.3072, "longitude": 73.1812},
    {"name": "Bhavnagar Chargelink", "address": "Sojiya Road, Bhavnagar", "city": "Bhavnagar", "state": "Gujarat", "type": "Level 2", "power_kw": 45, "amenities": "Parking", "latitude": 21.7645, "longitude": 72.1519},
    {"name": "Indore Charge Hub", "address": "Vijay Nagar, Indore", "city": "Indore", "state": "Madhya Pradesh", "type": "Level 2 + DC", "power_kw": 110, "amenities": "Parking, Lounge", "latitude": 22.7196, "longitude": 75.8577},
    {"name": "Bhopal Volt Plaza", "address": "Aishbagh, Bhopal", "city": "Bhopal", "state": "Madhya Pradesh", "type": "Level 2 + DC", "power_kw": 90, "amenities": "Parking, Restrooms", "latitude": 23.2599, "longitude": 77.4126},
    {"name": "Khargone EV Stop", "address": "Bus Stand, Khargone", "city": "Khargone", "state": "Madhya Pradesh", "type": "Level 2", "power_kw": 40, "amenities": "Parking", "latitude": 21.8254, "longitude": 75.6036},
    {"name": "Bilaspur Electric Bay", "address": "City Chowk, Bilaspur", "city": "Bilaspur", "state": "Chhattisgarh", "type": "Level 2", "power_kw": 45, "amenities": "Parking, Security", "latitude": 22.0797, "longitude": 82.1391},
    {"name": "Nagpur Grid Flex", "address": "Sadar, Nagpur", "city": "Nagpur", "state": "Maharashtra", "type": "DC Fast", "power_kw": 130, "amenities": "Security, Restrooms", "latitude": 21.1458, "longitude": 79.0882},
    {"name": "Nashik VoltPoint", "address": "College Road, Nashik", "city": "Nashik", "state": "Maharashtra", "type": "DC Fast", "power_kw": 100, "amenities": "Parking, Restrooms", "latitude": 20.0110, "longitude": 73.7900},
    {"name": "Mumbai Shell Charge", "address": "Andheri East, Mumbai", "city": "Mumbai", "state": "Maharashtra", "type": "DC Fast", "power_kw": 180, "amenities": "Coffee, Security", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Pune Smart Charge", "address": "Kalyani Nagar, Pune", "city": "Pune", "state": "Maharashtra", "type": "Level 2", "power_kw": 60, "amenities": "Parking, EV café", "latitude": 18.5204, "longitude": 73.8567},
    {"name": "Hyderabad Charge Plaza", "address": "Banjara Hills, Hyderabad", "city": "Hyderabad", "state": "Telangana", "type": "Level 2 + DC", "power_kw": 120, "amenities": "Parking, Restrooms", "latitude": 17.4065, "longitude": 78.4772},
    {"name": "Vijayawada E-Stop", "address": "Governorpet, Vijayawada", "city": "Vijayawada", "state": "Andhra Pradesh", "type": "Level 2 + DC", "power_kw": 75, "amenities": "Parking, Wi‑Fi", "latitude": 16.5062, "longitude": 80.6480},
    {"name": "Visakhapatnam Coastal Charge", "address": "Beach Road, Visakhapatnam", "city": "Visakhapatnam", "state": "Andhra Pradesh", "type": "DC Fast", "power_kw": 150, "amenities": "Seafront Parking", "latitude": 17.6868, "longitude": 83.2185},
    {"name": "Chennai Metro Charge", "address": "T Nagar, Chennai", "city": "Chennai", "state": "Tamil Nadu", "type": "DC Fast", "power_kw": 150, "amenities": "Shopping, Restrooms", "latitude": 13.0827, "longitude": 80.2707},
    {"name": "Coimbatore FlowCharge", "address": "Town Hall, Coimbatore", "city": "Coimbatore", "state": "Tamil Nadu", "type": "DC Fast", "power_kw": 120, "amenities": "Parking, Lounge", "latitude": 11.0168, "longitude": 76.9558},
    {"name": "Madurai EV Bay", "address": "Periyar Bus Stand, Madurai", "city": "Madurai", "state": "Tamil Nadu", "type": "Level 2", "power_kw": 45, "amenities": "Parking", "latitude": 9.9252, "longitude": 78.1198},
    {"name": "Tiruchirappalli PlugHub", "address": "Srirangam, Tiruchirappalli", "city": "Tiruchirappalli", "state": "Tamil Nadu", "type": "Level 2 + DC", "power_kw": 65, "amenities": "Parking, Security", "latitude": 10.7905, "longitude": 78.7047},
    {"name": "Bengaluru Green Hub", "address": "MG Road, Bengaluru", "city": "Bengaluru", "state": "Karnataka", "type": "DC Fast", "power_kw": 150, "amenities": "Café, Washrooms, Wi‑Fi", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Mysuru Charge Grid", "address": "Mysuru Palace Road, Mysuru", "city": "Mysuru", "state": "Karnataka", "type": "Level 2", "power_kw": 50, "amenities": "Parking", "latitude": 12.2958, "longitude": 76.6394},
    {"name": "Hubballi Electra Stop", "address": "Old Bus Stand, Hubballi", "city": "Hubballi", "state": "Karnataka", "type": "Level 2", "power_kw": 45, "amenities": "Parking, Restrooms", "latitude": 15.3647, "longitude": 75.1240},
    {"name": "Mangaluru ChargeLine", "address": "State Bank Road, Mangaluru", "city": "Mangaluru", "state": "Karnataka", "type": "Level 2 + DC", "power_kw": 70, "amenities": "Parking, Café", "latitude": 12.9141, "longitude": 74.8560},
    {"name": "Kochi RapidCharge", "address": "Marine Drive, Kochi", "city": "Kochi", "state": "Kerala", "type": "DC Fast", "power_kw": 120, "amenities": "Parking, Lounge", "latitude": 9.9312, "longitude": 76.2673},
    {"name": "Kannur ECharge", "address": "Thavakkara, Kannur", "city": "Kannur", "state": "Kerala", "type": "Level 2", "power_kw": 40, "amenities": "Parking, Café", "latitude": 11.8745, "longitude": 75.3704},
    {"name": "Thiruvananthapuram E-Point", "address": "Technopark, Thiruvananthapuram", "city": "Thiruvananthapuram", "state": "Kerala", "type": "DC Fast", "power_kw": 100, "amenities": "Security, Wi‑Fi", "latitude": 8.5241, "longitude": 76.9366},
    {"name": "Goa Beach EV", "address": "Panaji, Goa", "city": "Panaji", "state": "Goa", "type": "Level 2", "power_kw": 45, "amenities": "Parking, Restrooms", "latitude": 15.4909, "longitude": 73.8278},
    {"name": "Puducherry PlugPoint", "address": "Beach Road, Puducherry", "city": "Puducherry", "state": "Puducherry", "type": "Level 2", "power_kw": 35, "amenities": "Parking", "latitude": 11.9416, "longitude": 79.8083},
    {"name": "Silchar EV Bay", "address": "Station Road, Silchar", "city": "Silchar", "state": "Assam", "type": "Level 2", "power_kw": 30, "amenities": "Parking", "latitude": 24.8275, "longitude": 92.7986},
]


def load_stations_from_csv() -> List[Dict[str, Any]]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "india_ev_charging_points.csv"
    if not data_file.exists():
        return DEFAULT_STATIONS

    stations: List[Dict[str, Any]] = []
    with data_file.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                station = {
                    "name": str(row.get("name", "")).strip(),
                    "address": str(row.get("address", "")).strip(),
                    "city": str(row.get("city", "")).strip(),
                    "state": str(row.get("state", "")).strip(),
                    "type": str(row.get("type", "")).strip(),
                    "power_kw": float(row.get("power_kw", 0) or 0),
                    "amenities": str(row.get("amenities", "")).strip(),
                    "latitude": float(row.get("latitude", 0) or 0),
                    "longitude": float(row.get("longitude", 0) or 0),
                }
                if station["name"] and station["latitude"] and station["longitude"]:
                    stations.append(station)
            except (TypeError, ValueError):
                continue
    return stations or DEFAULT_STATIONS


STATIONS: List[Dict[str, Any]] = load_stations_from_csv()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def get_nearest_stations(
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    limit: int = 5,
    stations: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    station_list = stations if stations is not None else STATIONS
    if user_lat is None or user_lon is None:
        fallback_lat, fallback_lon = DEFAULT_LOCATION["lat"], DEFAULT_LOCATION["lon"]
        measured = [
            {**station, "distance_km": haversine_km(fallback_lat, fallback_lon, station["latitude"], station["longitude"])}
            for station in station_list
        ]
        return sorted(measured, key=lambda item: item["distance_km"])[:limit]

    scored = [
        {**station, "distance_km": haversine_km(user_lat, user_lon, station["latitude"], station["longitude"])}
        for station in station_list
    ]
    return sorted(scored, key=lambda item: item["distance_km"])[:limit]


MAJOR_INDIAN_CITIES: Dict[str, Dict[str, float]] = {
    "New Delhi / NCR": {"lat": 28.6139, "lon": 77.2090},
    "Noida (UP)": {"lat": 28.5355, "lon": 77.3910},
    "Gurugram (Haryana)": {"lat": 28.4595, "lon": 77.0266},
    "Mumbai (Maharashtra)": {"lat": 19.0760, "lon": 72.8777},
    "Pune (Maharashtra)": {"lat": 18.5204, "lon": 73.8567},
    "Bengaluru (Karnataka)": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad (Telangana)": {"lat": 17.4065, "lon": 78.4772},
    "Chennai (Tamil Nadu)": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata (West Bengal)": {"lat": 22.5726, "lon": 88.3639},
    "Asansol (West Bengal)": {"lat": 23.6739, "lon": 86.9524},
    "Durgapur (West Bengal)": {"lat": 23.5204, "lon": 87.3119},
    "Siliguri (West Bengal)": {"lat": 26.7271, "lon": 88.3953},
    "Ahmedabad (Gujarat)": {"lat": 23.0225, "lon": 72.5714},
    "Surat (Gujarat)": {"lat": 21.1702, "lon": 72.8311},
    "Jaipur (Rajasthan)": {"lat": 26.9124, "lon": 75.7873},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "Lucknow (Uttar Pradesh)": {"lat": 26.8467, "lon": 80.9462},
    "Kanpur (Uttar Pradesh)": {"lat": 26.4499, "lon": 80.3319},
    "Varanasi (Uttar Pradesh)": {"lat": 25.3176, "lon": 82.9739},
    "Agra (Uttar Pradesh)": {"lat": 27.1767, "lon": 78.0081},
    "Bhopal (Madhya Pradesh)": {"lat": 23.2599, "lon": 77.4126},
    "Indore (Madhya Pradesh)": {"lat": 22.7196, "lon": 75.8577},
    "Patna (Bihar)": {"lat": 25.5941, "lon": 85.1376},
    "Ranchi (Jharkhand)": {"lat": 23.3441, "lon": 85.3096},
    "Jamshedpur (Jharkhand)": {"lat": 22.8046, "lon": 86.2029},
    "Bhubaneswar (Odisha)": {"lat": 20.2961, "lon": 85.8245},
    "Kochi (Kerala)": {"lat": 9.9312, "lon": 76.2673},
    "Thiruvananthapuram (Kerala)": {"lat": 8.5241, "lon": 76.9366},
    "Coimbatore (Tamil Nadu)": {"lat": 11.0168, "lon": 76.9558},
    "Nagpur (Maharashtra)": {"lat": 21.1458, "lon": 79.0882},
    "Visakhapatnam (Andhra Pradesh)": {"lat": 17.6868, "lon": 83.2185},
    "Vijayawada (Andhra Pradesh)": {"lat": 16.5062, "lon": 80.6480},
    "Guwahati (Assam)": {"lat": 26.1445, "lon": 91.7362},
    "Panaji (Goa)": {"lat": 15.4909, "lon": 73.8278}
}


def fetch_ip_location() -> Optional[Dict[str, Any]]:
    """
    Server-side IP location lookup for reliable zero-permission location detection.
    """
    import urllib.request
    import json
    endpoints = ["https://ipwho.is/", "https://get.geojs.io/v1/ip/geo.json"]
    for endpoint in endpoints:
        try:
            req = urllib.request.Request(endpoint, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=3.5) as response:
                data = json.loads(response.read().decode("utf-8"))
                lat = data.get("latitude") or data.get("lat")
                lon = data.get("longitude") or data.get("lon")
                city = data.get("city")
                region = data.get("region")
                if lat and lon:
                    loc_name = f"{city}, {region}" if city and region else (city or "Detected IP Location")
                    return {
                        "lat": float(lat),
                        "lon": float(lon),
                        "city": loc_name,
                        "source": "network_ip",
                        "error": None
                    }
        except Exception:
            continue
    return None


def normalize_user_location(location_data: Optional[Dict[str, Any]]) -> Dict[str, Optional[float | str]]:
    if not isinstance(location_data, dict):
        return {"lat": None, "lon": None, "city": None, "source": None, "error": "Location data was not provided."}

    error = location_data.get("error")
    if error:
        return {"lat": None, "lon": None, "city": None, "source": None, "error": str(error)}

    lat = location_data.get("lat")
    lon = location_data.get("lon")

    if lat is None:
        lat = location_data.get("latitude")
    if lon is None:
        lon = location_data.get("longitude")

    if lat is None or lon is None:
        return {"lat": None, "lon": None, "city": None, "source": None, "error": None}

    try:
        normalized = {
            "lat": float(lat),
            "lon": float(lon),
            "city": str(location_data.get("city") or "Live Location"),
            "source": str(location_data.get("source") or "device"),
            "error": None,
        }
    except (TypeError, ValueError):
        return {"lat": None, "lon": None, "city": None, "source": None, "error": "Location coordinates were invalid."}

    return normalized


def build_google_maps_directions(origin_lat: Optional[float], origin_lon: Optional[float], destination_lat: float, destination_lon: float) -> str:
    if origin_lat is not None and origin_lon is not None:
        return (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={origin_lat},{origin_lon}"
            f"&destination={destination_lat},{destination_lon}"
            "&travelmode=driving"
        )
    return f"https://www.google.com/maps/search/?api=1&query={destination_lat},{destination_lon}"


