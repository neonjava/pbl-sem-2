"""
BloodBridge Matching Engine
===========================
Matches SOS blood requests to:
  1. Available donors within proximity
  2. Nearest hospitals with sufficient stock

Uses Haversine formula for distance. No external APIs needed.
All city coordinates are hardcoded for Karnataka + major Indian cities.
"""

import math
import secrets
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# City coordinate registry (lat, lon) – Karnataka cities + major metros
# ---------------------------------------------------------------------------
CITY_COORDS = {
    # Karnataka
    "davangere":    (14.4644, 75.9218),
    "bengaluru":    (12.9716, 77.5946),
    "bangalore":    (12.9716, 77.5946),
    "mysuru":       (12.2958, 76.6394),
    "mysore":       (12.2958, 76.6394),
    "hubli":        (15.3647, 75.1240),
    "dharwad":      (15.4589, 75.0078),
    "belagavi":     (15.8497, 74.4977),
    "belgaum":      (15.8497, 74.4977),
    "mangaluru":    (12.9141, 74.8560),
    "mangalore":    (12.9141, 74.8560),
    "tumakuru":     (13.3379, 77.1173),
    "tumkur":       (13.3379, 77.1173),
    "ballari":      (15.1394, 76.9214),
    "bellary":      (15.1394, 76.9214),
    "shivamogga":   (13.9299, 75.5681),
    "shimoga":      (13.9299, 75.5681),
    "chitradurga":  (14.2251, 76.3988),
    "chikkamagaluru":(13.3161, 75.7720),
    "hassan":       (13.0033, 76.0998),
    "udupi":        (13.3409, 74.7421),
    "raichur":      (16.2120, 77.3439),
    "bidar":        (17.9104, 77.5199),
    "vijayapura":   (16.8302, 75.7100),
    "kalaburagi":   (17.3297, 76.8343),
    "gulbarga":     (17.3297, 76.8343),
    "koppal":       (15.3508, 76.1547),
    "gadag":        (15.4314, 75.6236),
    "haveri":       (14.7939, 75.4006),
    "bagalkot":     (16.1826, 75.6961),
    "yadgir":       (16.7710, 77.1388),
    "chamarajanagar":(11.9249, 76.9440),
    "mandya":       (12.5218, 76.8951),
    "chikkaballapur":(13.4354, 77.7274),
    "kolar":        (13.1360, 78.1294),
    "ramanagara":   (12.7160, 77.2818),
    "kodagu":       (12.3375, 75.8069),
    "coorg":        (12.3375, 75.8069),
    "vijayanagara": (15.1394, 76.9214),
    # Major metros outside KA
    "mumbai":       (19.0760, 72.8777),
    "delhi":        (28.7041, 77.1025),
    "hyderabad":    (17.3850, 78.4867),
    "chennai":      (13.0827, 80.2707),
    "pune":         (18.5204, 73.8567),
    "kolkata":      (22.5726, 88.3639),
    "ahmedabad":    (23.0225, 72.5714),
}

# ---------------------------------------------------------------------------
# Blood compatibility map
# key = requested type → list of donor types that can donate to it
# ---------------------------------------------------------------------------
COMPATIBILITY = {
    "O+":  ["O+", "O-"],
    "O-":  ["O-"],
    "A+":  ["A+", "A-", "O+", "O-"],
    "A-":  ["A-", "O-"],
    "B+":  ["B+", "B-", "O+", "O-"],
    "B-":  ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
    "AB-": ["A-", "B-", "O-", "AB-"],
    # Legacy formats stored in DB (e.g. "O Positive")
    "O Positive":   ["O+", "O-", "O Positive", "O Negative"],
    "O Negative":   ["O-", "O Negative"],
    "A Positive":   ["A+", "A-", "O+", "O-", "A Positive", "A Negative", "O Positive", "O Negative"],
    "A Negative":   ["A-", "O-", "A Negative", "O Negative"],
    "B Positive":   ["B+", "B-", "O+", "O-", "B Positive", "B Negative", "O Positive", "O Negative"],
    "B Negative":   ["B-", "O-", "B Negative", "O Negative"],
    "AB Positive":  ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-",
                     "A Positive", "A Negative", "B Positive", "B Negative",
                     "O Positive", "O Negative", "AB Positive", "AB Negative"],
    "AB Negative":  ["A-", "B-", "O-", "AB-", "A Negative", "B Negative", "O Negative", "AB Negative"],
}

# Radius thresholds (km)
DONOR_RADIUS_KM    = 80   # look for donors within 80 km
HOSPITAL_RADIUS_KM = 120  # look for hospitals within 120 km


