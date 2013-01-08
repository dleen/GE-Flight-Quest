from utilities import date_utilities as dut
from utilities import sanity_check as sc

import pandas as pd
import numpy as np

import datetime


class Using_New_Data_Format():
    """
    Description
    """
    def __repr__(self):
        return "Using new data format"

    def __init__(self, folder_name):
        """
        Folder name specifies the location of where it should load the data from
        """
        self.condensed_data_folder_name = folder_name

    def run_day(self, day, pred):
        """
        All models should have a function like this.
        This says how to run the model/return a prediction
        for a single day.
        """
        return self.calculate_predictions(day, pred)

    def calculate_predictions(self, day, pred):
        """
        Main function for the model
        """

        # Load the data for the day
        data = self.load_day(day.folder_name)

        # Add the airport / airline delay column
        data = self.add_column_avg_gate_delays_by_arr_airport_and_airline(data)

        # Check for missing ERA / EGA values and if any are found replace them
        # with sensible values
        self.check_for_missing_era(data, day.midnight_time, day.cutoff_time)
        self.check_for_missing_ega(data, day.midnight_time, day.cutoff_time)

        # Fixes times where the runway arrival > gate arrival times
        self.fix_bad_EGA_times(data)

        # Replace any negative times with zero.
        # There's probably sometime better to do here?
        data['ERA_most_recent_minutes_after_midnight'] = \
            data['ERA_most_recent_minutes_after_midnight'].apply(lambda x: self.rectify(x))
        data['EGA_most_recent_minutes_after_midnight'] = \
            data['EGA_most_recent_minutes_after_midnight'].apply(lambda x: self.rectify(x))      

        # Check if any missing values made it through 
        self.test_for_missing(data)

        # Read the final ERA / EGA times from the data and put them
        # into the predictions object
        pred.get_predictions_from_data(data)

        # Get the 'test data' i.e. the true values for the times we're
        # trying to predict
        pred.get_test_from_data(data)

        # If we're in training mode, i.e. we know the true values
        # then run the code to tell us where the biggest problems are
        # and if we've made any really bad predictions!
        if "training" in day.mode:
            sc.sanity_check(pred, "training")

        self.save_day(pred, data, day.folder_name)

        # Return the prediction for this day
        return pred

    def test_for_missing(self, data):
        """
        Check for any MISSING or NULL values
        """
        temp1 = data[pd.isnull(data['EGA_most_recent_minutes_after_midnight'])]
        temp2 = data[pd.isnull(data['ERA_most_recent_minutes_after_midnight'])]

        if len(temp1) or len(temp2):
            print "MISSING values got through"

    def fix_bad_EGA_times(self, data):
        """
        A simple way to fix the situation where the ERA time is 
        greater than the EGA time. We assume that the ERA time is 
        correct and that the problem is with the gate arrival time.
        To fix this problem we say the new gate arrival time is actually
        the runway time plus the average time it takes to reach the gate
        from the runway for a given airport and airline 
        """
        temp = data[data['ERA_most_recent_minutes_after_midnight'] > data['EGA_most_recent_minutes_after_midnight']]

        for i, row in temp.iterrows():
            # The gate delay can be a positive time or the delay
            # can represent an early arrival as a negative time
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

    def load_day(self, folder_name):
        """
        Load the data needed for this model.
        """
        # data = pd.read_csv('/Users/dleen/Dropbox/GE Flight Quest/Data_for_modeling/' + \
        #     'model_2012_01_04/parsed_fhe_' + folder_name + '_' + 'test' + \
        #     '_filtered_with_dates_with_best_prediction.csv',             
        #     na_values=["MISSING"], keep_default_na=True)

        data = pd.read_csv(self.condensed_data_folder_name + \
            '/parsed_fhe_' + folder_name + '_' + 'test' + \
            '_filtered_with_dates_with_best_prediction.csv', 
            na_values=["MISSING"], keep_default_na=True)

        # data = pd.read_csv('output_csv/parsed_fhe_' + folder_name + '_' + 'test' + '_filtered.csv', 
        # na_values=["MISSING"], keep_default_na=True)

        return data

    def save_day(self, pred, data, folder_name):
        """
        Saves the output of this model for other uses.
        Output is saved to csv file
        """
        pred_rename = pred.flight_predictions.rename(columns={'actual_runway_arrival' : 'best_model_ARA',
            'actual_gate_arrival' : 'best_model_AGA'})

        if "best_model_ARA" not in data.columns and \
            "best_model_AGA" not in data.columns:
            data = pd.merge(left=data, right=pred_rename, on='flight_history_id',
                how='left', sort=False)
        else:
            data['best_model_ARA'] = pred_rename['best_model_ARA']
            data['best_model_AGA'] = pred_rename['best_model_AGA']

        data.to_csv('output_csv/parsed_fhe_' + folder_name + '_' + "test" + \
            '_filtered_with_dates_with_best_prediction.csv', index=False, na_rep="MISSING")

    def check_for_missing_era(self, data, midnight, cutoff):
        """
        Go through data checking for any missing ERA times and replace with
        times picked using ERA_pick_times_in_order
        """
        temp = data[pd.isnull(data['ERA_most_recent_minutes_after_midnight'])]

        for i, row in temp.iterrows():
            data['ERA_most_recent_minutes_after_midnight'][i] = \
                self.ERA_pick_times_in_order(row, midnight, cutoff)

    def check_for_missing_ega(self, data, midnight, cutoff):
        """
        Go through data checking for any missing EGA times and replace with
        times picked using EGA_pick_times_in_order
        """
        temp = data[pd.isnull(data['EGA_most_recent_minutes_after_midnight'])]

        for i, row in temp.iterrows():
            data['EGA_most_recent_minutes_after_midnight'][i] = \
                self.EGA_pick_times_in_order(row, midnight, cutoff)

    def EGA_pick_times_in_order(self, row, midnight, cutoff):
        """
        When the EGA is missing go through an list of alternatives:
        """
        # Check for the EGA
        if pd.notnull(row['EGA_most_recent_minutes_after_midnight']):
            return row['EGA_most_recent_minutes_after_midnight']
        # Check for the actual gate departure and block time
        # and if both exist: add the two together.
        # scheduled_block_time == estimated time from dep gate to arr gate
        elif pd.notnull(row['actual_gate_departure_minutes_after_midnight']) and \
            pd.notnull(row['scheduled_block_time']):
            return row['actual_gate_departure_minutes_after_midnight'] + \
                row['scheduled_block_time']
        # Use the runway arrival time and add on the average time to 
        # reach the gate for the given airport and airline
        elif pd.notnull(row['ERA_most_recent_minutes_after_midnight']) and \
            pd.notnull(row['gate_delay_seconds']):
            return row['ERA_most_recent_minutes_after_midnight'] + \
                row['gate_delay_seconds'] / float(60)
        # Use the scheduled time
        elif pd.notnull(row['scheduled_gate_arrival_minutes_after_midnight']):
            return row['scheduled_gate_arrival_minutes_after_midnight']
        # Finally use the runway times and add on the gate delay 
        else:
            era_time = self.ERA_pick_times_in_order(row, midnight)
            return era_time + row['gate_delay_seconds'] / float(60)

    def ERA_pick_times_in_order(self, row, midnight, cutoff):
        """
        When the ERA is missing go through an list of alternatives:
        """
        # Check for the ERA
        if pd.notnull(row['ERA_most_recent_minutes_after_midnight']):
            return row['ERA_most_recent_minutes_after_midnight']
        # Check for the actual runway departure and air time
        # and if both exist: add the two together.
        # scheduled_air_time == estimated time from dep runway to arr runway        
        elif pd.notnull(row['actual_runway_departure_minutes_after_midnight']) and \
            pd.notnull(row['scheduled_air_time']):
            return row['actual_runway_departure_minutes_after_midnight'] + \
                row['scheduled_air_time']
        # Else us the gate arrival time and subtract the average time to
        # reach the gate for the given airport and airline
        elif pd.notnull(row['EGA_most_recent_minutes_after_midnight']) and \
            pd.notnull(row['gate_delay_seconds']):
            return row['EGA_most_recent_minutes_after_midnight'] - \
                row['gate_delay_seconds'] / float(60)
        # Else use the scheduled time
        elif pd.notnull(row['scheduled_runway_arrival_minutes_after_midnight']):
            return row['scheduled_runway_arrival_minutes_after_midnight']
        # Else use the published arrival time
        elif pd.notnull(row['published_arrival_minutes_after_midnight']):
            return row['published_arrival_minutes_after_midnight']
        # Else use the cutoff time as the estimate 
        elif cutoff:
            return dut.minutes_difference(cutoff, midnight)
        # Otherwise there's a problem
        else:
            print row
            print "NO TIME TO USE" 

    def rectify(self, x):
        if x < 0:
            return 0
        else:
            return x

    def add_column_avg_gate_delays_by_arr_airport_and_airline(self, data):
        """
        Add the gate delay column to the data frame
        """
        # Read in the delays
        gate_delays = pd.read_csv('output_csv/average_gate_delay_by_arrival_airport_and_airline.csv')

        # Merge them with the existing data
        data_with_delays = pd.merge(left=data, 
            right=gate_delays, on=['arrival_airport_icao_code','airline_icao_code'], how='left', sort=False)

        return data_with_delays

    def add_column_avg_gate_delays_by_arr_airport(data):
        """
        Description
        """
        gate_delays = pd.read_csv('output_csv/average_gate_delay_by_arrival_airport_and_airline.csv')

        data_with_delays = pd.merge(left=data, 
            right=gate_delays, on='arrival_airport_icao_code', how='left', sort=False)

        return data_with_delays
