"""
Phase 4: Logistics & Capacity Agent
- Warehouse capacity management
- Shipment timing optimization
- Black Friday surge planning
"""

import pandas as pd
from src.tools.capacity_simulator import CapacitySimulator


def logistics_capacity_agent(state):
    """
    Logistics & Capacity Agent
    
    Scenarios:
    - Detect warehouse capacity constraints
    - Optimize shipment timing
    - Plan for Black Friday surge
    """
    
    inventory_plan = state["inventory_plan"]
    
    print("\n" + "="*80)
    print("PHASE 4: LOGISTICS & CAPACITY AGENT")
    print("="*80)
    
    alerts = []
    
    # Step 1: Display warehouse status
    print("\n→ Step 1: Warehouse Status Review")
    warehouse_df = CapacitySimulator.to_dataframe()
    print(warehouse_df.to_string(index=False))
    
    warehouse_capacity = warehouse_df.to_dict('records')
    
    # Step 2: Detect capacity constraints
    print(f"\n→ Step 2: Detecting Capacity Constraints...")
    constraints = CapacitySimulator.detect_capacity_constraints()
    
    if constraints:
        print(f"  ⚠ {len(constraints)} warehouse(s) near capacity:")
        for constraint in constraints:
            severity_symbol = "🔴" if constraint["severity"] == "HIGH" else "🟡"
            print(f"    {severity_symbol} {constraint['warehouse_name']}: "
                  f"{constraint['utilization_rate']*100:.1f}% utilization")
            alerts.append(
                f"CAPACITY: {constraint['warehouse_name']} - "
                f"Utilization {constraint['utilization_rate']*100:.1f}% ({constraint['severity']})"
            )
    else:
        print(f"  ✓ All warehouses have adequate capacity")
    
    # Step 3: Plan shipments
    print(f"\n→ Step 3: Planning Shipments...")
    total_quantity = inventory_plan["recommended_order_qty"].sum()
    print(f"  Total quantity to ship: {total_quantity:.0f} units")
    
    shipment_plan = CapacitySimulator.plan_shipments(int(total_quantity), horizon_days=7)
    
    if shipment_plan:
        print(f"  ✓ Shipment plan created ({len(shipment_plan)} warehouse(s)):")
        for shipment in shipment_plan:
            print(f"    - {shipment['warehouse_name']}: "
                  f"{shipment['quantity']} units in {shipment['shipments']} shipment(s) "
                  f"({shipment['estimated_days']} days)")
    else:
        alert_msg = "CRITICAL: Insufficient warehouse capacity for total demand"
        print(f"  ✗ {alert_msg}")
        alerts.append(alert_msg)
        shipment_plan = []
    
    # Step 4: Black Friday surge planning
    print(f"\n→ Step 4: Black Friday Surge Planning...")
    normal_demand = total_quantity
    surge_plan = CapacitySimulator.plan_black_friday_surge(int(normal_demand), surge_multiplier=5.0)
    
    print(f"  Normal Demand: {surge_plan['normal_demand']} units")
    print(f"  Black Friday Surge Demand ({surge_plan['surge_multiplier']}x): {surge_plan['surge_demand']} units")
    print(f"  Current Total Stock: {surge_plan['current_total_stock']} units")
    print(f"  Total Warehouse Capacity: {surge_plan['total_warehouse_capacity']} units")
    print(f"  Space Needed for Surge: {surge_plan['space_needed_for_surge']} units")
    
    if surge_plan['can_accommodate']:
        print(f"  ✓ {surge_plan['recommendation']}")
    else:
        alert_msg = (f"SURGE ALERT: {surge_plan['space_needed_for_surge']} additional units needed "
                    f"for Black Friday surge - {surge_plan['recommendation']}")
        print(f"  ⚠ {alert_msg}")
        alerts.append(alert_msg)
    
    # Step 5: Capacity-demand matching
    print(f"\n→ Step 5: Capacity-Demand Matching...")
    available_warehouses = CapacitySimulator.find_available_capacity(int(total_quantity))
    
    if available_warehouses:
        print(f"  ✓ Sufficient capacity found in {len(available_warehouses)} warehouse(s)")
        total_available = sum(w.available_capacity for w in available_warehouses)
        utilization_after = (total_quantity / total_available) * 100 if total_available > 0 else 0
        print(f"    Expected utilization post-allocation: {utilization_after:.1f}%")
    else:
        alert_msg = "CRITICAL: No warehouse with sufficient capacity for total demand"
        print(f"  ✗ {alert_msg}")
        alerts.append(alert_msg)
    
    print(f"\n✓ Logistics planning completed")
    print(f"  - Warehouses analyzed: {len(warehouse_df)}")
    print(f"  - Capacity constraints: {len(constraints)}")
    print(f"  - Shipment routes: {len(shipment_plan)}")
    print(f"  - Alerts: {len(alerts)}")
    
    return {
        "logistics_plan": pd.DataFrame(shipment_plan) if shipment_plan else pd.DataFrame(),
        "warehouse_capacity": warehouse_capacity,
        "capacity_alerts": alerts,
        "shipment_plan": pd.DataFrame(shipment_plan) if shipment_plan else pd.DataFrame(),
        "black_friday_plan": surge_plan
    }
