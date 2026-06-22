"""
utils.py — Utility Layer
Match Score Engine, Scholarship Insight Extractor, Export Functions, Smart Search.
"""

import re
import io
import datetime
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────
# 1. SCHOLARSHIP INSIGHT EXTRACTOR
# ─────────────────────────────────────────────

SCHOLARSHIP_TYPE_KEYWORDS = {
    "Merit": ["merit", "academic", "excellence", "top performer", "rank", "percentage", "marks"],
    "Government": ["government", "govt", "central", "state govt", "ministry", "national", "pm ", "pmss"],
    "Private": ["foundation", "trust", "corporate", "company", "private", "ngo"],
    "State": ["state", "rajya", "pradesh", "board", "state scholarship"],
    "International": ["international", "global", "foreign", "abroad", "overseas", "usa", "uk", "europe"],
    "Minority": ["minority", "muslim", "christian", "sikh", "buddhist", "zoroastrian"],
    "Disability": ["disability", "disabled", "handicapped", "pwd", "differently abled"],
    "Sports": ["sports", "athlete", "national games", "sports quota"],
}

AMOUNT_PATTERNS = [
    r'₹\s*[\d,]+(?:\.\d{1,2})?(?:\s*(?:lakh|lakhs|lac|thousand|crore))?',
    r'Rs\.?\s*[\d,]+(?:\.\d{1,2})?(?:\s*(?:lakh|lakhs|lac|thousand|crore))?',
    r'INR\s*[\d,]+(?:\.\d{1,2})?',
    r'\$\s*[\d,]+(?:\.\d{1,2})?',
    r'USD\s*[\d,]+(?:\.\d{1,2})?',
    r'\b[\d,]+\s*(?:per\s+(?:month|year|annum|semester))',
]

DEADLINE_PATTERNS = [
    r'\b(?:deadline|last\s+date|closing\s+date|due\s+date|apply\s+by|submission\s+date)\s*[:\-]?\s*'
    r'(?:\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4})',
    r'\b(?:apply\s+before|applications?\s+(?:due|close|deadline))\s*[:\-]?\s*'
    r'(?:\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})',
    r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\b',
    r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{4}\b',
    r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}\b',
]

ELIGIBILITY_KEYWORDS = [
    "eligible", "eligibility", "criteria", "requirement",
    "minimum", "must", "should", "income", "annual income",
    "family income", "cgpa", "percentage", "marks", "category",
    "caste", "sc", "st", "obc", "general", "minority",
]

DOCUMENT_KEYWORDS = [
    "document", "certificate", "proof", "submit", "attach",
    "upload", "required documents", "marksheet", "aadhar",
    "aadhaar", "income certificate", "caste certificate",
    "bonafide", "photo", "passport", "bank",
]


def extract_scholarship_type(text: str) -> str:
    """Detect scholarship type based on keyword matching."""
    text_lower = text.lower()
    type_scores = {}
    for stype, keywords in SCHOLARSHIP_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            type_scores[stype] = score

    if not type_scores:
        return "General"

    return max(type_scores, key=type_scores.get)


def extract_amounts(text: str) -> List[str]:
    """Extract all monetary amounts from text."""
    amounts = []
    for pattern in AMOUNT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        amounts.extend(matches)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for a in amounts:
        a_clean = a.strip()
        if a_clean.lower() not in seen:
            seen.add(a_clean.lower())
            unique.append(a_clean)

    return unique[:10]  # Return top 10


def extract_deadlines(text: str) -> List[str]:
    """Extract deadline/date information from text."""
    deadlines = []
    for pattern in DEADLINE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        deadlines.extend([m.strip() if isinstance(m, str) else m[0].strip() for m in matches])

    seen = set()
    unique = []
    for d in deadlines:
        if d.lower() not in seen and len(d) > 3:
            seen.add(d.lower())
            unique.append(d)

    return unique[:5]


