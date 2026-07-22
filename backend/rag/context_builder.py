import json
from datetime import datetime


def build_rag_context(
    retrieved_docs,
    farmer_profile=None,
    farm_context=None,
    weather_data=None,
    market_data=None,
):
    """
    Merges retrieved knowledge documents, farmer profile, farm specifications,
    weather forecast, and market prices into a unified structured context object.
    """
    # 1. Format Retrieved Knowledge
    knowledge_blocks = []
    categories_used = set()
    all_related_crops = set()
    sources = []

    for rank, doc in enumerate(retrieved_docs, 1):
        cat = doc.get("category", "general")
        categories_used.add(cat)
        title = doc.get("title", "")
        content = doc.get("content", "")
        score = doc.get("similarity_score", 0.0)
        doc_id = doc.get("document_id", f"doc_{rank}")
        crops = doc.get("related_crops", [])

        for c in crops:
            if c:
                all_related_crops.add(str(c).title())

        sources.append({
            "id": doc_id,
            "title": title,
            "category": cat,
            "similarity_score": score,
            "rank": rank,
            "source": doc.get("source", "Kisan Mitra Knowledge Base"),
        })

        knowledge_blocks.append(
            f"[Source {rank}] {title} (Category: {cat}, Match Score: {score:.4f})\n"
            f"Content: {content}\n"
            f"Keywords: {', '.join(doc.get('keywords', []))}"
        )

    formatted_knowledge_text = "\n\n".join(knowledge_blocks)

    # 2. Format Farmer Profile Context
    farmer_profile = farmer_profile or {}
    farmer_name = farmer_profile.get("name", "Farmer")
    location = farmer_profile.get("location", "India")
    state = farmer_profile.get("state", "")
    district = farmer_profile.get("district", "")
    language = farmer_profile.get("language", "English")

    formatted_farmer_ctx = (
        f"Farmer Name: {farmer_name}\n"
        f"Location: {district + ', ' if district else ''}{state if state else location}\n"
        f"Preferred Language: {language}"
    )

    # 3. Format Farm Context
    farm_context = farm_context or {}
    soil_type = farm_context.get("soil_type", "Loamy Soil")
    current_crop = farm_context.get("current_crop", farm_context.get("crop", "General Crops"))
    farm_area = farm_context.get("farm_area_acres", farm_context.get("area", 2.5))
    irrigation_source = farm_context.get("irrigation_type", farm_context.get("irrigation", "Canal / Borewell"))

    formatted_farm_ctx = (
        f"Soil Type: {soil_type}\n"
        f"Current Crop: {current_crop}\n"
        f"Farm Area: {farm_area} Acres\n"
        f"Irrigation System: {irrigation_source}"
    )

    # 4. Format Weather Data
    weather_data = weather_data or {}
    temp = weather_data.get("temp_c", weather_data.get("temperature", 28.0))
    humidity = weather_data.get("humidity", 65.0)
    rainfall = weather_data.get("rainfall_mm", weather_data.get("rainfall", 0.0))
    weather_desc = weather_data.get("condition", weather_data.get("description", "Partly Cloudy"))

    formatted_weather_ctx = (
        f"Temperature: {temp}°C\n"
        f"Humidity: {humidity}%\n"
        f"Rainfall: {rainfall} mm\n"
        f"Forecast Condition: {weather_desc}"
    )

    # 5. Format Market Data
    market_data = market_data or {}
    commodity = market_data.get("commodity", current_crop)
    mandi_price = market_data.get("mandi_price", market_data.get("price", "N/A"))
    msp = market_data.get("msp", "N/A")
    trend = market_data.get("trend", "Stable")

    formatted_market_ctx = (
        f"Commodity: {commodity}\n"
        f"Mandi Price: {mandi_price}\n"
        f"MSP Guarantee: {msp}\n"
        f"Price Trend: {trend}"
    )

    # Combined Full Prompt String (for LLM/Template consumption)
    full_prompt_context = (
        f"=== FARMER PROFILE ===\n{formatted_farmer_ctx}\n\n"
        f"=== FARM SPECIFICATIONS ===\n{formatted_farm_ctx}\n\n"
        f"=== CURRENT WEATHER ===\n{formatted_weather_ctx}\n\n"
        f"=== MARKET DATA ===\n{formatted_market_ctx}\n\n"
        f"=== RETRIEVED KNOWLEDGE ===\n{formatted_knowledge_text}"
    )

    return {
        "farmer_profile": farmer_profile,
        "farm_context": farm_context,
        "weather_data": weather_data,
        "market_data": market_data,
        "sources": sources,
        "categories_used": sorted(list(categories_used)),
        "related_crops": sorted(list(all_related_crops)),
        "formatted_knowledge_text": formatted_knowledge_text,
        "full_prompt_context": full_prompt_context,
        "created_at": datetime.now().isoformat(),
    }
