# Governance Regression Suite v0.1

## Objective

Validate whether the custom Microsoft Foundry evaluator can distinguish compliant Management Brief outputs from known governance failures.

## Custom Evaluator

Evidence Sufficiency & Association

## Platform

Microsoft Foundry

## Dataset

governance_regression_suite_v0.1

## Test Cases

### CASE_GOV_PASS_001

Expected:
PASS

Actual:
PASS

Purpose:
Verify that a correctly grounded response with complete evidence coverage is not incorrectly rejected.

---

### CASE_GOV_FAIL_EVIDENCE_001

Expected:
FAIL

Actual:
FAIL

Purpose:
Verify detection of incomplete evidence coverage.

The response combined current-period and previous-period metrics but did not cite all evidence records required to support the complete statement.

---

### CASE_GOV_FAIL_ASSOCIATION_001

Expected:
FAIL

Actual:
FAIL

Purpose:
Verify detection of unsupported associations.

The response linked a general missing-quantity issue to specific products even though the trusted context did not establish that relationship.

## Foundry Pass Rate

1 / 3

33%

This percentage represents the proportion of responses that passed the governance evaluator.

It is not evaluator accuracy.

## Regression Accuracy

3 / 3 expected outcomes matched actual outcomes.

Regression accuracy:

100%

## Conclusion

The custom evaluator successfully distinguished between:

* a compliant evidence-grounded response;
* an evidence-insufficient response;
* an unsupported-association response.

The governance regression suite therefore met its intended acceptance criteria.

No additional synthetic test expansion is required for the current portfolio scope.
