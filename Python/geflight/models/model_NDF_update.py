from models import model_Using_New_Data_Format as mundf

import flightday as fd
from utilities import date_utilities as dut
from utilities import test_data_utils as tdu
from utilities import row_helper_functions as rhf
from utilities import rmse
from utilities import column_functions as cf
from utilities import sanity_check as sc

import pandas as pd
import numpy as np

import datetime

class NDF_upd(mundf.Using_New_Data_Format):
    """
    Description
    """
    def __repr__(self):
        return "NDF Update"

    def using_most_recent_updates_individual_day(self, day, pred):

        data = self.load_day(day.folder_name)

        data = self.add_column_avg_gate_delays_by_arr_airport_and_airline(data)

        self.check_for_missing_era(data, day.midnight_time, day.cutoff_time)
        self.check_for_missing_ega(data, day.midnight_time, day.cutoff_time)


        self.initial_prediction(data)


        pred.flight_predictions = pred.flight_predictions.reindex(range(len(data['flight_history_id'])))

        pred.flight_predictions['flight_history_id']     = data['flight_history_id']
        pred.flight_predictions['actual_runway_arrival'] = data['ERA_most_recent_minutes_after_midnight']
        pred.flight_predictions['actual_gate_arrival']   = data['EGA_most_recent_minutes_after_midnight']

        pred.flight_predictions['actual_runway_arrival'] = \
            pred.flight_predictions['actual_runway_arrival'].apply(lambda x: self.rectify(x))

        pred.flight_predictions['actual_gate_arrival'] = \
            pred.flight_predictions['actual_gate_arrival'].apply(lambda x: self.rectify(x))

        temp1 = data[pd.isnull(data['EGA_most_recent_minutes_after_midnight'])]
        temp2 = data[pd.isnull(data['ERA_most_recent_minutes_after_midnight'])]

        if len(temp1) or len(temp2):
            print "MISSING values got through"

        pred.test_data = data[['flight_history_id','actual_runway_arrival_minutes_after_midnight',
            'actual_gate_arrival_minutes_after_midnight']]

        pred.test_data.columns = ['flight_history_id','actual_runway_arrival','actual_gate_arrival']

        if "training" in day.mode:
            sc.sanity_check(pred, "training")

        return pred

    def add_column_avg_gate_delays_by_arr_airport_and_airline(self, data):
        """
        Description
        """
        gaggo = pd.read_csv('output_csv/average_gate_delay_by_arrival_airport_and_airline.csv')

        temp = pd.merge(left=data, 
            right=gaggo, on=['arrival_airport_icao_code','airline_icao_code'], how='left', sort=False)

        return temp
