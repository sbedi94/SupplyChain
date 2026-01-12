"""
Phase 3: Supplier & Procurement Agent
- Handles supplier outage detection
- Alternative sourcing
- Negotiation attempts
- Escalation when negotiation fails
"""

import pandas as pd
from typing import Dict, List, Tuple
from src.tools.supplier_database import SupplierDatabase, SupplierStatus


def supplier_procurement_agent(state):
    """
    Supplier & Procurement Agent
    
    Scenarios:
    - Detect supplier outages
    - Find alternative sourcing
    - Attempt negotiations
    - Escalate if negotiation fails
    """
    
    inventory_plan = state["inventory_plan"]
    
    print("\n" + "="*80)
    print("PHASE 3: SUPPLIER & PROCUREMENT AGENT")
    print("="*80)
    
    supplier_status = {}
    procurement_plan = []
    alerts = []
    escalations = []
    
    # Step 1: Detect supplier outages
    print("\n→ Step 1: Detecting supplier outages...")
    outaged_suppliers = SupplierDatabase.detect_outages()
    
    if outaged_suppliers:
        for supplier in outaged_suppliers:
            alerts.append(f"OUTAGE: {supplier.name} is currently in outage")
            print(f"  ⚠ {supplier.name} (ID: {supplier.supplier_id}) - Status: OUTAGE")
    else:
        print("  ✓ No active outages detected")
    
    # Display all suppliers
    print(f"\n→ Supplier Status:")
    suppliers_df = SupplierDatabase.to_dataframe()
    print(suppliers_df.to_string(index=False))
    
    supplier_status = suppliers_df.to_dict('records')
    
    # Step 2: Process inventory requirements
    print(f"\n→ Step 2: Processing procurement for {len(inventory_plan)} items...")
    
    total_quantity_needed = inventory_plan["recommended_order_qty"].sum()
    
    for idx, row in inventory_plan.iterrows():
        store_id = row["store_id"]
        sku_id = row["sku_id"]
        qty_needed = row["recommended_order_qty"]
        
        # Primary supplier (S001 - Premium Supplies)
        primary_supplier_id = "S001"
        primary_supplier = SupplierDatabase.get_supplier(primary_supplier_id)
        
        procurement_entry = {
            "store_id": store_id,
            "sku_id": sku_id,
            "qty_needed": qty_needed,
            "primary_supplier": primary_supplier.name,
            "primary_supplier_status": primary_supplier.status.value,
            "supplier_cost": row["unit_cost"],
            "total_cost": row["total_cost"],
            "procurement_status": "pending"
        }
        
        # Step 3: Check supplier availability & alternative sourcing
        if primary_supplier.status == SupplierStatus.OUTAGE:
            print(f"  ⚠ Store {store_id}, SKU {sku_id}: Primary supplier in outage")
            
            # Find alternatives
            alternatives = SupplierDatabase.find_alternatives(primary_supplier_id, qty_needed)
            
            if alternatives:
                print(f"    → Found {len(alternatives)} alternative supplier(s)")
                
                # Select best alternative based on reliability & cost
                selected = alternatives[0]
                procurement_entry["alternative_supplier"] = selected.name
                procurement_entry["alternative_supplier_id"] = selected.supplier_id
                procurement_entry["alternative_cost"] = selected.cost_per_unit
                procurement_entry["procurement_status"] = "sourced_from_alternative"
                
                alerts.append(
                    f"ALTERNATIVE SOURCING: Store {store_id}, SKU {sku_id} - "
                    f"Using {selected.name} (Lead time: {selected.lead_time_days}d)"
                )
                print(f"      ✓ Selected alternative: {selected.name}")
            else:
                print(f"    ✗ No alternative suppliers found")
                alerts.append(f"CRITICAL: Store {store_id}, SKU {sku_id} - No alternative suppliers")
                procurement_entry["procurement_status"] = "no_supplier"
        else:
            procurement_entry["alternative_supplier"] = None
            procurement_entry["procurement_status"] = "active_supplier"
        
        procurement_plan.append(procurement_entry)
    
    # Step 4: Negotiation & Escalation simulation
    print(f"\n→ Step 3: Negotiation Attempts...")
    
    # Scenario: Negotiate for emergency supply if outage detected
    if outaged_suppliers and len(inventory_plan) > 0:
        print(f"  → Attempting negotiation with {len(outaged_suppliers)} outaged supplier(s)...")
        
        for supplier in outaged_suppliers:
            negotiation_result = _attempt_negotiation(supplier)
            
            if negotiation_result["success"]:
                print(f"    ✓ Negotiation successful: {supplier.name}")
                alerts.append(f"NEGOTIATION: {supplier.name} - Partial supply arranged ({negotiation_result['qty']} units)")
            else:
                print(f"    ✗ Negotiation failed: {supplier.name}")
                
                # Step 5: Escalation
                escalation = {
                    "timestamp": pd.Timestamp.now(),
                    "supplier": supplier.name,
                    "supplier_id": supplier.supplier_id,
                    "reason": "Supplier outage + negotiation failed",
                    "severity": "HIGH",
                    "action_required": "Management review required"
                }
                escalations.append(escalation)
                alerts.append(f"ESCALATION: {supplier.name} - Negotiation failed, requires management review")
                print(f"      → ESCALATING to management...")
    
    print(f"\n✓ Procurement planning completed")
    print(f"  - Items processed: {len(procurement_plan)}")
    print(f"  - Total quantity: {total_quantity_needed:.0f} units")
    print(f"  - Alerts: {len(alerts)}")
    print(f"  - Escalations: {len(escalations)}")
    
    return {
        "supplier_status": supplier_status,
        "procurement_plan": pd.DataFrame(procurement_plan),
        "supplier_alerts": alerts,
        "escalations": escalations
    }


def _attempt_negotiation(supplier) -> Dict:
    """
    Simulate negotiation with supplier
    
    Scenario 5: Negotiation attempt
    """
    import random
    
    supplier.negotiation_attempts += 1
    
    # Success probability based on reliability score and negotiation attempts
    base_success_rate = supplier.reliability_score / 100
    attempt_penalty = 0.1 * supplier.negotiation_attempts  # Penalty for repeated attempts
    success_probability = max(0.1, base_success_rate - attempt_penalty)
    
    if random.random() < success_probability:
        # Negotiation successful - can supply emergency qty
        emergency_qty = supplier.capacity * 0.3  # 30% of capacity as emergency supply
        return {
            "success": True,
            "qty": int(emergency_qty),
            "cost_adjustment": 1.2  # 20% premium for emergency supply
        }
    else:
        return {
            "success": False,
            "qty": 0,
            "cost_adjustment": 1.0
        }
