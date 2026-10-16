import sys
from pathlib import Path
from typing import Dict, Any

# EPA WARM (Waste Reduction Model) v15 & International Circular Economy Reference Factors:
# Units:
# - avoided_ghg_mtco2e_per_ton: Metric Tons CO2e avoided per metric ton recycled vs landfill
# - energy_saved_kwh_per_ton: Kilowatt-hours of primary energy saved per metric ton
# - virgin_material_offset_ratio: Ratio of virgin raw material offset per unit of secondary recovered material
# - density_kg_m3: approximate uncompacted density for landfill volume calculation (kg per cubic meter)

IMPACT_FACTORS = {
    "Plastic": {
        "avoided_ghg_kg_per_kg": 1.48,     # EPA WARM PET/HDPE blend
        "energy_saved_kwh_per_kg": 5.62,
        "virgin_material_offset_ratio": 0.88,
        "density_kg_m3": 45.0               # Landfill bulk uncompacted plastic volume
    },
    "Metal": {
        "avoided_ghg_kg_per_kg": 8.92,     # Secondary aluminum/steel smelting offset
        "energy_saved_kwh_per_kg": 14.10,
        "virgin_material_offset_ratio": 0.95,
        "density_kg_m3": 90.0               # Mixed municipal scrap cans
    },
    "Paper": {
        "avoided_ghg_kg_per_kg": 3.45,     # Methane avoidance in landfill + tree fiber offset
        "energy_saved_kwh_per_kg": 4.15,
        "virgin_material_offset_ratio": 0.82,
        "density_kg_m3": 110.0
    },
    "Cardboard": {
        "avoided_ghg_kg_per_kg": 3.12,     # Corrugated OCC recycling
        "energy_saved_kwh_per_kg": 3.85,
        "virgin_material_offset_ratio": 0.85,
        "density_kg_m3": 80.0
    },
    "Glass": {
        "avoided_ghg_kg_per_kg": 0.31,     # Furnace energy & carbonate decomposition reduction
        "energy_saved_kwh_per_kg": 0.72,
        "virgin_material_offset_ratio": 0.98,
        "density_kg_m3": 280.0
    },
    "Electronic Waste": {
        "avoided_ghg_kg_per_kg": 12.40,    # Precious metal extraction avoidance
        "energy_saved_kwh_per_kg": 22.50,
        "virgin_material_offset_ratio": 0.78,
        "density_kg_m3": 150.0
    },
    "General / Unmapped": {
        "avoided_ghg_kg_per_kg": 0.50,
        "energy_saved_kwh_per_kg": 1.20,
        "virgin_material_offset_ratio": 0.50,
        "density_kg_m3": 120.0
    }
}

def calculate_material_impact(material_category: str, weight_kg: float, purity_score: float = 0.90) -> Dict[str, Any]:
    """
    Transparently calculates environmental benefits based on documented EPA WARM v15 conversion indices.
    All calculations explicitly show input assumptions and conversion factors.
    """
    factors = IMPACT_FACTORS.get(material_category, IMPACT_FACTORS["General / Unmapped"])
    effective_pure_weight = max(0.0, weight_kg * purity_score)
    
    avoided_co2_kg = effective_pure_weight * factors["avoided_ghg_kg_per_kg"]
    energy_saved_kwh = effective_pure_weight * factors["energy_saved_kwh_per_kg"]
    virgin_offset_kg = effective_pure_weight * factors["virgin_material_offset_ratio"]
    landfill_diverted_m3 = (weight_kg / factors["density_kg_m3"]) if factors["density_kg_m3"] > 0 else 0.0

    return {
        "material_category": material_category,
        "input_weight_kg": round(weight_kg, 2),
        "purity_coefficient": round(purity_score, 3),
        "effective_recovered_weight_kg": round(effective_pure_weight, 2),
        "metrics": {
            "avoided_ghg_emissions_kg_co2e": round(avoided_co2_kg, 2),
            "avoided_ghg_emissions_mt_co2e": round(avoided_co2_kg / 1000.0, 4),
            "energy_saved_kwh": round(energy_saved_kwh, 2),
            "virgin_material_offset_kg": round(virgin_offset_kg, 2),
            "landfill_diverted_volume_m3": round(landfill_diverted_m3, 3)
        },
        "methodology": {
            "source": "EPA WARM v15 & Circular Resource Indices",
            "ghg_factor_used": f"{factors['avoided_ghg_kg_per_kg']} kg CO2e / kg recovered",
            "energy_factor_used": f"{factors['energy_saved_kwh_per_kg']} kWh / kg recovered",
            "virgin_offset_ratio": f"{int(factors['virgin_material_offset_ratio'] * 100)}% primary substitute ratio",
            "density_used": f"{factors['density_kg_m3']} kg/m³ landfill uncompacted bulk density"
        }
    }
