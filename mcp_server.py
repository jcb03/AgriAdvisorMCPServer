import os
import base64
from io import BytesIO
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastmcp import FastMCP
from pydantic import BaseModel
from PIL import Image
from openai import OpenAI

from auth import verify_bearer_token, get_my_number
from weather_service import WeatherService
from market_service import MarketService
from crop_database import INDIAN_CROPS, INDIAN_STATES_CLIMATE, DISEASE_TREATMENTS

class CropAnalysisRequest(BaseModel):
    image_data: str  # base64 encoded image
    location: Optional[str] = "India"
    crop_type: Optional[str] = None

class WeatherRequest(BaseModel):
    city: str
    state: Optional[str] = ""
    crop: Optional[str] = None

class MarketAnalysisRequest(BaseModel):
    crop: str
    state: Optional[str] = ""
    area_acres: Optional[float] = 1.0
    investment: Optional[float] = 0

class PlantingScheduleRequest(BaseModel):
    location: str
    crops: List[str]
    farm_size_acres: Optional[float] = 1.0

class SustainablePracticesRequest(BaseModel):
    crop: str
    soil_type: Optional[str] = "loam"
    current_practices: Optional[List[str]] = []

# Initialize FastMCP
mcp = FastMCP("Smart Agriculture Advisory")

# Initialize services
weather_service = WeatherService()
market_service = MarketService()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# REQUIRED PUCH AI TOOLS 
@mcp.tool()
async def validate() -> str:
    """Validation tool required by Puch"""
    return get_my_number()

@mcp.tool() 
async def about() -> Dict[str, str]:
    """About tool required by Puch AI - returns server metadata"""
    return {
        "name": "Smart Agriculture Advisor",
        "description": "AI-powered agricultural assistant for Indian farmers. Provides crop disease analysis, weather recommendations, market insights, planting schedules, sustainable farming practices, and personalized farming calendars. Supports Hindi language and focuses on Indian crops and agricultural conditions."
    }

# 🌾 AGRICULTURE TOOLS - SIMPLIFIED SIGNATURES
@mcp.tool()
async def analyze_crop_disease(
    image_data: str,
    location: str = "India", 
    crop_type: str = ""
) -> str:
    """
    Analyze crop photos for disease identification and treatment suggestions.
    Tailored for Indian crops and farming conditions.
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Prepare the image for OpenAI Vision API
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Create prompt for Indian agriculture context
        prompt = f"""
You are an expert agricultural pathologist specializing in Indian crops. 
Analyze this crop image and provide:

1. Crop identification (if not specified: {crop_type})
2. Disease/pest identification with confidence level
3. Severity assessment (mild/moderate/severe)
4. Treatment recommendations (both chemical and organic)
5. Prevention measures
6. Cost-effective solutions suitable for Indian farmers
7. Immediate actions needed

Location context: {location}

Provide response in both English and Hindi for key recommendations.
Focus on solutions available in Indian agricultural markets.
"""
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        analysis = response.choices[0].message.content
        
        return f"""
🔍 **Crop Disease Analysis**

📍 Location: {location}
🌱 Crop: {crop_type or 'Auto-detected'}

{analysis}

🏥 **Next Steps:**
- Follow treatment recommendations immediately
- Monitor crop closely for 7-10 days
- Contact local agricultural extension officer if needed
- Take preventive measures for other plants

Built with ❤️ for Indian farmers 🌾
"""
        
    except Exception as e:
        return f"❌ Error analyzing crop disease: {str(e)}"

@mcp.tool()
async def get_weather_recommendations(
    city: str,
    state: str = "",
    crop: str = ""
) -> str:
    """
    Provide weather-based farming recommendations and irrigation scheduling
    for Indian agricultural regions.
    """
    try:
        # Get weather data
        weather_data = await weather_service.get_weather_data(city, state)
        
        if "error" in weather_data:
            return f"❌ Weather data unavailable for {city}, {state}. Using general recommendations."
        
        # Get irrigation recommendation
        irrigation_rec = weather_service.get_irrigation_recommendation(weather_data, crop or "general")
        
        # Generate comprehensive farming recommendations
        prompt = f"""
