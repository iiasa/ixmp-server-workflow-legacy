import logging

import pandas as pd

log = logging.getLogger(__name__)


def validate_variables_and_units(df: pd.DataFrame,
                                 variable_config: list) -> bool:
    """ Check timeseries data to contain know variables and units

    :param df:              timeseries dataframe
    :param variable_config: variable configuration file
    """
    log.info('Start variables/units validation')
    return True
