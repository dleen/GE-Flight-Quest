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

class NDF_upd_2(mundf.Using_New_Data_Format):
    """
    Description
    """
    def __repr__(self):
        return "NDF Update part 2"

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

    def initial_prediction(self, data):
        temp = data[data['ERA_most_recent_minutes_after_midnight'] > data['EGA_most_recent_minutes_after_midnight']]

        # for i, row in temp.iterrows():
        #     data['EGA_most_recent_minutes_after_midnight'][i] = \
        #         data['ERA_most_recent_minutes_after_midnight'][i]


        # pos_delay = data[data['gate_delay_seconds'] >= 0]
        # temp = pos_delay[pos_delay['EGA_most_recent_minutes_after_midnight'] - \
        #     pos_delay['ERA_most_recent_minutes_after_midnight'] > \
        #     pos_delay['gate_delay_seconds'] / float(60)]

        # for i, row in temp.iterrows():
        #     data['EGA_most_recent_minutes_after_midnight'][i] = \
        #         data['ERA_most_recent_minutes_after_midnight'][i] + \
        #         data['gate_delay_seconds'][i] / float(60)

        # neg_delay = data[data['gate_delay_seconds'] < 0]
        # temp = neg_delay[neg_delay['EGA_most_recent_minutes_after_midnight'] - \
        #         neg_delay['ERA_most_recent_minutes_after_midnight'] > \
        #     abs(neg_delay['gate_delay_seconds'] / float(60))]

        # for i, row in temp.iterrows():
        #     data['EGA_most_recent_minutes_after_midnight'][i] = \
        #         data['ERA_most_recent_minutes_after_midnight'][i] + \
        #         abs(data['gate_delay_seconds'][i] / float(60))

        for i, row in temp.iterrows():
            if row['gate_delay_seconds'] >= 0:
                gd = row['gate_delay_seconds'] / float(60)
                data['EGA_most_recent_minutes_after_midnight'][i] = \
                    data['ERA_most_recent_minutes_after_midnight'][i] + gd
            elif row['gate_delay_seconds'] < 0:
                gd = abs(row['gate_delay_seconds']) / float(60)
                data['EGA_most_recent_minutes_after_midnight'][i] = \
                    data['ERA_most_recent_minutes_after_midnight'][i] + gd
            else:
                data['EGA_most_recent_minutes_after_midnight'][i] = \
                    data['ERA_most_recent_minutes_after_midnight'][i]

    def EGA_pick_times_in_order(self, row, midnight, cutoff):
        if pd.notnull(row['EGA_most_recent_minutes_after_midnight']):
            return row['EGA_most_recent_minutes_after_midnight']
        elif pd.notnull(row['actual_gate_departure_minutes_after_midnight']) and \
            pd.notnull(row['scheduled_block_time']):
            return row['actual_gate_departure_minutes_after_midnight'] + \
                row['scheduled_block_time']
        elif pd.notnull(row['ERA_most_recent_minutes_after_midnight']) and \
            pd.notnull(row['gate_delay_seconds']):
            return row['ERA_most_recent_minutes_after_midnight'] + \
                row['gate_delay_seconds'] / float(60)
        elif pd.notnull(row['scheduled_gate_arrival_minutes_after_midnight']):
            return row['scheduled_gate_arrival_minutes_after_midnight']
        else:
            self.ERA_pick_times_in_order(row, midnight)

    def ERA_pick_times_in_order(self, row, midnight, cutoff):
        """
        When the ERA is missing go through an list of alternatives:
        """
        if pd.notnull(row['ERA_most_recent_minutes_after_midnight']):
            return row['ERA_most_recent_minutes_after_midnight']
        elif pd.notnull(row['actual_runway_departure_minutes_after_midnight']) and \
            pd.notnull(row['scheduled_air_time']):
            return row['actual_runway_departure_minutes_after_midnight'] + \
                row['scheduled_air_time']        
        elif pd.notnull(row['EGA_most_recent_minutes_after_midnight']) and \
            pd.notnull(row['gate_delay_seconds']):
            return row['EGA_most_recent_minutes_after_midnight'] - \
                row['gate_delay_seconds'] / float(60)
        elif pd.notnull(row['scheduled_runway_arrival_minutes_after_midnight']):
            return row['scheduled_runway_arrival_minutes_after_midnight']
        elif pd.notnull(row['published_arrival_minutes_after_midnight']):
            return row['published_arrival_minutes_after_midnight']
        elif cutoff:
            return dut.minutes_difference(cutoff, midnight)
        else:
            print row
            print "NO TIME TO USE" 

    def add_column_avg_gate_delays_by_arr_airport_and_airline(self, data):
        """
        Add the gate delay column to the data frame
        """
        gate_delays = pd.read_csv('output_csv/average_gate_delay_by_arrival_airport_and_airline.csv')

        data_with_delays = pd.merge(left=data, 
            right=gate_delays, on=['arrival_airport_icao_code','airline_icao_code'], how='left', sort=False)

        return data_with_delays
