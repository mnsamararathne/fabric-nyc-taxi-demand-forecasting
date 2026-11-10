# Executed Forecasting Results

This report was **generated from local execution** using official NYC TLC data.

- Selected model by validation MAE: **random_forest**
- Best ML candidate: **random_forest**
- Previous-week baseline validation MAE: **4.1659**
- Best ML validation MAE: **3.9722**
- Previous-week baseline retrospective test MAE: **4.7324**
- Best ML retrospective test MAE: **3.9264**

**Evaluation design:** Train January 8–20, validate January 21–25, retrospective test January 26–31. Only one-hour-ahead updates with realised historical pickups.

**Limitations:** One month of TLC Yellow Taxi records, highly zero-heavy zones, and test dates previously inspected in earlier exploratory work. This is not an untouched future holdout. Models were selected using validation MAE, and no model superiority is assumed before calculation.

See `validation_model_comparison.csv`, category metrics, predictions and figures.
