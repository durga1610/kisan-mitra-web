"""
advisory_rules.py — Agronomic, Weather, Market, and Soil Rule Definitions
for Kisan Mitra Personalized AI Advisory Engine.
"""

def evaluate_weather_rules(weather_data, crop_name, soil_type):
    """
    Evaluates weather conditions against agronomic thresholds.
    Returns a list of Weather & Pest Advisory objects.
    """
    advisories = []
    weather_data = weather_data or {}

    temp = float(weather_data.get("temp_c", weather_data.get("temperature", 25.0)))
    humidity = float(weather_data.get("humidity", 60.0))
    rainfall = float(weather_data.get("rainfall_mm", weather_data.get("rainfall", 0.0)))
    condition = weather_data.get("condition", weather_data.get("description", "Clear")).lower()

    # Rule 1: Heavy Rainfall Alert (Critical)
    if rainfall >= 20.0 or "heavy rain" in condition or "downpour" in condition:
        advisories.append({
            "id": "adv_weather_heavy_rain",
            "category": "Weather Advisory",
            "title": "Heavy Rainfall Alert: Delay Irrigation & Prepare Field Drainage",
            "description": (
                f"Heavy rainfall of {rainfall:.1f} mm forecast for your farm. "
                "Immediately suspend scheduled irrigation and top-dressing chemical fertilizers. "
                "Clear drainage channels to prevent waterlogging around root zones."
            ),
            "priority": "Critical",
            "reason": f"Rainfall forecast ({rainfall:.1f} mm) exceeds high risk threshold (20 mm).",
            "source": "Weather Advisory Service & ICAR Drainage Guidelines",
            "confidence": 0.95,
        })

    # Rule 2: High Humidity & Fungal Disease Risk (High)
    if humidity >= 75.0 and temp >= 22.0:
        advisories.append({
            "id": "adv_pest_high_humidity",
            "category": "Pest & Disease Advisory",
            "title": "Fungal Disease Warning: High Humidity Alert",
            "description": (
                f"Ambient humidity is high at {humidity:.1f}% with temperature {temp:.1f}°C. "
                f"These microclimatic conditions favor fungal outbreaks such as Blast, Rust, or Blight in {crop_name}. "
                "Monitor lower leaves closely and consider a preventive organic neem oil spray (5ml/L)."
            ),
            "priority": "High",
            "reason": f"Relative humidity ({humidity:.1f}%) exceeds 75% threshold in warm conditions.",
            "source": "Plant Protection Advisory & Agrometeorology Division",
            "confidence": 0.90,
        })

    # Rule 3: Extreme Heatwave Alert (High)
    if temp >= 38.0:
        advisories.append({
            "id": "adv_weather_heatwave",
            "category": "Weather Advisory",
            "title": "Heatwave Warning: Increase Soil Moisture Protection",
            "description": (
                f"High temperature of {temp:.1f}°C detected. "
                "Provide light frequent irrigation during early morning or evening hours. "
                "Apply crop straw mulching to conserve root zone soil moisture."
            ),
            "priority": "High",
            "reason": f"Temperature ({temp:.1f}°C) exceeds heat stress threshold (38°C).",
            "source": "Crop Stress & Water Management Guidelines",
            "confidence": 0.92,
        })

    # Rule 4: Cold Wave / Frost Risk (Critical)
    if temp <= 8.0:
        advisories.append({
            "id": "adv_weather_cold_wave",
            "category": "Weather Advisory",
            "title": "Cold Wave & Frost Precaution Alert",
            "description": (
                f"Low night temperature of {temp:.1f}°C detected. "
                "Apply light evening irrigation to raise soil thermal mass and protect tender foliage from frost damage."
            ),
            "priority": "Critical",
            "reason": f"Temperature ({temp:.1f}°C) dropped below safe threshold (8°C).",
            "source": "National Agrometeorology Advisory",
            "confidence": 0.94,
        })

    return advisories


