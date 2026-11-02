# Urban Mobility Intelligence: NYC Taxi Demand Forecasting

## 1. Project Overview

This project aims to develop an end-to-end data analytics and machine learning solution using Microsoft Fabric to analyse historical New York City taxi trip records and forecast hourly taxi pickup demand across different geographic zones.

The project combines data engineering, exploratory data analysis, statistical modelling, machine learning and business intelligence to investigate how historical travel patterns can support demand forecasting and data-driven transport planning.

**Project Type:** MSc Data Science Portfolio Project  
**Domain:** Urban Mobility and Transportation Analytics  
**Platform:** Microsoft Fabric  
**Technologies:** Python, PySpark, SQL, Scikit-learn, MLflow, Delta Lake, GitHub and Power BI (Web)

## 2. Business Problem

Taxi demand varies depending on the time of day, day of the week, location and seasonal travel patterns.

Without reliable demand forecasts, transport operators may experience inefficient vehicle allocation, passenger delays and missed business opportunities.

This project investigates whether historical taxi pickup information can be used to predict future demand and provide insights that may support operational planning.

## 3. Research Question

**How accurately can machine learning models predict hourly taxi pickup demand across New York City taxi zones using historical trip records and temporal features?**

### Research Objectives

1. Develop a scalable data ingestion and transformation pipeline using Microsoft Fabric.
2. Investigate temporal and geographical patterns in historical taxi demand.
3. Engineer features relevant to short-term demand forecasting.
4. Develop and compare baseline, statistical and machine learning forecasting approaches.
5. Evaluate predictive performance using appropriate error metrics and time-based validation.
6. Present findings through a reproducible analytical workflow and interactive visualisations.
7. Discuss model limitations and potential applications in transport planning.

## 4. Dataset

**Source:** New York City Taxi and Limousine Commission (NYC TLC)

Official data portal: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

The dataset includes publicly available records of taxi journeys, with fields such as pickup and drop-off timestamps, pickup and drop-off location identifiers, trip distance, passenger count and fare information.

The initial project will focus on Yellow Taxi trip records from a selected historical period.

The proposed approach is to use six consecutive months for initial development, expanding the historical period if required by the modelling results and available computing resources.

The dataset is historical and observational. Recorded trip counts represent fulfilled journeys and may not capture all unmet passenger demand.

## 5. Project Scope

### In Scope

- Ingesting historical taxi trip records into Microsoft Fabric.
- Designing Bronze, Silver and Gold Lakehouse layers.
- Cleaning and validating trip records using PySpark.
- Building hourly and geographical demand aggregations.
- Performing statistical and exploratory analysis.
- Developing and comparing forecasting models.
- Tracking experiments and evaluation metrics.
- Creating analytical visualisations.
- Documenting the solution using GitHub.

### Out of Scope

- Real-time GPS tracking.
- Direct integration with operational taxi dispatch systems.
- Production deployment of a passenger booking application.
- Guaranteed prediction of individual passenger behaviour.
- Real-world vehicle allocation optimisation without fleet availability data.

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Microsoft Fabric | Integrated analytics platform |
| Fabric Data Factory | Data ingestion and orchestration |
| OneLake / Lakehouse | Cloud data storage and management |
| Delta Lake | Managed analytical tables |
| PySpark | Distributed data processing |
| SQL | Querying and analytical transformations |
| Python | Statistical and predictive analysis |
| Scikit-learn / XGBoost | Machine learning |
| MLflow | Experiment tracking and model management |
| Power BI Web | Reporting and visualisation |
| GitHub | Version control and project documentation |

## 7. Planned Deliverables

1. Documented source dataset and data dictionary.
2. Working data ingestion pipeline.
3. Bronze, Silver and Gold analytical tables.
4. Reproducible data cleaning and feature engineering notebooks.
5. Exploratory data analysis and statistical findings.
6. Baseline and machine learning forecasting models.
7. Model comparison and evaluation report.
8. Interactive analytical dashboard, subject to platform access.
9. Documented system architecture.
10. GitHub repository containing code, methodology, results and limitations.

## 8. Success Criteria

The project will be considered successful when:

- Historical data can be ingested and transformed through a repeatable workflow.
- Data quality checks are documented and passed.
- Forecasting models are evaluated on previously unseen future periods.
- Machine learning performance is compared against a meaningful baseline.
- Prediction errors are analysed across time periods and geographic zones.
- Outputs can be reproduced using documented data, code and configurations.
- The final report communicates findings, limitations and practical implications.

## 9. Expected Contribution

This project is intended to demonstrate how Microsoft Fabric can support an integrated data science workflow, connecting large-scale data engineering with statistical analysis, machine learning and operational decision support.

The final findings will depend on experimental evaluation and will not be assumed in advance.

## 10. Project Status

**Status:** Planning and environment setup  
**Current Phase:** Project documentation and Microsoft Fabric workspace configuration

Implementation results, final model selections and performance metrics will be added as the project progresses.