import os
import json

# Define the backend directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BACKEND_DIR, "documents")
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. Start with 15 highly detailed hand-crafted crops, now including category
CROP_DATA = [
    {
        "name": "Grape",
        "category": "Fruit Crops",
        "season": "Rabi",
        "soil_requirements": "Well-drained sandy loam or gravelly clay loam soil with pH between 6.5 and 7.5. Avoid heavy soils with poor drainage and high salt content.",
        "water_requirements": "Moderate water requirements. Drip irrigation is highly recommended. Critical watering stages are bud burst, flowering, and berry development. Avoid waterlogging and excessive humidity to prevent fungal infections.",
        "fertilizer_schedule": {
            "npk": "50:50:100 kg of N:P:K per acre",
            "application": [
                "Apply full dose of Phosphorus and Potassium during pruning.",
                "Apply Nitrogen in split doses: 50% post-pruning and 50% during berry growth.",
                "Apply Boron and Zinc foliar sprays before flowering to improve fruit set."
            ]
        },
        "growth_stages": {"vegetative": 45, "flowering": 90, "fruiting": 120, "harvesting": 150},
        "disease_information": "Downy Mildew, Powdery Mildew, Anthracnose, and Black Rot. Downy Mildew causes white cottony growth on the leaf underside; control by spraying copper oxychloride (3g/L) or systemic fungicides.",
        "pest_management": "Mealybugs, Thrips, and Flea beetles are common. Thrips feed on blossoms causing scarred berries. Control using yellow sticky traps and spraying neem oil or spinosad.",
        "harvest_information": "Harvest when berries are fully ripe, sweet, and uniform in color. Avoid harvesting after rain. Keep in cold storage at 0-2 degrees Celsius with 90% relative humidity to prolong shelf life."
    },
    {
        "name": "Banana",
        "category": "Fruit Crops",
        "season": "Kharif",
        "soil_requirements": "Deep, well-drained loamy soil rich in organic matter. Optimal pH is 6.0 to 7.5. Extremely sensitive to soil waterlogging and high salinity.",
        "water_requirements": "High water requirement. Requires regular irrigation of 30-40 liters per plant per day. Provide drip irrigation. Ensure constant moisture but avoid standing water around the pseudostem.",
        "fertilizer_schedule": {
            "npk": "110:35:140 kg of N:P:K per acre",
            "application": [
                "Apply full Phosphorus dose as basal fertilizer during planting.",
                "Apply Nitrogen and Potassium in 4 equal splits at 2, 4, 6, and 8 months after planting.",
                "Apply Zinc Sulphate (0.5%) and Ferrous Sulphate (0.2%) as foliar sprays to boost plant vigour."
            ]
        },
        "growth_stages": {"vegetative": 120, "flowering": 240, "fruiting": 300, "harvesting": 360},
        "disease_information": "Panama Wilt (Fusarium oxysporum) and Sigatoka Leaf Spot. Sigatoka causes dark brown streaks on leaves. Control with propiconazole spray (1ml/L) and removing infected leaves.",
        "pest_management": "Pseudostem Weevil and Rhizome Weevil. Weevil larvae tunnel into rootstocks and stems. Control by keeping the basin clean and applying neem cake to the soil.",
        "harvest_information": "Harvest bunches when the ridges on the fruit surface become round and skin color turns from deep green to light green. Handle gently to prevent bruising."
    },
    {
        "name": "Papaya",
        "category": "Fruit Crops",
        "season": "Kharif",
        "soil_requirements": "Well-drained sandy loam or alluvial soil with pH between 6.0 and 6.5. Must have excellent drainage; water logging for even 24 hours can kill the root system.",
        "water_requirements": "Moderate to high water requirements. Irrigate every 8-10 days in winter and 6-8 days in summer. Drip irrigation is ideal. Avoid water contact with the stem trunk to prevent stem rot.",
        "fertilizer_schedule": {
            "npk": "100:100:200 kg of N:P:K per acre",
            "application": [
                "Apply NPK in monthly splits starting from the second month after transplanting.",
                "Incorporate well-rotted farmyard manure (FYM) and vermicompost at planting.",
                "Spray Borax (0.1%) during flowering to prevent fruit cracking."
            ]
        },
        "growth_stages": {"vegetative": 60, "flowering": 150, "fruiting": 210, "harvesting": 270},
        "disease_information": "Papaya Ring Spot Virus (PRSV), Damping-off, and Foot Rot. Ring Spot Virus is transmitted by aphids, causing mosaic symptoms. Control aphid vectors using yellow sticky traps and insecticidal soap sprays.",
        "pest_management": "Spider Mites, Whiteflies, and Aphids. Mites cause yellowing and dry webbing under leaves. Spray wettable sulphur (3g/L) for mite control.",
        "harvest_information": "Harvest fruits when they show yellow streaks on the green skin (color break stage). Cut with a sharp knife leaving a short stem. Store at 10-12 degrees Celsius."
    },
    {
        "name": "Mango",
        "category": "Fruit Crops",
        "season": "Kharif",
        "soil_requirements": "Deep, well-drained loamy soil with pH 5.5 to 7.5. Avoid alkaline, calcareous, or stony soils.",
        "water_requirements": "Moderate water requirements. Irrigate weekly for young trees, and every 10-15 days during fruit development for mature trees. Stop watering 2-3 weeks before flowering.",
        "fertilizer_schedule": {
            "npk": "80:40:80 kg of N:P:K per acre (for mature trees)",
            "application": [
                "Apply full dose of fertilizer in two splits: post-harvest pruning (June/July) and pre-monsoon (October).",
                "Apply organic manure (50kg per tree) annually.",
                "Foliar spray Zinc and Boron before flower bud initiation."
            ]
        },
        "growth_stages": {"vegetative": 60, "flowering": 120, "fruiting": 210, "harvesting": 270},
        "disease_information": "Powdery Mildew, Anthracnose, and Mango Malformation. Anthracnose causes black spots on leaves and fruit. Spray carbendazim (1g/L) to manage Anthracnose.",
        "pest_management": "Mango Hopper, Mealybugs, and Fruit Fly. Hoppers suck sap from inflorescence, causing flower drop. Spray neem formulations or imidacloprid during early panicle stage.",
        "harvest_information": "Harvest fruits when they are fully mature (shoulders outgrow the stalk). Pluck with stalk attached to prevent latex burn. Wipe latex off fruits."
    },
    {
        "name": "Pomegranate",
        "category": "Fruit Crops",
        "season": "Kharif",
        "soil_requirements": "Deep loam or sandy loam soil with pH 6.0 to 8.0. Tolerates slightly alkaline soil but requires excellent root zone drainage.",
        "water_requirements": "Low to moderate water requirement. Regular drip irrigation is necessary to prevent dry periods, which lead to severe fruit cracking.",
        "fertilizer_schedule": {
            "npk": "50:25:25 kg of N:P:K per acre",
            "application": [
                "Apply Nitrogen and Potassium in split doses during bahar treatment (flowering induction).",
                "Apply full Phosphorus dose basal during pruning.",
                "Apply micronutrients (Zinc and Boron) to reduce fruit splitting."
            ]
        },
        "growth_stages": {"vegetative": 45, "flowering": 90, "fruiting": 150, "harvesting": 210},
        "disease_information": "Bacterial Blight (Oily Spot disease) and Wilt. Bacterial blight causes black spots on leaves and fruits; prune affected stems and spray streptocycline (0.5g/L).",
        "pest_management": "Pomegranate Butterfly (Anar Butterfly), Thrips, and Aphids. Butterfly larvae bore into fruits. Bag young fruits or spray spinosad (0.5ml/L) to control.",
        "harvest_information": "Harvest fruits when skin turns yellowish-red, becomes hard, and produces a metallic sound when tapped. Avoid pulling fruits; cut using secateurs."
    },
    {
        "name": "Rose",
        "category": "Plantation Crops",
        "season": "Zaid",
        "soil_requirements": "Well-drained sandy loam soil rich in organic matter. Ideal pH is 6.0 to 6.5. Avoid heavy clay soils which restrict aeration.",
        "water_requirements": "Moderate water requirement. Irrigate twice a week in winter, and every alternate day in summer. Drip irrigation keeps foliage dry, preventing fungal diseases.",
        "fertilizer_schedule": {
            "npk": "40:40:40 kg of N:P:K per acre",
            "application": [
                "Apply well-rotted cow manure (FYM) post-pruning.",
                "Apply NPK split doses during vegetative and bud initiation stages.",
                "Apply magnesium sulphate and micronutrients to improve flower size and color."
            ]
        },
        "growth_stages": {"vegetative": 30, "flowering": 60, "fruiting": 90, "harvesting": 100},
        "disease_information": "Black Spot, Powdery Mildew, and Dieback. Dieback causes blackening of branches downwards from pruned ends. Apply copper oxychloride paste to pruned tips.",
        "pest_management": "Thrips, Aphids, and Red Spider Mites. Thrips cause brown scarring on flower petals. Control by spraying neem oil (5ml/L) or imidacloprid.",
        "harvest_information": "Harvest in the cool early morning or late evening. Cut flowers at the tight bud stage when color starts showing. Place stems immediately in clean water."
    },
    {
        "name": "Marigold",
        "category": "Plantation Crops",
        "season": "Kharif",
        "soil_requirements": "Well-drained loamy or sandy loam soil with pH 7.0 to 7.5. Tolerates a wide variety of soils but avoid waterlogged clay zones.",
        "water_requirements": "Low to moderate water requirements. Water weekly. Avoid overhead watering as it causes flower rot and damping-off.",
        "fertilizer_schedule": {
            "npk": "40:80:40 kg of N:P:K per acre",
            "application": [
                "Apply full Phosphorus dose and half of Nitrogen and Potassium as basal.",
                "Apply the remaining Nitrogen and Potassium 30 days after transplanting.",
                "Perform pinch-off (removing apical buds) to promote branching and flowering."
            ]
        },
        "growth_stages": {"vegetative": 30, "flowering": 60, "fruiting": 80, "harvesting": 90},
        "disease_information": "Damping-off of seedlings, Alternaria Leaf Spot, and Flower Bud Rot. Bud rot causes brown discoloration. Spray copper-based fungicides to control.",
        "pest_management": "Red Spider Mites and Aphids. Mites cause leaf yellowing and webbing. Spray wettable sulphur (2g/L) to control mites.",
        "harvest_information": "Harvest fully opened flowers when they achieve mature size. Harvest in mornings. Store in ventilated crates and keep cool."
    },
    {
        "name": "Jasmine",
        "category": "Plantation Crops",
        "season": "Zaid",
        "soil_requirements": "Well-drained sandy loam or clay loam soil with pH 6.5 to 7.5. Prefers soil rich in organic humus.",
        "water_requirements": "Moderate water requirement. Water twice a week during dry seasons and prune regularly to stimulate fresh shoots and flower buds.",
        "fertilizer_schedule": {
            "npk": "30:60:60 kg of N:P:K per acre",
            "application": [
                "Apply fertilizer in two equal splits: immediately after annual pruning (December/January) and during the peak monsoon.",
                "Apply compost and vermicompost around root basins.",
                "Use foliar iron sprays if leaves show chlorosis (yellowing)."
            ]
        },
        "growth_stages": {"vegetative": 40, "flowering": 80, "fruiting": 110, "harvesting": 120},
        "disease_information": "Leaf Blight and Rust. Leaf blight causes reddish-brown spots. Spray mancozeb (2g/L) for control.",
        "pest_management": "Bud Worm and Jasmine Leaf Folder. Bud worm larvae bore into jasmine buds making them turn pinkish and drop. Spray spinosad or neem formulations.",
        "harvest_information": "Harvest flower buds in the early morning (before sunrise) when they are white and fully developed but unopened. Keep buds cool to avoid browning."
    },
    {
        "name": "Chilli",
        "category": "Spices",
        "season": "Kharif",
        "soil_requirements": "Well-drained black soil or sandy loam soil rich in organic matter. Ideal pH range is 6.0 to 7.0. Very sensitive to waterlogging.",
        "water_requirements": "Moderate water requirements. Avoid water stress during flowering and fruit development stages, which causes flower drop and low pungency.",
        "fertilizer_schedule": {
            "npk": "60:30:30 kg of N:P:K per acre",
            "application": [
                "Apply 50% Nitrogen and full dose of Phosphorus and Potassium as basal dose.",
                "Apply remaining Nitrogen in two equal splits at 30 and 60 days after transplanting."
            ]
        },
        "growth_stages": {"vegetative": 35, "flowering": 75, "fruiting": 110, "harvesting": 140},
        "disease_information": "Damping-off, Powdery Mildew, and Chilli Leaf Curl Virus. Leaf curl virus is spread by whiteflies, causing leaves to curl upward and stunt plant growth. Control whiteflies.",
        "pest_management": "Thrips, Aphids, and Whiteflies. Thrips cause leaf edges to curl upwards. Spray neem oil (5ml/L) or fipronil to control.",
        "harvest_information": "Harvest green chillies when fully grown and firm. Harvest red chillies when they turn completely red. Dry red chillies in sun on clean sheets."
    },
    {
        "name": "Onion",
        "category": "Spices",
        "season": "Rabi",
        "soil_requirements": "Sandy loam or alluvial loamy soil with pH 6.0 to 7.0. Avoid heavy clay or stony soils that restrict bulb expansion.",
        "water_requirements": "Moderate water requirement. Needs regular irrigation every 7-10 days. Stop irrigation 10-15 days before harvesting to ensure long shelf life.",
        "fertilizer_schedule": {
            "npk": "40:20:30 kg of N:P:K per acre",
            "application": [
                "Apply half Nitrogen and full Phosphorus and Potassium as basal.",
                "Apply remaining Nitrogen 30 days after transplanting.",
                "Apply Sulphur (15kg/acre) to improve onion bulb pungency and quality."
            ]
        },
        "growth_stages": {"vegetative": 40, "flowering": 90, "fruiting": 120, "harvesting": 140},
        "disease_information": "Purple Blotch and Downy Mildew. Purple blotch causes purple concentric lesions on leaves. Spray mancozeb or copper oxychloride.",
        "pest_management": "Onion Thrips are the primary pest, causing silver streaks on leaves. Control with yellow sticky traps and neem oil sprays.",
        "harvest_information": "Harvest when 50-70% of the crop canopy falls over (neck fall stage). Pull out bulbs, cure in shade for 3-5 days, and trim tops before storing."
    },
    {
        "name": "Garlic",
        "category": "Spices",
        "season": "Rabi",
        "soil_requirements": "Well-drained rich loamy soil with pH 6.0 to 7.0. Heavy soils lead to deformed garlic bulbs and rot.",
        "water_requirements": "Moderate water requirements. Water every 8-10 days during vegetative growth. Reduce watering as bulbs mature and stop entirely 2 weeks before harvest.",
        "fertilizer_schedule": {
            "npk": "50:20:25 kg of N:P:K per acre",
            "application": [
                "Apply organic manure and full Phosphorus/Potassium as basal.",
                "Apply Nitrogen in two splits at 30 and 45 days after sowing.",
                "Sulphur application is essential to promote garlic bulb yield and flavor compounds."
            ]
        },
        "growth_stages": {"vegetative": 45, "flowering": 100, "fruiting": 130, "harvesting": 150},
        "disease_information": "White Rot and Purple Blotch. White rot causes root decay with white cottony mycelium. Ensure crop rotation and use healthy seed cloves.",
        "pest_management": "Thrips and Nematodes. Thrips suck sap from leaves causing silvering. Apply neem seed kernel extract (NSKE 5%) or dimethoate.",
        "harvest_information": "Harvest when leaves turn yellow-brown and start drying. Dig bulbs carefully, cure in dry shade for a week, and store in well-ventilated dry spaces."
    },
    {
        "name": "Turmeric",
        "category": "Spices",
        "season": "Kharif",
        "soil_requirements": "Sandy loam or clay loam soil rich in humus with pH 6.0 to 7.5. Requires highly porous soil to facilitate rhizome expansion.",
        "water_requirements": "High water requirement. Requires regular irrigation every 7-10 days. Very sensitive to water logging, which causes rhizome rot.",
        "fertilizer_schedule": {
            "npk": "50:25:50 kg of N:P:K per acre",
            "application": [
                "Apply full Phosphorus and half Potassium as basal dose.",
                "Apply Nitrogen and remaining Potassium in splits at 30, 60, and 90 days.",
                "Apply organic mulch to retain soil moisture and reduce weeds."
            ]
        },
        "growth_stages": {"vegetative": 60, "flowering": 120, "fruiting": 200, "harvesting": 240},
        "disease_information": "Rhizome Rot (Pythium species) and Leaf Spot. Rhizome rot causes leaves to turn yellow and roots to decay. Avoid waterlogging and drench soil with copper fungicides.",
        "pest_management": "Rhizome Scale and Shoot Borer. Shoot borer larvae tunnel into pseudostems causing leaf drying. Spray neem oil (0.5%) to manage.",
        "harvest_information": "Harvest when leaves turn dry and yellow-brown. Dig rhizomes carefully, boil in clean water for 45 minutes, dry in sun for 10-15 days, and polish."
    },
    {
        "name": "Groundnut",
        "category": "Oilseeds",
        "season": "Kharif",
        "soil_requirements": "Well-drained sandy loam or sandy soil with pH 6.0 to 6.5. Loose, sandy soil is critical for pegging (pods growing under the soil).",
        "water_requirements": "Low to moderate water requirement. Critical watering stages are flowering, pegging, and pod development. Avoid dry soils during pegging.",
        "fertilizer_schedule": {
            "npk": "10:20:30 kg of N:P:K per acre",
            "application": [
                "Apply all NPK as basal dose during sowing.",
                "Apply Gypsum (200kg/acre) at 40-45 days (pegging stage) to supply Calcium for pod shell formation.",
                "Apply Boron to prevent 'hollow-heart' disease in seeds."
            ]
        },
        "growth_stages": {"vegetative": 30, "flowering": 60, "fruiting": 90, "harvesting": 120},
        "disease_information": "Tikka Leaf Spot and Rust. Tikka spot causes small dark brown leaf lesions. Spray chlorothalonil or mancozeb to manage.",
        "pest_management": "Red Hairy Caterpillar, Leaf Miner, and Aphids. Red hairy caterpillars defoliate fields. Collect caterpillars manually and install light traps.",
        "harvest_information": "Harvest when leaves turn yellow and inner shell of pods shows blackish coloration. Pull out plants, dry pods in sun for 3-5 days to reduce moisture to 8%."
    },
    {
        "name": "Millets",
        "category": "Cereals",
        "season": "Kharif",
        "soil_requirements": "Highly resilient crop. Grows in sandy loam, gravelly, or marginal soils with pH 5.5 to 8.0. Sensitive to clay compaction.",
        "water_requirements": "Low water requirement. Extremely drought-resilient. Requires only 350-500mm of rainfall. Supplementary watering only during flowering if dry spells exceed 3 weeks.",
        "fertilizer_schedule": {
            "npk": "20:10:10 kg of N:P:K per acre",
            "application": [
                "Apply half Nitrogen and full Phosphorus and Potassium as basal.",
                "Apply remaining Nitrogen at active tillering (30 days after sowing).",
                "Apply organic compost or vermicompost to enrich marginal soils."
            ]
        },
        "growth_stages": {"vegetative": 30, "flowering": 60, "fruiting": 80, "harvesting": 95},
        "disease_information": "Downy Mildew (Green Ear disease) and Ergot. Ergot causes sticky sugary liquid on earheads, turning dark. Destroy infected earheads and practice crop rotation.",
        "pest_management": "Shoot Fly and Stem Borer. Shoot fly larvae cause 'dead-hearts' in young seedlings. Sow early and apply neem cake to soil.",
        "harvest_information": "Harvest when grains become hard, and moisture drops below 15%. Cut earheads first, thresh, clean, and dry grains to 10-12% moisture for safe storage."
    },
    {
        "name": "Cotton",
        "category": "Plantation Crops",
        "season": "Kharif",
        "soil_requirements": "Requires deep, well-drained black clayey or rich alluvial soil with pH between 6.0 and 8.0. Avoid waterlogged or quick-draining sandy soils.",
        "water_requirements": "Moderate water requirement. Drip irrigation is ideal. Critical watering stages are squaring, flowering, and boll development. Avoid waterlogging and excessive rainfall during maturity to prevent boll rot.",
        "fertilizer_schedule": {
            "npk": "40:20:20 kg of N:P:K per acre",
            "application": [
                "Apply full dose of Phosphorus and Potassium during sowing as basal.",
                "Apply Nitrogen in split doses: 1/3rd at sowing, 1/3rd at squaring (40-45 days), and 1/3rd at peak flowering (70-75 days).",
                "Spray Magnesium Sulphate (1%) and Potassium Nitrate (1-2%) during boll development to prevent leaf reddening."
            ]
        },
        "growth_stages": {"vegetative": 50, "flowering": 100, "fruiting": 140, "harvesting": 180},
        "disease_information": "Cotton Leaf Curl Virus, Bacterial Blight, and Root Rot. Leaf Curl Virus is transmitted by whiteflies; control by using resistant varieties and yellow sticky traps.",
        "pest_management": "Bollworms (American, Pink, Spotted), Whiteflies, Aphids, and Thrips. Install pheromone traps and spray NSKE (5%) or spinosad for bollworms.",
        "harvest_information": "Harvest when bolls are fully open and dry. Pick in dry weather and separate stained or damaged cotton. Store in clean, dry, well-ventilated rooms."
    }
]

