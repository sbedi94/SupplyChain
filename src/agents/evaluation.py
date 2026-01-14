
from sklearn.metrics import mean_absolute_percentage_error
from src.llm.provider import llm

def evaluation_agent(state):
    df = state["forecasts"]
    # Since we don't have actual future values, calculate summary statistics instead
    mean_forecast = float(df["forecast"].mean())
    std_forecast = float(df["forecast"].std())
    total_forecast = float(df["forecast"].sum())

    p90 = float(df["forecast"].quantile(0.9))
    p10 = float(df["forecast"].quantile(0.1))
    skew = float(df["forecast"].skew())

    prompt = f"""
        You are a senior demand planning analyst.

        Forecast distribution summary:
        - Mean: {mean_forecast:.2f}
        - Std Dev: {std_forecast:.2f}
        - P10: {p10:.2f}
        - P90: {p90:.2f}
        - Skewness: {skew:.2f}

        Answer ONLY in JSON:
        {{
        "confidence_adjustment": number between 0.85 and 1.15,
        "risk_comment": short phrase
        }}
    """
    try:
        llm_response = llm.invoke(prompt).content
        print("evaluation {}".format(llm_response))
        analysis = eval(llm_response)  # trusted internal LLM
        adjustment = float(analysis.get("confidence_adjustment", 1.0))
    except Exception:
        adjustment = 1.0
    
    adjusted_mean = mean_forecast * adjustment

    return {"metrics": {
        "mean_forecast": round(float(adjusted_mean), 2),
        "std_forecast": round(float(std_forecast), 2),
        "total_forecast": round(float(total_forecast), 2)
    }}
