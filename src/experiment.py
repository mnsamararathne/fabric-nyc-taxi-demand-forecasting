"""Reproducible one-step-ahead hourly zone demand experiments.

Only *observed* hourly counts prior to prediction time are used for lags.
The test window in the original exercise was previously inspected and should
not be described as a pristine held-out experiment.
"""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ['day_of_month', 'is_weekend', 'lag_1', 'lag_2', 'lag_24', 'lag_168',
           'rolling_mean_3h', 'rolling_mean_24h']
CATEGORICAL = ['PULocationID', 'hour_of_day', 'day_of_week']
FEATURES = CATEGORICAL + NUMERIC


def category_table(train: pd.DataFrame) -> pd.DataFrame:
    """Classify zones from training labels ONLY; for evaluation/analysis."""
    avg = train.groupby('PULocationID', as_index=False)['pickup_count'].mean()
    avg['demand_category'] = pd.cut(avg.pickup_count,
        bins=[-np.inf, 1, 10, 50, np.inf],
        right=False, labels=['Very Low', 'Low', 'Medium', 'High']).astype(str)
    return avg[['PULocationID', 'demand_category']]


def _score(y, prediction):
    values=np.asarray(prediction, dtype=float).reshape(-1)
    values=np.maximum(0.0,values)
    target=np.asarray(y,dtype=float).reshape(-1)
    abs_error=np.abs(target-values)
    return {
        'MAE': float(mean_absolute_error(target, values)),
        'RMSE': float(np.sqrt(mean_squared_error(target, values))),
        'WAPE_percent': float(100*abs_error.sum()/target.sum()) if target.sum()>0 else None,
        'bias':float(np.mean(values-target)),
    }


def _fit_models(train, seed=42, fast=False):
    # Ridge is OHE encoded. Tree models operate on the same numeric + OHE encoded
    # features, so categorical zone IDs are not treated as meaningful distances.
    cat_enc = OneHotEncoder(handle_unknown='ignore')
    preprocessing = ColumnTransformer([
       ('cats',cat_enc,CATEGORICAL),
       ('nums',Pipeline([('impute',SimpleImputer(strategy='median')),
                         ('scale',StandardScaler())]),NUMERIC),
    ])
    models = {
       'ridge':Pipeline([('preprocess',preprocessing),('model',Ridge(alpha=100.0))]),
       'random_forest':Pipeline([
          ('preprocess',ColumnTransformer([
             ('cats',OneHotEncoder(handle_unknown='ignore'),CATEGORICAL),
             ('nums',SimpleImputer(strategy='median'),NUMERIC)
          ])),
          ('model',RandomForestRegressor(n_estimators=25 if fast else 80,
              max_depth=12, min_samples_leaf=5, random_state=seed,n_jobs=-1))
       ]),
       'hist_gradient_boosting':Pipeline([
          ('preprocess',ColumnTransformer([
             ('cats',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CATEGORICAL),
             ('nums',SimpleImputer(strategy='median'),NUMERIC)
          ], sparse_threshold=0)),
          ('model',HistGradientBoostingRegressor(max_iter=40 if fast else 150,
            learning_rate=0.08, max_leaf_nodes=25, l2_regularization=2.0,
            random_state=seed))
       ]),
    }
    # Avoid a huge dense one-hot matrix for HistGradientBoosting by using
    # ordinal category codes with a training-fitted ordinal encoder instead.
    from sklearn.preprocessing import OrdinalEncoder
    models['hist_gradient_boosting'].set_params(preprocess=ColumnTransformer([
        ('cats',OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1),CATEGORICAL),
        ('nums',SimpleImputer(strategy='median'),NUMERIC)
    ]))
    for m in models.values():
        m.fit(train[FEATURES],train['pickup_count'])
    return models