def extract_eligibility_sentences(text: str, max_sentences: int = 8) -> List[str]:
    """Extract sentences containing eligibility-related information."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    eligibility = []
    for sent in sentences:
        sent_lower = sent.lower()
        if any(kw in sent_lower for kw in ELIGIBILITY_KEYWORDS):
            clean = sent.strip()
            if len(clean) > 20:
                eligibility.append(clean)

    return eligibility[:max_sentences]


def extract_required_documents(text: str) -> List[str]:
    """Extract required document mentions."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    docs = []
    for sent in sentences:
        sent_lower = sent.lower()
        if any(kw in sent_lower for kw in DOCUMENT_KEYWORDS):
            clean = sent.strip()
            if len(clean) > 15:
                docs.append(clean)

    return docs[:6]


def extract_all_insights(text: str) -> Dict:
    """
    Run all extractors on the document text.
    Returns a dict with all scholarship insights.
    """
    return {
        "scholarship_type": extract_scholarship_type(text),
        "amounts": extract_amounts(text),
        "deadlines": extract_deadlines(text),
        "eligibility": extract_eligibility_sentences(text),
        "required_documents": extract_required_documents(text),
    }


# ─────────────────────────────────────────────
# 2. MATCH SCORE ENGINE
# ─────────────────────────────────────────────

