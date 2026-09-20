import re
from sqlalchemy.orm import Session
from .models import Scheme, Message

HINDI_MARKERS = ["मुझे", "चाहिए", "किसान", "योजना", "सरकारी", "मदद", "आर्थिक", "दस्तावेज", "खेती"]
MARATHI_MARKERS = ["मला", "हवी", "शेतकरी", "शेतकऱ्यांना", "शेतकऱ्यांसाठी", "योजना", "मदत", "कागदपत्र", "शेती"]
ROMAN_MARATHI = ["mala", "havi", "shetkari", "shetkary", "madat", "sheti", "aahe", "pahije", "shetkar"]
ROMAN_HINDI = ["mujhe", "chahiye", "kisan", "kisanon", "yojana", "madad", "arthik", "hai", "ke", "kheti"]


def detect_language(text: str) -> str:
    t = text.lower()
    if any("\u0900" <= c <= "\u097f" for c in text):
        hm = sum(1 for x in HINDI_MARKERS if x in text)
        mm = sum(1 for x in MARATHI_MARKERS if x in text)
        return "Marathi" if mm > hm else "Hindi"
    words = set(re.findall(r"[a-z]+", t))
    rm = sum(x in words for x in ROMAN_MARATHI)
    rh = sum(x in words for x in ROMAN_HINDI)
    if rm or rh:
        return "Roman Marathi" if rm > rh else "Roman Hindi"
    return "English"


def detect_intent(text: str) -> str:
    t = text.lower()
    # Specific domain cues take precedence over the generic word “scheme”.
    if any(x in t for x in ["farmer", "farming", "seeds", "agriculture", "kisan", "kisanon", "किसान", "खेती", "शेतकरी", "शेतकऱ्य", "शेती", "shetkari", "shetkary", "shetkar"]):
        if any(x in t for x in ["crop damaged", "crop loss", "heavy rain", "फसल", "पीक", "पाऊस", "damaged"]):
            return "crop_loss"
        return "agriculture_assistance"
    checks = [
        ("documents", ["document", "documents", "दस्तावेज", "कागदपत्र"]),
        ("application_process", ["apply", "application", "how do i", "कैसे", "अर्ज"]),
        ("crop_loss", ["crop damaged", "crop loss", "heavy rain", "फसल", "पीक", "पाऊस", "damaged"]),
        ("business_assistance", ["business", "shop", "व्यवसाय", "दुकान", "startup"]),
        ("housing_assistance", ["house", "housing", "home", "घर", "आवास"]),
        ("cooperative_services", ["cooperative", "सहकारी", "सहकार"]),
        ("financial_assistance", ["loan", "money", "financial", "finance", "पैसे", "आर्थिक", "कर्ज", "अर्थिक", "madat", "madad"]),
        ("agriculture_assistance", ["farmer", "farming", "seeds", "agriculture", "kisan", "kisanon", "किसान", "खेती", "शेतकरी", "शेतकऱ्य", "शेती", "shetkari", "shetkary", "shetkar"]),
        ("eligibility", ["eligible", "eligibility", "पात्र", "पात्रता"]),
        ("benefits", ["benefit", "benefits", "लाभ", "फायदा"]),
        ("scheme_search", ["scheme", "schemes", "योजना", "yojana"]),
    ]
    for intent, terms in checks:
        if any(x in t for x in terms):
            return intent
    return "general_information"


def extract_entities(text: str) -> dict:
    entities = {}
    age = re.search(r"\b(1[8-9]|[2-9]\d|1[0-2]\d)\b", text)
    if age:
        entities["age"] = int(age.group())
    state_patterns = {
        "Maharashtra": r"maharashtra|महाराष्ट्र",
        "Gujarat": r"gujarat|गुजरात",
        "Karnataka": r"karnataka|कर्नाटक",
        "Madhya Pradesh": r"madhya\s+pradesh|मध्य प्रदेश",
        "Rajasthan": r"rajasthan|राजस्थान",
        "Uttar Pradesh": r"uttar\s+pradesh|उत्तर प्रदेश",
    }
    for state, pattern in state_patterns.items():
        if re.search(pattern, text, re.I):
            entities["state"] = state
            break
    if re.search(r"farmer|kisan|किसान|शेतकरी|शेतकऱ्य|शेतकऱ्यांसाठी|shetkari|shetkary", text, re.I):
        entities["occupation"] = "Farmer"
        entities["farmer_status"] = "Yes"
    if re.search(r"seed|seeds|बीज|बियाणे", text, re.I):
        entities["purpose"] = "Seeds / farming inputs"
    if re.search(r"crop|फसल|पीक|rain|पाऊस|बारिश|heavy rain", text, re.I):
        entities["purpose"] = "Crop loss / damage"
    if re.search(r"loan|money|financial|आर्थिक|पैसे|कर्ज|madat|madad", text, re.I):
        entities["assistance_type"] = "Financial"
    if re.search(r"business|shop|व्यवसाय|दुकान", text, re.I):
        entities["assistance_type"] = "Business"
    return entities


def merge_entities(*sources: dict | None) -> dict:
    result = {}
    for source in sources:
        if source:
            result.update({k: v for k, v in source.items() if v not in (None, "")})
    return result


