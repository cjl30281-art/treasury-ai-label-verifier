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
    return re.sub(r"\\s+", " ", s or "").strip().casefold()

def compact(s):
    return re.sub(r"[^a-z0-9]+", "", normalize(s))

def compare_text(field, expected, text):
    if not expected.strip():
        return Check(field, "REVIEW", "", "", "No application value supplied.")
    if compact(expected) in compact(text):
        return Check(field, "PASS", expected, expected, "Expected value detected.")
    # Conservative token coverage: only routes plausible OCR variants to review.
    exp = set(re.findall(r"[a-z0-9]+", normalize(expected)))
    got = set(re.findall(r"[a-z0-9]+", normalize(text)))
    coverage = len(exp & got) / max(len(exp), 1)
    if coverage >= .75:
        return Check(field, "REVIEW", expected, "", "Possible OCR/case variation; verify visually.")
    return Check(field, "MISSING", expected, "", "Expected value was not detected.")

def check_warning(text):
    heading = re.search(r"GOVERNMENT\\s+WARNING\\s*:", text) is not None
    phrases = ["According to the Surgeon General",
               "women should not drink alcoholic beverages during pregnancy",
               "risk of birth defects",
               "Consumption of alcoholic beverages impairs your ability to drive a car",
               "operate machinery", "may cause health problems"]
    missing = [p for p in phrases if compact(p) not in compact(text)]
    if heading and not missing:
        return Check("Government health warning","PASS",GOVERNMENT_WARNING,"GOVERNMENT WARNING: …",
                     "Required heading and prescribed language detected.")
    if not missing:
        return Check("Government health warning","REVIEW",GOVERNMENT_WARNING,"",
                     "Language appears present; required all-caps heading was not confirmed.")
    return Check("Government health warning","MISSING",GOVERNMENT_WARNING,"",
                 "Required warning language was incomplete or not detected.")

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