def evaluate_market_rules(market_data, crop_name):
    """
    Evaluates mandi price trends and MSP guarantees.
    Returns a list of Market & Selling Advisory objects.
    """
    advisories = []
    market_data = market_data or {}

    commodity = market_data.get("commodity", crop_name)
    trend = str(market_data.get("trend", "Stable")).capitalize()
    mandi_price_str = str(market_data.get("mandi_price", market_data.get("price", "0")))
    msp_str = str(market_data.get("msp", "0"))

    # Extract numerical values if present
    try:
        price_num = float(''.join(c for c in mandi_price_str if c.isdigit() or c == '.'))
    except ValueError:
        price_num = 0.0

    try:
        msp_num = float(''.join(c for c in msp_str if c.isdigit() or c == '.'))
    except ValueError:
        msp_num = 0.0

    # Rule 1: Upward Price Trend (High)
    if trend == "Upward" or (price_num > 0 and msp_num > 0 and price_num >= msp_num * 1.1):
        advisories.append({
            "id": "adv_market_price_surge",
            "category": "Market Advisory",
            "title": f"Favorable Market Trend for {commodity}: Strategic Selling Advice",
            "description": (
                f"Mandi prices for {commodity} are currently trending UPWARD ({mandi_price_str}). "
                "If clean dry storage facilities are available, hold stock for 2-3 days to capture peak market rates. "
                "Ensure moisture content is below 12% before bagging."
            ),
            "priority": "High",
            "reason": f"Market price trend is Upward and trading above baseline.",
            "source": "e-NAM Market Intelligence & Agmarknet",
            "confidence": 0.88,
        })

    # Rule 2: Price Below MSP (High)
    if price_num > 0 and msp_num > 0 and price_num < msp_num:
        advisories.append({
            "id": "adv_market_msp_procurement",
            "category": "Government Scheme Advisory",
            "title": f"MSP Protection Alert for {commodity}",
            "description": (
                f"Private mandi prices for {commodity} ({mandi_price_str}) are currently below the official MSP rate ({msp_str}). "
                "Sell your produce at official Government Procurement Centers (FCI/State Warehousing) to secure full MSP value."
            ),
            "priority": "High",
            "reason": f"Mandi market price is below government Minimum Support Price (MSP).",
            "source": "Ministry of Agriculture & Farmers Welfare (MSP Cell)",
            "confidence": 0.93,
        })

    return advisories


def evaluate_crop_agronomic_rules(crop_name, soil_type, farm_area, growth_stage=None):
    """
    Evaluates crop stage, soil nutrient management, and fertilizer timing.
    Returns a list of Crop, Soil, Fertilizer, and Irrigation Advisories.
    """
    advisories = []
    crop_lower = crop_name.lower()
    soil_lower = soil_type.lower()
    stage = (growth_stage or "Vegetative").capitalize()

    # Rule 1: Fertilizer Top-Dressing at Flowering/Tillering (High)
    if stage in ["Vegetative", "Flowering", "Tillering"]:
        advisories.append({
            "id": "adv_crop_fertilizer_split",
            "category": "Fertilizer Advisory",
            "title": f"{crop_name} {stage} Stage Nutrient Top-Dressing",
            "description": (
                f"Your {crop_name} crop is currently in the active {stage} growth stage. "
                "Apply the recommended split dose of Nitrogen (Urea @ 25-30 kg/acre) along with Micronutrient Zinc Sulphate. "
                "Ensure soil is moist prior to fertilizer application."
            ),
            "priority": "High",
            "reason": f"Crop entered critical nutrient absorption stage ({stage}).",
            "source": "ICAR Recommended Fertilizer Management Schedule",
            "confidence": 0.91,
        })

    # Rule 2: Acidic Soil Lime Application (Medium)
    if "red" in soil_lower or "acidic" in soil_lower:
        advisories.append({
            "id": "adv_soil_lime_amendment",
            "category": "Soil Advisory",
            "title": "Red Soil Acid Neutralization Guidance",
            "description": (
                f"Red soils tend to be acidic (pH < 6.0), which restricts Phosphorus absorption for {crop_name}. "
                "Incorporate Agricultural Lime or Dolomite (200 kg/acre) during land preparation or early tillering."
            ),
            "priority": "Medium",
            "reason": "Red soil characteristics tend toward lower pH and reduced Phosphorus availability.",
            "source": "Soil Health Management Division",
            "confidence": 0.86,
        })

    # Rule 3: Alkaline / Heavy Black Soil Management (Medium)
    if "black" in soil_lower or "clay" in soil_lower:
        advisories.append({
            "id": "adv_soil_black_drainage",
            "category": "Soil Advisory",
            "title": "Black Clay Soil Moisture & Aeration Management",
            "description": (
                "Black clay soil possesses high water retention but poor aeration when saturated. "
                "Maintain broad-bed furrowing or raised beds to prevent root suffocation during irrigation."
            ),
            "priority": "Medium",
            "reason": "Black clay soil requires structured aeration to prevent waterlogging stress.",
            "source": "National Soil Survey & Land Use Planning",
            "confidence": 0.87,
        })

    return advisories


def evaluate_government_schemes():
    """
    Returns standard baseline farmer scheme advisories.
    """
    return [
        {
            "id": "adv_scheme_pm_kisan",
            "category": "Government Scheme Advisory",
            "title": "PM-KISAN Financial Support & Soil Health Card Scheme",
            "description": (
                "Ensure your PM-KISAN e-KYC is completed to receive the 3 annual financial installments (₹6,000/year). "
                "Get your soil tested for free under the Soil Health Card Scheme at your nearest Block Agriculture Office."
            ),
            "priority": "Low",
            "reason": "Universal farmer financial welfare & soil testing scheme.",
            "source": "PM-KISAN Portal & Department of Agriculture",
            "confidence": 0.98,
        }
    ]
