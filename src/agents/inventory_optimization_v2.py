"""
Phase 2: Inventory Optimization Agent (Budget-Aware)
- Inputs: Demand (from forecasting agent), budget constraints
- Output: Allocation plan with budget compliance
- Detects: Budget overrun (Scenario 4)
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Dict, List


def inventory_optimization_agent(state):
    """
    Budget-Aware Inventory Optimization Agent
    
    Scenario 4: Detect budget overrun and alert
    """
    
    df = state["forecasts"]
    alerts = []
    
    # Define budget constraints
    BUDGET_LIMIT = 100000  # Total inventory budget
    UNIT_COST = 50  # Cost per unit (simplified)
    
    print("\n" + "="*80)
    print("PHASE 2: INVENTORY OPTIMIZATION AGENT (Budget-Aware)")
    print("="*80)
    print(f"Total Budget: ${BUDGET_LIMIT:,.2f}")
    print(f"Unit Cost: ${UNIT_COST}")
    
    if df.empty or "store_id" not in df.columns or "sku_id" not in df.columns:
        print("✗ No forecast data available")
        return {
            "inventory_plan": pd.DataFrame(),
            "budget_constraints": {"limit": BUDGET_LIMIT, "cost_per_unit": UNIT_COST},
            "budget_alerts": ["No forecast data available"]
        }
    
    z = norm.ppf(0.95)  # 95% service level
    lead_time = 7
    rows = []
    total_cost = 0
    budget_exceeded = False
    
    for (store, sku), g in df.groupby(["store_id", "sku_id"]):
        mean_d = g["forecast"].mean()
        std_d = g["forecast"].std()
        
        # Calculate safety stock and ROP
        safety_stock = z * std_d * np.sqrt(lead_time)
        rop = mean_d * lead_time + safety_stock
        recommended_qty = rop
        
        # Scenario 4: Budget overrun detection
        item_cost = recommended_qty * UNIT_COST
        total_cost += item_cost
        
        # Check if budget exceeded
        cost_ratio = total_cost / BUDGET_LIMIT
        is_over_budget = cost_ratio > 1.0
        
        if is_over_budget and not budget_exceeded:
            budget_exceeded = True
            alerts.append(f"BUDGET ALERT: Total cost (${total_cost:,.2f}) exceeds budget of ${BUDGET_LIMIT:,.2f}")
        
        rows.append({
            "store_id": store,
            "sku_id": sku,
            "mean_daily_demand": round(mean_d, 2),
            "safety_stock": round(safety_stock, 2),
            "reorder_point": round(rop, 2),
            "recommended_order_qty": round(rop, 0),
            "unit_cost": UNIT_COST,
            "total_cost": round(item_cost, 2),
            "cost_ratio": round(cost_ratio, 3),
            "budget_compliant": not is_over_budget
        })
    
    inventory_df = pd.DataFrame(rows)
    
    # Calculate aggregate budget info
    total_cost = inventory_df["total_cost"].sum()
    avg_cost_ratio = total_cost / BUDGET_LIMIT
    compliant_items = len(inventory_df[inventory_df["budget_compliant"]])
    total_items = len(inventory_df)
    
    print(f"\n✓ Optimization completed")
    print(f"  - Items analyzed: {total_items}")
    print(f"  - Budget-compliant items: {compliant_items}/{total_items}")
    print(f"  - Total cost: ${total_cost:,.2f}")
    print(f"  - Budget utilization: {avg_cost_ratio*100:.1f}%")
    
    if budget_exceeded:
        print(f"  ⚠ BUDGET OVERRUN DETECTED!")
        
        # Scenario 4a: Implement cost reduction strategy
        print(f"\n→ Applying cost reduction strategy...")
        
        # Reduce safety stock to save costs
        reduction_factor = BUDGET_LIMIT / total_cost * 0.95  # 95% of budget
        
        for idx, row in inventory_df.iterrows():
            reduced_qty = row["recommended_order_qty"] * reduction_factor
            reduced_cost = reduced_qty * UNIT_COST
            inventory_df.at[idx, "recommended_order_qty"] = round(reduced_qty, 0)
            inventory_df.at[idx, "total_cost"] = round(reduced_cost, 2)
        
        new_total_cost = inventory_df["total_cost"].sum()
        alerts.append(f"COST REDUCTION: Reduced quantities by {(1-reduction_factor)*100:.1f}% to fit budget. New total: ${new_total_cost:,.2f}")
        print(f"  ✓ New total cost: ${new_total_cost:,.2f}")
    
    budget_constraints = {
        "limit": BUDGET_LIMIT,
        "cost_per_unit": UNIT_COST,
        "total_cost": round(float(total_cost), 2),
        "budget_utilization": round(float(avg_cost_ratio), 3),
        "budget_exceeded": budget_exceeded
    }
    
    print(f"  - Alerts: {len(alerts)}")
    
    return {
        "inventory_plan": inventory_df,
        "budget_constraints": budget_constraints,
        "budget_alerts": alerts
    }
