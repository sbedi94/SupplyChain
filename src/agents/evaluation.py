
from sklearn.metrics import mean_absolute_percentage_error

def evaluation_agent(state):
    df = state["forecasts"]
    # Since we don't have actual future values, calculate summary statistics instead
    mean_forecast = df["forecast"].mean()
    std_forecast = df["forecast"].std()
    total_forecast = df["forecast"].sum()
    return {"metrics": {
        "mean_forecast": round(float(mean_forecast), 2),
        "std_forecast": round(float(std_forecast), 2),
        "total_forecast": round(float(total_forecast), 2)
    }}
