
from src.graph import build_graph

app = build_graph()
result = app.invoke({})

if "final_inventory_plan" in result:
    result["final_inventory_plan"].to_excel(
        "final_inventory_plan.xlsx", index=False
    )

print("Decision:", result.get("human_decision"))
print("Metrics:", result.get("metrics"))