def run_experiments(panel: pd.DataFrame, out: Path, fast=False, expected_counts=True):
    """Fit only on train; compare on validation; freeze choice before test.

    panel must have complete lag_168 and all FEATURE columns; no future data
    or current-hour target is part of FEATURES. Predict one hour ahead with
    realised earlier pickup counts already available.
    """
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    data=panel.copy()
    data['pickup_hour']=pd.to_datetime(data['pickup_hour'])
    if data.duplicated(['PULocationID','pickup_hour']).any():
        raise ValueError('Duplicate zone/hour keys')
    if data[FEATURES].isna().any().any():
        raise ValueError('Missing features: require 168-hour lag warm-up')
    train=data[data.pickup_hour<'2025-01-21'].copy()
    valid=data[(data.pickup_hour>='2025-01-21') & (data.pickup_hour<'2025-01-26')].copy()
    test=data[data.pickup_hour>='2025-01-26'].copy()
    if expected_counts and (len(train),len(valid),len(test))!=(80808,31080,37296):
        raise ValueError('Unexpected panel split sizes; check dataset')
    if min(map(len,(train,valid,test)))==0:
        raise ValueError('Empty train, validation or test split')
    zone_categories=category_table(train)
    zone_categories.to_csv(out/'training_zone_categories.csv',index=False)
    fitted=_fit_models(train,fast=fast)
    comparisons=[]
    for name,model in fitted.items():
        predictions=np.maximum(0,model.predict(valid[FEATURES]))
        scores=_score(valid.pickup_count,predictions)
        comparisons.append({'model':name,**scores})
    for name,col in [('previous_hour','lag_1'),('previous_day','lag_24'),('previous_week','lag_168')]:
        comparisons.append({'model':name,**_score(valid.pickup_count,valid[col])})
    comp=pd.DataFrame(comparisons).sort_values('MAE')
    comp.to_csv(out/'validation_model_comparison.csv',index=False)
    # Selection is based on validation ONLY, and includes the naive baseline.
    best_name=str(comp.iloc[0]['model'])
    candidate_name=str(pd.DataFrame(comparisons[:len(fitted)]).sort_values('MAE').iloc[0]['model'])
    joblib.dump(fitted[candidate_name],out/'best_ml_candidate.joblib')
    results={'status':'calculated_from_local_data', 'forecast_horizon':'one hour ahead',
       'train_rows':len(train),'validation_rows':len(valid),'test_rows':len(test),
       'validation_reference_weekly_MAE':_score(valid.pickup_count,valid.lag_168)['MAE'],
       'selected_by_validation_MAE':best_name,
       'best_machine_learning_candidate':candidate_name,
       'validation_models':comp.to_dict(orient='records'),
       'test_previously_inspected':True,
       'data_provenance':'Official January 2025 TLC data downloaded separately',
       'note':'Original test dates were inspected during guided project; retrospective, not untouched.'}
    predictions={}
    for split_name,split in [('validation',valid),('test_retrospective',test)]:
        joined=split[['PULocationID','pickup_hour','pickup_count','lag_168']].copy()
        for model_name,model in fitted.items():
            joined['pred_'+model_name]=np.maximum(0,model.predict(split[FEATURES]))
        joined['pred_previous_week']=split.lag_168.to_numpy()
        joined=joined.merge(zone_categories,on='PULocationID',how='left',validate='many_to_one')
        joined.to_csv(out/f'{split_name}_predictions.csv',index=False)
        predictions[split_name]=joined
        # Evaluate the baseline and the best ML candidate within training-defined
        # demand strata, to prevent low-volume zones hiding busy-zone errors.
        group_records=[]
        for category,group in joined.groupby('demand_category'):
            for model_name,col in [('previous_week','pred_previous_week'),(candidate_name,'pred_'+candidate_name)]:
                group_records.append({'demand_category':category,'model':model_name,
                                      'observations':len(group),**_score(group.pickup_count,group[col])})
        pd.DataFrame(group_records).to_csv(out/f'{split_name}_category_metrics.csv',index=False)
        results[split_name+'_metrics']={
            'previous_week':_score(joined.pickup_count,joined.pred_previous_week),
            'best_ml_candidate':_score(joined.pickup_count,joined['pred_'+candidate_name]),
            'selected_model':best_name}
    # Chart outputs for portfolio presentation.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,5))
    plt.barh(comp.model[::-1],comp.MAE[::-1])
    plt.xlabel('Validation MAE (pickups per zone-hour)')
    plt.title('One-hour-ahead NYC Taxi Forecasting: Baselines vs ML')
    plt.tight_layout();plt.savefig(out/'validation_model_comparison.png',dpi=160);plt.close()
    example=predictions['validation']
    example=example[example.PULocationID==161].sort_values('pickup_hour').head(72)
    if len(example):
        plt.figure(figsize=(12,4))
        plt.plot(example.pickup_hour,example.pickup_count,label='Actual')
        plt.plot(example.pickup_hour,example['pred_'+candidate_name],label=candidate_name)
        plt.plot(example.pickup_hour,example.pred_previous_week,label='Previous-week baseline',alpha=0.8)
        plt.legend();plt.title('Midtown Center: first 72 validation hours')
        plt.xticks(rotation=25);plt.tight_layout();plt.savefig(out/'midtown_validation_forecast.png',dpi=160);plt.close()
    (out/'metrics.json').write_text(json.dumps(results,indent=2,default=str)+'\n')
    README=f'''# Executed Forecasting Results\n\nThis report was **generated from local execution** using official NYC TLC data.\n\n- Selected model by validation MAE: **{best_name}**\n- Best ML candidate: **{candidate_name}**\n- Previous-week baseline validation MAE: **{results["validation_reference_weekly_MAE"]:.4f}**\n- Best ML validation MAE: **{results["validation_metrics"]["best_ml_candidate"]["MAE"]:.4f}**\n- Previous-week baseline retrospective test MAE: **{results["test_retrospective_metrics"]["previous_week"]["MAE"]:.4f}**\n- Best ML retrospective test MAE: **{results["test_retrospective_metrics"]["best_ml_candidate"]["MAE"]:.4f}**\n\n**Evaluation design:** Train January 8–20, validate January 21–25, retrospective test January 26–31. Only one-hour-ahead updates with realised historical pickups.\n\n**Limitations:** One month of TLC Yellow Taxi records, highly zero-heavy zones, and test dates previously inspected in earlier exploratory work. This is not an untouched future holdout. Models were selected using validation MAE, and no model superiority is assumed before calculation.\n\nSee `validation_model_comparison.csv`, category metrics, predictions and figures.\n'''
    (out/'EXECUTED_REPORT.md').write_text(README)
    return results