def compute_match_score(profile: Dict, insights: Dict, text: str) -> Dict:
    """
    Compute scholarship match score (0–100) based on student profile.

    Scoring breakdown:
    - Income match: 30 pts
    - CGPA match: 30 pts
    - Category match: 20 pts
    - Course relevance: 10 pts
    - State relevance: 10 pts

    Returns dict with total score and breakdown.
    """
    breakdown = {}
    total = 0

    text_lower = text.lower()

    # ── Income Score (30 pts) ──────────────────
    income = profile.get("income", 0)
    income_score = 0
    income_reason = ""

    # Try to detect income limit from text
    income_patterns = [
        r'(?:annual|family|household|parental)\s+income(?:[^0-9\n]*?)(?:below|less\s+than|not\s+exceeding|up\s+to|upto|limit|ceiling|criteria)\s*(?:is|should\s+be|must\s+be)?\s*[₹$]?\s*([\d,]+)',
        r'income\s+(?:limit|ceiling|criteria)\s*(?:is|should\s+be|must\s+be)?\s*[:\-]?\s*[₹$]?\s*([\d,]+)',
        r'([\d,]+)\s*(?:per\s+annum|lakhs?|year|annual|family\s+income)',
    ]
    detected_limit = None
    for pat in income_patterns:
        m = re.search(pat, text_lower)
        if m:
            try:
                detected_limit = int(m.group(1).replace(',', ''))
                break
            except Exception:
                continue

    if detected_limit:
        if income <= detected_limit:
            income_score = 30
            income_reason = f"✅ Income ₹{income:,} is within limit of ₹{detected_limit:,}"
        elif income <= detected_limit * 1.2:
            income_score = 15
            income_reason = f"⚠️ Income slightly above limit (₹{detected_limit:,})"
        else:
            income_score = 0
            income_reason = f"❌ Income ₹{income:,} exceeds limit ₹{detected_limit:,}"
    else:
        # No income requirement detected
        if income < 800000:
            income_score = 25
        elif income < 1500000:
            income_score = 15
        else:
            income_score = 10
        income_reason = f"ℹ️ No specific income limit found. Score based on profile (₹{income:,}/yr)"

    breakdown["Income"] = {"score": income_score, "max": 30, "reason": income_reason}
    total += income_score

    # ── CGPA Score (30 pts) ────────────────────
    cgpa = profile.get("cgpa", 0.0)
    cgpa_score = 0
    cgpa_reason = ""

    cgpa_patterns = [
        r'(?:minimum|min\.?|at\s+least)\s+(?:cgpa|gpa|grade\s+point)(?:[^0-9\n]*?)(\d+(?:\.\d+)?)',
        r'(?:cgpa|gpa|grade\s+point)(?:[^0-9\n]*?)(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*(?:or\s+above|and\s+above)?\s*(?:cgpa|gpa|grade\s+point)',
        r'(?:percentage|marks)(?:[^0-9\n]*?)(\d+)%?',
    ]
    detected_cgpa_min = None
    for pat in cgpa_patterns:
        m = re.search(pat, text_lower)
        if m:
            try:
                val = float(m.group(1))
                # Normalize: if percentage given, convert rough CGPA
                if val > 10:
                    val = val / 10
                detected_cgpa_min = val
                break
            except Exception:
                continue

    if detected_cgpa_min:
        if cgpa >= detected_cgpa_min:
            cgpa_score = 30
            cgpa_reason = f"✅ CGPA {cgpa} meets requirement of {detected_cgpa_min}"
        elif cgpa >= detected_cgpa_min - 0.5:
            cgpa_score = 15
            cgpa_reason = f"⚠️ CGPA {cgpa} slightly below requirement ({detected_cgpa_min})"
        else:
            cgpa_score = 0
            cgpa_reason = f"❌ CGPA {cgpa} below required {detected_cgpa_min}"
    else:
        if cgpa >= 8.5:
            cgpa_score = 30
        elif cgpa >= 7.5:
            cgpa_score = 22
        elif cgpa >= 6.5:
            cgpa_score = 15
        elif cgpa >= 5.5:
            cgpa_score = 8
        else:
            cgpa_score = 0
        cgpa_reason = f"ℹ️ No minimum CGPA found. Score based on profile CGPA {cgpa}"

    breakdown["CGPA"] = {"score": cgpa_score, "max": 30, "reason": cgpa_reason}
    total += cgpa_score

    # ── Category Score (20 pts) ────────────────
    category = profile.get("category", "").upper()
    cat_score = 0
    cat_reason = ""

    priority_categories = {
        "SC": ["sc", "scheduled caste", "sc/st"],
        "ST": ["st", "scheduled tribe", "sc/st"],
        "OBC": ["obc", "other backward", "backward class"],
        "EWS": ["ews", "economically weaker"],
        "MINORITY": ["minority", "muslim", "christian", "sikh"],
        "GENERAL": ["general", "open"],
    }

    def has_cat(cat_keywords):
        for kw in cat_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return True
        return False

    user_cat_keywords = priority_categories.get(category, [])
    user_cat_mentioned = has_cat(user_cat_keywords)

    other_cats_mentioned = []
    for cat_key, keywords in priority_categories.items():
        if cat_key != category and cat_key != "GENERAL":
            if has_cat(keywords):
                other_cats_mentioned.append(cat_key)

    if user_cat_mentioned:
        cat_score = 20
        cat_reason = f"✅ Your category ({category}) is explicitly targeted/eligible"
    elif not other_cats_mentioned:
        cat_score = 15
        cat_reason = "ℹ️ No specific category restriction detected. Open to all"
    else:
        if category == "GENERAL":
            cat_score = 5
            cat_reason = f"⚠️ Scholarship targets {', '.join(other_cats_mentioned)}; you are General"
        else:
            cat_score = 8
            cat_reason = f"⚠️ Scholarship targets {', '.join(other_cats_mentioned)}; you are {category}"

    breakdown["Category"] = {"score": cat_score, "max": 20, "reason": cat_reason}
    total += cat_score

    # ── Course Score (10 pts) ──────────────────
    course = profile.get("course", "").lower()
    course_score = 0
    course_reason = ""

    if course:
        course_words = re.findall(r'\b\w{3,}\b', course)
        matches = sum(1 for w in course_words if w in text_lower)
        if matches >= 2:
            course_score = 10
            course_reason = f"✅ Course '{profile.get('course')}' matches document"
        elif matches == 1:
            course_score = 5
            course_reason = f"⚠️ Partial course match"
        else:
            # Check for general terms
            if any(t in text_lower for t in ["all courses", "any stream", "all streams", "undergraduate", "postgraduate"]):
                course_score = 8
                course_reason = "✅ Scholarship is open to all courses"
            else:
                course_score = 2
                course_reason = f"⚠️ Course '{profile.get('course')}' not explicitly mentioned"
    else:
        course_score = 5
        course_reason = "ℹ️ No course specified in profile"

    breakdown["Course"] = {"score": course_score, "max": 10, "reason": course_reason}
    total += course_score

    # ── State Score (10 pts) ───────────────────
    state = profile.get("state", "").lower()
    state_score = 0
    state_reason = ""

    if state:
        if state in text_lower:
            state_score = 10
            state_reason = f"✅ State '{profile.get('state')}' mentioned in document"
        elif any(t in text_lower for t in ["all india", "national", "pan india", "all states"]):
            state_score = 8
            state_reason = "✅ National scholarship — all states eligible"
        else:
            state_score = 3
            state_reason = f"⚠️ State '{profile.get('state')}' not found in document"
    else:
        state_score = 5
        state_reason = "ℹ️ No state specified in profile"

    breakdown["State"] = {"score": state_score, "max": 10, "reason": state_reason}
    total += state_score

    # ── Final Score ────────────────────────────
    total = min(100, max(0, total))
    grade = "Excellent" if total >= 80 else "Good" if total >= 60 else "Moderate" if total >= 40 else "Low"

    return {
        "total_score": total,
        "grade": grade,
        "breakdown": breakdown,
        "recommendation": _get_recommendation(total),
    }


