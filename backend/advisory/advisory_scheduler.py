import os
import sys
import json
from datetime import datetime

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from advisory.personalized_advisory import generate_personalized_advisories


def run_advisory_pipeline(
    farmer_profile=None,
    farm_context=None,
    weather_data=None,
    market_data=None,
    crop_recommendations=None,
    growth_stage=None,
):
    """
    Scheduler / Entrypoint for simultaneously running all advisory generators
    and producing a structured multi-category advisory bundle.
    """
    advisories = generate_personalized_advisories(
        farmer_profile=farmer_profile,
        farm_context=farm_context,
        weather_data=weather_data,
        market_data=market_data,
        crop_recommendations=crop_recommendations,
        growth_stage=growth_stage,
    )

    # Calculate Priority Breakdown
    priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    categories_set = set()

    for adv in advisories:
        p = adv.get("priority", "Medium")
        if p in priority_counts:
            priority_counts[p] += 1
        else:
            priority_counts[p] = 1

        categories_set.add(adv.get("category", "General"))

    farmer_id = (farmer_profile or {}).get("user_id", (farmer_profile or {}).get("name", "farmer_default"))

    return {
        "farmer_id": farmer_id,
        "total_advisories": len(advisories),
        "priority_breakdown": priority_counts,
        "categories_generated": sorted(list(categories_set)),
        "advisories": advisories,
        "generated_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print("Testing Advisory Scheduler Pipeline...")
    sample_weather = {"temp_c": 31.0, "humidity": 80.0, "rainfall_mm": 25.0, "condition": "Heavy Rain"}
    sample_market = {"commodity": "Rice", "mandi_price": "₹2,300/qtn", "msp": "₹2,183/qtn", "trend": "Upward"}
    sample_farm = {"crop": "Rice", "soil": "Alluvial Soil", "area": 3.0}

    result = run_advisory_pipeline(
        farm_context=sample_farm,
        weather_data=sample_weather,
        market_data=sample_market,
        growth_stage="Flowering"
    )

    print(f"\nGenerated {result['total_advisories']} Advisories.")
    print(f"Priority Breakdown: {result['priority_breakdown']}")
    print(f"Categories: {result['categories_generated']}")
    for a in result['advisories']:
        print(f"\n[{a['priority'].upper()}] {a['title']} ({a['category']})")
        print(f"  Description: {a['description']}")
