from label_verifier.validators import evaluate_label, overall_status
GOOD="""OLD TOM DISTILLERY
Kentucky Straight Bourbon Whiskey
45% Alc./Vol. (90 Proof)
750 mL
Bottled by Old Tom Distillery, Louisville, KY
GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects.
(2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems."""
EXPECTED={"brand_name":"OLD TOM DISTILLERY","class_type":"Kentucky Straight Bourbon Whiskey",
"alcohol_content":"45% Alc./Vol. (90 Proof)","net_contents":"750 mL","producer":"Old Tom Distillery",
"imported":False,"country_origin":""}
def test_complete_label_passes():
    assert overall_status(evaluate_label(GOOD,EXPECTED))=="PASS"
def test_missing_warning_needs_action():
    assert overall_status(evaluate_label(GOOD.split("GOVERNMENT WARNING:")[0],EXPECTED))=="ACTION NEEDED"
