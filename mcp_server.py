import os
import base64
from io import BytesIO
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastmcp import FastMCP
from pydantic import BaseModel
from PIL import Image
from openai import OpenAI

from auth import verify_bearer_token
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

# 👇 ADD THE HEALTH CHECK ENDPOINT HERE - RIGHT AFTER INITIALIZATION
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to test if server is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Smart Agriculture MCP Server is running! 🌾",
        "version": "1.0.0",
        "features": [
            "Crop Disease Analysis",
            "Weather Recommendations", 
            "Market Analysis",
            "Planting Schedule",
            "Sustainable Practices",
            "Farming Calendar"
        ],
        "supported_crops": list(INDIAN_CROPS.keys()),
        "server_info": {
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "bearer_token_configured": bool(os.getenv("BEARER_TOKEN")),
            "openai_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
    }

# 👇 OPTIONALLY ADD THESE DEBUG ENDPOINTS TOO
@mcp.tool()
async def test_openai_connection() -> Dict[str, Any]:
    """Test OpenAI API connection"""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": "Hello, this is a test for Indian agriculture server"}],
            max_tokens=50
        )
        return {
            "status": "success",
            "message": "OpenAI API working perfectly! ✅",
            "model_used": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "test_response": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"OpenAI API failed: {str(e)} ❌",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool() 
async def test_weather_apis() -> Dict[str, Any]:
    """Test all weather API connections"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    try:
        # Test with Delhi as default Indian city
        weather_data = await weather_service.get_weather_data("Delhi", "Delhi")
        results["tests"]["weather_service"] = {
            "status": "success" if "error" not in weather_data else "error",
            "data_source": weather_data.get("source", "unknown"),
            "sample_data": {
                "location": weather_data.get("location"),
                "has_current_data": "current" in weather_data,
                "has_forecast_data": "forecast" in weather_data
            }
        }
    except Exception as e:
        results["tests"]["weather_service"] = {
            "status": "error",
            "error": str(e)
        }
    
    return results

@mcp.tool()
async def analyze_crop_disease(request: CropAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze crop photos for disease identification and treatment suggestions.
    Tailored for Indian crops and farming conditions.
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_data)
        image = Image.open(BytesIO(image_data))
        
        # Prepare the image for OpenAI Vision API
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Create prompt for Indian agriculture context
        prompt = f"""
        You are an expert agricultural pathologist specializing in Indian crops. 
        Analyze this crop image and provide:
        
        1. Crop identification (if not specified: {request.crop_type})
        2. Disease/pest identification with confidence level
        3. Severity assessment (mild/moderate/severe)
        4. Treatment recommendations (both chemical and organic)
        5. Prevention measures
        6. Cost-effective solutions suitable for Indian farmers
        7. Immediate actions needed
        
        Location context: {request.location}
        
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
        
        # Extract disease name for treatment lookup
        disease_detected = None
        for disease in DISEASE_TREATMENTS.keys():
            if disease.lower() in analysis.lower():
                disease_detected = disease
                break
        
        treatment_info = {}
        if disease_detected:
            treatment_info = DISEASE_TREATMENTS[disease_detected]
        
        return {
            "analysis": analysis,
            "location": request.location,
            "crop_type": request.crop_type,
            "treatment_database": treatment_info,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@mcp.tool()
async def get_weather_recommendations(request: WeatherRequest) -> Dict[str, Any]:
    """
    Provide weather-based farming recommendations and irrigation scheduling
    for Indian agricultural regions.
    """
    try:
        # Get weather data
        weather_data = await weather_service.get_weather_data(request.city, request.state)
        
        if "error" in weather_data:
            return {"error": weather_data["error"], "success": False}
        
        # Get irrigation recommendation
        irrigation_rec = weather_service.get_irrigation_recommendation(weather_data, request.crop or "general")
        
        # Generate comprehensive farming recommendations
        prompt = f"""
        Based on the current weather conditions in {request.city}, {request.state}, provide farming recommendations:
        
        Weather Data: {weather_data.get('current', {})}
        Crop: {request.crop or 'general farming'}
        
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
        
        return {
            "location": f"{request.city}, {request.state}",
            "weather_data": weather_data["current"],
            "forecast": weather_data.get("forecast", {}),
            "irrigation_recommendation": irrigation_rec,
            "detailed_recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@mcp.tool()
async def calculate_planting_schedule(request: PlantingScheduleRequest) -> Dict[str, Any]:
    """
    Calculate optimal planting and harvesting times for different crops
    based on Indian agricultural seasons and regional conditions.
    """
    try:
        current_month = datetime.now().month
        schedule = {}
        
        for crop in request.crops:
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
                
                # Calculate harvesting months
                harvesting_months = crop_data["harvesting_months"]
                
                schedule[crop] = {
                    "hindi_name": crop_data["hindi_name"],
                    "season": crop_data["seasons"][0],
                    "next_planting_month": next_planting,
                    "harvesting_months": harvesting_months,
                    "suitable_for_location": request.location in crop_data.get("suitable_states", []),
                    "soil_requirement": crop_data["soil_type"],
                    "water_requirement": crop_data["water_requirement"],
                    "market_season": crop_data["market_season"]
                }
        
        # Generate AI recommendations
        prompt = f"""
        Create a comprehensive farming calendar for a {request.farm_size_acres} acre farm in {request.location}.
        
        Crops to grow: {', '.join(request.crops)}
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
        
        ai_recommendations = response.choices[0].message.content
        
        return {
            "location": request.location,
            "farm_size_acres": request.farm_size_acres,
            "crop_schedule": schedule,
            "ai_recommendations": ai_recommendations,
            "current_month": current_month,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@mcp.tool()
async def get_market_analysis(request: MarketAnalysisRequest) -> Dict[str, Any]:
    """
    Offer market price predictions and crop profitability analysis
    for Indian agricultural markets.
    """
    try:
        # Get current market prices
        market_data = await market_service.get_market_prices(request.crop, request.state)
        
        # Calculate profitability
        profitability = market_service.calculate_profitability(
            request.crop, 
            request.area_acres, 
            request.investment
        )
        
        # Generate AI market analysis
        prompt = f"""
        Provide comprehensive market analysis for {request.crop} cultivation in {request.state or 'India'}.
        
        Current market data: {market_data}
        Farm details: {request.area_acres} acres, investment: ₹{request.investment}
        
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
        
        return {
            "crop": request.crop,
            "location": request.state or "India",
            "current_market_data": market_data,
            "profitability_analysis": profitability,
            "market_insights": market_analysis,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@mcp.tool()
async def suggest_sustainable_practices(request: SustainablePracticesRequest) -> Dict[str, Any]:
    """
    Suggest sustainable farming practices based on soil and climate data
    suitable for Indian agriculture.
    """
    try:
        prompt = f"""
        Recommend sustainable farming practices for {request.crop} cultivation in India.
        
        Current details:
        - Crop: {request.crop}
        - Soil type: {request.soil_type}
        - Current practices: {', '.join(request.current_practices) if request.current_practices else 'Traditional farming'}
        
        Provide sustainable recommendations for:
        1. Soil health improvement
        2. Water conservation techniques
        3. Organic pest management
        4. Natural fertilizers and composting
        5. Crop diversification strategies
        6. Carbon footprint reduction
        7. Cost-effective implementation
        8. Government incentives available
        
        Focus on practices suitable for Indian climate and affordable for small farmers.
        Include both traditional Indian methods and modern sustainable techniques.
        """
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        sustainability_advice = response.choices[0].message.content
        
        # Add specific Indian sustainable practices
        indian_practices = {
            "water_conservation": [
                "Drip irrigation (ड्रिप सिंचाई)",
                "Rainwater harvesting (वर्षा जल संचयन)",
                "Mulching with crop residues"
            ],
            "soil_health": [
                "Vermicompost (केंचुआ खाद)",
                "Green manuring with dhaincha/sunhemp",
                "Crop rotation with legumes"
            ],
            "pest_management": [
                "Neem-based pesticides",
                "Pheromone traps",
                "Beneficial insects conservation"
            ],
            "government_schemes": [
                "PM-KISAN",
                "Soil Health Card Scheme",
                "Paramparagat Krishi Vikas Yojana (PKVY)"
            ]
        }
        
        return {
            "crop": request.crop,
            "soil_type": request.soil_type,
            "sustainability_recommendations": sustainability_advice,
            "indian_traditional_practices": indian_practices,
            "implementation_timeline": "3-6 months for basic practices, 1-2 years for complete transition",
            "expected_benefits": "20-30% cost reduction, improved soil health, better market prices for organic produce",
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

@mcp.tool()
async def create_farming_calendar(location: str, crops: List[str], farm_size: float = 1.0) -> Dict[str, Any]:
    """
    Create personalized farming calendars with seasonal activities
    for Indian agricultural regions.
    """
    try:
        current_date = datetime.now()
        calendar_data = {}
        
        # Generate 12-month calendar
        for month_offset in range(12):
            target_date = current_date + timedelta(days=30 * month_offset)
            month = target_date.month
            month_name = target_date.strftime("%B")
            
            monthly_activities = []
            
            # Check activities for each crop
            for crop in crops:
                crop_lower = crop.lower()
                if crop_lower in INDIAN_CROPS:
                    crop_data = INDIAN_CROPS[crop_lower]
                    
                    # Planting activities
                    if month in crop_data["planting_months"]:
                        monthly_activities.append({
                            "activity": "Planting/Sowing",
                            "crop": crop,
                            "hindi_name": crop_data["hindi_name"],
                            "details": f"Sow {crop} seeds, prepare field"
                        })
                    
                    # Harvesting activities
                    if month in crop_data["harvesting_months"]:
                        monthly_activities.append({
                            "activity": "Harvesting",
                            "crop": crop,
                            "hindi_name": crop_data["hindi_name"],
                            "details": f"Harvest {crop}, post-harvest processing"
                        })
            
            # General seasonal activities
            if month in [6, 7, 8]:  # Monsoon season
                monthly_activities.append({
                    "activity": "Monsoon Preparation",
                    "crop": "All crops",
                    "details": "Drainage maintenance, pest monitoring"
                })
            elif month in [10, 11, 12]:  # Post-monsoon
                monthly_activities.append({
                    "activity": "Rabi Preparation",
                    "crop": "Wheat, Mustard, Gram",
                    "details": "Field preparation for rabi crops"
                })
            
            calendar_data[month_name] = {
                "month": month,
                "activities": monthly_activities,
                "season": "Kharif" if month in [6, 7, 8, 9] else "Rabi" if month in [10, 11, 12, 1, 2, 3] else "Zaid"
            }
        
        # Generate AI-powered insights
        prompt = f"""
        Create a comprehensive farming calendar for {location} with the following crops: {', '.join(crops)}.
        Farm size: {farm_size} acres.
        
        Provide:
        1. Month-wise priority activities
        2. Labor requirement planning
        3. Input procurement schedule
        4. Weather-based contingency plans
        5. Market timing strategies
        6. Festival/seasonal considerations for Indian farmers
        
        Make it practical and actionable for Indian farmers.
        """
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        ai_insights = response.choices[0].message.content
        
        return {
            "location": location,
            "crops": crops,
            "farm_size_acres": farm_size,
            "calendar": calendar_data,
            "ai_insights": ai_insights,
            "created_date": current_date.isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

# Add authentication middleware
@mcp.add_middleware
async def auth_middleware(request, call_next):
    """Authentication middleware"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        if verify_bearer_token(token):
            return await call_next(request)
    
    from fastapi import HTTPException
    raise HTTPException(status_code=401, detail="Invalid authentication")