Based on the current weather conditions in {city}, {state}, provide farming recommendations:

Weather Data: {weather_data.get('current', {})}
Crop: {crop or 'general farming'}

Provide recommendations for:
1. Irrigation schedule (in Hindi and English)
2. Field operations to perform/avoid
3. Disease/pest alerts for current weather
4. Fertilizer application timing
5. Harvesting decisions (if applicable)
6. Precautions for next 2-3 days

Focus on Indian farming practices and local conditions.
"""
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        recommendations = response.choices[0].message.content
        current = weather_data.get("current", {})
        
        return f"""
🌤️ **Weather-Based Farming Recommendations**

📍 Location: {city}, {state}
🌾 Crop: {crop or 'General farming'}

**Current Conditions:**
🌡️ Temperature: {current.get('temp', 'N/A')}°C
💧 Humidity: {current.get('humidity', 'N/A')}%
🌧️ Rain: {current.get('rain', {}).get('1h', 0)}mm

**Irrigation Advice:**
{irrigation_rec}

**Detailed Recommendations:**
{recommendations}

⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M IST')}
🌾 Built for Indian farmers
"""
        
    except Exception as e:
        return f"❌ Error getting weather recommendations: {str(e)}"

@mcp.tool()
async def get_market_analysis(
    crop: str,
    state: str = "",
    area_acres: float = 1.0,
    investment: float = 0
) -> str:
    """
    Offer market price predictions and crop profitability analysis
    for Indian agricultural markets.
    """
    try:
        # Get current market prices
        market_data = await market_service.get_market_prices(crop, state)
        
        # Calculate profitability
        profitability = market_service.calculate_profitability(crop, area_acres, investment)
        
        # Generate AI market analysis
        prompt = f"""
Provide comprehensive market analysis for {crop} cultivation in {state or 'India'}.

Current market data: {market_data}
Farm details: {area_acres} acres, investment: ₹{investment}

Analyze:
1. Price trends and seasonal patterns
2. Best selling periods
3. Market demand factors
4. Price risk mitigation strategies
5. Value addition opportunities
6. Government schemes and support
7. Export opportunities (if applicable)

Focus on Indian agricultural markets and policies.
"""
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        market_analysis = response.choices[0].message.content
        
        # Format profitability data
        profit_info = ""
        if 'error' not in profitability:
            profit_info = f"""
**Profitability Analysis:**
💰 Expected Income: ₹{profitability.get('gross_income', 'N/A')}
💵 Investment: ₹{investment}
📈 Net Profit: ₹{profitability.get('net_profit', 'N/A')}
📊 Profit Margin: {profitability.get('profit_margin_percent', 'N/A')}%
"""
        
        market_info = ""
        if 'data' in market_data:
            data = market_data['data']
            market_info = f"""
**Current Market Prices:**
💰 Price: ₹{data.get('price_per_quintal', 'N/A')}/quintal
📊 Trend: {data.get('trend', 'N/A')}
🏪 Markets: {', '.join(data.get('markets', [])[:3])}
"""
        
        return f"""
📈 **Market Analysis for {crop.title()}**

📍 Location: {state or 'India'}
📏 Farm Size: {area_acres} acres

{market_info}

{profit_info}

**AI Market Insights:**
{market_analysis}

⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M IST')}
🌾 Built for Indian farmers
"""
        
    except Exception as e:
        return f"❌ Error getting market analysis: {str(e)}"

@mcp.tool()
async def create_farming_calendar(
    location: str, 
    crops: List[str], 
    farm_size: float = 1.0
) -> str:
    """
    Create personalized farming calendars with seasonal activities
    for Indian agricultural regions.
    """
    try:
        current_date = datetime.now()
        current_month = current_date.month
        
        # Generate crop schedule
        schedule_info = []
        for crop in crops:
            crop_lower = crop.lower()
            if crop_lower in INDIAN_CROPS:
                crop_data = INDIAN_CROPS[crop_lower]
                
                # Determine next planting window
                planting_months = crop_data["planting_months"]
                next_planting = None
                
                for month in planting_months:
                    if month >= current_month:
                        next_planting = month
                        break
                
                if not next_planting:
                    next_planting = planting_months[0]  # Next year
                
                month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                
                schedule_info.append(f"""
