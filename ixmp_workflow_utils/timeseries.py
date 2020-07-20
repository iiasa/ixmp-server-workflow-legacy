import logging

import pandas as pd
import yaml

log = logging.getLogger(__name__)


def validate_variables_and_units(df: pd.DataFrame,
                                 variable_config: dict) -> bool:
    """ Check timeseries data to contain know variables and units

    :param df:              timeseries dataframe
    :param variable_config: variable configuration file
    """
    log.debug('Start variables/units validation')
    valid = True

    # check for unknown variable names
    unknown_variables = set(df.variable.unique()) - set(variable_config.keys())
    if len(unknown_variables) > 0:
        log.warning(f'Unknown variable(s): {", ".join(unknown_variables)}')
        valid = False

    # check variables for units
    for variable in variable_config:
        unit = variable_config[variable]['unit']
        variable_df = df[(df.variable == variable) & (df.unit != unit)]
        unknown_units = list(variable_df.unit.unique())
        if len(unknown_units) > 0:
            log.warning(f'Unknown unit(s) for variable {variable}: '
                        f'{", ".join(unknown_units)}')
            valid = False
    log.debug('Finish variables/units validation')
    return valid


def validate_allowed_scenarios(df: pd.DataFrame,
                               allowed_scenarios: list) -> bool:
    scenarios = set(df.scenario.unique())
    unknown_scenarios = scenarios - set(allowed_scenarios)
    valid = True
    if len(unknown_scenarios) > 0:
        log.warning(f'Scenario(s) not allowed: {", ".join(unknown_scenarios)}')
        valid = False
    return valid


def read_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
