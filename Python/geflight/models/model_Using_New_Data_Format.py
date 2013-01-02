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

# def rectify(x):
#     if x < 0:
#         return 0
#     else:
#         return x

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
        pred.flight_predictions['actual_runway_arrival'] = data['ERA_minutes_after_cutoff']
        pred.flight_predictions['actual_gate_arrival']   = data['EGA_minutes_after_cutoff']

        pred.flight_predictions['actual_runway_arrival'] = \
            pred.flight_predictions['actual_runway_arrival'].apply(lambda x: rectify(x))

        pred.flight_predictions['actual_gate_arrival'] = \
            pred.flight_predictions['actual_gate_arrival'].apply(lambda x: rectify(x))


        temp1 = data[pd.isnull(data['EGA_minutes_after_cutoff'])]
        temp2 = data[pd.isnull(data['ERA_minutes_after_cutoff'])]

        if len(temp1) or len(temp2):
            print "MISSING values got through"

        pred.test_data = day.test_data.copy()

        if day.mode in ["training", "nofiltering"]: 
            pred.test_data = \
                dut.convert_predictions_from_datetimes_to_minutes(pred.test_data, day.midnight_time)

        sc.sanity_check(pred, "training")

        return pred

    def initial_prediction(self, data):
        temp = data[data['ERA_most_recent'] > data['EGA_most_recent']]

        for i, row in temp.iterrows():
            if row['gate_delay_mins'] >= 0:
                gd = datetime.timedelta(seconds=row['gate_delay_mins'])
                data['EGA_minutes_after_cutoff'][i] = data['ERA_minutes_after_cutoff'][i] + gd
            elif row['gate_delay_mins'] < 0:
                gd = datetime.timedelta(seconds=abs(row['gate_delay_mins']))
                data['EGA_minutes_after_cutoff'][i] = data['ERA_minutes_after_cutoff'][i]
                data['ERA_minutes_after_cutoff'][i] = data['EGA_minutes_after_cutoff'][i] - gd
            else:
                data['EGA_minutes_after_cutoff'][i] = data['ERA_minutes_after_cutoff'][i]

    def load_day(self, folder_name):
        data = pd.read_csv('output_csv/parsed_fhe_' + folder_name + '_' + 'test_data' + '_filtered.csv', 
            na_values=["MISSING"], keep_default_na=True)
        return data

    def check_for_missing_era(self, data, midnight, cutoff):
        data['ERA_minutes_after_cutoff'] = data['ERA_minutes_after_cutoff'].apply(lambda x: float(x))

        temp = data[pd.isnull(data['ERA_minutes_after_cutoff'])]

        for i, row in temp.iterrows():
            data['ERA_minutes_after_cutoff'][i] = \
                self.ERA_pick_times_in_order(row, midnight, cutoff)

    def check_for_missing_ega(self, data, midnight, cutoff):
        data['EGA_minutes_after_cutoff'] = data['EGA_minutes_after_cutoff'].apply(lambda x: float(x))

        temp = data[pd.isnull(data['EGA_minutes_after_cutoff'])]

        for i, row in temp.iterrows():
            data['EGA_minutes_after_cutoff'][i] = \
                self.EGA_pick_times_in_order(row, midnight, cutoff)

    def EGA_pick_times_in_order(self, row, midnight, cutoff):
        if pd.notnull(row['EGA_minutes_after_cutoff']):
            return row['EGA_minutes_after_cutoff']
        elif pd.notnull(row['ERA_minutes_after_cutoff']):
            return row['ERA_minutes_after_cutoff']
        elif pd.notnull(row['scheduled_gate_arrival']):
            return dut.minutes_difference(dut.parse_to_utc(row['scheduled_gate_arrival']), midnight)
        else:
            self.ERA_pick_times_in_order(row, midnight)

    def ERA_pick_times_in_order(self, row, midnight, cutoff):
        if pd.notnull(row['ERA_minutes_after_cutoff']):
            return row['ERA_minutes_after_cutoff']
        elif pd.notnull(row['EGA_minutes_after_cutoff']):
            return row['EGA_minutes_after_cutoff']
        elif pd.notnull(row['scheduled_runway_arrival']):
            return dut.minutes_difference(dut.parse_to_utc(row['scheduled_runway_arrival']), midnight)
        elif pd.notnull(row['published_arrival']):
            return dut.minutes_difference(dut.parse_to_utc(row['published_arrival']), midnight)
        elif cutoff:
            return dut.minutes_difference(cutoff, midnight)
        else:
            print row
            print "NO TIME TO USE"


# Update it to best 9.029 model and check it that works.

# Then try and beat it.
