import os
import json
import random

# Categories and entities for generation
CROPS = ["tomato", "rice", "cotton", "maize", "potato", "wheat", "sugarcane", "mustard", "onion", "soybean", "groundnut", "chilli"]
LOCATIONS = ["Maharashtra", "Punjab", "Gujarat", "Karnataka", "Uttar Pradesh", "Haryana", "Madhya Pradesh", "Tamil Nadu", "Andhra Pradesh", "Rajasthan"]
SOILS = ["Alluvial", "Black", "Sandy", "Clayey", "Red", "Loamy"]
SEASONS = ["Kharif", "Rabi", "Zaid", "winter", "summer", "monsoon"]
WATER_LEVELS = ["high", "medium", "low", "abundant", "scarce", "regular"]
PESTS = ["aphids", "armyworm", "whiteflies", "spider mites", "bollworm", "thrips", "stem borer", "jassids", "cutworm"]
DISEASES = ["early blight", "late blight", "leaf spot", "rust", "blast", "bacterial blight", "mosaic virus", "powdery mildew", "root rot"]
NAMES = ["Rajesh", "Ramesh", "Suresh", "Amit", "Vijay", "Sunita", "Anil", "Sanjay", "Dinesh", "Mahesh"]

INTENT_TEMPLATES = {
    "WEATHER_QUERY": [
        "what is the weather today in {location}",
        "will it rain tomorrow in {location}",
        "temperature forecast for {location}",
        "weather report for {location} for next week",
        "is there any storm warning in {location}",
        "how is the climate in {location} right now",
        "show me the weather in {location}",
        "rain prediction for {location}",
        "is it going to rain in {location} this week",
        "current temperature in {location}",
        "forecast for {location} for today",
        "humidity levels in {location}",
        "wind speed forecast for {location}",
        "is there extreme weather expected in {location}"
    ],
    "FERTILIZER_QUERY": [
        "best fertilizers for {crop}",
        "what dose of nitrogen is needed for {crop}",
        "how much NPK for {crop} during sowing",
        "when should I apply potash to {crop}",
        "manure and fertilizer management for {crop}",
        "fertilizer schedule for {crop} crop",
        "how to apply urea to {crop}",
        "recommended fertilizer dose for {crop}",
        "organic fertilizer options for {crop}",
        "potassium deficiency treatment in {crop}",
        "what is the NPK ratio for {crop}",
        "best micronutrients for {crop} growth",
        "how to fertilize {crop} in {soil} soil",
        "zinc application timing for {crop}"
    ],
    "IRRIGATION_QUERY": [
        "how much water does {crop} need",
        "critical irrigation stages for {crop}",
        "how often to water {crop}",
        "drip irrigation guide for {crop}",
        "watering requirement for {crop} in {soil} soil",
        "when should I irrigate {crop}",
        "water scheduling for {crop}",
        "does {crop} require high irrigation",
        "best watering practices for {crop}",
        "signs of water stress in {crop}",
        "irrigation interval for {crop} in summer",
        "sprinkler irrigation for {crop} farm",
        "how to manage water for {crop} during flowering",
        "flood irrigation versus drip irrigation for {crop}"
    ],
    "PEST_QUERY": [
        "how to control {pest} in {crop}",
        "biological control for {pest}",
        "symptoms of {pest} on {crop}",
        "pesticides to kill {pest}",
        "organic treatment for {pest} attack",
        "preventing {pest} infection in {crop} farm",
        "best spray for {pest} in {crop}",
        "pest management guide for {crop} crop",
        "how to identify {pest} damage on leaves",
        "natural predators of {pest}",
        "integrated pest management for {pest} on {crop}",
        "how to eradicate {pest} infestation",
        "chemical controls for {pest}",
        "neem oil spray to control {pest}"
    ],
    "FARM_DATA_QUERY": [
        "where is my farm located",
        "what is the size of my farm",
        "show my farm land area",
        "details about my farm soil type",
        "what crops are currently planted on my land",
        "details of my farm in {location}",
        "give me a summary of my farm data for {location}",
        "what is the soil type of my land in {location}",
        "how many acres is my farm in {location}",
        "show my profile and farm info",
        "retrieve my farm location coordinates in {location}",
        "what is my current water availability source",
        "give me my farm profile details",
        "who is the owner of the farm",
        "show details for the farm owned by {name}",
        "what crops does {name} have in the farm",
        "find land details for {name}",
        "what is the land area of {name}'s farm",
        "retrieve farm coordinates for owner {name}",
        "is {crop} currently planted in {name}'s farm"
    ],
    "CROP_RECOMMENDATION_QUERY": [
        "what should I crop next season",
        "best crops to plant in {soil} soil",
        "crop recommendation for {location} in {season}",
        "suggest some crops for my farm",
        "which crops grow best with {water} water availability",
        "what are the profitable crops for {season} season",
        "crop recommendations based on weather",
        "should I plant {crop} or something else next season",
        "what can I plant in {soil} soil with {water} water",
        "alternative crops to plant for crop rotation",
        "best crop suggestions for {location} region",
        "what crops can be grown in {season} in my location",
        "suggest Rabi crops for my clayey soil",
        "recommend some Kharif crops to plant"
    ],
    "DISEASE_QUERY": [
        "how to cure {disease} in {crop}",
        "symptoms of {disease}",
        "treat {disease} leaf spot",
        "chemical control for {disease} blast",
        "remedies for {disease}",
        "leaf turning yellow due to {disease}",
        "how to prevent {disease} spreading in {crop}",
        "fungicide to control {disease} in {crop}",
        "organic solutions for {disease}",
        "identify leaf spots that look like {disease}",
        "bacterial spot control in {crop}",
        "signs of {disease} on plant stem",
        "how does {disease} affect {crop} yield",
        "management guide for {disease} disease"
    ],
    "CROP_SOIL_REQUIREMENT_QUERY": [
        "best soil for {crop}",
        "soil requirements for {crop}",
        "what type of soil does {crop} need",
        "ideal soil for growing {crop}",
        "suitable soil for {crop}",
        "what soil is best for {crop}",
        "{crop} soil requirement",
        "soil requirements of {crop}",
        "soil type for growing {crop}",
        "optimal soil parameters for {crop}"
    ]
}

