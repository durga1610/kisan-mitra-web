import os
import json

# Define the backend directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BACKEND_DIR, "documents")
os.makedirs(DOCS_DIR, exist_ok=True)

# List of 105 crops categorized with detailed agronomic guidelines
CROP_DATA = [
    # 1. Fruits
    {
        "name": "Grape",
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
    # 2. Flowers
    {
        "name": "Rose",
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
    # 3. Spices
    {
        "name": "Chilli",
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
    # 4. Oilseeds & Millets
    {
        "name": "Groundnut",
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

# Generate more crops to reach 105 crops
COMMON_CROPS_TEMPLATES = [
    # Grains & Cereals
    ("Rice", "alluvial or clayey", "high", "48:24:24", "Blast, Bacterial Leaf Blight", "Stem Borer, Leaf Folder", "monsoon", "transplanting"),
    ("Wheat", "clayey loam or alluvial", "moderate", "48:24:12", "Rust, Leaf Blight", "Termites, Aphids", "winter", "sowing"),
    ("Maize", "well-drained loam", "moderate", "48:24:20", "Downy Mildew, Leaf Blight", "Fall Armyworm, Stem Borer", "summer", "sowing"),
    ("Barley", "well-drained loam", "low", "24:12:12", "Rust, Powdery Mildew", "Aphids, Armyworms", "winter", "sowing"),
    ("Oats", "sandy loam", "moderate", "24:12:12", "Leaf Spot, Smut", "Aphids, Thrips", "winter", "sowing"),
    ("Sorghum", "loam to clay loam", "low", "30:15:15", "Grain Smut, Anthracnose", "Shoot Fly, Stem Borer", "monsoon", "sowing"),
    ("Pearl Millet", "sandy loam", "low", "20:10:10", "Downy Mildew, Ergot", "Shoot Fly, White Grubs", "monsoon", "sowing"),
    ("Finger Millet", "red loam", "low", "20:15:15", "Blast disease", "Stem Borer, Aphids", "monsoon", "transplanting"),
    ("Foxtail Millet", "sandy loam", "low", "15:10:10", "Blast, Rust", "Armyworm, Grasshopper", "monsoon", "sowing"),
    ("Kodo Millet", "poor marginal", "low", "15:10:10", "Head Smut", "Stem Borer", "monsoon", "sowing"),
    ("Barnyard Millet", "sandy loam", "low", "15:10:10", "Smut", "Shoot Fly", "monsoon", "sowing"),
    ("Proso Millet", "sandy loam", "low", "15:10:10", "Head Smut", "Aphids", "monsoon", "sowing"),
    
    # Pulses
    ("Black Gram", "loam or clayey", "low", "10:20:10", "Powdery Mildew, Leaf Spot", "Whitefly, Pod Borer", "monsoon", "sowing"),
    ("Green Gram", "sandy loam", "low", "10:20:10", "Yellow Mosaic Virus, Powdery Mildew", "Whitefly, Thrips", "summer", "sowing"),
    ("Bengal Gram", "sandy loam", "low", "10:25:10", "Wilt, Ascochyta Blight", "Pod Borer, Cutworm", "winter", "sowing"),
    ("Pigeon Pea", "well-drained loam", "low", "15:30:15", "Fusarium Wilt, Sterility Mosaic", "Pod Borer, Plume Moth", "monsoon", "sowing"),
    ("Lentil", "loamy or sandy", "low", "10:20:10", "Wilt, Rust", "Pod Borer, Aphids", "winter", "sowing"),
    ("Peas", "loamy", "moderate", "15:30:20", "Powdery Mildew, Rust", "Pod Borer, Leaf Miner", "winter", "sowing"),
    ("Cowpea", "sandy loam", "low", "10:20:10", "Mosaic Virus, Wilt", "Aphids, Pod Borer", "summer", "sowing"),
    ("Horse Gram", "marginal red/sandy", "low", "10:15:10", "Dry Root Rot", "Leaf Hopper", "monsoon", "sowing"),
    
    # Vegetables
    ("Tomato", "sandy loam to clayey", "moderate", "60:30:30", "Early Blight, Late Blight", "Fruit Borer, Whiteflies", "monsoon", "transplanting"),
    ("Potato", "sandy loam", "moderate", "48:24:36", "Late Blight, Early Blight", "Aphids, Potato Tuber Moth", "winter", "sowing"),
    ("Mustard", "sandy loam to alluvial", "low", "30:15:15", "White Rust, Alternaria Blight", "Aphids, Mustard Sawfly", "winter", "sowing"),
    ("Sugarcane", "deep clayey loam", "high", "120:60:60", "Red Rot, Smut", "Early Shoot Borer, Whitefly", "annual", "planting"),
    ("Soybean", "well-drained loam", "moderate", "10:30:20", "Rust, Yellow Mosaic", "Girdle Beetle, Tobacco Caterpillar", "monsoon", "sowing"),
    ("Ginger", "sandy loam to laterite", "high", "30:20:20", "Soft Rot, Leaf Spot", "Shoot Borer, Rhizome Scale", "annual", "planting"),
    ("Bitter Gourd", "sandy loam", "moderate", "20:30:30", "Downy Mildew, Powdery Mildew", "Fruit Fly, Epilachna Beetle", "summer", "sowing"),
    ("Bottle Gourd", "sandy loam", "moderate", "20:25:25", "Powdery Mildew, Mosaic", "Fruit Fly, Aphids", "summer", "sowing"),
    ("Ridge Gourd", "sandy loam", "moderate", "20:25:25", "Downy Mildew", "Fruit Fly, Mites", "summer", "sowing"),
    ("Sponge Gourd", "sandy loam", "moderate", "20:25:25", "Powdery Mildew", "Fruit Fly", "summer", "sowing"),
    ("Snake Gourd", "sandy loam", "moderate", "20:25:25", "Mosaic Virus", "Fruit Fly", "summer", "sowing"),
    ("Pumpkin", "loam to sandy loam", "moderate", "20:20:20", "Powdery Mildew", "Fruit Fly, Red Pumpkin Beetle", "summer", "sowing"),
    ("Cucumber", "sandy loam", "moderate", "30:20:30", "Downy Mildew", "Red Pumpkin Beetle, Fruit Fly", "summer", "sowing"),
    ("Watermelon", "sandy loam", "moderate", "40:30:30", "Fusarium Wilt, Bud Necrosis", "Red Pumpkin Beetle, Aphids", "summer", "sowing"),
    ("Muskmelon", "sandy loam", "moderate", "30:30:30", "Powdery Mildew", "Fruit Fly, Beetle", "summer", "sowing"),
    ("Okra", "sandy loam to loam", "moderate", "40:20:20", "Yellow Vein Mosaic Virus", "Shoot and Fruit Borer, Whitefly", "summer", "sowing"),
    ("Brinjal", "sandy loam to silt loam", "moderate", "60:40:30", "Phomopsis Blight, Little Leaf", "Shoot and Fruit Borer, Aphids", "monsoon", "transplanting"),
    ("Cabbage", "sandy loam to clay loam", "moderate", "60:40:40", "Black Rot, Club Root", "Diamondback Moth, Aphids", "winter", "transplanting"),
    ("Cauliflower", "sandy loam to clay loam", "moderate", "60:40:40", "Downy Mildew, Black Rot", "Diamondback Moth", "winter", "transplanting"),
    ("Spinach", "sandy loam", "moderate", "30:20:20", "Damping-off, Leaf Spot", "Aphids, Caterpillars", "winter", "sowing"),
    ("Radish", "sandy loam", "moderate", "20:20:20", "White Rust", "Aphids, Mustard Sawfly", "winter", "sowing"),
    ("Carrot", "deep sandy loam", "moderate", "30:30:40", "Alternaria Blight", "Rust Fly, Aphids", "winter", "sowing"),
    ("Beetroot", "sandy loam", "moderate", "30:40:40", "Leaf Spot", "Leaf Miner, Aphids", "winter", "sowing"),
    ("Sweet Potato", "sandy loam", "moderate", "20:20:40", "Scurf, Black Rot", "Sweet Potato Weevil", "monsoon", "planting"),
    ("Yam", "deep sandy loam", "moderate", "30:30:60", "Anthracnose", "Scale Insects", "monsoon", "planting"),
    ("Colocasia", "sandy loam", "high", "30:20:40", "Leaf Blight", "Aphids, Spider Mites", "monsoon", "planting"),
    ("Drumstick", "sandy loam to loam", "low", "60:60:60", "Twig Canker", "Bud Worm, Hairy Caterpillar", "annual", "planting"),
    ("Coriander Leaves", "sandy loam", "moderate", "20:20:20", "Powdery Mildew", "Aphids", "winter", "sowing"),
    ("Mint", "sandy loam to clay loam", "high", "20:10:10", "Rust", "Spider Mites", "summer", "planting"),
    
    # Flowers
    ("Marigold", "sandy loam", "moderate", "40:80:40", "Damping-off, Flower Rot", "Spider Mites, Thrips", "summer", "transplanting"),
    ("Jasmine", "sandy loam", "moderate", "30:60:60", "Leaf Blight, Rust", "Bud Worm, Jasmine Leaf Folder", "monsoon", "planting"),
    ("Chrysanthemum", "well-drained loam", "moderate", "40:40:40", "Leaf Spot, Wilt", "Aphids, Thrips", "winter", "transplanting"),
    ("Anthurium", "porous rich humus", "high", "10:10:20", "Bacterial Blight", "Thrips, Spider Mites", "annual", "planting"),
    ("Orchid", "bark/coconut fiber", "moderate", "10:10:10", "Root Rot, Black Rot", "Mealybugs, Scales", "annual", "planting"),
    ("Gerbera", "sandy loam", "high", "30:30:60", "Powdery Mildew, Root Rot", "Whitefly, Leaf Miner", "annual", "transplanting"),
    ("Carnation", "sandy loam", "moderate", "40:30:50", "Wilt, Rust", "Red Spider Mite, Thrips", "winter", "transplanting"),
    ("Gladiolus", "sandy loam", "moderate", "40:80:80", "Corm Rot", "Thrips, Cutworm", "winter", "planting"),
    ("Tuberose", "sandy loam", "moderate", "40:80:80", "Stem Rot", "Nematodes, Aphids", "summer", "planting"),
    
    # Cash Crops & Plantation
    ("Cardamom", "forest loamy", "high", "30:30:60", "Katte virus, Capsule Rot", "Thrips, Stem Borer", "annual", "planting"),
    ("Coriander", "sandy loam", "moderate", "15:15:10", "Powdery Mildew", "Aphids", "winter", "sowing"),
    ("Cumin", "sandy loam", "low", "15:15:10", "Wilt, Blight", "Aphids, Thrips", "winter", "sowing"),
    ("Fennel", "loam to sandy loam", "moderate", "20:20:15", "Stem Rot", "Aphids", "winter", "sowing"),
    ("Fenugreek", "loamy", "low", "15:20:10", "Powdery Mildew", "Aphids", "winter", "sowing"),
    ("Black Pepper", "laterite or loamy", "high", "40:40:80", "Quick Wilt, Foot Rot", "Pollu Beetle, Scale Insects", "annual", "planting"),
    ("Tea", "laterite acidic soil", "high", "60:30:30", "Blister Blight", "Tea Mosquito Bug, Red Crevice Mite", "annual", "planting"),
    ("Coffee", "laterite or volcanic loam", "high", "60:40:60", "Coffee Leaf Rust", "White Stem Borer, Berry Borer", "annual", "planting"),
    ("Rubber", "laterite acidic", "high", "30:30:30", "Abnormal Leaf Fall", "Scale Insects, Mealybugs", "annual", "planting"),
    ("Coconut", "sandy or loamy", "high", "500g:320g:1200g per tree", "Bud Rot, Stem Bleeding", "Rhinoceros Beetle, Red Palm Weevil", "annual", "planting"),
    ("Areca nut", "laterite or red loam", "high", "100g:40g:140g per tree", "Mahali fruit rot", "Spindle Bug, Yellow Leaf disease", "annual", "planting"),
    ("Cashew", "laterite or sandy", "low", "80:40:40", "Dieback, Root Rot", "Tea Mosquito Bug, Stem Borer", "annual", "planting"),
    ("Tobacco", "sandy loam", "moderate", "40:30:80", "Frog eye spot", "Budworm, Aphids", "winter", "transplanting"),
    ("Jute", "alluvial loamy", "high", "30:20:20", "Stem Rot", "Yellow Mite, Semilooper", "monsoon", "sowing"),
    
    # Fruits Continued
    ("Guava", "alluvial or loamy", "moderate", "40:30:40", "Wilt, Anthracnose", "Fruit Fly, Tea Mosquito Bug", "annual", "planting"),
    ("Citrus", "sandy loam", "moderate", "60:30:45", "Citrus Canker, Gummosis", "Citrus Psylla, Leaf Miner", "annual", "planting"),
    ("Orange", "well-drained loam", "moderate", "60:30:45", "Citrus Canker", "Fruit Sucking Moth, Psylla", "annual", "planting"),
    ("Mosambi", "well-drained loam", "moderate", "60:30:45", "Gummosis", "Leaf Miner, Psylla", "annual", "planting"),
    ("Apple", "loamy rich organic", "moderate", "40:30:60", "Apple Scab, Powdery Mildew", "Codling Moth, Woolly Aphid", "annual", "planting"),
    ("Pear", "loamy", "moderate", "30:20:40", "Fire Blight", "Psylla, Codling Moth", "annual", "planting"),
    ("Peach", "sandy loam", "moderate", "30:30:40", "Leaf Curl", "Aphids, Peach Borer", "annual", "planting"),
    ("Plum", "sandy loam", "moderate", "30:25:35", "Plum Pocket", "Aphids, Fruit Fly", "annual", "planting"),
    ("Apricot", "sandy loam", "moderate", "30:25:35", "Brown Rot", "Scale Insects", "annual", "planting"),
    ("Almond", "deep loamy", "moderate", "50:40:60", "Leaf Spot", "Spider Mites, Borers", "annual", "planting"),
    ("Walnut", "deep loamy silt", "moderate", "60:40:80", "Walnut Blight", "Codling Moth", "annual", "planting"),
    ("Pineapple", "sandy loam acidic", "high", "30:15:30", "Heart Rot", "Mealybugs", "annual", "planting"),
    ("Jackfruit", "deep alluvial or loam", "moderate", "50:30:50", "Fruit Rot", "Bud Borer, Shoot Borer", "annual", "planting"),
    ("Sapota", "alluvial or sandy loam", "moderate", "40:20:40", "Leaf Spot", "Chiku Bud Borer, Scale Insects", "annual", "planting"),
    ("Custard Apple", "sandy loam", "low", "30:30:30", "Anthracnose", "Mealybugs, Scale Insects", "annual", "planting"),
    ("Fig", "sandy loam", "low", "30:20:30", "Fig Rust", "Fig Fly, Borers", "annual", "planting"),
    ("Amla", "sandy loam or dry soils", "low", "30:30:30", "Rust", "Bark Eating Caterpillar", "annual", "planting"),
    ("Jamun", "deep loam alluvial", "moderate", "40:30:40", "Leaf Spot", "Fruit Fly", "annual", "planting"),
    ("Tamarind", "alluvial or poor soils", "low", "30:30:30", "Powdery Mildew", "Scale Insects, Borers", "annual", "planting"),
    
    # Medicinal & Aromatic
    ("Aloe Vera", "sandy loam", "low", "10:10:10", "Root Rot", "Mealybugs, Aphids", "summer", "planting"),
    ("Ashwagandha", "sandy loam or red soil", "low", "15:20:10", "Seedling Wilt", "Mites, Aphids", "monsoon", "sowing"),
    ("Lemongrass", "sandy loam or gravelly", "moderate", "20:20:20", "Leaf Blight", "Stem Borer", "monsoon", "planting"),
    ("Mentha", "sandy loam rich in organic", "high", "40:30:30", "Rust, Powdery Mildew", "Termites, Cutworm", "summer", "planting")
]

# De-duplicate template crops from custom list
defined_names = {c["name"].lower() for c in CROP_DATA}

for name, soil, water, npk_ratio, disease, pest, season_lbl, type_lbl in COMMON_CROPS_TEMPLATES:
    if name.lower() in defined_names:
        continue
    
    # Generate growth stages
    if type_lbl == "transplanting":
        stages = {"vegetative": 35, "flowering": 75, "fruiting": 105, "harvesting": 130}
    elif type_lbl == "planting":
        stages = {"vegetative": 50, "flowering": 100, "fruiting": 150, "harvesting": 180}
    else: # sowing
        stages = {"vegetative": 30, "flowering": 60, "fruiting": 90, "harvesting": 115}
        
    if season_lbl == "monsoon":
        season_val = "Kharif"
    elif season_lbl == "winter":
        season_val = "Rabi"
    elif season_lbl == "summer":
        season_val = "Zaid"
    else:
        season_val = "Kharif"
        
    CROP_DATA.append({
        "name": name,
        "season": season_val,
        "soil_requirements": f"Requires well-drained {soil} soil. Optimal soil pH is 6.0 to 7.5.",
        "water_requirements": f"{water.capitalize()} water requirement. Irrigate regularly during critical stages like flowering and pod development, avoiding waterlogging.",
        "fertilizer_schedule": {
            "npk": f"{npk_ratio} kg of N:P:K per acre",
            "application": [
                f"Apply all Phosphorus and Potassium and half Nitrogen as basal dose during field preparation.",
                f"Apply remaining Nitrogen in splits during the active growth and tillering phases.",
                f"Supplement with organic compost or farmyard manure (FYM) to improve soil structure."
            ]
        },
        "growth_stages": stages,
        "disease_information": f"Common diseases affecting {name} are {disease}. Spray systemic fungicides or remove infected parts to prevent spread.",
        "pest_management": f"Common pests are {pest}. Manage by installing pheromone traps and spraying organic neem oil formulations.",
        "harvest_information": f"Harvest when leaves dry and stalks turn brown. Thresh, clean, and dry grains or fruits to safe moisture levels (below 12%) before packaging."
    })
    defined_names.add(name.lower())

print(f"Total compiled crops: {len(CROP_DATA)}")

# 1. Output crop_profiles.json
crop_profiles = {}
for crop in CROP_DATA:
    crop_profiles[crop["name"].lower()] = crop

profiles_path = os.path.join(BACKEND_DIR, "crop_profiles.json")
with open(profiles_path, "w", encoding="utf-8") as f:
    json.dump(crop_profiles, f, ensure_ascii=False, indent=2)
print(f"Saved crop profiles dataset containing {len(crop_profiles)} crops to: {profiles_path}")

# 2. Output detailed RAG text files to documents/
for crop in CROP_DATA:
    name = crop["name"]
    filename = f"{name.lower().replace(' ', '_')}.txt"
    filepath = os.path.join(DOCS_DIR, filename)
    
    # Reformat fertilizer schedule bullets
    fert_bullets = "\n".join(f"- {b}" for b in crop["fertilizer_schedule"]["application"])
    
    content = f"""=== {name.upper()} CROP GUIDE ===

1. Fertilizers:
{name} requires balanced nutrient applications. Recommended dose is {crop['fertilizer_schedule']['npk']}.
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
