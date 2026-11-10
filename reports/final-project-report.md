# Urban Mobility Intelligence: NYC Yellow Taxi Demand Forecasting

## Executive summary

This portfolio project creates an hourly, geographic view of **recorded** New York City Yellow Taxi pickups using the official January 2025 TLC trip records. A Fabric Bronze–Silver–Gold design supports quality checks, hourly aggregation and historical feature engineering. Three naive forecasting rules were evaluated over chronological validation and retrospective test windows. The previous-week rule was the most accurate baseline in both windows. A fully specified local machine-learning experiment and reporting pipeline is supplied, but advanced ML outcomes **must not be claimed** until real source files have been downloaded and the experiments run.

## Objectives

1. Establish a quality-auditable, repeatable data pipeline for January 2025 Yellow Taxi pickups.
2. Convert eligible pickups into a complete observed-zone × hourly time series.
3. Examine spatial, diurnal, weekly and sparse-zone patterns.
4. Construct lagged and rolling demand predictors without using the target hour.
5. Compare baseline forecasts, then examine candidate regressors with a chronological training/validation/test design.

## Data source and boundaries

- Provider: NYC Taxi and Limousine Commission, official Yellow Taxi January 2025 trip file and taxi zone lookup.
- Core unit: recorded pickup event, subsequently aggregated to zone-hour.
- Zone universe: 259 zones with at least one valid pickup during January; no assumptions about unobserved zones.
- Eligibility: pickup within `[2025-01-01, 2025-02-01)` and pickup-zone IDs other than 264 and 265, with geographical flags retained for traceability.
- A 0-imputed zone-hour indicates **no recorded eligible pickup in this file** under source coverage assumptions; not proof of zero passenger demand.

## Results verified during the original Microsoft Fabric exercise

| Check | Recorded result |
| --- | ---: |
| Bronze / Silver original rows | 3,475,226 |
| Eligible pickups | 3,465,683 |
| Ineligible retained rows | 9,543 |
| Observed pickup zones | 259 |
| January hours | 744 |
| Gold zone-hour rows | 192,696 |
| Zero-imputed zone-hours | 96,942 |
| Model-ready rows after weekly-lag history | 149,184 |
| Training / validation / retrospective test rows | 80,808 / 31,080 / 37,296 |

### Spatial and temporal observations

- The strongest citywide recorded pickup hour was **18:00** (267,303 pickups summed over January); the weakest was **04:00** (19,957).
- Average daily pickups: **112,566.52** for weekdays versus **109,581.63** for weekend days.
- Midtown Center (LocationID 161) led the zones with **169,977** January pickups.
- **145 out of 259** zones recorded zero pickups in over half the hours, demonstrating important geographic sparsity.
- **34 high-demand zones** supplied 2,905,514 pickups (83.84%) in January-wide *exploratory* categories; categories used for predictive evaluation must instead be built from training-period data.

### Baseline forecast performance

| Baseline | Validation MAE (Jan 21–25) | Earlier-inspected test MAE (Jan 26–31) |
| --- | ---: | ---: |
| Previous hour | 6.2557 | 5.5845 |
| Previous day | 6.4114 | 6.2047 |
| Previous week | **4.1659** | **4.7324** |

The previous-week baseline won across all four training-defined demand categories on validation. Its high-demand-category MAE was **22.5667**, compared to **0.4595** in the very-low-demand group. Raw MAEs between groups are not directly comparable as relative performance measures because scales vary substantially.

## Machine-learning experiment methodology (fully implemented; awaiting source-data execution)

A DuckDB implementation reconstructs Silver, Gold and features from official Parquet and CSV sources. It evaluates **Ridge regression, Random Forest and histogram-based gradient boosting** using numerical lag/calendar features and training-fitted zone/hour/day encodings. All models are trained on **Jan 8–20**, compared with naive baselines on **Jan 21–25**; the model with minimum validation MAE is selected before retrospective reporting on **Jan 26–31**. Alongside MAE, the pipeline calculates RMSE, WAPE where meaningful, prediction bias, and demand-category metrics. It saves prediction tables, a model artefact, figures and a machine-generated report.

**No advanced-ML accuracy is stated here because the experiment was not executed on the official raw dataset in this delivery environment.** Once the pipeline is executed successfully, the authoritative computed results will appear in `results/local_run/EXECUTED_REPORT.md` and `metrics.json`.

## Risk assessment and limitations

- January-only data cannot establish annual seasonality or long-term generalisability.
- The dates Jan 26–31 were previously inspected during interactive baseline development. They cannot be presented as a pristine, never-seen holdout.
- The modelling protocol is **rolling one-hour-ahead**: historical actual pickup counts are assumed to become available before the next-hour prediction. A simultaneous multi-hour-ahead forecast requires a different design.
- Sparse zones may dominate overall error comparisons by having nearly zero activity; metrics must also be inspected by demand category.
- No weather, events, holidays or live availability information are included; unexpected events may cause forecasting errors.
- Train-derived grouping and preprocessing avoid future-period leakage. Original trip-level flags preserve suspicious rows while avoiding unwanted removal of a valid pickup event for a bad distance measurement.

## Reproducibility

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-local.txt
python scripts/download_data.py
python scripts/check_source_data.py
python scripts/run_local.py
pytest -q tests/
```

The public sources are downloaded on first run. They are **not packaged**, so this report is a methodological and original-observation record until the full pipeline runs locally. The CI tests use generated synthetic data and do not validate real NYC model accuracy.

## Conclusion

This work demonstrates an end-to-end approach to **quality-aware spatiotemporal aggregation and comparative demand forecasting**. The key established baseline finding is the usefulness of previous-week pickup counts for January 2025. Extending the historical window and running the included ML experiment are essential to judge whether learned models can reliably beat the baseline in additional periods.
