import pandas as pd
#from src.tools.forecast_cache import ForecastCache, FallbackForecaster
from src.tools.cache_tools import load_cached_data, save_cached_data

def data_loader_agent(state):
    try:
        
        df = pd.read_excel("data/retail_demand_6_months.xlsx")
        df["date"] = pd.to_datetime(df["date"])
        save_cached_data(df)
        print("cache saved")
        return {"raw_data": df}

    except Exception:
        print("in exception")
        cached_data = load_cached_data()# or []
        print("data_loader df {}".format(cached_data))
        return {
            "raw_data": cached_data,
            "Alerts":["Using Cached data , possibility of Staleness"]
        }
