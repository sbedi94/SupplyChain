"""
Phase 1: Enhanced Demand Forecasting Agent
- Inputs: Historical sales, seasonality detection
- Output: SKU * Store demand forecast
- Tools: Cached forecast, Fallback logic (Scenario 3)
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from src.tools.forecast_cache import ForecastCache, FallbackForecaster
from src.rag.retriever import get_supplier_context
from src.llm.provider import llm

load_dotenv()

# Initialize LLM
#api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
#api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
#if not api_key:
#    raise ValueError("Google API key not found")

#llm = llm[].format(api_key)

# Initialize cache
forecast_cache = ForecastCache(ttl_hours=24)

PROMPT = PromptTemplate(
    input_variables=["store", "sku", "history"],
    template="""
You are a retail demand forecasting expert.

Context:
{context}

Store: {store}
SKU: {sku}

Below is the last 30 days of daily sales:
{history}

Task:
1. Identify trend and seasonality if any
2. Forecast demand for the next 7 days
3. Return ONLY valid JSON like:

{{
"day_1": 10,
"day_2": 11,
"day_3": 12,
"day_4": 12,
"day_5": 13,
"day_6": 13,
"day_7": 14
}}
"""
)


def detect_seasonality(history: pd.DataFrame) -> Dict:
    """
    Detect seasonality patterns in historical data
    
    Scenario 1: Black Friday surge detection
    Scenario 2: Weekly patterns
    """
    if history.empty or len(history) < 7:
        return {"pattern": "insufficient_data", "confidence": 0}
    
    # Calculate day-of-week averages
    history = history.copy()
    history["dow"] = history["date"].dt.dayofweek
    dow_avg = history.groupby("dow")["units_sold"].mean()
    dow_std = dow_avg.std()
    
    # Calculate week-over-week patterns
    history["week"] = history["date"].dt.isocalendar().week
    weekly_avg = history.groupby("week")["units_sold"].mean()
    
    # Detect surge (values > mean + 2*std)
    mean_sales = history["units_sold"].mean()
    std_sales = history["units_sold"].std()
    surge_threshold = mean_sales + (2 * std_sales)
    surge_days = len(history[history["units_sold"] > surge_threshold])
    surge_ratio = surge_days / len(history) if len(history) > 0 else 0
    
    # Determine pattern
    if surge_ratio > 0.2:
        pattern = "surge_detected"
    elif dow_std > mean_sales * 0.2:
        pattern = "weekly_seasonality"
    else:
        pattern = "stable_demand"
    
    return {
        "pattern": pattern,
        "confidence": round(float(dow_std / mean_sales) if mean_sales > 0 else 0, 2),
        "mean_daily_sales": round(float(mean_sales), 2),
        "std_dev": round(float(std_sales), 2),
        "surge_ratio": round(surge_ratio, 3)
    }


def demand_forecasting_agent(state):
    """
    Enhanced Demand Forecasting Agent
    
    Scenario 1: Normal forecasting with cache & LLM
    Scenario 2: Seasonality detected - apply surge planning
    Scenario 3: LLM fails - fallback to statistical methods
    """
    
    df = state["raw_data"]
    forecasts = []
    alerts = []
    cache_stats = {"hits": 0, "misses": 0}
    
    print("\n" + "="*80)
    print("PHASE 1: DEMAND FORECASTING AGENT (Enhanced)")
    print("="*80)
    print(f"Total store-SKU combinations to forecast: {df[['store_id', 'sku_id']].drop_duplicates().shape[0]}")
    
    for (store, sku), g in df.groupby(["store_id", "sku_id"]):
        if len(forecasts) >= 5 * 7:  # Limit for demo
            break
        
        recent = g.sort_values("date").tail(30)
        
        # Detect seasonality (Scenario 2)
        seasonality_info = detect_seasonality(recent)
        if seasonality_info["pattern"] == "surge_detected":
            alerts.append(f"SEASONALITY: Store {store}, SKU {sku} - Surge pattern detected ({seasonality_info['surge_ratio']})")
        
        history_text = "\n".join(
            f"{row.date.date()}: {int(row.units_sold)}"
            for _, row in recent.iterrows()
        )
        
        # Check cache (Scenario 1: Cache Hit)
        cached_forecast = forecast_cache.get(str(store), str(sku), history_text)
        if cached_forecast:
            print(f"✓ CACHE HIT: Store {store}, SKU {sku}")
            cache_stats["hits"] += 1
            forecast_json = cached_forecast
        else:
            cache_stats["misses"] += 1
            context = get_supplier_context()
            print(f"→ Forecasting: Store {store}, SKU {sku} (Seasonality: {seasonality_info['pattern']})")
            
            prompt = PROMPT.format(
                store=store,
                sku=sku,
                history=history_text,
                context=context
            )
            
            try:
                # Try LLM forecasting
                response = llm.invoke(prompt).content
                
                # Extract JSON
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    forecast_json = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Cache the forecast
                forecast_cache.set(str(store), str(sku), history_text, forecast_json)
                print(f"✓ LLM Forecast successful - Cached")
                
            except Exception as e:
                # Scenario 3: Fallback logic
                print(f"✗ LLM Failed: {str(e)}")
                print(f"→ Using fallback statistical forecast for Store {store}, SKU {sku}")
                forecast_json = FallbackForecaster.statistical_forecast(recent, horizon=7)
                alerts.append(f"FALLBACK: Store {store}, SKU {sku} - Used statistical forecast")
        
        # Store forecasts
        for i, qty in enumerate(forecast_json.values(), start=1):
            forecasts.append({
                "store_id": store,
                "sku_id": sku,
                "horizon_day": i,
                "forecast": max(0, float(qty)),
                "seasonality_pattern": seasonality_info["pattern"]
            })
    
    print(f"\n✓ Forecasting completed")
    print(f"  - Generated forecasts: {len(forecasts)}")
    print(f"  - Cache hits: {cache_stats['hits']}")
    print(f"  - Cache misses: {cache_stats['misses']}")
    print(f"  - Alerts: {len(alerts)}")
    
    return {
        "forecasts": pd.DataFrame(forecasts),
        "forecast_cache": forecast_cache.get_stats(),
        "forecast_alerts": alerts
    }
