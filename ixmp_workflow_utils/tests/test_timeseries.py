import pandas as pd
from ixmp_workflow_utils import *
import yaml

def test_read_config():
    obs = read_config('ixmp_workflow_utils/tests/sample_variable_config.yaml')
    assert isinstance(obs, dict)
    assert obs['Emissions|CO2']['unit'] == 'Mt CO2/yr'


def test_validate_variables(caplog):
    df = pd.read_csv('ixmp_workflow_utils/tests/sample_timeseries.csv')
    df = df[df.scenario == 'valid_scenario']
    cfg = read_config('ixmp_workflow_utils/tests/sample_variable_config.yaml')
    assert validate_variables_and_units(df, cfg)
    assert 'Unknown unit' not in caplog.text


def test_validate_variables_invalid_unit(caplog):
    df = pd.read_csv('ixmp_workflow_utils/tests/sample_timeseries.csv')
    cfg = read_config('ixmp_workflow_utils/tests/sample_variable_config.yaml')
    assert not validate_variables_and_units(df, cfg)
    assert 'Unknown unit' in caplog.text


def test_validate_variables_invalid_variable(caplog):
    df = pd.read_csv('ixmp_workflow_utils/tests/sample_timeseries.csv')
    cfg = read_config('ixmp_workflow_utils/tests/sample_variable_config.yaml')
    assert not validate_variables_and_units(df, cfg)
    assert 'Unknown variable' in caplog.text


def test_validate_allowed_scenarios(caplog):
    df = pd.read_csv('ixmp_workflow_utils/tests/sample_timeseries.csv')
    with open('ixmp_workflow_utils/tests'
              '/sample_allowed_scenarios.yaml', 'r') as f:
        allowed_scenarios = yaml.load(f, yaml.FullLoader)
    assert not validate_allowed_scenarios(df, allowed_scenarios)
    assert 'Scenario(s) not allowed' in caplog.text
