# Research Methodology

## 1. Introduction

This document outlines the proposed research methodology for the Urban Mobility Intelligence: NYC Taxi Demand Forecasting project.

The research adopts a quantitative, experimental approach, combining large-scale data processing, exploratory data analysis and supervised machine learning to investigate short-term urban taxi demand forecasting.

The methodology is designed to support reproducible experimentation, transparent evaluation and critical interpretation of predictive results.

## 2. Research Design

**Research approach:** Quantitative

**Research strategy:** Comparative predictive modelling

**Analytical framework:** Adapted CRISP-DM (Cross-Industry Standard Process for Data Mining)

The research follows six stages:

1. Business understanding
2. Data understanding
3. Data preparation
4. Modelling
5. Evaluation
6. Deployment and communication of results

The modelling process will be iterative. Findings from data exploration and model evaluation may inform revisions to feature engineering and model selection.

## 3. Data Collection

### 3.1 Data Source

The primary dataset will be obtained from the New York City Taxi and Limousine Commission (NYC TLC).

Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Monthly Yellow Taxi trip records will be collected in Parquet format.

### 3.2 Sampling Strategy

The initial development dataset will contain six consecutive months of historical Yellow Taxi records.

The selected period will be documented before modelling begins, along with any missing months, schema differences or data quality concerns.

If resources permit, the analysis will be extended to twelve consecutive months to improve coverage of seasonal patterns.

### 3.3 Unit of Analysis

The raw unit of observation is an individual recorded taxi journey.

The forecasting unit will be:

**Pickup zone × hourly time interval**

Trip records will be aggregated to calculate the number of recorded pickups in each zone during each hour.

The project predicts recorded pickup demand rather than the total number of passengers seeking transportation.

## 4. Data Engineering Methodology

### 4.1 Data Ingestion

Microsoft Fabric Data Factory will be used to orchestrate ingestion into OneLake.

The ingestion process will record:

- Source file name and reporting month
- Ingestion timestamp
- Record count
- Pipeline execution status
- Processing errors

### 4.2 Medallion Architecture

Data processing will follow three layers.

**Bronze — Raw Data**

Stores source records with minimal transformation to preserve traceability.

**Silver — Validated Data**

Contains cleaned records with standardised schema, validated timestamps, acceptable trip values and documented quality flags.

**Gold — Analytical Data**

Contains aggregated hourly taxi demand and model-ready datasets.

### 4.3 Data Quality Assessment

The following quality dimensions will be investigated:

| Dimension | Proposed assessment |
|---|---|
| Completeness | Missing and null values |
| Validity | Timestamps, location identifiers and numeric ranges |
| Consistency | Schema differences across monthly files |
| Uniqueness | Duplicate records and repeated source ingestion |
| Accuracy | Plausibility checks and comparison with documentation |
| Timeliness | Source reporting periods and publication delays |

Duplicate identification will require care because the original trip records may not contain a reliable unique trip identifier.

Cleaning decisions and exclusions will be logged. Suspicious records will be investigated before applying removal rules.

## 5. Exploratory Data Analysis

Exploratory analysis will examine:

- Total recorded pickups
- Hourly pickup distributions
- Weekday and weekend differences
- Peak and off-peak demand
- Geographic differences between pickup zones
- Weekly and potential seasonal patterns
- Missing or anomalous time intervals

Visualisations will include time-series plots, distribution plots, heatmaps and geographic summaries.

Descriptive statistics will include mean, median, standard deviation and relevant quantiles.

Statistical analysis may investigate differences between time periods or groups, with effect sizes and assumptions reported where applicable.

## 6. Feature Engineering

The forecasting target is the number of pickups during a future hourly interval.

Proposed features include:

| Feature | Purpose |
|---|---|
| Hour of day | Capture daily demand cycles |
| Day of week | Identify weekly patterns |
| Weekend indicator | Distinguish working and non-working days |
| Month | Represent seasonal variation |
| Pickup zone | Capture geographical differences |
| Previous-hour pickup count | Capture recent local demand |
| Same hour previous day | Capture daily recurrence |
| Same hour previous week | Capture weekly recurrence |
| Rolling historical mean | Represent recent demand levels |
| Holiday indicator | Capture calendar-related variation |

Lag and rolling features must be calculated using information available before the prediction time.

A complete hourly time index will be constructed for each included zone, and the difference between observed zero-demand intervals and missing source records will be considered.

## 7. Forecasting Strategy

