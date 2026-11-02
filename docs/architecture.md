# Technical Architecture

## 1. Architecture Overview

The Urban Mobility Intelligence project is designed as a cloud-based analytics and machine learning solution using Microsoft Fabric.

The proposed architecture integrates data ingestion, lakehouse storage, distributed processing, analytical modelling, machine learning and business intelligence.

The solution follows a Medallion Architecture to separate raw data, validated data and analytics-ready datasets.

**Architecture Status:** Proposed — subject to implementation and validation.

## 2. High-Level Architecture

```text
NYC TLC Open Data
       |
       v
Microsoft Fabric Data Factory
(Data Ingestion Pipeline)
       |
       v
Microsoft OneLake / Lakehouse
       |
       +-------------------------+
       |                         |
       v                         |
BRONZE LAYER                     |
Raw Parquet Files                |
       |                         |
       v                         |
PySpark Transformation           |
       |                         |
       v                         |
SILVER LAYER                     |
Validated Delta Tables           |
       |                         |
       v                         |
Gold Transformation              |
       |                         |
       v                         |
GOLD LAYER                       |
Hourly Demand Tables             |
       |                         |
       +-------------+-----------+
                     |
            +--------+--------+
            |                 |
            v                 v
    Fabric Data Science    SQL Analytics
    Python / ML Models     Endpoint
            |                 |
            v                 |
    MLflow Experiments        |
            |                 |
            v                 |
    Batch Predictions         |
            |                 |
            v                 v
       Gold Prediction & Reporting Tables
                     |
                     v
              Power BI Web
            Analytics Reports

GitHub: Version Control and Documentation
```

## 3. Platform Components

### 3.1 Microsoft Fabric Workspace

The workspace will organise and manage project resources.

**Workspace Name:** `Urban_Mobility_Intelligence`

Planned workspace items:

- Lakehouse
- Data ingestion pipeline
- PySpark notebooks
- Machine learning experiments
- SQL analytical views
- Reporting semantic model
- Power BI report, subject to access

### 3.2 Microsoft OneLake

OneLake will serve as the underlying data storage environment for the Fabric Lakehouse.

It will store source files and managed analytical tables.

### 3.3 Fabric Lakehouse

**Lakehouse Name:** `LH_NYC_Taxi`

The Lakehouse will provide storage and analytical access to historical taxi records.

The project will use Delta tables for processed datasets.

## 4. Medallion Architecture

### 4.1 Bronze Layer

**Purpose:** Preserve ingested source records.

Proposed storage location:

`Files/bronze/yellow_taxi/`

Responsibilities:

- Retain source Parquet data.
- Preserve reporting-month information.
- Record ingestion metadata.
- Support reprocessing when transformation logic changes.

The Bronze layer will avoid destructive source transformations.

### 4.2 Silver Layer

**Purpose:** Produce consistent, validated trip records.

Proposed Delta table:

`silver_yellow_taxi_trips`

Processing activities:

- Standardise column names and types.
- Validate pickup and drop-off timestamps.
- Investigate invalid location identifiers.
- Detect and document duplicate candidates.
- Identify unusual trip durations and distances.
- Apply consistent data quality rules.
- Record rejected or quarantined observations where appropriate.

The result will be a validated dataset suitable for analytical aggregation.

### 4.3 Gold Layer

**Purpose:** Produce business-ready analytical datasets.

Proposed tables:

| Table | Description |
|---|---|
| `gold_hourly_zone_demand` | Pickup counts by zone and hour |
| `gold_demand_features` | Model-ready forecasting features |
| `gold_forecast_predictions` | Actual and predicted demand |
| `gold_zone_summary` | Geographic analytical indicators |
| `gold_daily_summary` | Daily operational KPIs |

Table definitions will be refined during data modelling.

## 5. Data Model Design

The analytical model will distinguish dimensions from measurable facts.

### Proposed Dimension Tables

**dim_zone**

- zone_id
- borough
- zone_name
- service_zone

**dim_date**

- date_key
- calendar_date
- year
- quarter
- month
- day_of_week
- weekend_indicator

**dim_hour**

- hour_key
- hour_of_day
- time_period

### Proposed Fact Tables

**fact_hourly_demand**

- zone_id
- date_key
- hour_key
- pickup_count

**fact_demand_forecast**

- zone_id
- forecast_timestamp
- forecast_origin
- forecast_horizon_hours
- model_version
- predicted_pickup_count
- actual_pickup_count (when available)

The analytical grain and primary key relationships will be documented and tested.

Forecast records will retain the prediction timestamp and model version to support reproducibility and prevent ambiguity.

## 6. Data Processing

PySpark will be used to process trip records and create analytical tables.

The processing workflow will include:

1. Reading source Parquet files.
2. Validating source schema.
3. Applying documented quality rules.
4. Writing Silver Delta tables.
5. Generating hourly pickup aggregations.
6. Joining taxi zone metadata.
7. Constructing historical forecasting features.
8. Writing model-ready Gold tables.

