import json
from pathlib import Path
import nbformat

ROOT=Path(__file__).resolve().parents[1]

def test_required_notebooks_exist():
    for i in range(1,9):
        assert list((ROOT/'notebooks').glob(f'{i:02d}_*.ipynb'))

def test_notebook_json():
    for p in (ROOT/'notebooks').glob('*.ipynb'):
        nb=nbformat.read(p,as_version=4)
        assert len(nb.cells)>0

def test_observed_reconciliation():
    x=json.loads((ROOT/'results/observed_results.json').read_text())
    assert x['eligible_pickups']+x['ineligible_pickups']==x['silver_rows']
    assert x['observed_zones']*x['hours']==x['gold_rows']
    assert x['observed_nonzero_zone_hours']+x['zero_filled_zone_hours']==x['gold_rows']
    assert x['training_rows']+x['validation_rows']+x['test_rows']==x['model_ready_rows']