# 2. Large category dictionaries to programmatically generate 200+ crops
CATEGORY_CROPS = {
    "Leafy Vegetables": [
        "Spinach", "Lettuce", "Kale", "Swiss Chard", "Arugula", "Bok Choy", "Mustard Greens", 
        "Collard Greens", "Watercress", "Parsley", "Dill", "Celery", "Basil", "Cabbage", "Cauliflower",
        "Broccoli", "Brussels Sprouts", "Endive", "Escarole", "Chard", "Cress", "Mizuna", "Tatsoi",
        "Sorrel", "Radicchio", "Asparagus", "Artichoke", "Fennel Leaves", "Turnip Greens", "Beet Greens"
    ],
    "Cereals": [
        "Rice", "Wheat", "Maize", "Barley", "Oats", "Sorghum", "Pearl Millet", "Finger Millet",
        "Foxtail Millet", "Kodo Millet", "Barnyard Millet", "Proso Millet", "Rye", "Triticale", "Teff",
        "Fonio", "Spelt", "Kamut", "Emmer", "Einkorn", "Wild Rice", "Quinoa", "Amaranth", "Buckwheat",
        "Job's Tears", "Canary Grass", "Durum Wheat", "Paddy", "Corn", "Rye Grass"
    ],
    "Pulses": [
        "Black Gram", "Green Gram", "Bengal Gram", "Pigeon Pea", "Lentil", "Peas", "Cowpea", "Horse Gram",
        "Chickpea", "Faba Bean", "Mung Bean", "Urad Bean", "Kidney Bean", "Lima Bean", "Adzuki Bean",
        "Broad Bean", "Soybean", "Sword Bean", "Velvet Bean", "Lupin", "Garbanzo", "Field Pea", 
        "Cluster Bean", "Winged Bean", "Jack Bean", "Bambara Groundnut", "Sword Pea", "Pigeon Pea White"
    ],
    "Oilseeds": [
        "Sunflower", "Safflower", "Sesame", "Linseed", "Castor", "Niger Seed", "Rapeseed", "Canola",
        "Cottonseed", "Flaxseed", "Mustard Seed", "Soybean Oilseed", "Chia Seed", "Safflower Seed",
        "Sunflower Seed", "Sesame Seed", "Castor Seed", "Linseed Seed", "Niger Seed Oil", "Hemp Seed"
    ],
    "Fruit Crops": [
        "Mango", "Banana", "Papaya", "Pomegranate", "Grape", "Guava", "Citrus", "Orange", "Mosambi", 
        "Apple", "Pear", "Peach", "Plum", "Apricot", "Almond", "Walnut", "Pineapple", "Jackfruit", 
        "Sapota", "Custard Apple", "Fig", "Amla", "Jamun", "Tamarind", "Watermelon", "Muskmelon",
        "Strawberry", "Blueberry", "Raspberry", "Blackberry", "Cranberry", "Cherry", "Kiwi", "Avocado", 
        "Lychee", "Dragon Fruit", "Clementine", "Grapefruit", "Lemon", "Lime", "Mandarin", "Mangosteen", 
        "Passion Fruit", "Persimmon", "Quince", "Rambutan", "Soursop", "Star Fruit", "Tangerine"
    ],
    "Spices": [
        "Chilli", "Onion", "Garlic", "Turmeric", "Ginger", "Cardamom", "Coriander", "Cumin", "Fennel", 
        "Fenugreek", "Black Pepper", "Cinnamon", "Clove", "Nutmeg", "Saffron", "Vanilla", "Allspice", 
        "Anise", "Asafoetida", "Bay Leaf", "Caraway", "Celery Seed", "Chervil", "Chives", "Cilantro", 
        "Dill Seed", "Horseradish", "Lemongrass", "Mace", "Marjoram", "Oregano", "Paprika", "Rosemary", 
        "Sage", "Savory", "Star Anise", "Tarragon", "Thyme"
    ],
    "Plantation Crops": [
        "Tea", "Coffee", "Rubber", "Coconut", "Areca nut", "Cashew", "Tobacco", "Jute", "Sisal", "Abaca",
        "Hemp", "Sugarcane", "Betel Vine", "Cocoa", "Date Palm", "Palmyra Palm", "Sago Palm", "Bamboo",
        "Rattan", "Mulberry", "Indigo", "Wattle", "Eucalyptus", "Poplar", "Arecanut", "Tea Bush", "Coffee Bush"
    ],
    "Medicinal Crops": [
        "Aloe Vera", "Ashwagandha", "Lemongrass Medicinal", "Mentha", "Holy Basil", "Neem", "Stevia", 
        "Giloy", "Brahmi", "Shatavari", "Aconite", "Arnica", "Belladonna", "Calendula", "Chamomile", 
        "Citronella", "Echinacea", "Feverfew", "Ginseng", "Lavender", "Lemon Balm", "Licorice", 
        "Milk Thistle", "Nettle", "Patchouli", "Peppermint", "Safed Musli", "Valerian", "Vetiver", "Yarrow"
    ]
}

