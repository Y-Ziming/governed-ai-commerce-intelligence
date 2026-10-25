# Public / Private Data Boundary

## Purpose

This project is based on a real SME commerce scenario.

The public portfolio version is intentionally separated from the private implementation environment in order to protect confidential business and personal data.

## Private Project

The private implementation may contain:

- Original business Excel files
- Real order IDs
- Real order-line IDs
- Customer IDs
- Tracking numbers
- Commercially sensitive sales data
- Real company information
- Internal source-system details
- Raw operational exports

These assets remain in the private development environment.

## Public Portfolio

The public portfolio may contain:

- Synthetic datasets
- Aggregated or normalized metrics
- Generic product names
- Anonymized screenshots
- Architecture diagrams
- Data models
- Data-quality rules
- Selected sanitized source code
- AI evaluation results
- AI risk and governance artifacts
- Infrastructure-as-Code examples

## Principle

Real operational data is never copied directly into the public GitHub repository.

Public demonstrations use synthetic or anonymized data while preserving the architecture, engineering logic and decision-making process of the real implementation.