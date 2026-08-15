import re
from dataclasses import dataclass, asdict

GOVERNMENT_WARNING = """GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems."""

@dataclass
class Check:
    field: str
    status: str
    expected: str
    evidence: str
    note: str
    def dict(self): return asdict(self)

def normalize(s):
    return re.sub(r"\s+", " ", s or "").strip().casefold()

def compact(s):
    return re.sub(r"[^a-z0-9]+", "", normalize(s))

def compare_text(field, expected, text):
    if not expected.strip():
        return Check(field, "REVIEW", "", "", "No application value supplied.")
    if compact(expected) in compact(text):
        return Check(field, "PASS", expected, expected, "Expected value detected.")
    exp = set(re.findall(r"[a-z0-9]+", normalize(expected)))
    got = set(re.findall(r"[a-z0-9]+", normalize(text)))
    coverage = len(exp & got) / max(len(exp), 1)
    if coverage >= .75:
        return Check(field, "REVIEW", expected, "", "Possible OCR/case variation; verify visually.")
    return Check(field, "MISSING", expected, "", "Expected value was not detected.")

def _phrase_coverage(phrase, text):
    """Token coverage tolerates small OCR errors while remaining deterministic."""
    expected = re.findall(r"[a-z0-9]+", normalize(phrase))
    observed = set(re.findall(r"[a-z0-9]+", normalize(text)))
    if not expected:
        return 0.0
    return sum(token in observed for token in expected) / len(expected)

def check_warning(text):
    # OCR commonly drops punctuation or misreads a character in long small-print warnings.
    # Require the distinctive all-caps heading plus strong coverage across every statutory clause.
    heading = re.search(r"\bGOVERNMENT\s+WARNING\b", text, flags=re.I) is not None
    clauses = [
        "According to the Surgeon General women should not drink alcoholic beverages during pregnancy",
        "because of the risk of birth defects",
        "Consumption of alcoholic beverages impairs your ability to drive a car",
        "or operate machinery",
        "and may cause health problems",
    ]
    coverages = [_phrase_coverage(c, text) for c in clauses]
    strong = all(score >= .80 for score in coverages)
    borderline = all(score >= .65 for score in coverages)

    if heading and strong:
        return Check("Government health warning", "PASS", GOVERNMENT_WARNING,
                     "GOVERNMENT WARNING: …",
                     "Required heading and prescribed warning language detected (OCR-tolerant match).")
    if heading and borderline:
        return Check("Government health warning", "REVIEW", GOVERNMENT_WARNING,
                     "GOVERNMENT WARNING: …",
                     "Warning appears substantially present, but OCR uncertainty requires visual review.")
    return Check("Government health warning", "MISSING", GOVERNMENT_WARNING, "",
                 "Required warning heading/language was not sufficiently detected.")

def evaluate_label(text, expected):
    checks = [
        compare_text("Brand name", expected.get("brand_name",""), text),
        compare_text("Class / type", expected.get("class_type",""), text),
        compare_text("Alcohol content", expected.get("alcohol_content",""), text),
        compare_text("Net contents", expected.get("net_contents",""), text),
        compare_text("Bottler / producer", expected.get("producer",""), text),
    ]
    if expected.get("imported"):
        checks.append(compare_text("Country of origin", expected.get("country_origin",""), text))
    checks.append(check_warning(text))
    return checks

def overall_status(checks):
    statuses={c.status for c in checks}
    return "ACTION NEEDED" if "MISSING" in statuses else ("HUMAN REVIEW" if "REVIEW" in statuses else "PASS")