# 3. Defaults & Templates per Category
CATEGORY_TEMPLATES = {
    "Leafy Vegetables": {
        "soil": "Requires well-drained sandy loam soil rich in organic matter. Optimal pH is 6.0 to 7.0.",
        "water": "Moderate water requirement. Needs uniform moisture; irrigate every 4-6 days, avoiding waterlogging.",
        "npk": "30:20:20 kg of N:P:K per acre",
        "application": [
            "Apply full dose of Phosphorus and Potassium and 50% Nitrogen during sowing/transplanting.",
            "Apply remaining Nitrogen in two split doses during the active vegetative growth phase.",
            "Supplement with micronutrient foliar sprays (Iron and Zinc) if chlorosis appears."
        ],
        "stages": {"vegetative": 30, "flowering": 50, "fruiting": 70, "harvesting": 80},
        "disease": "Downy Mildew, Damping-off, Leaf Spot. Spray copper-based fungicides if symptoms appear.",
        "pest": "Aphids, Caterpillars, Leaf Miners. Control using neem oil spray or yellow sticky traps.",
        "harvest": "Harvest early in the morning by cutting above soil level. Keep cool and store in well-ventilated crates."
    },
    "Cereals": {
        "soil": "Requires well-drained alluvial, loamy or clayey loam soil. Optimal soil pH is 6.0 to 7.5.",
        "water": "Moderate water requirement. Irrigate regularly during critical stages like tillering, flowering and grain filling.",
        "npk": "40:20:20 kg of N:P:K per acre",
        "application": [
            "Apply all Phosphorus and Potassium and half Nitrogen as basal dose during field preparation.",
            "Apply remaining Nitrogen in splits during the active growth and tillering phases.",
            "Supplement with organic compost or farmyard manure (FYM) to improve soil structure."
        ],
        "stages": {"vegetative": 35, "flowering": 75, "fruiting": 105, "harvesting": 130},
        "disease": "Rust, Blast, Smut. Spray systemic fungicides or remove infected parts to prevent spread.",
        "pest": "Stem Borer, Shoot Fly, Aphids. Manage by installing pheromone traps and spraying organic neem oil formulations.",
        "harvest": "Harvest when leaves dry and stalks turn brown. Thresh, clean, and dry grains below 12% moisture for storage."
    },
    "Pulses": {
        "soil": "Requires well-drained loamy or sandy loam soil. Optimal soil pH is 6.0 to 7.5. Sensitive to salinity.",
        "water": "Low water requirement. Drought-resilient. Irrigate at flowering and pod development stages.",
        "npk": "10:20:10 kg of N:P:K per acre",
        "application": [
            "Apply all NPK as a basal dose during sowing.",
            "Inoculate seeds with Rhizobium culture before sowing to enhance nitrogen fixation.",
            "Apply secondary nutrients (Sulphur) to increase seed yield."
        ],
        "stages": {"vegetative": 30, "flowering": 60, "fruiting": 90, "harvesting": 110},
        "disease": "Wilt, Root Rot, Powdery Mildew. Spray broad-spectrum fungicides and use resistant varieties.",
        "pest": "Pod Borer, Aphids, Whitefly. Use pheromone traps and spray spinosad or neem formulations.",
        "harvest": "Harvest when pods turn dry, yellow-brown. Hand pull or cut plants, dry in sun, and thresh."
    },
    "Oilseeds": {
        "soil": "Requires well-drained sandy loam or clay loam soil. Optimal soil pH is 6.0 to 7.5.",
        "water": "Low to moderate water requirement. Water at critical stages: flowering, pegging, and pod/seed filling.",
        "npk": "20:20:20 kg of N:P:K per acre",
        "application": [
            "Apply all Phosphorus, Potassium and 50% Nitrogen as basal dressing during sowing.",
            "Apply remaining Nitrogen 30 days after sowing.",
            "Apply Gypsum or Sulphur to boost oil content and improve pod shell strength."
        ],
        "stages": {"vegetative": 30, "flowering": 60, "fruiting": 90, "harvesting": 120},
        "disease": "Alternaria Blight, Tikka Leaf Spot, Rust. Spray Mancozeb or Chlorothalonil to manage.",
        "pest": "Aphids, Semi-looper, Caterpillar. Collect manually or spray neem seed kernel extract (NSKE 5%).",
        "harvest": "Harvest when leaves yellow and dry. Pull out plants, thresh, and dry pods/seeds in sun to 8% moisture."
    },
    "Fruit Crops": {
        "soil": "Requires deep, well-drained loamy or clay loam soil rich in organic humus. Optimal pH is 5.5 to 7.5.",
        "water": "Moderate to high water requirement. Regular drip irrigation is highly recommended. Avoid water stress during flowering.",
        "npk": "60:40:60 kg of N:P:K per acre (or per tree equivalent)",
        "application": [
            "Apply organic compost and full Phosphorus/Potassium as basal post-harvest pruning.",
            "Apply Nitrogen in splits: pre-flowering and post-fruit set.",
            "Foliar spray Zinc and Boron before flowering to improve fruit set and reduce cracking."
        ],
        "stages": {"vegetative": 60, "flowering": 120, "fruiting": 210, "harvesting": 270},
        "disease": "Anthracnose, Powdery Mildew, Canker. Prune affected branches and spray copper-based fungicides.",
        "pest": "Fruit Fly, Mealybugs, Thrips. Use yellow sticky traps, pheromone traps, and spray spinosad or neem oil.",
        "harvest": "Harvest when fruits achieve mature size and color break stage. Handle gently to prevent bruising."
    },
    "Spices": {
        "soil": "Requires rich, well-drained sandy loam or clay loam soil with high organic content. Optimal pH is 6.0 to 7.0.",
        "water": "Moderate water requirement. Water every 7-10 days depending on dry spells. Avoid waterlogging at root zones.",
        "npk": "30:20:30 kg of N:P:K per acre",
        "application": [
            "Apply full Phosphorus, Potassium and half Nitrogen basal during field preparation.",
            "Apply remaining Nitrogen in splits at 30, 60, and 90 days after planting.",
            "Apply Sulphur to enhance flavor, pungency, and compound concentration."
        ],
        "stages": {"vegetative": 45, "flowering": 90, "fruiting": 130, "harvesting": 150},
        "disease": "Rhizome Rot, Leaf Spot, Blight. Drench soil with copper fungicides; ensure proper field drainage.",
        "pest": "Thrips, Shoot Borer, Rhizome Scale. Control with yellow sticky traps and spraying neem oil.",
        "harvest": "Harvest when leaves turn yellow-brown and start drying. Dig rhizomes/bulbs carefully and cure in shade."
    },
    "Plantation Crops": {
        "soil": "Requires deep, well-drained forest loam, laterite, or alluvial soil. Optimal pH is 5.0 to 6.5.",
        "water": "High water requirement. Regularly irrigate, especially during dry months. Ensure excellent drainage.",
        "npk": "80:40:80 kg of N:P:K per acre (or per tree/bush equivalent)",
        "application": [
            "Apply fertilizer in two splits: post-monsoon (October) and pre-monsoon (May).",
            "Apply organic manure and oil cakes annually to enrich the root basin.",
            "Foliar spray secondary nutrients and trace elements to boost leaf/stem growth."
        ],
        "stages": {"vegetative": 120, "flowering": 240, "fruiting": 300, "harvesting": 365},
        "disease": "Leaf Rust, Root Rot, Blight. Prune and spray copper oxychloride or systemic fungicides.",
        "pest": "White Stem Borer, Berry Borer, Mealybugs. Install traps and use organic biological controls.",
        "harvest": "Harvest according to commodity guidelines (e.g., plucking buds/leaves, gathering pods, or nuts)."
    },
    "Medicinal Crops": {
        "soil": "Requires well-drained sandy loam, red loamy, or gravelly marginal soil. Optimal pH is 6.0 to 7.5.",
        "water": "Low water requirement. Highly drought-resilient. Avoid excessive irrigation, which causes root rot.",
        "npk": "15:15:15 kg of N:P:K per acre",
        "application": [
            "Apply all Phosphorus, Potassium and 50% Nitrogen as basal dressing.",
            "Apply remaining Nitrogen in monthly splits.",
            "Integrate organic vermicompost and farmyard manure (FYM) to maximize active compounds."
        ],
        "stages": {"vegetative": 40, "flowering": 80, "fruiting": 110, "harvesting": 120},
        "disease": "Root Rot, Seedling Blight. Avoid waterlogging and spray organic bio-fungicides (Trichoderma).",
        "pest": "Mites, Aphids, Whitefly. Manage by spraying neem oil (0.5%) or insecticidal soap.",
        "harvest": "Harvest at peak maturity of the active part (roots, leaves, stems). Dry in shade to preserve ingredients."
    }
}

