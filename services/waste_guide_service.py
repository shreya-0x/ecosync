"""
EcoSync Waste Taxonomy & Citizen Waste Guide Service
Defines the official 8-category household waste taxonomy,
class mappings from Computer Vision, and the comprehensive
8-point "How to Handle This Waste" guidance for ordinary citizens.
"""

from typing import Dict, List, Optional, Any

# 1. Official 8 Broad Waste Categories
WASTE_CATEGORIES = {
    "Recyclable materials": {
        "id": "recyclable",
        "name": "Recyclable materials",
        "short_desc": "Clean paper, cardboard, plastic containers, metal cans, and glass jars that can be remanufactured.",
        "bin_color": "Blue",
        "bin_label": "Dry / Recyclables Bin",
        "badge_class": "badge-blue",
        "icon": "♻️",
        "standard_weight_factor_kg": 0.08,
        "diverted_co2_factor_per_kg": 1.45,
        "energy_saved_kwh_per_kg": 3.8
    },
    "Organic and biodegradable waste": {
        "id": "organic",
        "name": "Organic and biodegradable waste",
        "short_desc": "Kitchen food scraps, fruit/vegetable peels, tea leaves, coffee grounds, and garden green waste.",
        "bin_color": "Green",
        "bin_label": "Wet / Compost Bin",
        "badge_class": "badge-green",
        "icon": "🌱",
        "standard_weight_factor_kg": 0.15,
        "diverted_co2_factor_per_kg": 0.52,
        "energy_saved_kwh_per_kg": 0.6
    },
    "Municipal solid waste": {
        "id": "msw",
        "name": "Municipal solid waste",
        "short_desc": "Non-recyclable household residual trash, composite packaging, worn multi-material plastics, and dust.",
        "bin_color": "Black / Grey",
        "bin_label": "General Trash Bin",
        "badge_class": "badge-grey",
        "icon": "🗑️",
        "standard_weight_factor_kg": 0.05,
        "diverted_co2_factor_per_kg": 0.0,
        "energy_saved_kwh_per_kg": 0.0
    },
    "Hazardous waste": {
        "id": "hazardous",
        "name": "Hazardous waste",
        "short_desc": "Household batteries, fluorescent CFL bulbs, paint thinners, solvent residues, and toxic chemicals.",
        "bin_color": "Red / Designated Drop-off",
        "bin_label": "Hazardous Collection Kiosk",
        "badge_class": "badge-red",
        "icon": "⚠️",
        "standard_weight_factor_kg": 0.12,
        "diverted_co2_factor_per_kg": 2.10,
        "energy_saved_kwh_per_kg": 5.2
    },
    "Electronic waste": {
        "id": "ewaste",
        "name": "Electronic waste",
        "short_desc": "Discarded electronics, mobile phones, chargers, circuit boards, cables, and home appliances.",
        "bin_color": "Orange / E-Waste Bin",
        "bin_label": "Certified E-Waste Drop-off",
        "badge_class": "badge-orange",
        "icon": "⚡",
        "standard_weight_factor_kg": 0.25,
        "diverted_co2_factor_per_kg": 3.60,
        "energy_saved_kwh_per_kg": 11.4
    },
    "Liquid waste": {
        "id": "liquid",
        "name": "Liquid waste",
        "short_desc": "Used cooking grease/oils, vehicle motor oil, and concentrated household liquid chemicals.",
        "bin_color": "Sealed Container",
        "bin_label": "Grease Drop-off / Hazardous Depot",
        "badge_class": "badge-purple",
        "icon": "🛢️",
        "standard_weight_factor_kg": 0.50,
        "diverted_co2_factor_per_kg": 1.80,
        "energy_saved_kwh_per_kg": 4.1
    },
    "Construction and demolition waste": {
        "id": "construction",
        "name": "Construction and demolition waste",
        "short_desc": "Rubble, brick fragments, ceramic tile shards, plasterboard drywall, and lumber offcuts.",
        "bin_color": "Yellow / Heavy Skip",
        "bin_label": "C&D Skip / Municipal Yard",
        "badge_class": "badge-yellow",
        "icon": "🧱",
        "standard_weight_factor_kg": 2.50,
        "diverted_co2_factor_per_kg": 0.25,
        "energy_saved_kwh_per_kg": 0.8
    },
    "Biomedical and healthcare waste": {
        "id": "biomedical",
        "name": "Biomedical and healthcare waste",
        "short_desc": "Used syringes, diabetic lancets, expired pharmaceuticals, surgical dressings, and sterile kits.",
        "bin_color": "Yellow / Biohazard Puncture-Proof Box",
        "bin_label": "Pharmacy Return / Clinical Biohazard",
        "badge_class": "badge-rose",
        "icon": "🩹",
        "standard_weight_factor_kg": 0.04,
        "diverted_co2_factor_per_kg": 0.80,
        "energy_saved_kwh_per_kg": 1.2
    }
}