def _get_recommendation(score: int) -> str:
    if score >= 80:
        return "🎯 Highly recommended! You are an excellent match for this scholarship."
    elif score >= 60:
        return "✅ Good match! Consider applying — you meet most criteria."
    elif score >= 40:
        return "⚠️ Partial match. Review eligibility carefully before applying."
    else:
        return "❌ Low match. You may not meet the key eligibility requirements."


# ─────────────────────────────────────────────
# 3. EXPORT FUNCTIONS
# ─────────────────────────────────────────────

def export_summary_txt(
    filename: str,
    metadata: Dict,
    insights: Dict,
    match_result: Optional[Dict] = None,
    profile: Optional[Dict] = None,
) -> bytes:
    """Generate a TXT summary report."""
    lines = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 60)
    lines.append("     AI SCHOLARSHIP ASSISTANT PRO — ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {timestamp}")
    lines.append(f"File: {filename}")
    lines.append("")

    # Document Stats
    lines.append("── DOCUMENT STATISTICS ──────────────────────────────")
    lines.append(f"  Pages      : {metadata.get('page_count', 'N/A')}")
    lines.append(f"  Words      : {metadata.get('word_count', 'N/A'):,}" if isinstance(metadata.get('word_count'), int) else f"  Words      : {metadata.get('word_count', 'N/A')}")
    lines.append(f"  Characters : {metadata.get('char_count', 'N/A'):,}" if isinstance(metadata.get('char_count'), int) else f"  Characters : {metadata.get('char_count', 'N/A')}")
    lines.append(f"  File Size  : {metadata.get('file_size_kb', 'N/A')} KB")
    lines.append(f"  Chunks     : {metadata.get('num_chunks', 'N/A')}")
    lines.append("")

    # Student Profile
    if profile:
        lines.append("── STUDENT PROFILE ──────────────────────────────────")
        lines.append(f"  Name     : {profile.get('name', 'N/A')}")
        lines.append(f"  Course   : {profile.get('course', 'N/A')}")
        lines.append(f"  CGPA     : {profile.get('cgpa', 'N/A')}")
        lines.append(f"  Category : {profile.get('category', 'N/A')}")
        lines.append(f"  Income   : ₹{profile.get('income', 0):,}/year")
        lines.append(f"  State    : {profile.get('state', 'N/A')}")
        lines.append("")

    # Match Score
    if match_result:
        lines.append("── MATCH SCORE ──────────────────────────────────────")
        lines.append(f"  Total Score  : {match_result['total_score']}/100")
        lines.append(f"  Grade        : {match_result['grade']}")
        lines.append(f"  Recommendation: {match_result['recommendation']}")
        lines.append("")
        lines.append("  Score Breakdown:")
        for factor, data in match_result["breakdown"].items():
            lines.append(f"    {factor}: {data['score']}/{data['max']} — {data['reason']}")
        lines.append("")

    # Scholarship Insights
    lines.append("── SCHOLARSHIP INSIGHTS ─────────────────────────────")
    lines.append(f"  Type: {insights.get('scholarship_type', 'N/A')}")
    lines.append("")

    amounts = insights.get("amounts", [])
    lines.append(f"  💰 Amount(s) Found ({len(amounts)}):")
    for a in amounts:
        lines.append(f"    • {a}")
    lines.append("")

    deadlines = insights.get("deadlines", [])
    lines.append(f"  📅 Deadline(s) Found ({len(deadlines)}):")
    for d in deadlines:
        lines.append(f"    • {d}")
    lines.append("")

    eligibility = insights.get("eligibility", [])
    lines.append(f"  ✅ Eligibility Criteria ({len(eligibility)}):")
    for i, e in enumerate(eligibility, 1):
        lines.append(f"    {i}. {e}")
    lines.append("")

    docs = insights.get("required_documents", [])
    lines.append(f"  📋 Required Documents ({len(docs)}):")
    for i, d in enumerate(docs, 1):
        lines.append(f"    {i}. {d}")
    lines.append("")

    lines.append("=" * 60)
    lines.append("         Generated by AI Scholarship Assistant PRO")
    lines.append("=" * 60)

    return "\n".join(lines).encode("utf-8")


