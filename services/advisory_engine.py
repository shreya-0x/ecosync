import os
import sys
import logging
from typing import Dict, List, Any, Optional
from database.db import get_db_connection
from config import Config
from services.waste_guide_service import WASTE_CATEGORIES, ITEM_GUIDES, get_category_info

logger = logging.getLogger("ecosync.advisory_engine")

# Material handling and contamination rules grounded in technical circular economy standards
CIRCULAR_RULES = {
    "Plastic": {
        "handling_protocol": "Separate by polymer resin code (PET #1, HDPE #2, PP #5). Rinse containers and crush flat. Avoid thermal blending of PVC.",
        "optical_detection_criteria": "Near-infrared (NIR) reflection spectra 1100-1700nm to differentiate clear PET from PVC.",
        "contamination_risks": [
            "Thermal discoloration if PET is contaminated with >50ppm PVC.",
            "Density separation failure when PET flakes have residual closures.",
            "Food and grease residues contaminating clean polymer flake washing lines."
        ],
        "target_facility": "PRP-02 (Piedmont Polymer Reclamation Center)",
        "household_advice": "Rinse empty bottles with leftover rinse water. Keep caps on or off according to local bin rules. Never put flexible plastic wraps or bags into rigid curbside bins."
    },
    "Metal": {
        "handling_protocol": "Employ overhead magnetic cross-belt for ferrous tinplate; high-frequency eddy current separator for aluminum beverage cans.",
        "optical_detection_criteria": "Conductivity and density validation; induction sensor array.",
        "contamination_risks": [
            "Combustible volatiles in closed aerosol containers.",
            "Iron attachment in aluminum shred reducing secondary alloy value.",
            "Food residuals attracting vermin and causing odors."
        ],
        "target_facility": "MSR-04 (Apex Non-Ferrous & Alloy Refiners)",
        "household_advice": "Empty all liquids. Aluminum cans can be crushed flat to save space; leave pull tabs attached to the can."
    },
    "Paper": {
        "handling_protocol": "Keep strictly dry. Bale under hydraulic compression. Route to hydropulping de-inking unit.",
        "optical_detection_criteria": "Moisture sensor index <12%; fiber integrity analysis.",
        "contamination_risks": [
            "Grease or wax coatings (e.g. unlined food takeout boxes) ruin fiber slurry.",
            "Moisture fosters fungal breakdown and degrades tensile fiber strength."
        ],
        "target_facility": "FPU-03 (Cascadia Fiber & Pulp Processing Hub)",
        "household_advice": "Tear off greasy pizza box bottoms and compost them or put in general trash; recycle only the clean top lid."
    },
    "Cardboard": {
        "handling_protocol": "Break down flat, strip synthetic adhesive tape, bale into OCC Grade 11 specs.",
        "optical_detection_criteria": "Flute structure scanning; weight-to-area bulk ratio.",
        "contamination_risks": [
            "Oil saturation prevents re-pulping in secondary paper mills.",
            "Expanded polystyrene or plastic packaging left inside cartons."
        ],
        "target_facility": "FPU-03 (Cascadia Fiber & Pulp Processing Hub)",
        "household_advice": "Always flatten cartons before recycling to save collection truck volume."
    },
    "Glass": {
        "handling_protocol": "Separate by color cullet (Flint/Clear, Amber/Brown, Green). Avoid heat-resistant ceramic or Pyrex mixing.",
        "optical_detection_criteria": "Optical transmittance and laser cullet sorting.",
        "contamination_risks": [
            "Ceramics (even 100g in 1 ton) do not melt at glass furnace temperatures and form inclusion defects in new containers.",
            "Lead crystal mixing creates regulatory hazardous toxicity."
        ],
        "target_facility": "GBC-05 (ClearCycle Glass Beneficiation Works)",
        "household_advice": "Rinse jars and remove metal lids. Never put drinking glasses, Pyrex, ceramics, or light bulbs into bottle recycling."
    }
}

