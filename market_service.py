import httpx
from typing import Dict, Any, List
import json
from datetime import datetime

class MarketService:
    def __init__(self):
        # Indian government APIs for market prices
        self.agmarknet_url = "https://api.data.gov.in/resource"
        
    async def get_market_prices(self, crop: str, state: str = "") -> Dict[str, Any]:
        """Get current market prices for crops in India"""
        try:
            # Mock market data - in production, integrate with actual APIs
            mock_prices = {
                "rice": {"price_per_quintal": 2100, "trend": "stable", "markets": ["Delhi", "Mumbai", "Kolkata"]},
                "wheat": {"price_per_quintal": 2050, "trend": "rising", "markets": ["Delhi", "Chandigarh", "Ludhiana"]},
                "cotton": {"price_per_quintal": 6800, "trend": "falling", "markets": ["Ahmedabad", "Mumbai", "Nagpur"]},
                "sugarcane": {"price_per_quintal": 350, "trend": "stable", "markets": ["Lucknow", "Pune", "Coimbatore"]},
                "tomato": {"price_per_quintal": 1500, "trend": "volatile", "markets": ["Bangalore", "Delhi", "Mumbai"]},
                "onion": {"price_per_quintal": 1200, "trend": "rising", "markets": ["Nashik", "Bangalore", "Delhi"]}
            }
            
            crop_lower = crop.lower()
            if crop_lower in mock_prices:
                return {
                    "crop": crop,
                    "data": mock_prices[crop_lower],
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "Market Intelligence"
                }
            else:
                return {"error": f"Price data not available for {crop}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_profitability(self, crop: str, area_acres: float, investment: float) -> Dict[str, Any]:
        """Calculate crop profitability for Indian farmers"""
        try:
            # Average yields per acre for different crops in India
            avg_yields = {
                "rice": 25,  # quintals per acre
                "wheat": 20,
                "cotton": 8,
                "sugarcane": 300,
                "tomato": 150,
                "onion": 120
            }
            
            # Get current market price
            crop_lower = crop.lower()
            if crop_lower not in avg_yields:
                return {"error": "Crop data not available"}
            
            # Mock calculation
            yield_per_acre = avg_yields[crop_lower]
            total_yield = yield_per_acre * area_acres
            
            # Assume current price (this would come from market API)
            price_per_quintal = {
                "rice": 2100, "wheat": 2050, "cotton": 6800,
                "sugarcane": 350, "tomato": 1500, "onion": 1200
            }.get(crop_lower, 1000)
            
            gross_income = total_yield * price_per_quintal
            net_profit = gross_income - investment
            profit_margin = (net_profit / investment) * 100 if investment > 0 else 0
            
            return {
                "crop": crop,
                "area_acres": area_acres,
                "expected_yield_quintals": total_yield,
                "price_per_quintal": price_per_quintal,
                "gross_income": gross_income,
                "investment": investment,
                "net_profit": net_profit,
                "profit_margin_percent": round(profit_margin, 2),
                "roi_months": 6 if crop_lower in ["rice", "wheat"] else 4
            }
            
        except Exception as e:
            return {"error": str(e)}
