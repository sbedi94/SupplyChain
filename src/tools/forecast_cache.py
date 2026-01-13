"""
Forecast Caching Tool
- Prevents redundant API calls
- Stores historical forecasts
- Implements fallback logic for missing predictions
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import pandas as pd


class ForecastCache:
    """Cache manager for demand forecasts"""
    
    def __init__(self, ttl_hours: int = 24):
        """
        Initialize cache with TTL (Time To Live)
        
        Args:
            ttl_hours: How long to keep cached forecasts (default 24 hours)
        """
        self.cache = {}
        self.ttl_hours = ttl_hours
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, store_id: str, sku_id: str, history_data: str) -> str:
        """Generate cache key from store, SKU, and history"""
        cache_string = f"{store_id}_{sku_id}_{history_data}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, store_id: str, sku_id: str, history_data: str) -> Optional[Dict]:
        """
        Retrieve forecast from cache
        
        Returns:
            Forecast dict if found and not expired, None otherwise
        """
        key = self._generate_key(store_id, sku_id, history_data)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return entry["forecast"]
    
    def set(self, store_id: str, sku_id: str, history_data: str, forecast: Dict) -> None:
        """Store forecast in cache"""
        key = self._generate_key(store_id, sku_id, history_data)
        self.cache[key] = {
            "forecast": forecast,
            "expires_at": datetime.now() + timedelta(hours=self.ttl_hours),
            "created_at": datetime.now(),
            "store_id": store_id,
            "sku_id": sku_id
        }
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "total_requests": total,
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "cached_items": len(self.cache)
        }
    
    def clear(self) -> None:
        """Clear all cached forecasts"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class FallbackForecaster:
    """Fallback logic for when LLM forecasting fails (Scenario 3)"""
    
    @staticmethod
    def statistical_forecast(history: pd.DataFrame, horizon: int = 7) -> Dict:
        """
        Generate forecast using statistical methods (fallback)
        
        Scenario 3: When LLM fails, use:
        - Moving average
        - Trend extrapolation
        - Seasonality detection
        
        Args:
            history: DataFrame with date and units_sold columns
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with day_1 to day_N forecasts
        """
        if history.empty or len(history) < 7:
            # If insufficient data, return average
            avg = history["units_sold"].mean() if not history.empty else 10
            return {f"day_{i}": int(avg) for i in range(1, horizon + 1)}
        
        # Calculate moving average
        ma_7 = history["units_sold"].rolling(window=7, min_periods=1).mean().iloc[-1]
        
        # Calculate trend (last 7 days vs previous 7 days)
        if len(history) >= 14:
            recent = history["units_sold"].iloc[-7:].mean()
            previous = history["units_sold"].iloc[-14:-7].mean()
            trend = (recent - previous) / previous if previous > 0 else 0
        else:
            trend = 0
        
        # Calculate seasonality (today vs 7 days ago)
        if len(history) >= 7:
            today = history["units_sold"].iloc[-1]
            week_ago = history["units_sold"].iloc[-7]
            seasonality = (today - week_ago) / week_ago if week_ago > 0 else 0
        else:
            seasonality = 0
        
        # Generate forecasts with trend and seasonality
        forecasts = {}
        base = ma_7
        for i in range(1, horizon + 1):
            # Apply trend and slight seasonality decay
            adjustment = 1 + (trend * (i / horizon)) + (seasonality * 0.5)
            forecast_value = max(0, int(base * adjustment))
            forecasts[f"day_{i}"] = forecast_value
        
        return forecasts
    
    @staticmethod
    def simple_average_forecast(history: pd.DataFrame, horizon: int = 7) -> Dict:
        """Simple average forecast as last resort"""
        avg = int(history["units_sold"].mean()) if not history.empty else 10
        return {f"day_{i}": avg for i in range(1, horizon + 1)}