# De-duplicate defined names
defined_names = {c["name"].lower() for c in CROP_DATA}

# 4. Generate all crops from categories
for category, crops_list in CATEGORY_CROPS.items():
    template = CATEGORY_TEMPLATES[category]
    for crop_name in crops_list:
        if crop_name.lower() in defined_names:
            # Update category on existing if needed
            for c in CROP_DATA:
                if c["name"].lower() == crop_name.lower():
                    c["category"] = category
            continue

        # Build entries
        CROP_DATA.append({
            "name": crop_name,
            "category": category,
            "season": "Kharif" if category in ["Cereals", "Pulses", "Oilseeds", "Plantation Crops", "Medicinal Crops"] else "Rabi",
            "soil_requirements": template["soil"],
            "water_requirements": template["water"],
            "fertilizer_schedule": {
                "npk": template["npk"],
                "application": template["application"]
            },
            "growth_stages": template["stages"],
            "disease_information": f"Common diseases affecting {crop_name} are {template['disease']}",
            "pest_management": f"Common pests affecting {crop_name} are {template['pest']}",
            "harvest_information": f"For {crop_name}, {template['harvest']}"
        })
        defined_names.add(crop_name.lower())

print(f"Total compiled crops: {len(CROP_DATA)}")

# 5. Output crop_profiles.json
crop_profiles = {}
for crop in CROP_DATA:
    crop_profiles[crop["name"].lower()] = crop

