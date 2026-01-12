
import pandas as pd

def human_review_agent(state):
    df = state["inventory_plan"]
    print("\nHUMAN REVIEW REQUIRED")
    print(df)

    decision = input("Decision (approve / modify / reject): ").lower()

    if decision == "approve":
        final = df
    elif decision == "modify":
        factor = float(input("Adjustment factor (e.g. 1.1): "))
        final = df.copy()
        final["recommended_order_qty"] = (
            final["recommended_order_qty"] * factor
        ).round(0)
    else:
        final = pd.DataFrame()

    return {
        "human_decision": decision,
        "final_inventory_plan": final
    }
