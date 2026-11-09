"""Synthetic smoke tests; do NOT represent measured NYC model accuracy."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.experiment import run_experiments, category_table


def sample_panel():
    time=pd.date_range('2025-01-01',periods=744,freq='h')
    rows=[]
    for zone in [11,161,201]:
        pickup=np.array([max(0,int(zone%16 + 12*np.sin(2*np.pi*(i%24)/24)+
                     3*np.cos(2*np.pi*(i%168)/168))) for i in range(744)])
        for i in range(168,744):
            window=pickup[max(i-24,0):i]
            rows.append({'PULocationID':zone,'pickup_hour':time[i],
                'pickup_count':pickup[i],'hour_of_day':time[i].hour,
                'day_of_week':time[i].dayofweek,'day_of_month':time[i].day,
                'is_weekend':int(time[i].dayofweek>=5),
                'lag_1':pickup[i-1],'lag_2':pickup[i-2],
                'lag_24':pickup[i-24],'lag_168':pickup[i-168],
                'rolling_mean_3h':float(np.mean(pickup[i-3:i])),
                'rolling_mean_24h':float(np.mean(window))})
    return pd.DataFrame(rows)


def test_synthetic_pipeline(tmp_path):
    panel=sample_panel()
    assert len(panel)==1728
    report=run_experiments(panel,tmp_path,fast=True,expected_counts=False)
    assert report['train_rows']==936
    assert report['validation_rows']==360
    assert report['test_rows']==432
    assert (tmp_path/'metrics.json').exists()
    assert (tmp_path/'validation_model_comparison.csv').exists()
    assert (tmp_path/'EXECUTED_REPORT.md').exists()
    assert (tmp_path/'best_ml_candidate.joblib').exists()
    assert (tmp_path/'validation_model_comparison.png').exists()
    assert report['selected_by_validation_MAE'] in {
        'previous_hour','previous_day','previous_week','ridge','random_forest','hist_gradient_boosting'}


def test_categories_training_only():
    train=pd.DataFrame({'PULocationID':[1,1,2,2], 'pickup_count':[0,1,80,100]})
    result=category_table(train).set_index('PULocationID')
    assert result.loc[1,'demand_category']=='Very Low'
    assert result.loc[2,'demand_category']=='High'