profiles_path = os.path.join(BACKEND_DIR, "crop_profiles.json")
with open(profiles_path, "w", encoding="utf-8") as f:
    json.dump(crop_profiles, f, ensure_ascii=False, indent=2)
print(f"Saved crop profiles dataset containing {len(crop_profiles)} crops to: {profiles_path}")

# 6. Output detailed RAG text files to documents/
for crop in CROP_DATA:
    name = crop["name"]
    filename = f"{name.lower().replace(' ', '_')}.txt"
    filepath = os.path.join(DOCS_DIR, filename)
    
    fert_bullets = "\n".join(f"- {b}" for b in crop["fertilizer_schedule"]["application"])
    
    content = f"""=== {name.upper()} CROP GUIDE ===

1. Fertilizers:
{name} requires balanced nutrient applications. Recommended dose is {crop['fertilizer_schedule']['npk']}.
Category: {crop['category']}
{fert_bullets}

2. Irrigation:
{name} irrigation and water requirements: {crop['water_requirements']}

3. Pest Management:
{name} pest management: {crop['pest_management']}

4. Growth Stages:
{name} has the following stage cycle durations:
- Vegetative Stage: Sowing up to {crop['growth_stages']['vegetative']} days.
- Flowering Stage: From {crop['growth_stages']['vegetative']} days to {crop['growth_stages']['flowering']} days.
- Fruiting Stage: From {crop['growth_stages']['flowering']} days to {crop['growth_stages']['fruiting']} days.
- Harvesting Stage: From {crop['growth_stages']['fruiting']} days onwards.

5. Harvesting:
{name} harvesting and post-harvest practices: {crop['harvest_information']}

6. Diseases:
{name} diseases: {crop['disease_information']}

7. Soil Requirements:
{name} soil requirements: {crop['soil_requirements']}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())
        
print(f"Programmatically generated {len(CROP_DATA)} crop guides in: {DOCS_DIR}")
