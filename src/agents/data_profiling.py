
def data_profiling_agent(state):
    df = state["raw_data"]
    df = df.sort_values(["store_id", "sku_id", "date"])
    df["units_sold"] = df["units_sold"].clip(lower=0)
    return {"processed_data": df}