# 2. Comprehensive 8-Point Guidance Directory for Specific Household Items
ITEM_GUIDES = {
    # Plastics / Containers
    "plastic_bottle": {
        "id": "plastic_bottle",
        "display_name": "Plastic Beverage Bottle (PET / HDPE)",
        "category": "Recyclable materials",
        "material": "PET #1 or HDPE #2 Plastic",
        "estimated_weight_kg": 0.025,
        "guide": {
            "what_is_it": "A single-use or rigid plastic bottle typically used for water, soda, cooking oil, or liquid detergents.",
            "what_to_do_now": "Empty all remaining liquid immediately. Do not leave half-full bottles in recycling bins.",
            "which_bin": "Blue Recycling Bin (Clean Dry Recyclables).",
            "how_to_prepare": "Rinse briefly with residual water, remove cap (or keep screwed on if local rules specify), and crush flat to save bin volume.",
            "what_to_avoid": "Do not leave liquids inside. Do not put bottles containing chemicals or engine oil into the plastics recycling bin.",
            "where_should_it_go": "Curbside dry recycling pickup or local bottle deposit reverse-vending kiosk.",
            "why_matters": "PET bottles can be recycled up to 7-10 times into new bottles or polyester fibers, cutting virgin crude oil use by over 60%.",
            "citizen_action": "Carry a refillable stainless steel or BPA-free bottle for daily hydration to avoid 150+ single-use bottles per year."
        }
    },
    "disposable_cup": {
        "id": "disposable_cup",
        "display_name": "Disposable Beverage Cup",
        "category": "Municipal solid waste",
        "material": "Poly-coated Paperboard or Polypropylene",
        "estimated_weight_kg": 0.018,
        "guide": {
            "what_is_it": "Hot or cold takeout beverage cup with a thin polyethylene plastic interior water barrier.",
            "what_to_do_now": "Separate the plastic lid and the paper sleeve from the cup body.",
            "which_bin": "Cup goes to General Waste (Black/Grey Bin); clean cardboard sleeve goes to Recycling (Blue Bin).",
            "how_to_prepare": "Empty ice or liquid. Discard straw into general waste. Flatten the cardboard sleeve.",
            "what_to_avoid": "Avoid tossing coated cups into the paper recycling bin, as the fused plastic liner jams hydropulpers.",
            "where_should_it_go": "General household municipal solid waste, unless your city has a specialized cup-takeback pilot program.",
            "why_matters": "Keeping poly-lined cups out of paper bales prevents entire loads of clean paper from being rejected at paper mills.",
            "citizen_action": "Bring your own insulated travel mug to the cafe. Many cafes offer a discount for reusable cups!"
        }
    },
    "aluminum_can": {
        "id": "aluminum_can",
        "display_name": "Aluminum Beverage Can",
        "category": "Recyclable materials",
        "material": "UBC Aluminum Alloy",
        "estimated_weight_kg": 0.015,
        "guide": {
            "what_is_it": "Lightweight aluminum container used for soft drinks, sparkling water, or juices.",
            "what_to_do_now": "Empty contents completely.",
            "which_bin": "Blue Recycling Bin (Dry Recyclables / Metals).",
            "how_to_prepare": "Rinse lightly. The pull tab can be left attached to the can so it does not get lost during sorting.",
            "what_to_avoid": "Do not fill cans with cigarette butts, food waste, or other trash before recycling.",
            "where_should_it_go": "Curbside recycling or community scrap metal collection center.",
            "why_matters": "Recycling aluminum consumes 95% less energy than mining and smelting virgin bauxite ore, and can be recycled indefinitely.",
            "citizen_action": "Collect clean aluminum cans separately to donate to community fundraising or scrap deposit programs."
        }
    },
    "cardboard_box": {
        "id": "cardboard_box",
        "display_name": "Cardboard Box / Corrugated Carton",
        "category": "Recyclable materials",
        "material": "Corrugated Kraft Paperboard",
        "estimated_weight_kg": 0.250,
        "guide": {
            "what_is_it": "Shipping carton or cereal/packaging box made from unbleached or bleached wood pulp fibers.",
            "what_to_do_now": "Remove all internal plastic air pillows, bubble wrap, and styrofoam inserts.",
            "which_bin": "Blue Recycling Bin (Dry Paper & Cardboard).",
            "how_to_prepare": "Cut or break down flat so it lays flush, and keep strictly dry.",
            "what_to_avoid": "Do not put wet, greasy, or oil-soaked cardboard (e.g. greasy pizza box bottoms) into paper recycling.",
            "where_should_it_go": "Curbside paper/cardboard collection or community baling depot.",
            "why_matters": "Recycling 1 ton of cardboard saves 17 trees, 7,000 gallons of water, and 4,000 kWh of electricity.",
            "citizen_action": "Save sturdy delivery boxes for home storage, moving, or reuse before sending to recycling."
        }
    },
    "glass_container": {
        "id": "glass_container",
        "display_name": "Glass Bottle or Jar",
        "category": "Recyclable materials",
        "material": "Soda-Lime Silicate Glass",
        "estimated_weight_kg": 0.280,
        "guide": {
            "what_is_it": "Glass container for beverages, sauces, olive oil, or jams.",
            "what_to_do_now": "Empty remaining food or liquid.",
            "which_bin": "Blue Recycling Bin (Glass stream) or community glass igloo bank.",
            "how_to_prepare": "Rinse off food residues. Remove metal or plastic lids and place lids in their appropriate bin.",
            "what_to_avoid": "Never mix drinking glasses, Pyrex, ceramics, window glass, or mirrors with bottle glass—their melting points differ and will ruin the furnace.",
            "where_should_it_go": "Municipal glass collection or local glass recycling bank.",
            "why_matters": "Glass is 100% recyclable infinitely with zero loss in purity or quality.",
            "citizen_action": "Wash and reuse glass jars for storing pantry spices, dried beans, or leftovers."
        }
    },

    # Organic & Biodegradable Food Scraps
    "food_scraps_peels": {
        "id": "food_scraps_peels",
        "display_name": "Food Scraps & Fruit/Vegetable Peels",
        "category": "Organic and biodegradable waste",
        "material": "Biodegradable Organic Cellulose",
        "estimated_weight_kg": 0.080,
        "guide": {
            "what_is_it": "Kitchen waste such as banana peels, apple cores, citrus rinds, vegetable cutoffs, and bread crusts.",
            "what_to_do_now": "Keep separate from plastics, stickers, plastic wraps, and non-biodegradable packaging.",
            "which_bin": "Green Organic / Wet Waste Bin or household compost tumbler.",
            "how_to_prepare": "Peel off any plastic brand stickers found on fruits before composting.",
            "what_to_avoid": "Do not enclose in standard plastic bags unless using certified 100% compostable bags.",
            "where_should_it_go": "Municipal organic collection, community compost hub, or home composting unit.",
            "why_matters": "When organic waste is buried in landfills, it decomposes anaerobically producing methane (CH4)—a greenhouse gas 28x more potent than CO2.",
            "citizen_action": "Start a balcony vermicompost bin or indoor bokashi bucket to turn kitchen cutoffs into rich nutrient soil."
        }
    },

    # Electronic Waste
    "smartphone_device": {
        "id": "smartphone_device",
        "display_name": "Mobile Phone / Electronic Gadget",
        "category": "Electronic waste",
        "material": "Lithium-Ion Battery, PCB, Copper & Aluminum Chassis",
        "estimated_weight_kg": 0.180,
        "guide": {
            "what_is_it": "Obsolete, damaged, or discarded electronic communication device or handheld gadget.",
            "what_to_do_now": "Factory-reset and wipe personal data. Check if the battery is swollen or punctured.",
            "which_bin": "Never put in curbside bins! Take to an authorized E-Waste Collection Kiosk.",
            "how_to_prepare": "Keep battery intact inside the device. If the battery is separate or swollen, tape the terminals with non-conductive electrical tape.",
            "what_to_avoid": "Never burn, crush, or casually dismantle electronics. Never throw into household trash—risk of lithium fire.",
            "where_should_it_go": "Certified e-waste collection center, brand trade-in drop-off, or local electronic recycling event.",
            "why_matters": "Recycling 1 million cell phones recovers 35,000 lbs of copper, 772 lbs of silver, 75 lbs of gold, and 33 lbs of palladium.",
            "citizen_action": "Donate working old phones to educational nonprofits or trade them in for refurbished device credits."
        }
    },
    "computer_peripherals": {
        "id": "computer_peripherals",
        "display_name": "Computer Peripherals (Mouse, Keyboard, Remote)",
        "category": "Electronic waste",
        "material": "ABS Plastic, Membrane Circuit, Copper Wiring",
        "estimated_weight_kg": 0.150,
        "guide": {
            "what_is_it": "Computer mice, keyboards, game controllers, or infrared remote controls.",
            "what_to_do_now": "Remove any alkaline or rechargeable AA/AAA batteries before disposal.",
            "which_bin": "E-Waste Bin or Electronics Recycling depot (Orange / Designated).",
            "how_to_prepare": "Bundle any attached cords neatly. Recycle the removed batteries separately in a battery kiosk.",
            "what_to_avoid": "Do not throw into normal plastic or dry recycling bins—mixed electronics jam sorting machinery.",
            "where_should_it_go": "Municipal electronic waste drive or electronics retailer recycling box.",
            "why_matters": "Prevents toxic flame retardants and heavy metals from leaching into water tables.",
            "citizen_action": "Try cleaning sticky buttons with isopropyl alcohol or replacing switch contacts before replacing peripherals."
        }
    },

    # Personal Care / Municipal Solid Waste
    "manual_toothbrush": {
        "id": "manual_toothbrush",
        "display_name": "Manual Toothbrush",
        "category": "Municipal solid waste",
        "material": "Composite Nylon Bristles & Molded Polypropylene",
        "estimated_weight_kg": 0.020,
        "guide": {
            "what_is_it": "Standard hygiene brush with nylon bristles fused directly into a hard polymer handle.",
            "what_to_do_now": "Check if it can be repurposed for household cleaning before disposal.",
            "which_bin": "Black / Grey Bin (Municipal Solid Waste).",
            "how_to_prepare": "Rinse clean. (If using bamboo toothbrushes, pluck nylon bristles with pliers before composting the bamboo handle).",
            "what_to_avoid": "Do not put plastic toothbrushes into the blue plastics recycling bin—the fused bristles make them non-recyclable in standard facilities.",
            "where_should_it_go": "General household municipal solid waste, or specialized brand take-back programs (e.g. TerraCycle).",
            "why_matters": "Over 1 billion plastic toothbrushes are discarded yearly. Knowing what cannot be mechanically recycled avoids contaminating recyclables.",
            "citizen_action": "Repurpose retired toothbrushes to clean bike chains, grout, shoe edges, or computer vents."
        }
    },

    # Hazardous Household Items
    "household_batteries": {
        "id": "household_batteries",
        "display_name": "Household Batteries (AA, AAA, Lithium Coin)",
        "category": "Hazardous waste",
        "material": "Alkaline / Zinc-Carbon / Lithium Chemistry",
        "estimated_weight_kg": 0.050,
        "guide": {
            "what_is_it": "Electrochemical energy storage cells used in toys, remotes, watches, and household gadgets.",
            "what_to_do_now": "Store in a cool, dry plastic container away from flammable materials and metallic objects.",
            "which_bin": "Never place in household bins! Use dedicated Battery Drop-off Boxes.",
            "how_to_prepare": "Cover positive and negative terminals with transparent or electrical tape to prevent short circuits and sparks.",
            "what_to_avoid": "Never throw batteries into trash or recycling bins. Compacting trucks crush them, causing dangerous fires.",
            "where_should_it_go": "Supermarket battery collection bins, municipal hazardous waste facility, or hardware store drop-offs.",
            "why_matters": "Recovers valuable manganese, zinc, nickel, and prevents corrosive acids and heavy metals from contaminating groundwater.",
            "citizen_action": "Switch to rechargeable NiMH batteries to eliminate dozens of disposable batteries every year."
        }
    },

    # Liquid Waste
    "used_cooking_oil": {
        "id": "used_cooking_oil",
        "display_name": "Used Cooking Oil & Grease",
        "category": "Liquid waste",
        "material": "Vegetable / Animal Lipid Triglycerides",
        "estimated_weight_kg": 0.400,
        "guide": {
            "what_is_it": "Residual cooking or frying oil from kitchen pans and deep fryers.",
            "what_to_do_now": "Allow hot oil to cool completely before touching or transferring.",
            "which_bin": "Do NOT pour into any standard bin, and NEVER pour down the kitchen sink drain!",
            "how_to_prepare": "Pour cooled oil through a strainer into an airtight, non-breakable container (like an old glass jar or screw-top jug).",
            "what_to_avoid": "Never pour oil or grease down sink drains or toilets—it solidifies into massive 'fatbergs' that clog city sewers.",
            "where_should_it_go": "Drop off at a local biofuel collection station or seal tightly in the jar for solid municipal waste collection.",
            "why_matters": "1 liter of discarded oil can pollute up to 1 million liters of drinking water. Collected oil is converted into green biodiesel.",
            "citizen_action": "Filter and reuse frying oil 1-2 times when cooking clean foods, or donate to local waste-to-biodiesel collectors."
        }
    },

    # Biomedical / Healthcare
    "expired_medicines": {
        "id": "expired_medicines",
        "display_name": "Expired Medications & Blister Packs",
        "category": "Biomedical and healthcare waste",
        "material": "Active Pharmaceutical Ingredients & Foil Blisters",
        "estimated_weight_kg": 0.030,
        "guide": {
            "what_is_it": "Unused, expired, or discontinued prescription drugs, syrups, or over-the-counter tablets.",
            "what_to_do_now": "Keep out of reach of children and pets. Do not flush down the toilet or drain.",
            "which_bin": "Pharmacy Prescription Take-Back Kiosk (Yellow / Biohazard stream).",
            "how_to_prepare": "Black out any personal patient information on labels. Keep pills inside original blister packs or containers.",
            "what_to_avoid": "Never flush pharmaceuticals down the toilet—wastewater facilities cannot filter hormones and antibiotics from drinking water.",
            "where_should_it_go": "Authorized pharmacy return bin, hospital dispensary drop-off, or municipal drug take-back day.",
            "why_matters": "Flushed medicines contaminate aquatic wildlife, disrupt reproductive biology in fish, and contribute to antibiotic resistance.",
            "citizen_action": "Check your household medicine cabinet every 6 months and return expired medications to a pharmacy kiosk."
        }
    },
    "medical_sharps": {
        "id": "medical_sharps",
        "display_name": "Used Needles, Lancets & Syringes (Sharps)",
        "category": "Biomedical and healthcare waste",
        "material": "Stainless Steel Needle & Molded Polypropylene",
        "estimated_weight_kg": 0.015,
        "guide": {
            "what_is_it": "Diabetic lancets, allergy injection needles, auto-injectors, and insulin pen needles used in home healthcare.",
            "what_to_do_now": "Place immediately into a rigid, puncture-resistant container with a tight-fitting screw cap (e.g. approved yellow sharps container or heavy-duty HDPE detergent jug).",
            "which_bin": "Yellow Biohazard Sharps Container. NEVER in household trash or curbside recycling!",
            "how_to_prepare": "Do not attempt to bend, break, or recap needles. Seal the heavy plastic container with strong duct tape when 3/4 full.",
            "what_to_avoid": "NEVER throw loose needles into trash bags or recycling bins—this causes severe needle-stick injuries and infection risks to sanitation workers.",
            "where_should_it_go": "Municipal healthcare sharps drop-off site, local hospital disposal kiosk, or mail-back sharps service.",
            "why_matters": "Proper disposal eliminates risk of bloodborne pathogen transmission (HIV, Hepatitis B/C) to sanitation and sorting personnel.",
            "citizen_action": "Keep an FDA-cleared sharps container or sturdy laundry detergent jug designated specifically for household sharps."
        }
    },

    # Construction and Demolition Waste
    "broken_ceramic_tiles": {
        "id": "broken_ceramic_tiles",
        "display_name": "Broken Ceramic Tiles & Masonry Shards",
        "category": "Construction and demolition waste",
        "material": "Kiln-Fired Glazed Ceramic & Silicate Mortar",
        "estimated_weight_kg": 1.500,
        "guide": {
            "what_is_it": "Heavy porcelain or ceramic floor/wall tiles, grout chunks, and sanitary ceramic pieces from DIY renovations.",
            "what_to_do_now": "Wear heavy work gloves to avoid sharp edge cuts. Separate from metals, drywall, and timber.",
            "which_bin": "Municipal Construction & Demolition Skip (Yellow / Designated C&D Yard).",
            "how_to_prepare": "Place in heavy-duty rubble bags (woven polypropylene sacks). Do not overload bags beyond 20 kg for safe handling.",
            "what_to_avoid": "Do NOT place in blue glass recycling bins—ceramic melting points (>1700°C) ruin glass furnaces and contaminate container cullet.",
            "where_should_it_go": "Local civic amenity site, municipal rubble recovery station, or hired C&D skip.",
            "why_matters": "Crushed clean ceramic and rubble can be crushed into aggregate base material for road sub-bases, preventing virgin quarrying.",
            "citizen_action": "Intact leftover tiles can be donated to community makerspaces, mosaic artists, or home reuse networks."
        }
    },
    "gypsum_drywall": {
        "id": "gypsum_drywall",
        "display_name": "Drywall & Plasterboard Offcuts",
        "category": "Construction and demolition waste",
        "material": "Calcium Sulfate Dihydrate (Gypsum) Core & Paper Liners",
        "estimated_weight_kg": 2.200,
        "guide": {
            "what_is_it": "Wallboard, sheetrock, or plasterboard remnants from home partitioning, repairs, or ceiling work.",
            "what_to_do_now": "Keep dry and sheltered from rain. Wet drywall degrades and releases pungent odorous compounds.",
            "which_bin": "Dedicated Gypsum / Plasterboard Recycling Skip at Civic Amenity Site.",
            "how_to_prepare": "Remove screws, nails, corner beadings, and large patches of wallpaper before loading.",
            "what_to_avoid": "Do not bury in general municipal landfill—anaerobic decomposition of gypsum produces toxic, foul hydrogen sulfide (H2S) gas.",
            "where_should_it_go": "Municipal C&D transfer station with a dedicated gypsum recovery container.",
            "why_matters": "Recovered gypsum powder is calcined into recycled plasterboard or used as an agricultural soil conditioning amendment.",
            "citizen_action": "Measure carefully before cutting new panels to minimize scrap drywall offcuts during home DIY renovations."
        }
    },

    # Hazardous Household Items
    "cfl_lightbulb": {
        "id": "cfl_lightbulb",
        "display_name": "CFL & Fluorescent Light Bulbs",
        "category": "Hazardous waste",
        "material": "Silicate Glass Tube, Phosphor Coating & Elemental Mercury Vapor",
        "estimated_weight_kg": 0.080,
        "guide": {
            "what_is_it": "Compact fluorescent lamps (CFLs) or linear fluorescent tubes used for indoor illumination.",
            "what_to_do_now": "Handle very carefully by the plastic base to avoid shattering the glass tube.",
            "which_bin": "Designated Hazardous Waste Drop-off / Hardware Store Bulb Collection Kiosk.",
            "how_to_prepare": "Pack in original cardboard sleeve or bubble wrap. If broken, ventilate the room for 15 minutes, scoop up shards with cardboard (never vacuum!), and seal in a glass jar.",
            "what_to_avoid": "NEVER throw into regular curbside bins or glass recycling. Breaking releases neurotoxic elemental mercury vapor.",
            "where_should_it_go": "Local hardware store take-back kiosk (e.g. Home Depot/IKEA), or municipal household hazardous waste facility.",
            "why_matters": "Mercury is a persistent bioaccumulative neurotoxin. Recycling recovers 100% of the mercury, glass, and aluminum end-caps.",
            "citizen_action": "Upgrade burned-out fixtures to solid-state LED bulbs, which contain zero mercury and use 40% less electricity."
        }
    },
    "paint_thinner_can": {
        "id": "paint_thinner_can",
        "display_name": "Leftover Paint, Solvents & Thinners",
        "category": "Hazardous waste",
        "material": "Volatile Organic Compounds (VOCs), Mineral Spirits & Tinplate Can",
        "estimated_weight_kg": 0.850,
        "guide": {
            "what_is_it": "Oil-based paints, polyurethane varnishes, turpentine, mineral spirits, or chemical paint removers.",
            "what_to_do_now": "Seal the container lid tightly to prevent solvent evaporation and flammable vapor buildup.",
            "which_bin": "Hazardous Waste Collection Kiosk / Municipal Chemical Depot (Red Stream).",
            "how_to_prepare": "Keep in the original manufacturer can with legible labeling. Store upright in a cool, well-ventilated location away from pilot lights.",
            "what_to_avoid": "NEVER pour paint or solvents down the drain, into storm sewers, or onto backyard soil. Never throw liquid paint into household trash.",
            "where_should_it_go": "Community hazardous waste collection day or local paint recycling drop-off depot.",
            "why_matters": "Solvents leach into aquifers, contaminate city water reservoirs, and emit hazardous photochemical smog-forming VOCs.",
            "citizen_action": "Share leftover paint cans with neighbors, theater groups, or school art departments through community sharing apps."
        }
    },

    # Additional Liquid Waste
    "motor_oil": {
        "id": "motor_oil",
        "display_name": "Used Automotive Engine Oil & Fluids",
        "category": "Liquid waste",
        "material": "Petroleum Hydrocarbons, Heavy Metals & Lubricant Additives",
        "estimated_weight_kg": 0.900,
        "guide": {
            "what_is_it": "Drained motor engine oil, transmission fluid, or brake fluid from personal car or motorcycle maintenance.",
            "what_to_do_now": "Allow fluid to cool, then drain directly into a clean oil drain pan.",
            "which_bin": "Sealed Container at Certified Automotive Return Depot. NEVER in curbside bins!",
            "how_to_prepare": "Pour via funnel into a clean, leak-proof plastic container (like the original oil bottle). Do not mix with antifreeze, solvent, or water.",
            "what_to_avoid": "CRITICAL: NEVER pour used oil down storm drains, sink pipes, or onto the ground. 1 gallon of used motor oil ruins 1 million gallons of fresh water.",
            "where_should_it_go": "Auto parts retailers (AutoZone, Advance Auto, Canadian Tire), certified service stations, or municipal chemical depots.",
            "why_matters": "Used motor oil never wears out—it only gets dirty. Re-refining consumes 85% less energy than refining crude oil into fresh lubricants.",
            "citizen_action": "Take your container to free automotive retailer recycling bins immediately after completing DIY oil changes."
        }
    },

    # Additional Electronic Waste
    "electronic_cables": {
        "id": "electronic_cables",
        "display_name": "Power Cables, Charging Cords & Adapters",
        "category": "Electronic waste",
        "material": "PVC / TPE Flexible Jacket & High-Purity Copper Wire",
        "estimated_weight_kg": 0.080,
        "guide": {
            "what_is_it": "Damaged or obsolete USB cables, laptop power cords, audio cables, HDMI cords, and plug-in transformers.",
            "what_to_do_now": "Bundle neatly with a rubber band or twist-tie so cables do not tangle with other items.",
            "which_bin": "E-Waste Bin or Electronics Drop-off Depot (Orange / Designated).",
            "how_to_prepare": "Keep cords bundled. Inspect if the adapter contains internal batteries (like power banks); recycle power banks in battery bins.",
            "what_to_avoid": "Do not put loose cables into blue curbside recycling bins! Loose cords are 'tanglers' that wrap around optical sorting screens, jamming MRFs.",
            "where_should_it_go": "Community electronics recycling drive or consumer electronics retail recycling bins.",
            "why_matters": "Cables contain over 50% high-grade electrical copper, which can be melted and re-drawn into new wiring with 85% lower carbon footprint.",
            "citizen_action": "Label cables at home with masking tape to avoid rebuying duplicate cords when cleaning entertainment centers."
        }
    },

    # Additional Municipal Solid Waste
    "snack_wrappers": {
        "id": "snack_wrappers",
        "display_name": "Multi-Layer Snack & Chip Wrappers",
        "category": "Municipal solid waste",
        "material": "Metallized Biaxially-Oriented Polypropylene (BOPP/Aluminum)",
        "estimated_weight_kg": 0.005,
        "guide": {
            "what_is_it": "Shiny flexible bags for potato chips, candy wrappers, biscuit liners, and energy bar packaging.",
            "what_to_do_now": "Perform the scrunch test: ball it in your hand. If it bounces back open, it is multi-layer film.",
            "which_bin": "Black / Grey Bin (Municipal Solid Waste / General Trash).",
            "how_to_prepare": "Shake out crumbs. Keep flat or folded inside the general household trash bag.",
            "what_to_avoid": "Do not place in the blue recycling bin. The microscopic vacuum-deposited aluminum film cannot be melted together with normal plastics.",
            "where_should_it_go": "General household municipal solid waste, or specialized brand take-back programs (e.g. TerraCycle wrappers box).",
            "why_matters": "Preventing non-recyclable multi-layer pouches from entering plastic recycling lines preserves the purity and market value of genuine PET/HDPE bales.",
            "citizen_action": "Buy snacks in bulk family sizes and portion into reusable snack tubs to cut single-serving wrapper trash."
        }
    },

    # Additional Organic Waste
    "yard_clippings": {
        "id": "yard_clippings",
        "display_name": "Garden Leaves, Grass & Plant Trimmings",
        "category": "Organic and biodegradable waste",
        "material": "Lignocellulosic Plant Biomass",
        "estimated_weight_kg": 1.200,
        "guide": {
            "what_is_it": "Lawn mower clippings, fallen autumn leaves, garden pruning trimmings, and faded potted flowers.",
            "what_to_do_now": "Keep separate from plastic plant pots, synthetic garden twine, and pesticide containers.",
            "which_bin": "Green Municipal Yard Waste Bin or backyard compost pile.",
            "how_to_prepare": "Prune woody branches to under 3 feet in length and 2 inches in diameter so municipal shredders can process them.",
            "what_to_avoid": "Do not mix invasive weeds, diseased plant leaves, or chemically treated lumber shavings into yard waste.",
            "where_should_it_go": "Curbside green yard waste collection or community industrial composting facility.",
            "why_matters": "Composted yard waste produces nutrient-rich organic compost and mulch, replenishing depleted municipal parks and garden topsoil.",
            "citizen_action": "Leave grass clippings on the lawn after mowing ('grasscycling') to return natural nitrogen to the turf and reduce bin waste."
        }
    },

    # Additional Recyclable Material
    "tin_food_can": {
        "id": "tin_food_can",
        "display_name": "Steel / Tin Canned Food Can",
        "category": "Recyclable materials",
        "material": "Tin-Coated Ferrous Steel (Tinplate)",
        "estimated_weight_kg": 0.050,
        "guide": {
            "what_is_it": "Canned vegetables, tomato paste, tuna, soup, or pet food cans made from magnetic ferrous steel.",
            "what_to_do_now": "Empty remaining food into organic/compost or general waste.",
            "which_bin": "Blue Recycling Bin (Dry Recyclables / Metals).",
            "how_to_prepare": "Give a quick 5-second rinse. Push the metal lid inside the can or leave it attached so it does not create a sharp cutting hazard.",
            "what_to_avoid": "Do not leave half-empty food inside, which rots during transport and attracts pests at sorting facilities.",
            "where_should_it_go": "Curbside recycling or community scrap metal collection point.",
            "why_matters": "Steel is magnetic and easily separated by overhead electromagnets at MRFs. It can be recycled infinitely with zero degradation.",
            "citizen_action": "Use a manual can opener that leaves smooth edges, and tuck the lid safely inside the washed can before recycling."
        }
    }
}

