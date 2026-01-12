from src.graph import build_graph
import json

print("\n" + "="*80)
print("SUPPLY CHAIN OPTIMIZATION PIPELINE - 4 PHASES")
print("="*80)

app = build_graph()
result = app.invoke({})

# Aggregate all alerts from all phases
all_alerts = []
all_alerts.extend(result.get("forecast_alerts", []))
all_alerts.extend(result.get("budget_alerts", []))
all_alerts.extend(result.get("supplier_alerts", []))
all_alerts.extend(result.get("capacity_alerts", []))

print("\n" + "="*80)
print("EXECUTIVE SUMMARY")
print("="*80)

# Display metrics
print("\n📊 METRICS:")
if result.get("metrics"):
    for key, value in result["metrics"].items():
        print(f"  - {key}: {value}")

# Display budget info
if result.get("budget_constraints"):
    budget = result["budget_constraints"]
    print(f"\n💰 BUDGET STATUS:")
    print(f"  - Budget Limit: ${budget.get('limit', 0):,.2f}")
    print(f"  - Total Cost: ${budget.get('total_cost', 0):,.2f}")
    print(f"  - Utilization: {budget.get('budget_utilization', 0)*100:.1f}%")
    print(f"  - Status: {'⚠️ OVERRUN' if budget.get('budget_exceeded') else '✓ COMPLIANT'}")

# Display all alerts
print(f"\n⚠️  SYSTEM ALERTS ({len(all_alerts)}):")
if all_alerts:
    for i, alert in enumerate(all_alerts, 1):
        print(f"  {i}. {alert}")
else:
    print("  ✓ No critical alerts")

# Display escalations
escalations = result.get("escalations", [])
if escalations:
    print(f"\n🔴 ESCALATIONS ({len(escalations)}):")
    for i, esc in enumerate(escalations, 1):
        print(f"  {i}. Supplier: {esc.get('supplier')}")
        print(f"     Reason: {esc.get('reason')}")
        print(f"     Severity: {esc.get('severity')}")
        print(f"     Action: {esc.get('action_required')}")

# Export final plan
if not result.get("final_inventory_plan").empty:
    result["final_inventory_plan"].to_excel(
        "final_inventory_plan.xlsx", index=False
    )
    print(f"\n✓ Final inventory plan exported to 'final_inventory_plan.xlsx'")

print(f"\nDecision: {result.get('human_decision', 'pending')}")
print("\n" + "="*80)
