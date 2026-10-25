# Microsoft Foundry Baseline Experiment v0.2

## Objective

Evaluate whether improved evidence design and stricter output controls resolve the issues identified in baseline experiment v0.1.

## Controlled Variables

Model:
gpt-5-mini

Model changed from v0.1:
No

## Changed Variables

Input schema:
management_brief_input_example_v0.2.json

System prompt:
management_brief_system_v0.2.md

## Key Changes from v0.1

- Added evidence IDs to overall performance.
- Added evidence ID to period comparison.
- Added explicit metric-availability evidence.
- Prohibited invented evidence IDs.
- Added evidence-completeness requirements.
- Added unsupported-association controls.
- Strengthened causality rules.
- Defined confidence-level semantics.
- Required machine-readable JSON output.
- Added explicit pre-response self-check instructions.

## Evaluation Criteria

1. JSON format compliance
2. Evidence-reference validity
3. Evidence completeness
4. Numeric consistency
5. Unsupported-metric avoidance
6. Unsupported-association avoidance
7. Causal-claim discipline
8. Recommendation safety
9. Confidence consistency
10. Human-review status compliance

## Result

## Result

Status:
NEEDS_REVISION

Control checks passed:
7 / 10

## Improvements from v0.1

* Output was valid structured JSON.
* No fabricated evidence identifiers were observed.
* All referenced evidence IDs existed in the supplied context.
* Unsupported commercial metrics were not inferred.
* Numeric values remained grounded in the supplied analytics context.
* Causal claims remained appropriately constrained.
* Recommendations remained advisory.
* Human-review requirements were correctly preserved.

## Remaining Issues

### 1. Evidence completeness

A statement comparing current and previous-period performance used facts from both `EV_OVERALL_001` and `EV_PERIOD_001`, but referenced only `EV_PERIOD_001`.

Evidence validity therefore passed, while evidence completeness failed.

### 2. Confidence consistency

Some direct quantitative observations were assigned MEDIUM confidence even though the confidence policy defines direct evidence-supported observations as HIGH confidence.

### 3. Unsupported association

The model associated a general missing-quantity data-quality issue with specific products even though the context did not identify which product was affected.

This violated the unsupported-association rule.

### 4. Evidence-semantic mismatch

One caveat referenced metric-availability evidence to support a statement about AI usage-policy compliance, although that evidence did not support the entire claim.

### 5. Scope wording

Regional ranking language could be interpreted as applying to all regions even though the synthetic context contained only a subset of regional records.

## Regression Conclusion

Version 0.2 materially improved structured-output compliance, evidence-reference validity, grounding and governance behavior compared with version 0.1.

However, prompt-only controls were insufficient to guarantee:

* complete evidence coverage;
* confidence-policy compliance;
* prevention of unsupported associations;
* semantic alignment between statements and cited evidence.

The next implementation stage will introduce deterministic automated validation rather than relying solely on prompt instructions and manual review.

