from .engine import merge_entities

RULES = {
    "PM-KISAN": {"category": "Agriculture", "requires": ["farmer_status", "land_ownership", "state"], "checks": ["farmer"]},
    "Pradhan Mantri Fasal Bima Yojana": {"category": "Agriculture", "requires": ["farmer_status", "state", "purpose"], "checks": ["farmer", "crop"]},
    "Kisan Credit Card": {"category": "Finance", "requires": ["farmer_status", "state", "purpose"], "checks": ["farmer", "finance_or_farming"]},
    "Pradhan Mantri Mudra Yojana": {"category": "Business", "requires": ["occupation", "state", "purpose"], "checks": ["business"]},
    "Pradhan Mantri Awas Yojana": {"category": "Housing", "requires": ["state", "income_range", "purpose"], "checks": ["housing"]},
    "Pradhan Mantri Jan-Dhan Yojana": {"category": "Finance", "requires": ["state", "age"], "checks": ["finance"]},
}

def rule_match(name, context):
    rule = RULES.get(name, {"requires": [], "checks": []})
    reasons, missing = [], []
    if context.get("farmer_status") in ("Yes", "Farmer") and "farmer" in rule["checks"]:
        reasons.append("Farmer status")
    if context.get("purpose") == "Crop loss / damage" and "crop" in rule["checks"]:
        reasons.append("Crop-loss need")
    if context.get("purpose") in ("Seeds / farming inputs", "Agricultural loan") and "finance_or_farming" in rule["checks"]:
        reasons.append("Agricultural financial need")
    if context.get("assistance_type") == "Financial" and "finance_or_farming" in rule["checks"]:
        reasons.append("Financial / farming need")
    if context.get("occupation") and context.get("occupation").lower() in ("business", "shop owner", "entrepreneur") and "business" in rule["checks"]:
        reasons.append("Business purpose")
    if context.get("assistance_type") == "Business" and "business" in rule["checks"]:
        reasons.append("Business assistance")
    if context.get("assistance_type") == "Finance" and "finance" in rule["checks"]:
        reasons.append("Financial-service need")
    if context.get("assistance_type") == "Housing" and "housing" in rule["checks"]:
        reasons.append("Housing need")
    if context.get("purpose") in ("Housing", "house", "home") and "housing" in rule["checks"]:
        reasons.append("Housing need")
    for field in rule["requires"]:
        if not context.get(field): missing.append(field)
    # A contextual match is useful even when some fields are still missing.
    return reasons, missing

def evaluate_schemes(schemes, profile=None, answers=None):
    context = merge_entities(profile or {}, answers or {})
    results=[]
    for scheme in schemes:
        reasons, missing = rule_match(scheme.name, context)
        # Category-level evidence gives a neutral match explanation without inventing eligibility.
        if not reasons:
            cat=scheme.category.lower()
            if context.get("assistance_type") and context["assistance_type"].lower() in cat:
                reasons.append(f"{scheme.category} assistance")
            if context.get("occupation") == "Farmer" and scheme.category == "Agriculture":
                reasons.append("Farmer profile")
        if reasons:
            results.append({
                "id": scheme.id,
                "name": scheme.name,
                "category": scheme.category,
                "why_match": list(dict.fromkeys(reasons)),
                "missing_information": missing,
                "potential_eligibility": scheme.eligibility,
                "benefits": scheme.benefits,
                "documents": scheme.documents,
                "application_procedure": scheme.application_procedure,
                "official_url": scheme.official_url,
                "verification_notes": scheme.verification_notes,
                "disclaimer": "You may be eligible based on the information provided. Please verify current eligibility on the official government portal."
            })
    # Evidence-first ordering: matches with more concrete reasons before generic category suggestions.
    results.sort(key=lambda x: (len(x["why_match"]), -len(x["missing_information"])), reverse=True)
    return results[:6]