def conversation_context(db: Session, conversation_id: int | None) -> dict:
    if not conversation_id:
        return {}
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.id).all()
    context = {}
    for message in messages:
        if message.role == "user":
            context = merge_entities(context, extract_entities(message.text))
    return context


def missing_followup(intent: str, context: dict) -> str | None:
    if intent in {"agriculture_assistance", "crop_loss"}:
        if not context.get("state"):
            return "state"
        if not context.get("assistance_type") and intent != "crop_loss":
            return "assistance_type"
    if intent == "housing_assistance" and not context.get("state"):
        return "state"
    if intent == "business_assistance" and not context.get("state"):
        return "state"
    return None


def followup_response(language: str, field: str) -> str:
    prompts = {
        "state": {
            "English": "Which state are you from? This helps me narrow the relevant government services.",
            "Hindi": "आप किस राज्य से हैं? इससे मैं संबंधित सरकारी सेवाओं को बेहतर तरीके से बता सकूँगा।",
            "Marathi": "तुम्ही कोणत्या राज्यातून आहात? त्यामुळे मी संबंधित सरकारी सेवा अधिक अचूकपणे सांगू शकतो."
        },
        "assistance_type": {
            "English": "What kind of farming help do you need?",
            "Hindi": "आपको खेती के लिए किस प्रकार की सहायता चाहिए?",
            "Marathi": "तुम्हाला शेतीसाठी कोणत्या प्रकारची मदत हवी आहे?"
        }
    }
    base = language if language in prompts[field] else ("Hindi" if "Hindi" in language else "Marathi" if "Marathi" in language else "English")
    return prompts[field][base]


def match_schemes(db: Session, text: str, profile: dict | None = None, context: dict | None = None):
    context = merge_entities(context, profile, extract_entities(text))
    intent = detect_intent(text)
    # Context-aware follow-ups such as “what documents do I need?” inherit the prior domain.
    effective_intent = intent
    if intent == "documents" and context.get("occupation") == "Farmer":
        effective_intent = "agriculture_assistance"
    terms = set(re.findall(r"[a-z]+", text.lower()))
    if context.get("purpose"):
        terms.update(re.findall(r"[a-z]+", str(context["purpose"]).lower()))
    scored = []
    for s in db.query(Scheme).filter(Scheme.active == True).all():
        hay = " ".join([s.name, s.category, s.description, " ".join(s.benefits), " ".join(s.eligibility)]).lower()
        score = sum(1 for term in terms if len(term) > 2 and term in hay)
        if effective_intent in ("agriculture_assistance", "crop_loss") and s.category == "Agriculture": score += 5
        if effective_intent == "housing_assistance" and s.category == "Housing": score += 5
        if effective_intent == "business_assistance" and s.category in ("Business", "Finance"): score += 5
        if effective_intent == "financial_assistance" and s.category in ("Finance", "Agriculture", "Business"): score += 3
        if context.get("state") and s.state_scope.lower() not in ("all india", "india-wide") and context["state"].lower() not in s.state_scope.lower():
            score -= 1
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:4]]


def make_response(language: str, intent: str, entities: dict, schemes: list[Scheme]) -> str:
    if not schemes:
        if language in ("Hindi", "Roman Hindi"): return "मैं आपकी सहायता कर सकता हूँ। कृपया अपनी जरूरत, राज्य और सहायता का प्रकार बताएं।"
        if language in ("Marathi", "Roman Marathi"): return "मी तुम्हाला मदत करू शकतो. कृपया तुमची गरज, राज्य आणि मदतीचा प्रकार सांगा."
        return "I can help narrow this down. Please tell me your state and the type of assistance you need."
    names = ", ".join(s.name for s in schemes[:3])
    if intent == "documents":
        docs = []
        for s in schemes[:2]:
            docs.extend(s.documents[:4])
        docs = list(dict.fromkeys(docs))[:6]
        if language in ("Hindi", "Roman Hindi"):
            return f"आपके संदर्भ में {names} से जुड़े दस्तावेज़ उपयोगी हो सकते हैं: {', '.join(docs)}। दस्तावेज़ों की वर्तमान सूची आधिकारिक पोर्टल पर सत्यापित करें।"
        if language in ("Marathi", "Roman Marathi"):
            return f"तुमच्या संदर्भात {names} साठी हे कागदपत्र उपयोगी ठरू शकतात: {', '.join(docs)}. सध्याची कागदपत्रांची यादी अधिकृत पोर्टलवर तपासा."
        return f"For your context, documents related to {names} may include: {', '.join(docs)}. Verify the current document list on the official government portal."
    if language in ("Hindi", "Roman Hindi"):
        return f"आपकी जानकारी के आधार पर {names} जैसी योजनाएं प्रासंगिक हो सकती हैं। यह केवल मार्गदर्शन है; वर्तमान पात्रता आधिकारिक सरकारी पोर्टल पर सत्यापित करें।"
    if language in ("Marathi", "Roman Marathi"):
        return f"तुमच्या माहितीनुसार {names} सारख्या योजना संबंधित असू शकतात. हे फक्त मार्गदर्शन आहे; सध्याची पात्रता अधिकृत सरकारी पोर्टलवर तपासा."
    return f"Based on the information provided, schemes such as {names} may be relevant. This is guidance only; please verify current eligibility on the official government portal."
