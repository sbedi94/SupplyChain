
import pandas as pd

def data_loader_agent(state):
    df = pd.read_excel("data/retail_demand_6_months.xlsx")
    df["date"] = pd.to_datetime(df["date"])
    return {"raw_data": df}
