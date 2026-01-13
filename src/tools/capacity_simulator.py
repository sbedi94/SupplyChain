"""
Capacity Simulator Tool
- Warehouse capacity calculations
- Shipment timing optimization
- Black Friday surge planning
"""

import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Warehouse:
    """Warehouse information"""
    warehouse_id: str
    name: str
    location: str
    total_capacity: int  # Units
    current_utilization: int  # Units
    operating_days: int  # Days per week
    max_shipments_per_day: int
    
    @property
    def available_capacity(self) -> int:
        return self.total_capacity - self.current_utilization
    
    @property
    def utilization_rate(self) -> float:
        return self.current_utilization / self.total_capacity if self.total_capacity > 0 else 0


class CapacitySimulator:
    """Warehouse capacity and logistics simulation"""
    
    # Sample warehouses
    WAREHOUSES = {
        "W001": Warehouse(
            warehouse_id="W001",
            name="East Coast Hub",
            location="New Jersey",
            total_capacity=100000,
            current_utilization=65000,
            operating_days=7,
            max_shipments_per_day=500
        ),
        "W002": Warehouse(
            warehouse_id="W002",
            name="Central Hub",
            location="Texas",
            total_capacity=80000,
            current_utilization=55000,
            operating_days=7,
            max_shipments_per_day=400
        ),
        "W003": Warehouse(
            warehouse_id="W003",
            name="West Coast Hub",
            location="California",
            total_capacity=120000,
            current_utilization=90000,
            operating_days=7,
            max_shipments_per_day=600
        ),
        "W004": Warehouse(
            warehouse_id="W004",
            name="Regional Storage",
            location="Illinois",
            total_capacity=50000,
            current_utilization=48000,  # Near capacity
            operating_days=5,
            max_shipments_per_day=200
        ),
    }
    
    @classmethod
    def get_warehouse(cls, warehouse_id: str) -> Warehouse:
        """Get warehouse by ID"""
        return cls.WAREHOUSES.get(warehouse_id)
    
    @classmethod
    def get_all_warehouses(cls) -> List[Warehouse]:
        """Get all warehouses"""
        return list(cls.WAREHOUSES.values())
    
    @classmethod
    def find_available_capacity(cls, quantity: int) -> List[Warehouse]:
        """Find warehouses with available capacity"""
        available = []
        for warehouse in cls.get_all_warehouses():
            if warehouse.available_capacity >= quantity:
                available.append(warehouse)
        
        # Sort by available capacity (desc)
        available.sort(key=lambda x: -x.available_capacity)
        return available
    
    @classmethod
    def detect_capacity_constraints(cls) -> List[Dict]:
        """
        Detect warehouses near capacity (>80%)
        Scenario: Capacity alerts
        """
        constraints = []
        for warehouse in cls.get_all_warehouses():
            utilization = warehouse.utilization_rate
            if utilization > 0.8:
                constraint = {
                    "warehouse_id": warehouse.warehouse_id,
                    "warehouse_name": warehouse.name,
                    "utilization_rate": round(utilization, 3),
                    "available_capacity": warehouse.available_capacity,
                    "severity": "HIGH" if utilization > 0.95 else "MEDIUM"
                }
                constraints.append(constraint)
        
        return constraints
    
    @classmethod
    def plan_shipments(cls, total_qty: int, horizon_days: int = 7) -> List[Dict]:
        """
        Plan shipments considering warehouse capacity
        
        Scenario: Shipment timing optimization
        """
        warehouses = cls.get_all_warehouses()
        active_warehouses = [w for w in warehouses if w.operating_days >= 5]
        
        total_available = sum(w.available_capacity for w in active_warehouses)
        
        if total_available < total_qty:
            return None  # Cannot fulfill
        
        shipment_plan = []
        remaining_qty = total_qty
        
        for warehouse in sorted(active_warehouses, key=lambda x: -x.available_capacity):
            if remaining_qty <= 0:
                break
            
            qty_from_warehouse = min(remaining_qty, warehouse.available_capacity)
            shipments_needed = (qty_from_warehouse + warehouse.max_shipments_per_day - 1) // warehouse.max_shipments_per_day
            
            shipment_plan.append({
                "warehouse_id": warehouse.warehouse_id,
                "warehouse_name": warehouse.name,
                "location": warehouse.location,
                "quantity": int(qty_from_warehouse),
                "shipments": shipments_needed,
                "shipment_capacity": warehouse.max_shipments_per_day,
                "estimated_days": max(1, shipments_needed // max(1, warehouse.operating_days // 2))
            })
            
            remaining_qty -= qty_from_warehouse
        
        return shipment_plan if remaining_qty <= 0 else None
    
    @classmethod
    def plan_black_friday_surge(cls, normal_demand: int, surge_multiplier: float = 5.0) -> Dict:
        """
        Plan for Black Friday surge
        
        Scenario: Seasonal surge planning
        """
        surge_demand = int(normal_demand * surge_multiplier)
        
        # Pre-position inventory
        warehouses = cls.get_all_warehouses()
        total_capacity = sum(w.total_capacity for w in warehouses)
        total_current = sum(w.current_utilization for w in warehouses)
        
        space_needed_for_surge = surge_demand - (total_capacity - total_current)
        
        return {
            "normal_demand": normal_demand,
            "surge_multiplier": surge_multiplier,
            "surge_demand": surge_demand,
            "current_total_stock": total_current,
            "total_warehouse_capacity": total_capacity,
            "space_needed_for_surge": max(0, space_needed_for_surge),
            "can_accommodate": space_needed_for_surge <= 0,
            "pre_positioning_required": space_needed_for_surge > 0,
            "recommendation": "Increase inventory" if space_needed_for_surge > 0 else "Current capacity sufficient"
        }
    
    @classmethod
    def to_dataframe(cls) -> pd.DataFrame:
        """Convert warehouses to DataFrame"""
        data = []
        for warehouse in cls.get_all_warehouses():
            data.append({
                "warehouse_id": warehouse.warehouse_id,
                "name": warehouse.name,
                "location": warehouse.location,
                "total_capacity": warehouse.total_capacity,
                "current_utilization": warehouse.current_utilization,
                "available_capacity": warehouse.available_capacity,
                "utilization_rate": round(warehouse.utilization_rate * 100, 1),
                "operating_days": warehouse.operating_days,
                "max_shipments_per_day": warehouse.max_shipments_per_day
            })
        return pd.DataFrame(data)
