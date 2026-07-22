import os
import sys
import json
from datetime import datetime

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from advisory.advisory_rules import (
    evaluate_weather_rules,
    evaluate_market_rules,
    evaluate_crop_agronomic_rules,
    evaluate_government_schemes,
)

PRIORITY_ORDER = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
}


def generate_personalized_advisories(
    farmer_profile=None,
    farm_context=None,
    weather_data=None,
    market_data=None,
    crop_recommendations=None,
    growth_stage=None,
):
    """
    Generates personalized, multi-category agronomic advisories based on
    farmer profile, farm specs, weather forecasts, market prices, and ML recommendations.

    Returns:
    List of deduplicated advisory objects sorted by priority (Critical > High > Medium > Low).
    """
    farmer_profile = farmer_profile or {}
    farm_context = farm_context or {}
    weather_data = weather_data or {}
    market_data = market_data or {}

    # Extract farm context attributes
    crop_name = farm_context.get("current_crop", farm_context.get("crop", "Rice"))
    soil_type = farm_context.get("soil_type", farm_context.get("soil", "Alluvial Soil"))
    farm_area = farm_context.get("farm_area_acres", farm_context.get("area", 2.5))

    # Evaluate all rule categories simultaneously
    raw_advisories = []

    # 1. Weather & Pest Advisories
    weather_advs = evaluate_weather_rules(weather_data, crop_name, soil_type)
    raw_advisories.extend(weather_advs)

    # 2. Market & Selling Advisories
    market_advs = evaluate_market_rules(market_data, crop_name)
    raw_advisories.extend(market_advs)

    # 3. Crop, Fertilizer, & Soil Advisories
    crop_advs = evaluate_crop_agronomic_rules(crop_name, soil_type, farm_area, growth_stage)
    raw_advisories.extend(crop_advs)

    # 4. Crop Recommendation ML Advisory (If provided)
    if crop_recommendations and isinstance(crop_recommendations, list) and len(crop_recommendations) > 0:
        top_rec = crop_recommendations[0]
        rec_crop = top_rec.get("crop", top_rec.get("name", "Recommended Crop")).title()
        prob = top_rec.get("probability", top_rec.get("confidence", 0.90))

        if rec_crop.lower() != crop_name.lower():
            raw_advisories.append({
                "id": f"adv_ml_rec_{rec_crop.lower()}",
                "category": "Crop Advisory",
                "title": f"ML Crop Recommendation: Consider Rotation with {rec_crop}",
                "description": (
                    f"Based on your farm's {soil_type} and weather parameters, our Random Forest ML model "
                    f"predicts **{rec_crop}** as an optimal crop with {prob*100:.1f}% confidence. "
                    "Consider rotating into this crop in the upcoming season to maximize yield and profitability."
                ),
                "priority": "High",
                "reason": f"Random Forest ML model identified {rec_crop} with high agronomic suitability.",
                "source": "Kisan Mitra Crop Recommendation ML Model (99.5% F1-Score)",
                "confidence": round(float(prob), 4),
            })

    # 5. Government Scheme Advisories
    scheme_advs = evaluate_government_schemes()
    raw_advisories.extend(scheme_advs)

    # STEP 8: Deduplication & Relevance Filtering
    seen_ids = set()
    seen_titles = set()
    unique_advisories = []
    current_time_iso = datetime.now().isoformat()

    for adv in raw_advisories:
        adv_id = adv.get("id")
        title = adv.get("title")

        if adv_id in seen_ids or title in seen_titles:
            continue

        seen_ids.add(adv_id)
        seen_titles.add(title)

        # Attach standard timestamp & ensure required keys
        adv["timestamp"] = current_time_iso
        adv["priority"] = adv.get("priority", "Medium")
        adv["confidence"] = round(float(adv.get("confidence", 0.85)), 4)

        unique_advisories.append(adv)

    # STEP 5: Sort Advisories by Priority Level (Critical > High > Medium > Low)
    unique_advisories.sort(key=lambda x: PRIORITY_ORDER.get(x["priority"], 99))

    return unique_advisories