# 3. Model Class to Household Item Resolution Matrix
# Maps standard YOLO detection classes to our verified household items
MODEL_CLASS_MAP = {
    "bottle": {
        "item_id": "plastic_bottle",
        "object_identity": "Plastic Beverage Bottle",
        "default_category": "Recyclable materials",
        "candidate_material": "PET / HDPE Plastic",
        "confidence_weight": 0.90
    },
    "wine glass": {
        "item_id": "glass_container",
        "object_identity": "Glassware / Glass Container",
        "default_category": "Recyclable materials",
        "candidate_material": "Silicate Glass",
        "confidence_weight": 0.92
    },
    "cup": {
        "item_id": "disposable_cup",
        "object_identity": "Disposable Beverage Cup",
        "default_category": "Municipal solid waste",
        "candidate_material": "Polymer-coated Paperboard",
        "confidence_weight": 0.84
    },
    "bowl": {
        "item_id": "disposable_cup",
        "object_identity": "Bowl / Food Container",
        "default_category": "Municipal solid waste",
        "candidate_material": "Ceramic or Plastic Composite",
        "confidence_weight": 0.80
    },
    "fork": {
        "item_id": "aluminum_can",
        "object_identity": "Metal Cutlery / Utensil",
        "default_category": "Recyclable materials",
        "candidate_material": "Stainless Steel / Alloy",
        "confidence_weight": 0.85
    },
    "knife": {
        "item_id": "aluminum_can",
        "object_identity": "Metal Cutlery / Knife",
        "default_category": "Recyclable materials",
        "candidate_material": "Stainless Steel",
        "confidence_weight": 0.85
    },
    "spoon": {
        "item_id": "aluminum_can",
        "object_identity": "Metal Cutlery / Spoon",
        "default_category": "Recyclable materials",
        "candidate_material": "Stainless Steel",
        "confidence_weight": 0.85
    },
    "banana": {
        "item_id": "food_scraps_peels",
        "object_identity": "Banana Peel / Food Scrap",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Biodegradable Biomass",
        "confidence_weight": 0.95
    },
    "apple": {
        "item_id": "food_scraps_peels",
        "object_identity": "Apple Core / Fruit Scrap",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Biodegradable Biomass",
        "confidence_weight": 0.95
    },
    "sandwich": {
        "item_id": "food_scraps_peels",
        "object_identity": "Food Leftover / Bread Scrap",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Cooked Organic Food Scrap",
        "confidence_weight": 0.90
    },
    "orange": {
        "item_id": "food_scraps_peels",
        "object_identity": "Citrus Peel / Fruit Scrap",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Biodegradable Biomass",
        "confidence_weight": 0.95
    },
    "broccoli": {
        "item_id": "food_scraps_peels",
        "object_identity": "Vegetable Scrap",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Plant Matter",
        "confidence_weight": 0.92
    },
    "carrot": {
        "item_id": "food_scraps_peels",
        "object_identity": "Vegetable Peel & Scrap",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Plant Matter",
        "confidence_weight": 0.92
    },
    "pizza": {
        "item_id": "food_scraps_peels",
        "object_identity": "Food Waste (Pizza Crust / Scrap)",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Food Leftovers",
        "confidence_weight": 0.88
    },
    "donut": {
        "item_id": "food_scraps_peels",
        "object_identity": "Food Waste (Bakery Scrap)",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Food Leftovers",
        "confidence_weight": 0.88
    },
    "cake": {
        "item_id": "food_scraps_peels",
        "object_identity": "Food Waste (Bakery Scrap)",
        "default_category": "Organic and biodegradable waste",
        "candidate_material": "Organic Food Leftovers",
        "confidence_weight": 0.88
    },
    "book": {
        "item_id": "cardboard_box",
        "object_identity": "Paper / Bound Book / Notebook",
        "default_category": "Recyclable materials",
        "candidate_material": "High Grade Cellulose Paper",
        "confidence_weight": 0.92
    },
    "suitcase": {
        "item_id": "cardboard_box",
        "object_identity": "Rigid Box / Container",
        "default_category": "Recyclable materials",
        "candidate_material": "Corrugated Board / Polymer Shell",
        "confidence_weight": 0.75
    },
    "backpack": {
        "item_id": "manual_toothbrush",
        "object_identity": "Textile Bag / Backpack",
        "default_category": "Municipal solid waste",
        "candidate_material": "Woven Synthetic Polymer Fabric",
        "confidence_weight": 0.80
    },
    "cell phone": {
        "item_id": "smartphone_device",
        "object_identity": "Smartphone / Mobile Device",
        "default_category": "Electronic waste",
        "candidate_material": "Lithium Battery, Glass & PCB",
        "confidence_weight": 0.94
    },
    "laptop": {
        "item_id": "smartphone_device",
        "object_identity": "Laptop / Portable Computer",
        "default_category": "Electronic waste",
        "candidate_material": "Lithium Battery, Chassis & Electronics",
        "confidence_weight": 0.94
    },
    "mouse": {
        "item_id": "computer_peripherals",
        "object_identity": "Computer Mouse / Peripheral",
        "default_category": "Electronic waste",
        "candidate_material": "ABS Plastic & Micro-circuitry",
        "confidence_weight": 0.90
    },
    "keyboard": {
        "item_id": "computer_peripherals",
        "object_identity": "Computer Keyboard / Input Device",
        "default_category": "Electronic waste",
        "candidate_material": "Polymer Keys & Membrane Circuit",
        "confidence_weight": 0.90
    },
    "remote": {
        "item_id": "computer_peripherals",
        "object_identity": "Remote Control Device",
        "default_category": "Electronic waste",
        "candidate_material": "Polymer Shell & Circuit Board",
        "confidence_weight": 0.88
    },
    "toothbrush": {
        "item_id": "manual_toothbrush",
        "object_identity": "Manual Toothbrush",
        "default_category": "Municipal solid waste",
        "candidate_material": "Molded Polymer & Nylon Bristles",
        "confidence_weight": 0.92
    },
    "scissors": {
        "item_id": "aluminum_can",
        "object_identity": "Scissors / Household Metal Tool",
        "default_category": "Recyclable materials",
        "candidate_material": "Ferrous Steel & Polymer Grip",
        "confidence_weight": 0.86
    },
    "vase": {
        "item_id": "glass_container",
        "object_identity": "Ceramic or Glass Vase",
        "default_category": "Municipal solid waste",
        "candidate_material": "Ceramic / Silicate Matrix",
        "confidence_weight": 0.82
    }
}