class AdvisoryEngine:
    @classmethod
    def get_operational_insights(cls) -> List[Dict[str, Any]]:
        """
        Analyzes live database tables to produce concrete, grounded operational recommendations.
        Identifies bottlenecks, pending verifications, and collection risks.
        """
        insights = []

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Check for high fill collection points
            cursor.execute("SELECT id, name, zone, fill_level_pct FROM collection_points WHERE fill_level_pct >= 75.0")
            critical_cps = cursor.fetchall()
            for cp in critical_cps:
                insights.append({
                    "id": f"rec-cp-{cp['id']}",
                    "level": "warning",
                    "category": "Collection Logistics",
                    "title": f"Collection Point Capacity Alert: {cp['name']}",
                    "summary": f"Fill level has reached {cp['fill_level_pct']}%. Dispatched route optimization is recommended to avoid bin overflow.",
                    "evidence": {
                        "entity_id": cp["id"],
                        "fill_level": f"{cp['fill_level_pct']}%",
                        "zone": cp["zone"]
                    },
                    "action_suggested": f"Schedule priority route for transport fleet to {cp['id']}."
                })

            # 2. Check for unverified batches
            cursor.execute("SELECT COUNT(*) FROM waste_batches WHERE status = 'Detected' OR status = 'Classified'")
            unverified_count = cursor.fetchone()[0]
            if unverified_count > 0:
                insights.append({
                    "id": "rec-unverified-stream",
                    "level": "info",
                    "category": "Quality Assurance",
                    "title": f"{unverified_count} Material Batches Pending Verification",
                    "summary": "Batches currently classified by computer vision have not yet received human confirmation.",
                    "evidence": {
                        "pending_count": unverified_count,
                        "rule": "Batches require human confirmation before advancing to Collected status."
                    },
                    "action_suggested": "Review detections in the Scanner inspection console and confirm waste categories."
                })

            # 3. Check facility load vs capacity
            cursor.execute("SELECT id, name, capacity_tpd, current_load_tpd, (current_load_tpd / capacity_tpd) * 100 as load_pct FROM facilities WHERE (current_load_tpd / capacity_tpd) >= 0.80")
            overloaded_facilities = cursor.fetchall()
            for fac in overloaded_facilities:
                insights.append({
                    "id": f"rec-fac-{fac['id']}",
                    "level": "warning",
                    "category": "Facility Throughput",
                    "title": f"Facility Near Peak Capacity: {fac['name']}",
                    "summary": f"Current throughput is at {round(fac['load_pct'], 1)}% of nominal rating ({fac['current_load_tpd']} / {fac['capacity_tpd']} TPD).",
                    "evidence": {
                        "facility_id": fac["id"],
                        "capacity_tpd": fac["capacity_tpd"],
                        "current_load_tpd": fac["current_load_tpd"]
                    },
                    "action_suggested": "Divert incoming raw secondary streams to overflow aggregation yards or buffer hoppers."
                })

            # 4. Circularity milestone
            cursor.execute("SELECT SUM(estimated_weight_kg) FROM waste_batches WHERE status = 'Processed'")
            processed_weight = cursor.fetchone()[0] or 0.0
            insights.append({
                "id": "rec-recovery-milestone",
                "level": "positive",
                "category": "Circularity Milestone",
                "title": f"{round(processed_weight, 1)} kg Successfully Recovered",
                "summary": "Material has completed the full transformation lifecycle through sorting, purification, and secondary remanufacturing.",
                "evidence": {
                    "total_processed_kg": processed_weight,
                    "active_stream": "Closed-loop circular recovery"
                },
                "action_suggested": "Export circularity compliance audit report."
            })

        return insights

    @classmethod
    def answer_query(cls, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Answers household waste disposal, reduction, recycling, and Digital Twin questions.
        Uses deterministic grounding by default; if GEMINI_API_KEY is configured,
        leverages Google GenAI for tailored synthesis.
        """
        q_lower = question.strip().lower()

        # Database telemetry summary
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(estimated_weight_kg) FROM waste_batches")
            total_b, total_w = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM household_scans")
            total_household_scans = cursor.fetchone()[0]

        # 1. If GEMINI_API_KEY is set, call Gemini API
        if Config.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=Config.GEMINI_API_KEY)

                system_prompt = (
                    "You are EcoSync's AI Waste Advisor, an expert assistant for everyday households. "
                    "Your mission is to help citizens answer: "
                    "1. What is this item? 2. What type of waste does it belong to? 3. How to handle and dispose safely? "
                    "4. How to reduce, reuse, or recycle it? 5. How waste habits improve the community. "
                    "All advice must be practical, concise, safety-conscious, and in English. "
                    "Never invent non-existent local collection centers or fake regulations. "
                    f"Operational context: EcoSync currently tracks {total_household_scans} household scans and {total_b} community batches. "
                    "Always emphasize personal safety: never pour oil down drains, never puncture batteries, and keep needles away from regular trash."
                )

                response = client.models.generate_content(
                    model=Config.GEMINI_MODEL,
                    contents=f"{system_prompt}\n\nUser Question: {question}"
                )

                return {
                    "answer": response.text,
                    "source": "Gemini AI (Grounded in EcoSync Knowledge & Live Telemetry)",
                    "matched_topic": "Generative Household Advisory",
                    "grounded_facts": {
                        "household_scans": total_household_scans,
                        "total_batches_tracked": total_b
                    }
                }
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to deterministic knowledge engine: {e}")

        # 2. Comprehensive Deterministic Knowledge Engine (100% offline, guaranteed)
        
        # A. Food scraps & composting
        if any(w in q_lower for w in ["food", "scrap", "organic", "banana", "compost", "peel", "vegetable"]):
            answer = (
                "### Practical Guidance: Food Scraps & Organic Waste 🌱\n\n"
                "**1. Category:** Organic and biodegradable waste (Green Bin / Wet Waste).\n\n"
                "**2. Immediate Handling:** Separate food preparation scraps (fruit rinds, vegetable peels, coffee grounds, eggshells) from plastics and packaging.\n\n"
                "**3. Home Composting Tip:** Kitchen cutoffs make fantastic nitrogen-rich compost! Layer with dry brown materials (cardboard shreds or dry leaves) in a 1:2 ratio to eliminate odors.\n\n"
                "**4. What to Avoid:** Remove plastic produce stickers before composting. Keep pet waste and large meat bones out of standard backyard compost bins.\n\n"
                "**5. Community Benefit:** Diverting 1 kg of organics from landfills eliminates up to 0.52 kg of greenhouse gas emissions (methane CH4)."
            )
            return {
                "answer": answer,
                "source": "EcoSync Household Citizen Knowledge Engine",
                "matched_topic": "Organic Waste & Composting",
                "category": "Organic and biodegradable waste"
            }

        # B. Electronics & Batteries
        if any(w in q_lower for w in ["electronic", "phone", "laptop", "battery", "e-waste", "gadget", "charger"]):
            answer = (
                "### Critical Safety Guidance: Electronics & Batteries ⚡⚠️\n\n"
                "**1. Category:** Electronic waste / Hazardous waste (Dedicated E-Waste Drop-off).\n\n"
                "**2. Urgent Safety Rule:** **NEVER throw batteries or electronics into household trash or blue recycling bins.** Compactor trucks crush them, causing thermal runaway lithium fires.\n\n"
                "**3. Preparation:** Tape the metal terminals of loose batteries with clear tape or electrical tape to prevent accidental short circuits. Perform a data wipe on old smartphones and laptops.\n\n"
                "**4. Where Should It Go:** Take to an authorized electronics retail drop-off box, supermarket battery bin, or municipal hazardous waste depot.\n\n"
                "**5. Environmental Value:** Recovers critical rare-earth metals (copper, silver, lithium, cobalt) and keeps toxic lead and mercury out of soil and water tables."
            )
            return {
                "answer": answer,
                "source": "EcoSync Household Citizen Knowledge Engine",
                "matched_topic": "Electronic Waste & Battery Safety",
                "category": "Electronic waste"
            }

        # C. Cooking oil & liquid grease
        if any(w in q_lower for w in ["cooking oil", "used oil", "motor oil", "drain", "sink", "liquid waste", "fatberg"]):
            answer = (
                "### Safe Handling: Used Cooking Oil & Grease 🛢️\n\n"
                "**1. Category:** Liquid waste (Never pour down household plumbing).\n\n"
                "**2. Immediate Action:** Let hot cooking oil cool completely in the pan.\n\n"
                "**3. Safe Storage:** Strain and pour into a sealed, non-breakable screw-top jar or clean bottle.\n\n"
                "**4. Critical Warning:** **NEVER pour oil or grease down kitchen sinks or toilets.** It coagulates inside pipes into massive 'fatbergs' that choke municipal sewer lines.\n\n"
                "**5. Citizen Recycling:** Collected cooking oil is transformed into clean renewable biodiesel! Search for local biofuel collection bins or municipal drop-offs."
            )
            return {
                "answer": answer,
                "source": "EcoSync Household Citizen Knowledge Engine",
                "matched_topic": "Liquid Waste Handling",
                "category": "Liquid waste"
            }

        # D. Pizza boxes & packaging cardboard
        if any(w in q_lower for w in ["pizza", "pizza box", "cardboard box", "carton"]):
            answer = (
                "### Recycling Guide: Pizza Boxes & Packaging 📦🍕\n\n"
                "**1. Can It Be Recycled?** Only the clean parts! Grease and cheese oil do not wash out of paper fibers during water pulping.\n\n"
                "**2. Recommended Household Action:** Tear the box in half along the crease:\n"
                "- **Clean Top Lid:** Blue Recycling Bin (Dry Paper & Cardboard).\n"
                "- **Greasy Bottom:** Compost bin (if unlined) or Black/Grey General Trash Bin.\n\n"
                "**3. What to Avoid:** Never place plastic dipping sauce cups, plastic table stands, or crust leftovers into recycling.\n\n"
                "**4. Why It Matters:** Grease causes oil spots in recycled paper rolls, ruining thousands of meters of new paper."
            )
            return {
                "answer": answer,
                "source": "EcoSync Household Citizen Knowledge Engine",
                "matched_topic": "Packaging & Cardboard Recycling",
                "category": "Recyclable materials"
            }

        # D. Household Waste Reduction (Zero-Waste tips)
        if any(w in q_lower for w in ["reduce", "reduction", "less waste", "habit", "zero waste", "household"]):
            answer = (
                "### 5 Practical Ways Your Household Can Drastically Cut Waste 🏡✨\n\n"
                "**1. Carry Reusable Carry Bags & Water Bottles:** Avoids 150+ single-use plastic bottles and 300+ thin film bags per person each year.\n\n"
                "**2. Master the 'Rinse & Dry' Habit:** Recyclables with food gunk contaminate entire bales at sorting facilities. A quick 5-second rinse makes them truly recyclable.\n\n"
                "**3. Flatten Delivery Cartons:** Breaking down corrugated shipping boxes preserves 70% more space in collection trucks, cutting transport fuel emissions.\n\n"
                "**4. Buy Pantry Staples in Bulk:** Cuts single-serving multi-layer sachets and packaging foil that cannot be mechanically recycled.\n\n"
                "**5. Plan Meal Portions:** About 30% of household food waste is preventable. Plan meals and freeze leftovers to cut kitchen expenses and landfill methane."
            )
            return {
                "answer": answer,
                "source": "EcoSync Household Citizen Knowledge Engine",
                "matched_topic": "Household Waste Reduction Habits",
                "category": "Waste Reduction"
            }

        # E. Digital Twin Simulation Explanation
        if any(w in q_lower for w in ["simulation", "digital twin", "twin", "scenario", "efficiency", "collection efficiency"]):
            answer = (
                "### How the Digital Twin & Scenario Simulation Work 🌐🔄\n\n"
                "**1. What It Represents:** A digital model of the waste journey from your home to collection trucks, optical sorting plants, and secondary recycling processors.\n\n"
                "**2. The Power of Source Segregation:** When households separate waste at source, sorting plants run at >90% purity. When unsegregated, up to 25% of recyclables are ruined by contamination.\n\n"
                "**3. Collection Efficiency:** Simulating higher collection capacities or daily volumes shows municipal planners and environmental administrators whether collection fleets face bottlenecks or overflowing bins.\n\n"
                "**4. Projections vs Real Data:** All scenario sliders in the Digital Twin are simulated on-the-fly and **never alter your real verified scan records**."
            )
            return {
                "answer": answer,
                "source": "EcoSync Digital Twin Diagnostic Core",
                "matched_topic": "Digital Twin Scenario Model",
                "category": "Digital Twin"
            }

        # F. Specific material rules (Plastic, Metal, Paper, Cardboard, Glass)
        matched_material = None
        for mat in CIRCULAR_RULES:
            if mat.lower() in q_lower:
                matched_material = mat
                break

        if matched_material:
            rule = CIRCULAR_RULES[matched_material]
            answer = (
                f"### Material Handling Protocol: {matched_material}\n\n"
                f"**Household Preparation:** {rule['household_advice']}\n\n"
                f"**Processing Protocol:** {rule['handling_protocol']}\n\n"
                f"**Assigned Recovery Facility:** **{rule['target_facility']}**\n\n"
                f"**Optical & Sensory Sorting Criteria:** {rule['optical_detection_criteria']}\n\n"
                f"**Key Contamination Risks to Avoid:**\n" +
                "\n".join([f"- {risk}" for risk in rule['contamination_risks']])
            )
            return {
                "answer": answer,
                "source": "EcoSync Grounded Material Intelligence Engine (Deterministic)",
                "matched_material": matched_material,
                "matched_topic": f"Material Protocol: {matched_material}",
                "handling_rules": rule,
                "grounded_facts": {
                    "rule_type": "Circular Economy Specification Sheet",
                    "facility_assigned": rule['target_facility']
                }
            }

        # G. Operational bottlenecks
        if any(w in q_lower for w in ["bottleneck", "capacity", "facility", "overflow"]):
            insights = cls.get_operational_insights()
            fac_insights = [i for i in insights if i["category"] in ["Facility Throughput", "Collection Logistics"]]
            summary_lines = [f"- **{i['title']}**: {i['summary']}" for i in fac_insights]
            return {
                "answer": "### Operational Throughput & Capacity Status\n\n" + ("\n".join(summary_lines) if summary_lines else "All facilities and collection points are currently operating within nominal design tolerances."),
                "source": "EcoSync Telemetry Diagnostics",
                "matched_material": None,
                "matched_topic": "Facility Throughput & Capacity Diagnostics",
                "grounded_facts": {"active_alerts": len(fac_insights)}
            }

        # H. Default Comprehensive Household Summary
        answer = (
            "### EcoSync Household Waste Assistant 🌍\n\n"
            "I can answer your questions about waste sorting, safe disposal, and environmental impact!\n\n"
            "**Try asking:**\n"
            "- *'How do I dispose of old phone batteries?'*\n"
            "- *'Can greasy pizza boxes be recycled?'*\n"
            "- *'What can I do with kitchen food scraps?'*\n"
            "- *'What are the contamination risks for Plastic PET?'*\n"
            "- *'How does source segregation improve collection efficiency?'*\n"
            "- *'What should I do with used cooking oil?'*\n\n"
            f"**Community Telemetry:** EcoSync has recorded {total_household_scans} citizen scans and coordinates {total_b} material batches across regional recovery centers."
        )
        return {
            "answer": answer,
            "source": "EcoSync Household Assistant",
            "matched_material": None,
            "matched_topic": "EcoSync Household Assistant",
            "grounded_facts": {"household_scans": total_household_scans, "batches": total_b}
        }