Pipeline transformations should be repeatable and designed to avoid duplicate data during reruns.

## 7. Machine Learning Architecture

Fabric Data Science notebooks will be used to develop and evaluate forecasting models.

### Model Development Workflow

```text
Gold Hourly Demand Data
          |
          v
Feature Engineering
          |
          v
Chronological Split
          |
          v
Baseline Forecast
          |
          v
Machine Learning Training
          |
          v
Validation & Backtesting
          |
          v
MLflow Experiment Tracking
          |
          v
Selected Model
          |
          v
Batch Prediction
          |
          v
Gold Forecast Table
```

Planned model candidates:

- Seasonal naïve forecasting
- Ridge Regression
- Random Forest
- Gradient Boosting / XGBoost

Model evaluation will use MAE, RMSE and WAPE where defined.

The final selected approach will depend on validation and testing results.

## 8. Prediction Scheduling

The proposed operational workflow will use batch scoring.

Possible stages:

1. Update historical trip data.
2. Run validation and transformation pipelines.
3. Refresh demand features.
4. Generate predictions using the selected model.
5. Store predictions with model version and forecast timestamps.
6. Refresh reporting outputs.

For the historical portfolio demonstration, scoring will operate on selected backtesting periods.

Because official taxi data is published retrospectively, the project will not claim to offer genuine live demand forecasts unless an appropriate real-time input source is added.

## 9. Reporting Architecture

Reporting will use Gold analytical tables.

Planned visualisations:

- Total historical pickups
- Hourly demand distribution
- Daily and weekly demand patterns
- Demand by pickup zone
- Actual versus predicted demand
- Model evaluation indicators
- Geographic forecasting error
- Peak-hour demand forecasts

Reports may be developed through the Power BI web experience where supported by the available Fabric environment.

## 10. GitHub Integration

**Repository:** `fabric-nyc-taxi-demand-forecasting`

GitHub will be used for:

- Source control
- Notebook versioning
- SQL scripts
- Pipeline definitions where supported
- Architecture documentation
- Research methodology
- Evaluation reports

Fabric Git integration may be configured where permissions and workspace capabilities allow.

GitHub will not be used as the primary storage location for large trip datasets.

Secrets, credentials and environment-specific access tokens must not be committed.

## 11. Data Quality and Reliability

Proposed quality controls include:

- Source-file ingestion validation
- Schema consistency checks
- Record-count reconciliation
- Null and invalid-value checks
- Detection of duplicated pipeline loads
- Validation of aggregation totals
- Forecast output completeness
- Prediction timestamp consistency

Unexpected data should be investigated and logged rather than silently discarded.

## 12. Performance and Cost Considerations

The platform design will take Fabric capacity and trial limitations into account.

Planned optimisation considerations include:

- Begin with a small historical sample.
- Process Parquet files using Spark.
- Avoid unnecessary full-dataset scans.
- Reuse validated Delta tables.
- Limit expensive exploratory notebook executions.
- Partition or optimise tables based on observed query patterns.
- Monitor pipeline execution and resource usage.
- Scale the historical dataset only when justified.

## 13. Security and Governance

Although the source dataset is publicly available, the solution will follow good engineering practices.

Planned controls include:

- Appropriate workspace permissions
- No credentials in GitHub
- Source data attribution
- Documented table ownership and lineage
- Reproducible transformation logic
- Restricted access to workspace configuration secrets

## 14. Deployment and Testing

The initial implementation will be a development environment.

Testing will include:

- Data ingestion verification
- Transformation reconciliation
- Analytical table validation
- Feature leakage checks
- Model evaluation reproducibility
- Prediction table consistency
- Reporting accuracy checks

The completed project will document which parts are functioning, which were tested and which remain proposed.

## 15. Known Constraints

- Fabric capabilities depend on account and capacity access.
- Public taxi data is retrospective.
- Demand forecasts are based on recorded pickups.
- Real operational dispatch integration is outside project scope.
- Compute capacity may restrict model experimentation.
- Fabric Git integration does not version the underlying lakehouse data itself.

## 16. Future Enhancements

Potential extensions include:

- Incorporating historical weather observations.
- Adding public holiday and event indicators.
- Forecasting multiple hours ahead.
- Comparing global and zone-specific models.
- Investigating forecast uncertainty.
- Developing a simulated vehicle allocation strategy.
- Adding automated model monitoring.

## 17. Architecture Status

**Current Status:** Proposed architecture

**Next Milestone:** Configure the Microsoft Fabric workspace and create the initial Lakehouse.

Implementation screenshots, validated table definitions, pipeline details and deployment evidence will be added as development progresses.

## 18. Technical References

- Microsoft Fabric: https://learn.microsoft.com/en-us/fabric/
- Microsoft Fabric Data Engineering: https://learn.microsoft.com/en-us/fabric/data-engineering/
- Microsoft Fabric Data Science: https://learn.microsoft.com/en-us/fabric/data-science/
- NYC TLC Open Data: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- MLflow: https://mlflow.org/docs/latest/