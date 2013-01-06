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



def add_column_avg_gate_delays_by_arr_airport(data):
    """
    Description
    """
    gaggo = pd.read_csv('output_csv/average_gate_delay_by_arrival_airport.csv')

    temp = pd.merge(left=data, 
        right=gaggo, on='arrival_airport_icao_code', how='left', sort=False)

    return temp

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

    def using_most_recent_updates_individual_day(self, day, pred):

        data = self.load_day(day.folder_name)

        data = add_column_avg_gate_delays_by_arr_airport(data)

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

    def initial_prediction(self, data):
        temp = data[data['ERA_most_recent_minutes_after_midnight'] > data['EGA_most_recent_minutes_after_midnight']]

        for i, row in temp.iterrows():
            if row['gate_delay_seconds'] >= 0:
                gd = row['gate_delay_seconds'] / float(60)
                data['EGA_most_recent_minutes_after_midnight'][i] = \
                    data['ERA_most_recent_minutes_after_midnight'][i] + gd
            elif row['gate_delay_seconds'] < 0:
                gd = abs(row['gate_delay_seconds']) / float(60)
                data['EGA_most_recent_minutes_after_midnight'][i] = \
                    data['ERA_most_recent_minutes_after_midnight'][i]
                data['ERA_most_recent_minutes_after_midnight'][i] = \
                    data['EGA_most_recent_minutes_after_midnight'][i] - gd
            else:
                data['EGA_most_recent_minutes_after_midnight'][i] = \
                    data['ERA_most_recent_minutes_after_midnight'][i]

    def load_day(self, folder_name):
        data = pd.read_csv('output_csv/parsed_fhe_' + folder_name + '_' + 'test' + '_filtered_with_dates.csv', 
        # data = pd.read_csv('output_csv/parsed_fhe_' + folder_name + '_' + 'test' + '_filtered.csv', 
            na_values=["MISSING"], keep_default_na=True)
        return data

    def save_day(self, pred, data):
        pred_rename = pred.flight_predictions.rename(columns={'actual_runway_arrival' : 'best_model_ARA',
            'actual_gate_arrival' : 'best_model_AGA'})

        data = pd.merge(left=data, right=pred_rename, on='flight_history_id',
            how='left', sort=False)

        data.to_csv('output_csv/parsed_fhe_' + day.folder_name + '_' + "test" + \
            '_filtered_with_dates_with_best_prediction.csv', index=False, na_rep="MISSING")

    def check_for_missing_era(self, data, midnight, cutoff):
        temp = data[pd.isnull(data['ERA_most_recent_minutes_after_midnight'])]

        for i, row in temp.iterrows():
            data['ERA_most_recent_minutes_after_midnight'][i] = \
                self.ERA_pick_times_in_order(row, midnight, cutoff)

    def check_for_missing_ega(self, data, midnight, cutoff):
        temp = data[pd.isnull(data['EGA_most_recent_minutes_after_midnight'])]

        for i, row in temp.iterrows():
            data['EGA_most_recent_minutes_after_midnight'][i] = \
                self.EGA_pick_times_in_order(row, midnight, cutoff)

    def EGA_pick_times_in_order(self, row, midnight, cutoff):
        if pd.notnull(row['EGA_most_recent_minutes_after_midnight']):
            return row['EGA_most_recent_minutes_after_midnight']
        elif pd.notnull(row['ERA_most_recent_minutes_after_midnight']):
            return row['ERA_most_recent_minutes_after_midnight']
        elif pd.notnull(row['scheduled_gate_arrival_minutes_after_midnight']):
            return row['scheduled_gate_arrival_minutes_after_midnight']
        else:
            self.ERA_pick_times_in_order(row, midnight)

    def ERA_pick_times_in_order(self, row, midnight, cutoff):
        if pd.notnull(row['ERA_most_recent_minutes_after_midnight']):
            return row['ERA_most_recent_minutes_after_midnight']
        elif pd.notnull(row['EGA_most_recent_minutes_after_midnight']):
            return row['EGA_most_recent_minutes_after_midnight']
        elif pd.notnull(row['scheduled_runway_arrival_minutes_after_midnight']):
            return row['scheduled_runway_arrival_minutes_after_midnight']
        elif pd.notnull(row['published_arrival_minutes_after_midnight']):
            return row['published_arrival_minutes_after_midnight']
        elif cutoff:
            return dut.minutes_difference(cutoff, midnight)
        else:
            print row
            print "NO TIME TO USE"

    def rectify(self, x):
        if x < 0:
            return 0
        else:
            return x
