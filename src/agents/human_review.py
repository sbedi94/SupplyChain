
import pandas as pd

def human_review_agent(state):
    df = state["inventory_plan"]
    print("\nHUMAN REVIEW REQUIRED")
    print(df)

    # Check if decision is already in state (from API)
    decision = state.get("human_decision")
    
    if not decision:
        # Only ask for input if running interactively (for CLI usage)
        print("Waiting for approval decision from API endpoint...")
        decision = "pending"  # Default to pending, wait for API
    
    decision = decision.lower() if decision else "pending"

    if decision == "approve":
        final = df
    elif decision == "modify":
        # For modify, we would need additional parameters from the API
        factor = state.get("adjustment_factor", 1.1)
        final = df.copy()
        final["recommended_order_qty"] = (
            final["recommended_order_qty"] * factor
        ).round(0)
    elif decision == "reject":
        final = pd.DataFrame()
    else:
        # Pending state - return empty until approved via API
        final = df

    return {
        "human_decision": decision,
        "final_inventory_plan": final
    }