🌾 **{crop.title()} ({crop_data['hindi_name']})**
   📅 Next Planting: {month_names[next_planting]}
   🔄 Season: {crop_data['seasons'][0].title()}
   🌾 Harvesting: {', '.join([month_names[m] for m in crop_data['harvesting_months']])}
   🌍 Suitable for {location}: {'✅' if location in crop_data.get('suitable_states', []) else '⚠️'}
""")
        
        # Generate AI recommendations
        prompt = f"""
Create a comprehensive farming calendar for a {farm_size} acre farm in {location}.

Crops to grow: {', '.join(crops)}
Current month: {current_month}

Provide:
1. Month-wise activity calendar
2. Crop rotation suggestions
3. Intercropping opportunities
4. Resource planning (seeds, fertilizer, labor)
5. Risk management strategies
6. Market timing advice

Focus on Indian farming practices and seasonal patterns.
"""
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        ai_insights = response.choices[0].message.content
        
        return f"""
📅 **Personalized Farming Calendar**

📍 Location: {location}
📏 Farm Size: {farm_size} acres
🌾 Crops: {', '.join(crops)}

**Crop Schedule:**
{''.join(schedule_info)}

**AI-Powered Insights:**
{ai_insights}

⏰ Generated: {current_date.strftime('%Y-%m-%d')}
🌾 Built for Indian farmers
"""
        
    except Exception as e:
        return f"❌ Error creating farming calendar: {str(e)}"

@mcp.tool()
async def help() -> str:
    """Get help and see all available Smart Agriculture tools"""
    return """
🌾 **Smart Agriculture Advisory - AI Farming Assistant for India**

**मुख्य सुविधाएं (Main Features):**

📸 **analyze_crop_disease** - फसल की तस्वीरों का विश्लेषण करें (Crop photo disease analysis)
🌤️ **get_weather_recommendations** - मौसम आधारित सिंचाई सुझाव (Weather-based irrigation advice)
📈 **get_market_analysis** - बाज़ार मूल्य और लाभ विश्लेषण (Market prices & profitability)
📅 **create_farming_calendar** - व्यक्तिगत खेती कैलेंडर (Personalized farming calendar)

**भारतीय फसलें (Supported Indian Crops):**
धान/चावल, गेहूं, कपास, गन्ना, टमाटर, प्याज और अन्य

**उपयोग कैसे करें (How to Use):**
1. WhatsApp पर Puch AI से जुड़ें
2. फसल की तस्वीर भेजें रोग विश्लेषण के लिए
3. "Delhi में धान के लिए मौसम सलाह" पूछें
4. "Punjab में गेहूं का market rate" जानें

**Example Commands:**
- "Analyze this crop disease" (with photo)
- "Weather advice for rice in Bihar"  
- "Market analysis for wheat in Punjab"
- "Create farming calendar for 5 acres"

**विशेषताएं (Features):**
✅ Indian Regional Languages + English support
✅ Indian weather data
✅ Regional market prices  
✅ Seasonal crop calendar
✅ Government scheme info

🚀 Built for Indian farmers with ❤️
🏆 #BuildWithPuch 
"""

@mcp.tool()
async def health() -> Dict[str, Any]:
    """Health check endpoint for monitoring and keep-alive"""
    return {
        "status": "healthy",
        "service": "AgriAdvisor MCP Server",
        "timestamp": datetime.now().isoformat(),
        "uptime": "server running",
        "tools_count": 7,
        "supported_crops": len(INDIAN_CROPS),
        "version": "1.0.0",
        "features": [
            "Crop Disease Analysis",
            "Weather Recommendations", 
            "Market Analysis",
            "Planting Schedule",
            "Farming Calendar"
        ]
    }

__all__ = ["mcp"]
