# Custom Governance Evaluator v0.1

## Evaluator

Evidence Sufficiency & Association

## Platform

Microsoft Foundry

## Evaluation Type

Prompt-based custom evaluator

## Scoring Method

Binary

## Dataset

semantic_eval_dataset_v0.1

## Expected Result

FAIL

## Actual Result

FAIL

## Detected Issue

The evaluator correctly identified incomplete evidence coverage in INSIGHT_002.

The statement referenced current-period values and previous-period comparison values but cited only EV_PERIOD_001.

Current-period values were supported by EV_OVERALL_001.

## Governance Conclusion

The custom evaluator successfully detected a governance issue that was not identified by the built-in Groundedness and Relevance evaluators.

This demonstrates that general semantic evaluation must be supplemented with domain-specific governance controls.

## Evaluation Cost Signal

Prompt tokens: 3584  
Completion tokens: 494  
Total tokens: 4078

Judge model:
gpt-5-mini-2025-08-07