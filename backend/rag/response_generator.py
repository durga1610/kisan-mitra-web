import re


def classify_query_intent(query_text):
    """
    Classifies the user query into agricultural intent categories.
    """
    q = query_text.lower()

    if any(k in q for k in ["fertilizer", "urea", "dap", "mop", "npk", "nutrient", "manure", "nitrogen", "phosphorus", "potassium"]):
        return "Fertilizer"

    if any(k in q for k in ["pest", "disease", "fungal", "blast", "rust", "blight", "borer", "insect", "spray", "pesticide", "fungicide"]):
        return "Pest & Disease"

    if any(k in q for k in ["irrigate", "irrigation", "water", "watering", "drip", "sprinkler", "awd", "furrow"]):
        return "Irrigation"

    if any(k in q for k in ["soil", "black soil", "red soil", "clay", "loam", "alluvial", "sandy", "ph", "fertility"]):
        return "Soil"

    if any(k in q for k in ["weather", "rain", "rainfall", "temperature", "humidity", "drought", "frost", "cold wave", "heatwave", "monsoon"]):
        return "Weather"

    if any(k in q for k in ["scheme", "government", "pm-kisan", "pmfby", "kcc", "yojana", "subsidy", "subsidies"]):
        return "Government Schemes"

    if any(k in q for k in ["market", "mandi", "msp", "price", "prices", "enam", "sell", "trading"]):
        return "Market"

    if any(k in q for k in ["crop", "grow", "cultivate", "variety", "plant", "suitable", "sowing", "harvest", "season"]):
        return "Crop Selection"

    return "General Farming"


def generate_local_response(query_text, context_data):
    """
    Generates a local RAG response grounded strictly in the retrieved knowledge base records.
    Constructs a 5-section response (Title, Explanation, Best Practices, Warnings, Source).
    """
    sources = context_data.get("sources", [])

    if not sources:
        top_score = 0.0
    else:
        top_score = sources[0].get("similarity_score", 0.0)

    category = classify_query_intent(query_text)
    related_crops = context_data.get("related_crops", [])
    categories_used = context_data.get("categories_used", [])

    # Exact Low Confidence Threshold Check (< 0.40)
    if top_score < 0.40:
        return {
            "answer": "Sorry, I don't have enough information in my local agricultural knowledge base.",
            "confidence_score": round(top_score, 4),
            "confidence_level": "Low",
            "category": category,
            "retrieved_sources": sources,
            "related_crops": related_crops,
            "knowledge_categories_used": categories_used,
            "weather_applied": False,
            "farm_applied": False,
        }

    # Determine confidence level
    if top_score >= 0.55:
        confidence_level = "High"
    else:
        confidence_level = "Medium"

    # Context variables
    farm_ctx = context_data.get("farm_context", {})
    weather_ctx = context_data.get("weather_data", {})

    top_doc = sources[0]
    top_title = top_doc.get("title", "Agricultural Knowledge Guide")
    doc_source = top_doc.get("source", "Kisan Mitra Agricultural Knowledge Base")

    # Extract top document content from formatted_knowledge_text
    knowledge_text = context_data.get("formatted_knowledge_text", "")
    top_content = ""
    if "Content: " in knowledge_text:
        top_content = knowledge_text.split("Content: ")[1].split("\nKeywords:")[0].strip()
    else:
        top_content = top_title

    # Section 1: Title
    answer_parts = [f"### **Title:** {top_title}\n"]

    # Section 2: Explanation
    answer_parts.append(f"**Explanation:**\n{top_content}\n")

    # Section 3: Best Practices
    soil_type = farm_ctx.get("soil_type")
    current_crop = farm_ctx.get("current_crop", farm_ctx.get("crop"))
    best_practices = [
        "• Follow standard dosage and timing specified in ICAR/KVK agronomic guidelines.",
        "• Ensure proper soil moisture levels before applying chemical inputs or fertilizers.",
        "• Maintain clean field drainage to promote healthy root aeration and prevent stagnation."
    ]
    if soil_type or current_crop:
        best_practices.append(
            f"• Tailored for your farm with **{soil_type or 'local soil'}** growing **{current_crop or 'target crop'}**."
        )

    answer_parts.append("**Best Practices:**\n" + "\n".join(best_practices) + "\n")

    # Section 4: Warnings (if available/applicable)
    warnings = []
    temp = weather_ctx.get("temp_c", weather_ctx.get("temperature"))
    humidity = weather_ctx.get("humidity")
    rainfall = weather_ctx.get("rainfall_mm", weather_ctx.get("rainfall"))

    weather_applied = False
    if humidity is not None and float(humidity) > 75.0:
        warnings.append(f"⚠️ **High Humidity Alert ({humidity}%)**: Ambient humidity is high, increasing fungal disease pressure. Inspect lower leaves daily.")
        weather_applied = True
    if rainfall is not None and float(rainfall) > 20.0:
        warnings.append(f"⚠️ **Heavy Rainfall Advisory ({rainfall} mm)**: Defer top-dressing chemical fertilizers or flood irrigation to prevent nutrient leaching.")
        weather_applied = True
    if temp is not None and float(temp) >= 38.0:
        warnings.append(f"⚠️ **Heatwave Stress ({temp}°C)**: Provide light frequent irrigation and apply crop straw mulching.")

    if not warnings:
        warnings.append("• No immediate weather or disease warnings detected. Maintain routine crop monitoring.")

    answer_parts.append("**Warnings:**\n" + "\n".join(warnings) + "\n")

    # Section 5: Source
    answer_parts.append(f"**Source:** {doc_source}")

    full_answer = "\n".join(answer_parts)

    return {
        "answer": full_answer,
        "confidence_score": round(top_score, 4),
        "confidence_level": confidence_level,
        "category": category,
        "retrieved_sources": sources,
        "related_crops": related_crops,
        "knowledge_categories_used": categories_used,
        "weather_applied": weather_applied,
        "farm_applied": bool(soil_type or current_crop),
    }