def get_category_info(category_name: str) -> Dict[str, Any]:
    """Returns metadata for an official waste category."""
    return WASTE_CATEGORIES.get(category_name, {
        "id": "unknown",
        "name": category_name,
        "short_desc": "General category.",
        "bin_color": "Grey / Standard",
        "bin_label": "Standard Collection",
        "badge_class": "badge-grey",
        "icon": "📦",
        "standard_weight_factor_kg": 0.1,
        "diverted_co2_factor_per_kg": 0.5,
        "energy_saved_kwh_per_kg": 1.0
    })


def get_item_guidance(item_id: str) -> Optional[Dict[str, Any]]:
    """Returns the full 8-point guidance for a specific household item."""
    return ITEM_GUIDES.get(item_id)


def resolve_model_detection(raw_class: str) -> Dict[str, Any]:
    """
    Translates a raw model class name (e.g. 'bottle', 'banana')
    into distinct separated concepts:
    1. Object detection (raw visual detection)
    2. Object identity (human name)
    3. Material classification (chemical/physical substrate)
    4. Waste category (one of the 8 canonical categories)
    5. Disposal & 8-point responsible citizen guide
    """
    raw_class_clean = raw_class.strip().lower()
    mapping = MODEL_CLASS_MAP.get(raw_class_clean)

    if mapping:
        item_id = mapping["item_id"]
        guide_record = ITEM_GUIDES.get(item_id, {})
        category_name = mapping["default_category"]
        category_info = get_category_info(category_name)

        return {
            "supported": True,
            "raw_class": raw_class_clean,
            "object_identity": mapping["object_identity"],
            "candidate_material": mapping["candidate_material"],
            "suggested_category": category_name,
            "category_info": category_info,
            "item_id": item_id,
            "estimated_weight_kg": guide_record.get("estimated_weight_kg", 0.05),
            "how_to_handle": guide_record.get("guide", _build_generic_guide(raw_class_clean, category_name)),
            "safety_warning": _extract_safety_warning(category_name, raw_class_clean)
        }
    else:
        # Honest fallback for unmapped classes
        cat_name = "Municipal solid waste"
        cat_info = get_category_info(cat_name)
        return {
            "supported": False,
            "raw_class": raw_class_clean,
            "object_identity": f"Detected Object ({raw_class_clean.title()})",
            "candidate_material": "Unknown / Mixed Composition",
            "suggested_category": cat_name,
            "category_info": cat_info,
            "item_id": "unmapped",
            "estimated_weight_kg": 0.05,
            "how_to_handle": _build_generic_guide(raw_class_clean, cat_name),
            "safety_warning": "Uncertain material identity. Verify packaging labels before disposal."
        }


