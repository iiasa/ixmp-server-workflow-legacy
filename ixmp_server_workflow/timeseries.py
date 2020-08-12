import logging
from typing import Union
import os
import pandas as pd
import yaml

log = logging.getLogger(__name__)
NL = '\n'


def log_validation_errors(message: str, errors: list,
                          level=logging.WARNING, limit=100) -> None:
    log.log(level, f'{message}:')
    for error in errors[:limit]:
        log.log(level, f'- {error}')
    if len(errors) > limit:
        log.log(level, f'and {len(errors) - limit} more...')


def validate_variables_and_units(df: pd.DataFrame,
                                 variable_config: dict) -> bool:
    """ Check timeseries data to contain know variables and units

    :param df:              timeseries dataframe
    :param variable_config: variable configuration file
    :return True if validation pass, False otherwise
    """
    log.debug('Start variables/units validation')
    valid = True

    # check for unknown variable names
    unknown_variables = set(df.variable.unique()) - set(variable_config.keys())
    if len(unknown_variables) > 0:
        log_validation_errors('Unknown variable(s)', list(unknown_variables))
        valid = False

    # check variables for units
    unknown_variable_units = []
    for variable in variable_config:
        unit = variable_config[variable]['unit']
        variable_df = df[(df.variable == variable) & (df.unit != unit)]
        unknown_units = list(variable_df.unit.unique())
        if len(unknown_units) > 0:
            unknown_variable_units.append(f'{variable}: '
                                          f'{", ".join(unknown_units)}')
            valid = False
    if len(unknown_variable_units) > 0:
        log_validation_errors('Unknown unit(s) for variable(s):',
                              list(unknown_variable_units))

    log.debug('Finish variables/units validation')
    return valid


def validate_required_variables(df: pd.DataFrame,
                                variable_config: dict) -> bool:
    """ Check timeseries data to contain know variables and units

    :param df:              timeseries dataframe
    :param variable_config: variable configuration file
    :return True if validation pass, False otherwise
    """
    log.debug('Start required variables validation')
    valid = True
    scenarios = set(df.scenario.unique())
    models = set(df.model.unique())

    for variable in variable_config:
        required = variable_config[variable].get('required', False)
        if required:
            variable_df = df[(df.variable == variable)]
            invalid_models = models - set(variable_df.model.unique())
            if len(invalid_models) > 0:
                log.warning(f'Following models miss required variable '
                            f'{variable}: {", ".join(invalid_models)}')
                valid = False
            invalid_scenarios = scenarios - set(variable_df.scenario.unique())
            if len(invalid_scenarios) > 0:
                log.warning(f'Following scenarios miss required variable '
                            f'{variable}: {", ".join(invalid_scenarios)}')
                valid = False

    log.debug('Finish required variables validation')
    return valid


def validate_allowed_scenarios(df: pd.DataFrame,
                               allowed_scenarios: list) -> bool:
    """ Check whether dataframe contains only allowed scenarios

    :param df:                  timeseries dataframe
    :param allowed_scenarios:   list of allowed scenarios
    :return True if validation pass, False otherwise
    """
    scenarios = set(df.scenario.unique())
    unknown_scenarios = scenarios - set(allowed_scenarios)
    valid = True
    if len(unknown_scenarios) > 0:
        log_validation_errors('Scenario(s) not allowed',
                              list(unknown_scenarios))
        valid = False
    return valid


def validate_region_mappings(df: pd.DataFrame,
                             region_mapping_path: str) -> bool:
    """ Check whether for every model in dataframe exists region mapping

    :param df: timeseries dataframe
    :param region_mapping_path: path to region mappings
    :return True if validation pass, False otherwise
    """
    models = list(df.model.unique())
    valid = True
    if len(models) == 0:
        log.warning('No models to process!')
        valid = False
    for model in models:
        region_mapping = find_region_mapping(region_mapping_path, model)
        if not region_mapping:
            log.error(f'Region mapping not found for model `{model}`')
            valid = False
            continue

        native_regions = region_mapping['native_regions']
        region_aggregation = region_mapping['region_aggregation']
        valid_region_names = set(
            list(native_regions.keys()) +
            list(region_aggregation.keys()) +
            ['World'])
        invalid_region_names = (set(df[df.model == model].region.unique())
                                .difference(valid_region_names))
        if invalid_region_names:
            log.warning(f'Model {model} contains unknown region names: '
                        f'{", ".join(invalid_region_names)}')
            valid = False
    return valid


def read_config(config_path: str) -> Union[dict, list]:
    with open(config_path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def find_region_mapping(mappings_path: str, model: str) -> Union[dict, None]:
    if not os.path.isdir(mappings_path):
        log.error('Directory containing region mappings does not exists')
        return None

    for filename in os.listdir(mappings_path):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            with open(os.path.join(mappings_path, filename), 'r') as stream:
                region_mapping = yaml.load(stream, Loader=yaml.FullLoader)
                if region_mapping.get('model') == model:
                    return region_mapping
    return None
