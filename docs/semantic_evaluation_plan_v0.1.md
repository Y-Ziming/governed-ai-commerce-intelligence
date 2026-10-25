# Semantic Evaluation Plan v0.1

## Purpose

Evaluate whether AI-generated Management Briefs are semantically grounded in the trusted analytics context and remain relevant to the management decision-support task.

## Evaluation Architecture

Layer 1 — Deterministic Validation

Purpose:
Validate hard structural and governance controls.

Implemented controls include:

- strict JSON parsing
- contract version
- reporting period
- report status
- evidence ID validity
- allowed confidence values
- allowed action types
- human-review status
- used-evidence reconciliation

Layer 2 — Semantic Evaluation

Purpose:
Evaluate whether the meaning of the generated response is supported by the trusted context.

Initial Microsoft Foundry evaluators:

- Groundedness
- Relevance

## Groundedness

Question:

Is the generated Management Brief supported by the supplied trusted analytics context without introducing unsupported factual claims?

Project target:

Prefer score >= 4 / 5.

A lower score requires investigation before release.

## Relevance

Question:

Does the generated output remain focused on the requested management decision-support task?

Project target:

Prefer score >= 4 / 5.

## Known Limitations of Built-in Evaluation

Built-in semantic evaluation does not replace domain-specific governance checks.

The following project-specific controls require custom evaluation:

- evidence completeness
- evidence-to-statement semantic alignment
- unsupported association detection
- confidence-policy consistency
- recommendation-policy compliance

These controls will be implemented as custom evaluators in a later evaluation layer.

## Evaluation Dataset

Version:
semantic_eval_dataset_v0.1

Initial case count:
1

Data type:
Synthetic

Real company data:
No

## Evaluation Strategy

The first run is a pipeline smoke test.

The evaluation dataset will later be expanded to include:

- normal performance scenarios
- declining-product scenarios
- missing-data scenarios
- unsupported-metric requests
- ambiguous evidence scenarios
- intentionally hallucinated outputs
- invalid causal claims
- unsafe recommendation scenarios

## Release Principle

A model response is not considered production-acceptable merely because it passes one evaluator.

Release requires:

1. deterministic validation pass;
2. semantic evaluation thresholds;
3. project-specific governance evaluation;
4. human review for Management Brief output.

这里的 >=4/5 是我们自己的项目目标，不是冒充 Foundry 默认值。

Foundry 当前 Groundedness 等 evaluator 通常使用 1–5 分，默认 PASS threshold 为 3；我们自己的项目可以采用更严格的目标。


## Evaluation Result v0.1

Evaluation name:
management-brief-semantic-eval-v0.1

Platform:
Microsoft Foundry

Dataset:
semantic_eval_dataset_v0.1

Dataset type:
Synthetic

Case count:
1

### Built-in Evaluator Results

* Erdung (Groundedness): PASS — 100% (1/1)
* Relevanz (Relevance): PASS — 100% (1/1)
* Overall: PASS — 100% (2/2)

## Interpretation

The first semantic evaluation smoke test passed both built-in Microsoft Foundry quality evaluators.

This confirms that the generated Management Brief was considered grounded in the supplied context and relevant to the requested task for the tested case.

However, this result does not imply that all project-specific governance requirements were satisfied.

Manual review identified issues that were not detected by the built-in evaluators, including:

* incomplete evidence coverage;
* unsupported associations between unrelated evidence;
* inconsistent confidence-level assignment.

Therefore, built-in semantic evaluation is treated as one layer of the overall AI quality architecture rather than a complete release criterion.

Project-specific custom evaluators are required for domain-specific governance controls.