def _extract_safety_warning(category_name: str, raw_class: str) -> Optional[str]:
    """Provides prominent safety warnings for hazardous, sharp, or battery-containing items."""
    if category_name == "Hazardous waste":
        return "SAFETY WARNING: Never crush, puncture, or burn hazardous items. Keep away from heat, water sources, and children."
    elif category_name == "Electronic waste":
        return "SAFETY WARNING: Lithium batteries can cause intense fires if punctured or crushed. Never place in household trash."
    elif category_name == "Biomedical and healthcare waste":
        return "SAFETY WARNING: Biohazard risk. Use puncture-proof containers for sharps. Never place loose needles in bags."
    elif category_name == "Liquid waste":
        return "SAFETY WARNING: Never pour oil, solvents, or chemicals into sinks, toilets, or storm drains."
    elif "knife" in raw_class or "scissors" in raw_class:
        return "SAFETY NOTE: Wrap sharp blades securely in cardboard before disposal to protect sanitation workers."
    return None


def _build_generic_guide(item_name: str, category_name: str) -> Dict[str, str]:
    """Provides structured 8-point guidance for generic or uncatalogued items."""
    cat_info = get_category_info(category_name)
    return {
        "what_is_it": f"{item_name.title()} classified under {category_name}.",
        "what_to_do_now": "Inspect the item to verify its condition, material marks, and cleanliness.",
        "which_bin": f"{cat_info['bin_color']} ({cat_info['bin_label']}).",
        "how_to_prepare": "Ensure the item is empty, clean, and free from food residue or liquid contaminants.",
        "what_to_avoid": "Do not mix with incompatible waste streams or place contaminated items into dry recycling.",
        "where_should_it_go": f"Follow local municipal schedule for {category_name} collection or drop-off.",
        "why_matters": "Accurate source separation increases community recycling yield and keeps landfills clean.",
        "citizen_action": "Check local municipal guidelines for item-specific drop-off options."
    }


def search_waste_guide(query: str = "", category: str = "", locality: str = "") -> List[Dict[str, Any]]:
    """
    Search and filter through the verified EcoSync Waste Guide catalog.
    Supports query text, waste category filter, and optional locality notes.
    """
    results = []
    q = query.strip().lower()

    for item_key, item_data in ITEM_GUIDES.items():
        # Filter by category if requested
        if category and item_data["category"] != category:
            continue

        # Filter by search query if requested
        match = True
        if q:
            searchable_text = (
                item_data["display_name"].lower() + " " +
                item_data["material"].lower() + " " +
                item_data["category"].lower() + " " +
                item_data["guide"]["what_is_it"].lower() + " " +
                item_data["guide"]["what_to_do_now"].lower() + " " +
                item_data["guide"]["which_bin"].lower()
            )
            match = q in searchable_text

        if match:
            item_copy = dict(item_data)
            item_copy["category_info"] = get_category_info(item_data["category"])
            if locality:
                item_copy["locality_note"] = f"Verified for {locality.title()} regional waste protocols."
            results.append(item_copy)

    return results
