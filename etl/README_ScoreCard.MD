---
title: "README - ScoreCard"
author: "GDI"
date: "16 December 2025"
lang: en
standalone: true
---

## Status

This index is **not final in any sense**. It is shared explicitly as a **conversation starter**, not as a finished product, endorsed methodology, or recommended public-facing metric.

The current approach almost certainly contains errors in thinking, logic, and intent. Methodological choices reflect the skills and time constraints of the project team rather than a co-designed process with stakeholders, which is always the preferred approach for composite indicators.

## Method

The index combines multiple electrification-related metrics into a single composite score at the **Region–Year–Month** level using a data-driven dimensionality-reduction approach.

Each metric is first transformed onto the real line to accommodate bounded percentages and strictly positive values, then normalised using **cross-sectional z-scores within each month**. This makes metrics comparable despite differing units and scales, and ensures the index reflects *relative regional performance within a given month*.

All transformed metrics are then combined using a **month-specific Principal Component Analysis (PCA)**, with the first principal component retained as the composite score. PCA is re-estimated independently for each month, allowing relationships between metrics to vary over time rather than imposing fixed weights.

The output includes both the composite score and the underlying metric values to support transparency and diagnostic work.

## How to interpret the score

The index is a **relative measure**, not an absolute indicator of electrification progress. Higher values indicate stronger performance relative to other regions in the same month across the included metrics.

Scores are **not directly comparable across months** because each month is normalised independently. Changes over time should therefore be interpreted as shifts in relative position rather than precise measures of absolute progress.

Metric directionality (e.g. where lower values are preferable) is handled implicitly through correlations captured by PCA, rather than by explicit sign constraints. This improves flexibility but reduces interpretability.

## QA status and why this has not been completed

Formal quality assurance of the composite index has **not yet been undertaken**. While individual metrics include basic internal checks, the index itself has not been tested for robustness to metric selection, missing data, or alternative modelling choices.

This reflects both project scope and the absence of agreed stakeholder guidance. Proper QA of a composite indicator requires alignment on what should be measured, how trade-offs should be handled, and how sensitive the score should be to individual metrics. Those discussions have not yet occurred.

## Caveats and next steps

This index should be treated as **exploratory and provisional**.

Metric selection is incomplete and driven by data availability rather than theory. Some domains are over-represented, others are missing, and sectoral balance has not been optimised. Missing values are filled with zeros to preserve a complete panel, which is a strong assumption and may bias results.

To ensure consistent joins across all included metrics, the index is restricted to the period 2020–2024. This means that more recent changes, including developments in 2025, are not captured. The restriction reflects uneven update cadences across data sources rather than a conceptual decision.

Because PCA is re-estimated each month, implicit metric weightings can change over time. This makes attribution difficult and means that changes in score may reflect changing correlations rather than real-world progress.

In an ideal design, the composite score would be converted into a **categorical or banded indicator** (e.g. grades or progress tiers) to improve interpretability and public communication. This step was not completed due to time constraints.

**Substantial input from Rewiring Aotearoa is required** before this index can be considered stable, interpretable, or suitable for external use. In particular, stakeholder guidance is needed on metric inclusion, directionality, weighting philosophy, scaling, and presentation. Until then, the index should be viewed solely as a technical prototype to support further discussion.
