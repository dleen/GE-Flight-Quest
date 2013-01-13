from utilities import date_utilities as dut
from utilities import sanity_check as sc

from models import model_Using_New_Data_Format as mundf
from models import asdiday as ad

import pandas as pd
import numpy as np

import datetime

class Using_ASDI_time_est(mundf.Using_New_Data_Format):
    """
    Description
    """
    def __repr__(self):
        return "Using ASDI times"

    def add_column_asdi_time_est(self, day, data):
        date_columns = ['estimatedarrivalutc']

        for c in date_columns:
            day.asdi_flight_plan[c + '_minutes_after_midnight'] = \
                day.asdi_flight_plan[c].apply(lambda x: float(dut.minutes_difference(x,day.midnight_time)))

        asdiday = pd.merge(left=data, right=day.asdi_flight_plan, on='flight_history_id',
            how='left', sort=False)