"""
Indian crop database with region-specific information
"""

INDIAN_CROPS = {
    "rice": {
        "hindi_name": "धान/चावल",
        "seasons": ["kharif"],
        "planting_months": [6, 7, 8],
        "harvesting_months": [10, 11, 12],
        "suitable_states": ["West Bengal", "Punjab", "Uttar Pradesh", "Andhra Pradesh", "Bihar"],
        "soil_type": "Clay loam, alluvial",
        "water_requirement": "High",
        "common_diseases": ["blast", "brown_spot", "sheath_blight"],
        "market_season": "November-February"
    },
    "wheat": {
        "hindi_name": "गेहूं",
        "seasons": ["rabi"],
        "planting_months": [11, 12, 1],
        "harvesting_months": [3, 4, 5],
        "suitable_states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh"],
        "soil_type": "Loam, clay loam",
        "water_requirement": "Medium",
        "common_diseases": ["rust", "smut", "bunt"],
        "market_season": "April-June"
    },
    "cotton": {
        "hindi_name": "कपास",
        "seasons": ["kharif"],
        "planting_months": [5, 6, 7],
        "harvesting_months": [10, 11, 12],
        "suitable_states": ["Gujarat", "Maharashtra", "Karnataka", "Andhra Pradesh"],
        "soil_type": "Black cotton soil",
        "water_requirement": "Medium",
        "common_diseases": ["bollworm", "leaf_curl", "root_rot"],
        "market_season": "November-February"
    },
    "sugarcane": {
        "hindi_name": "गन्ना",
        "seasons": ["annual"],
        "planting_months": [2, 3, 10, 11],
        "harvesting_months": [12, 1, 2, 3],
        "suitable_states": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu"],
        "soil_type": "Deep fertile loam",
        "water_requirement": "Very High",
        "common_diseases": ["red_rot", "smut", "wilt"],
        "market_season": "December-April"
    },
    "tomato": {
        "hindi_name": "टमाटर",
        "seasons": ["kharif", "rabi"],
        "planting_months": [6, 7, 11, 12],
        "harvesting_months": [9, 10, 2, 3],
        "suitable_states": ["Karnataka", "Uttar Pradesh", "Bihar", "West Bengal"],
        "soil_type": "Well-drained loam",
        "water_requirement": "Medium",
        "common_diseases": ["early_blight", "late_blight", "leaf_curl"],
        "market_season": "Year-round"
    },
    "onion": {
        "hindi_name": "प्याज",
        "seasons": ["rabi", "kharif"],
        "planting_months": [6, 7, 11, 12],
        "harvesting_months": [10, 11, 3, 4],
        "suitable_states": ["Maharashtra", "Karnataka", "Gujarat", "Uttar Pradesh"],
        "soil_type": "Well-drained loam",
        "water_requirement": "Medium",
        "common_diseases": ["purple_blotch", "downy_mildew", "basal_rot"],
        "market_season": "April-June, November-January"
    }
}

INDIAN_STATES_CLIMATE = {
    "Punjab": {"type": "subtropical", "rainfall": "medium", "temperature": "moderate"},
    "Haryana": {"type": "subtropical", "rainfall": "low", "temperature": "hot_dry"},
    "Uttar Pradesh": {"type": "subtropical", "rainfall": "medium", "temperature": "moderate"},
    "West Bengal": {"type": "tropical", "rainfall": "high", "temperature": "humid"},
    "Bihar": {"type": "subtropical", "rainfall": "medium", "temperature": "moderate"},
    "Gujarat": {"type": "arid", "rainfall": "low", "temperature": "hot_dry"},
    "Maharashtra": {"type": "tropical", "rainfall": "medium", "temperature": "moderate"},
    "Karnataka": {"type": "tropical", "rainfall": "medium", "temperature": "moderate"},
    "Tamil Nadu": {"type": "tropical", "rainfall": "medium", "temperature": "hot_humid"},
    "Andhra Pradesh": {"type": "tropical", "rainfall": "medium", "temperature": "hot_humid"}
}

DISEASE_TREATMENTS = {
    "blast": {
        "hindi_name": "ब्लास्ट रोग",
        "treatment": "Tricyclazole or Tebuconazole fungicide spray",
        "organic_treatment": "Neem oil spray, proper field drainage",
        "prevention": "Use resistant varieties, balanced fertilization"
    },
    "rust": {
        "hindi_name": "रस्ट रोग",
        "treatment": "Propiconazole or Mancozeb fungicide",
        "organic_treatment": "Copper oxychloride, garlic extract spray",
        "prevention": "Crop rotation, timely sowing"
    },
    "early_blight": {
        "hindi_name": "अर्ली ब्लाइट",
        "treatment": "Chlorothalonil or Metalaxyl spray",
        "organic_treatment": "Baking soda spray, neem oil",
        "prevention": "Proper spacing, drip irrigation"
    }
}