def generate_dataset(num_examples=1100):
    dataset = []
    seen = set()
    
    intents = list(INTENT_TEMPLATES.keys())
    examples_per_intent = (num_examples // len(intents)) + 20
    
    for intent in intents:
        templates = INTENT_TEMPLATES[intent]
        count = 0
        attempts = 0
        max_attempts = examples_per_intent * 20
        
        while count < examples_per_intent and attempts < max_attempts:
            attempts += 1
            tpl = random.choice(templates)
            text = tpl.format(
                crop=random.choice(CROPS),
                location=random.choice(LOCATIONS),
                soil=random.choice(SOILS),
                season=random.choice(SEASONS),
                water=random.choice(WATER_LEVELS),
                pest=random.choice(PESTS),
                disease=random.choice(DISEASES),
                name=random.choice(NAMES)
            )
            text = text.strip()
            
            if text not in seen:
                seen.add(text)
                dataset.append({
                    "text": text,
                    "label": intent
                })
                count += 1
                
    # Shuffle and trim to requested size
    random.shuffle(dataset)
    dataset = dataset[:num_examples]
    
    print(f"Generated {len(dataset)} examples across {len(intents)} intents.")
    
    distribution = {}
    for item in dataset:
        lbl = item["label"]
        distribution[lbl] = distribution.get(lbl, 0) + 1
    print("Label distribution:", distribution)
    
    return dataset

def main():
    dataset = generate_dataset(1200)
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "intent_train_dataset.json")
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Dataset saved successfully to: {output_path}")

if __name__ == "__main__":
    main()
