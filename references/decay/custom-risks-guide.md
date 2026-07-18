# Custom Risks Loading Guide

When `.decay-review.yaml` contains a `custom_risks` mapping, this guide specifies how these risks are loaded and scanned. Custom risks use `Cx` codes (C1, C2, …) — they do not conflict with the standard R1–R6 and T1–T6 namespaces.

---

## Loading

1. For each entry in `custom_risks`, verify it contains:
   - `name` — non-empty string
   - `question` — the diagnostic question to ask
   - `symptoms` — non-empty list of symptom patterns
   - `severity` — a mapping containing at least one of: `critical`, `warning`, `suggestion`

2. Register each valid entry as a `Cx` code, alongside R1–R6 / T1–T6. Once loaded, `Cx` codes become valid targets for `disable`, `focus`, and `severity` fields in the same config file.

3. Report any validation errors as config warnings (do not abort the review):
   - Missing required field: `"Config warning: C1 missing 'symptoms'"`
   - Invalid code format (must be `C` followed by a number): skip, log the error
   - Code conflicts with R/T namespace: skip, log the error

---

## Scanning

During analysis, treat each custom risk as an additional step after the standard flow:

- Use `question` as the diagnostic question
- Use `symptoms` as the symptom search list
- Use the `severity` mapping for tier classification
- Apply the Iron Law: the `Source` field should be `"[Project-defined risk] — <risk name>"`
- Include custom risk findings in the Health Score (deduction rules are the same as R/T codes)
- In the report, custom findings appear under the **### Project-Specific Risks** sub-heading, after the standard findings

---

## Configuration Validation Addendum

The following codes are valid in `disable`, `focus`, and `severity`:
- Standard: `R1`–`R6`, `T1`–`T6`
- Custom: any `Cx` code defined in `custom_risks`
- Any other code: skip and emit `"Config warning: X is not a valid risk code"`