def export_eligibility_report_txt(
    insights: Dict,
    match_result: Optional[Dict] = None,
    profile: Optional[Dict] = None,
) -> bytes:
    """Generate eligibility-focused report."""
    lines = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 60)
    lines.append("       ELIGIBILITY REPORT — AI SCHOLARSHIP ASSISTANT PRO")
    lines.append("=" * 60)
    lines.append(f"Generated: {timestamp}")
    lines.append("")

    if profile:
        lines.append("── STUDENT ───────────────────────────────────────────")
        lines.append(f"  {profile.get('name', 'Student')} | {profile.get('course', '')} | CGPA: {profile.get('cgpa', '')} | {profile.get('category', '')}")
        lines.append("")

    if match_result:
        score = match_result["total_score"]
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        lines.append(f"  MATCH SCORE: [{bar}] {score}/100 ({match_result['grade']})")
        lines.append(f"  {match_result['recommendation']}")
        lines.append("")
        for factor, data in match_result["breakdown"].items():
            lines.append(f"  {factor}: {data['score']}/{data['max']}")
            lines.append(f"    → {data['reason']}")
        lines.append("")

    eligibility = insights.get("eligibility", [])
    lines.append("── ELIGIBILITY REQUIREMENTS ─────────────────────────")
    if eligibility:
        for i, e in enumerate(eligibility, 1):
            lines.append(f"  {i}. {e}")
    else:
        lines.append("  No specific eligibility criteria extracted.")
    lines.append("")

    docs = insights.get("required_documents", [])
    lines.append("── REQUIRED DOCUMENTS ───────────────────────────────")
    if docs:
        for i, d in enumerate(docs, 1):
            lines.append(f"  {i}. {d}")
    else:
        lines.append("  No specific documents mentioned.")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines).encode("utf-8")


def highlight_text(text: str, keyword: str) -> str:
    """Wrap keyword matches in markdown bold for display."""
    if not keyword:
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group()}**", text)