### 7.1 Prediction Target

Let:

**y(z,t) = number of recorded taxi pickups in zone z during hour t**

The initial forecasting horizon is one hour ahead.

A secondary experiment may investigate longer horizons if the initial modelling process is successful.

### 7.2 Models

Four approaches are proposed:

1. **Seasonal Naïve Forecast** — Predict demand using an equivalent historical period.
2. **Ridge Regression** — Provide a regularised and relatively interpretable benchmark.
3. **Random Forest Regression** — Investigate nonlinear relationships and interactions.
4. **Gradient Boosting / XGBoost** — Evaluate a more flexible supervised learning approach.

Final model selection will depend on experimental results rather than model complexity alone.

## 8. Training, Validation and Testing

Random data splitting will not be used because it could introduce temporal leakage.

Instead, observations will be ordered chronologically and divided into:

- Training period
- Validation period
- Final holdout test period

The validation stage will use rolling-origin or expanding-window evaluation where computationally feasible.

Feature transformations and hyperparameter optimisation will use training and validation data only.

The final test dataset will remain untouched until the model selection process is complete.

## 9. Evaluation Metrics

### 9.1 Mean Absolute Error

MAE measures the average absolute difference between observed and predicted pickup counts.

MAE = mean(|actual - predicted|)

### 9.2 Root Mean Squared Error

RMSE gives greater weight to larger prediction errors.

RMSE = sqrt(mean((actual - predicted)²))

### 9.3 Weighted Absolute Percentage Error

WAPE measures aggregate absolute error relative to total observed demand.

WAPE = sum(|actual - predicted|) / sum(actual) × 100

WAPE will be reported only when the total observed demand in the evaluated group is greater than zero.

### 9.4 Comparative Evaluation

Model performance will be assessed by:

- Overall forecasting accuracy
- Comparison against the seasonal baseline
- Performance across pickup zones
- Peak-hour and off-peak errors
- Performance on high-demand and low-demand observations
- Forecasting reliability across time periods

The final report will discuss both aggregate error and practical forecasting limitations.

## 10. Model Explainability

Feature importance and interpretability techniques will be considered to investigate which variables contribute to predictions.

Potential methods include:

- Regression coefficient interpretation
- Permutation feature importance
- SHAP analysis, subject to compatibility and computational resources

Model explanations will describe predictive relationships, not causal effects.

## 11. Experiment Tracking

MLflow within Microsoft Fabric will be used, where available, to record:

- Model configurations
- Hyperparameters
- Training and evaluation metrics
- Experiment identifiers
- Model artefacts
- Selected model versions

Random seeds and software dependencies will be recorded where appropriate.

## 12. Operational Evaluation

The project will consider how predictions could contribute to taxi fleet planning.

A hypothetical planning exercise may compare forecast-based vehicle allocation with a simple historical allocation rule.

Any operational benefits will be presented as simulated outcomes, not proven improvements to real-world dispatch operations.

## 13. Ethics and Limitations

The analysis relies on publicly available trip records rather than directly collecting personal information.

However, public data does not eliminate all ethical or quality concerns.

Key limitations include:

- Recorded trips do not represent unmet passenger demand.
- Geographic coverage and supply conditions may influence observed demand.
- Missing data and unusual events may affect results.
- Seasonal analysis may be limited by the selected historical period.
- Pickup-zone demand does not provide vehicle availability information.
- Historical relationships may change over time.
- Model predictions do not establish causal relationships.

## 14. Reproducibility

Reproducibility will be supported through:

- Documented source data and reporting periods
- Version-controlled notebooks and SQL
- Recorded data preparation rules
- Documented training and evaluation splits
- Versioned experiments
- Stored configuration files
- Data quality and pipeline execution logs

## 15. Research Outputs

The completed project will produce:

1. Data quality assessment
2. Exploratory analysis report
3. Feature engineering documentation
4. Model comparison table
5. Forecast evaluation visualisations
6. Model limitations and sensitivity analysis
7. Recommendations for potential operational use

## 16. References and Documentation

- NYC Taxi and Limousine Commission: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Microsoft Fabric Documentation: https://learn.microsoft.com/en-us/fabric/
- Scikit-learn Documentation: https://scikit-learn.org/stable/
- MLflow Documentation: https://mlflow.org/docs/latest/

Formal academic references will be added as relevant research literature is reviewed.

**Status:** Proposed methodology — implementation and experimental findings pending.