def haversine(lat1, lon1, lat2, lon2):
    """Returns distance in kilometres between two lat/lon points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def get_coords(city_name):
    """Looks up city coordinates. Returns None if unknown."""
    if not city_name:
        return None
    return CITY_COORDS.get(city_name.strip().lower())


def is_donor_eligible(donor):
    """
    Returns True if the donor is:
      - marked available / healthy
      - past their 90-day cooldown since last donation
    """
    health = (donor.get("health_status") or "").lower()
    if health not in ("healthy", ""):
        return False
    is_avail = donor.get("is_available")
    if is_avail is not None and not is_avail and is_avail != 1:
        return False

    last_don = donor.get("last_donation")
    if last_don:
        if isinstance(last_don, str):
            try:
                last_don = datetime.strptime(last_don, "%Y-%m-%d")
            except ValueError:
                return True
        if isinstance(last_don, datetime):
            if datetime.now() < last_don + timedelta(days=90):
                return False
    return True


def generate_match_ref():
    """Generates a short human-readable match reference ID."""
    return "MATCH-" + secrets.token_hex(3).upper()


def find_matches(requested_blood_type, requester_city, donors, hospitals, hospital_stock):
    """
    Core matching function.

    Parameters
    ----------
    requested_blood_type : str
        e.g. "O+" or "B Positive"
    requester_city : str
        City name from the SOS form
    donors : list[dict]
        All donor rows from the DB
    hospitals : list[dict]
        All hospital rows from the DB
    hospital_stock : list[dict]
        All blood_stock rows from the DB (for all hospitals)

    Returns
    -------
    dict with keys:
        ref_id          : str  – unique match reference
        matched_donors  : list[dict] – sorted by distance, with distance_km added
        matched_hospitals : list[dict] – sorted by distance, with distance_km & stock added
        requester_coords : tuple | None
        radius_used_donors : int (km)
        radius_used_hospitals : int (km)
    """
    requester_coords = get_coords(requester_city)
    compatible_types = COMPATIBILITY.get(requested_blood_type, [requested_blood_type])

    # ── Match donors ────────────────────────────────────────────────────────
    matched_donors = []
    for donor in donors:
        if donor.get("role") and donor["role"] != "donor":
            continue
        if donor.get("blood_type") not in compatible_types:
            continue
        if not is_donor_eligible(donor):
            continue

        donor_city = donor.get("city", "")
        donor_coords = get_coords(donor_city)

        if requester_coords and donor_coords:
            dist = haversine(*requester_coords, *donor_coords)
            if dist > DONOR_RADIUS_KM:
                continue
        elif requester_coords and not donor_coords:
            # Unknown donor city – skip distance filter, still include (marked as "distance unknown")
            dist = None
        else:
            dist = None

        matched_donors.append({
            **dict(donor),
            "distance_km": round(dist, 1) if dist is not None else None,
        })

    # Sort: known distances first (ascending), then unknowns
    matched_donors.sort(key=lambda d: (d["distance_km"] is None, d["distance_km"] or 0))

    # ── Match hospitals ──────────────────────────────────────────────────────
    # Build a quick stock lookup: hospital_id → list of stock rows
    stock_by_hospital = {}
    for row in hospital_stock:
        hid = row["hospital_id"]
        stock_by_hospital.setdefault(hid, []).append(dict(row))

    matched_hospitals = []
    for hosp in hospitals:
        hosp_city  = hosp.get("city", "")
        hosp_coords = get_coords(hosp_city)

        if requester_coords and hosp_coords:
            dist = haversine(*requester_coords, *hosp_coords)
            if dist > HOSPITAL_RADIUS_KM:
                continue
        elif requester_coords and not hosp_coords:
            dist = None
        else:
            dist = None

        # Attach only the relevant stock lines for this hospital
        relevant_stock = [
            s for s in stock_by_hospital.get(hosp["id"], [])
            if s.get("blood_type") in compatible_types and s.get("units", 0) > 0
        ]

        matched_hospitals.append({
            **dict(hosp),
            "distance_km": round(dist, 1) if dist is not None else None,
            "relevant_stock": relevant_stock,
            "has_stock": len(relevant_stock) > 0,
        })

    # Sort: hospitals with stock first, then by distance
    matched_hospitals.sort(
        key=lambda h: (
            not h["has_stock"],
            h["distance_km"] is None,
            h["distance_km"] or 0
        )
    )

    return {
        "ref_id":               generate_match_ref(),
        "matched_donors":       matched_donors[:10],     # cap at 10
        "matched_hospitals":    matched_hospitals[:5],   # cap at 5
        "requester_coords":     requester_coords,
        "radius_used_donors":   DONOR_RADIUS_KM,
        "radius_used_hospitals": HOSPITAL_RADIUS_KM,
        "requested_blood_type": requested_blood_type,
        "requester_city":       requester_city,
        "match_time":           datetime.now().strftime("%d %b %Y, %H:%M"),
    }
