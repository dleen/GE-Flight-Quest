import flightday as fd
from utilities import date_utilities as dut
from utilities import test_data_utils as tdu
from utilities import row_helper_functions as rhf
from utilities import rmse
from utilities import column_functions as cf
from utilities import sanity_check as sc

import pandas as pd


class Using_New_Data_Format():
    """
    Description
    """
    def __repr__(self):
        return "Using new data format"

    def run_day(self, day, pred):
        """
        All models should have a function like this.
        This says how to run the model/return a prediction
        for a single day.
        """
        return self.using_most_recent_updates_individual_day(day, pred)
