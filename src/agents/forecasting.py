import pandas as pd
import json
import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from sambanova import SambaNova

load_dotenv()

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0
# )

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# client = SambaNova(
#     api_key=os.getenv("SAMBA_API_KEY"),
#    base_url="https://api.sambanova.ai/v1",
# )

PROMPT = PromptTemplate(
        input_variables=["store", "sku", "history"],
        template="""
    You are a retail demand forecasting expert.

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

def forecasting_agent(state):
    df = state["raw_data"]
    forecasts = []
    print("Starting forecasting...")
    print(f"Total store-SKU combinations to forecast: {df[['store_id', 'sku_id']].drop_duplicates().shape[0]}")
    for (store, sku), g in df.groupby(["store_id", "sku_id"]):
        # if len(forecasts) >= 5 * 7:  # 5 items × 7 days each
        #     break
        recent = g.sort_values("date").tail(30)

        history_text = "\n".join(
            f"{row.date.date()}: {int(row.units_sold)}"
            for _, row in recent.iterrows()
        )

        prompt = PROMPT.format(
            store=store,
            sku=sku,
            history=history_text
        )

        response = llm.invoke(prompt).content
        print(response)

        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                forecast_json = json.loads(json_str)
            else:
                continue
        except Exception:
            continue

        for i, qty in enumerate(forecast_json.values(), start=1):
            forecasts.append({
                "store_id": store,
                "sku_id": sku,
                "horizon_day": i,
                "forecast": max(0, float(qty))
            })
    print("Forecasting completed.")
    print(f"Generated forecasts for {len(forecasts)} store-SKU combinations.")
    print(forecasts)  # Print first 5 forecasts for verification
    return {"forecasts": pd.DataFrame(forecasts)}

