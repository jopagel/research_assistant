"""
Synthetic test data generation for agentic chatbot.
Generates 10 company profiles with varying attributes.
"""
import random
import json

industries = ["Automotive", "Tech", "Finance", "Healthcare", "Retail"]
products = ["Project Falcon", "Internal-Only", "EcoDrive", "SmartPay", "HealthPlus"]
risk_categories = ["Low", "Medium", "High"]

profiles = []
for i in range(10):
    name = f"Company_{i+1}"
    industry = random.choice(industries)
    prod = random.sample(products, 2)
    risk = random.choice(risk_categories)
    profiles.append({
        "name": name,
        "industry": industry,
        "products": prod,
        "risk_category": risk
    })

with open("synthetic_company_profiles.json", "w") as f:
    json.dump(profiles, f, indent=2)

print("Synthetic company profiles generated: synthetic_company_profiles.json")
