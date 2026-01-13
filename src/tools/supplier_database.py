"""
Supplier Database & Utilities
- Supplier status tracking
- Outage detection
- Alternative sourcing options
"""

import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class SupplierStatus(Enum):
    """Supplier operational status"""
    ACTIVE = "active"
    OUTAGE = "outage"
    DELAYED = "delayed"
    NEGOTIATING = "negotiating"
    ESCALATED = "escalated"


@dataclass
class Supplier:
    """Supplier information"""
    supplier_id: str
    name: str
    status: SupplierStatus
    location: str
    capacity: int  # Units per week
    lead_time_days: int
    cost_per_unit: float
    reliability_score: float  # 0-100
    negotiation_attempts: int = 0
    
    def __repr__(self):
        return f"Supplier({self.name}, {self.status.value}, capacity={self.capacity})"


class SupplierDatabase:
    """Supplier database and operations"""
    
    # Sample suppliers
    SUPPLIERS = {
        "S001": Supplier(
            supplier_id="S001",
            name="Premium Supplies Co",
            status=SupplierStatus.ACTIVE,
            location="USA",
            capacity=10000,
            lead_time_days=5,
            cost_per_unit=50,
            reliability_score=95
        ),
        "S002": Supplier(
            supplier_id="S002",
            name="Global Imports Ltd",
            status=SupplierStatus.ACTIVE,
            location="China",
            capacity=50000,
            lead_time_days=15,
            cost_per_unit=35,
            reliability_score=85
        ),
        "S003": Supplier(
            supplier_id="S003",
            name="Regional Distributors",
            status=SupplierStatus.OUTAGE,  # In outage
            location="Mexico",
            capacity=5000,
            lead_time_days=7,
            cost_per_unit=45,
            reliability_score=75
        ),
        "S004": Supplier(
            supplier_id="S004",
            name="Fast Track Logistics",
            status=SupplierStatus.ACTIVE,
            location="USA",
            capacity=8000,
            lead_time_days=3,
            cost_per_unit=60,
            reliability_score=90
        ),
        "S005": Supplier(
            supplier_id="S005",
            name="Emergency Supply Hub",
            status=SupplierStatus.ACTIVE,
            location="USA",
            capacity=2000,
            lead_time_days=1,
            cost_per_unit=85,
            reliability_score=92
        ),
    }
    
    @classmethod
    def get_supplier(cls, supplier_id: str) -> Optional[Supplier]:
        """Get supplier by ID"""
        return cls.SUPPLIERS.get(supplier_id)
    
    @classmethod
    def get_active_suppliers(cls) -> List[Supplier]:
        """Get all active suppliers"""
        return [s for s in cls.SUPPLIERS.values() if s.status == SupplierStatus.ACTIVE]
    
    @classmethod
    def get_suppliers_by_status(cls, status: SupplierStatus) -> List[Supplier]:
        """Get suppliers by status"""
        return [s for s in cls.SUPPLIERS.values() if s.status == status]
    
    @classmethod
    def detect_outages(cls) -> List[Supplier]:
        """Detect suppliers in outage"""
        return cls.get_suppliers_by_status(SupplierStatus.OUTAGE)
    
    @classmethod
    def find_alternatives(cls, preferred_supplier_id: str, required_capacity: int) -> List[Supplier]:
        """
        Find alternative suppliers
        
        Scenario: Supplier outage -> Find alternatives
        """
        preferred = cls.get_supplier(preferred_supplier_id)
        alternatives = []
        
        for supplier in cls.get_active_suppliers():
            if supplier.supplier_id != preferred_supplier_id:
                if supplier.capacity >= required_capacity:
                    alternatives.append(supplier)
        
        # Sort by reliability score (desc) and then by cost (asc)
        alternatives.sort(key=lambda x: (-x.reliability_score, x.cost_per_unit))
        return alternatives
    
    @classmethod
    def simulate_outage(cls, supplier_id: str, duration_hours: int = 24) -> None:
        """Simulate supplier outage"""
        supplier = cls.get_supplier(supplier_id)
        if supplier:
            supplier.status = SupplierStatus.OUTAGE
            print(f"⚠ OUTAGE SIMULATED: {supplier.name} - Duration: {duration_hours}h")
    
    @classmethod
    def clear_outage(cls, supplier_id: str) -> None:
        """Clear supplier outage"""
        supplier = cls.get_supplier(supplier_id)
        if supplier:
            supplier.status = SupplierStatus.ACTIVE
            print(f"✓ OUTAGE CLEARED: {supplier.name}")
    
    @classmethod
    def to_dataframe(cls) -> pd.DataFrame:
        """Convert supplier database to DataFrame"""
        data = []
        for supplier in cls.SUPPLIERS.values():
            data.append({
                "supplier_id": supplier.supplier_id,
                "name": supplier.name,
                "status": supplier.status.value,
                "location": supplier.location,
                "capacity": supplier.capacity,
                "lead_time_days": supplier.lead_time_days,
                "cost_per_unit": supplier.cost_per_unit,
                "reliability_score": supplier.reliability_score
            })
        return pd.DataFrame(data)
