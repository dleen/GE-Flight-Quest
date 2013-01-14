from utilities import date_utilities as dut
from utilities import sanity_check as sc

from models import model_Using_New_Data_Format as mundf
from models import asdiday as ad

import pandas as pd


class Using_ASDI_time_est(mundf.Using_New_Data_Format):
    """
    Description
    """
    def __repr__(self):
        return "Using ASDI times"

    def calculate_predictions(self, day, pred):
        """
        Main function for the model
        """

        # Load the data for the day
        data = self.load_day(day.folder_name)

        # Add the airport / airline delay column
        if "gate_delay_seconds" not in data.columns:
            data = \
            self.add_column_avg_gate_delays_by_arr_airport_and_airline(data)

        # Add the asdi estimate column
        if "estimatedarrivalutc_minutes_after_midnight" not in data.columns:
            day.asdi_flight_plan = self.get_most_recent_asdi_time_est(day)
            data = self.add_column_asdi_time_est(day, data)

        # Check for missing ERA / EGA values and if any are found replace them
        # with sensible values
        self.check_for_missing_era(data, day.midnight_time, day.cutoff_time)
        self.check_for_missing_ega(data, day.midnight_time, day.cutoff_time)

        # Fixes times where the runway arrival > gate arrival times
        self.fix_bad_EGA_times(data)

        self.use_asdi_est(data)

        # Replace any negative times with zero.
        # There's probably sometime better to do here?
        data['ERA_most_recent_minutes_after_midnight'] = \
            data['ERA_most_recent_minutes_after_midnight'].apply(
                lambda x: self.rectify(x))
        data['EGA_most_recent_minutes_after_midnight'] = \
            data['EGA_most_recent_minutes_after_midnight'].apply(
                lambda x: self.rectify(x))

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

        # self.save_day(pred, data, day.folder_name)

        # Return the prediction for this day
        return pred

    def add_column_asdi_time_est(self, day, data):
        date_columns = ['estimatedarrivalutc']

        for c in date_columns:
            day.asdi_flight_plan[c + '_minutes_after_midnight'] = \
                day.asdi_flight_plan[c].apply(lambda x: float(dut.minutes_difference(x, day.midnight_time)))

        data_with_asdi_est = pd.merge(left=data, right=day.asdi_flight_plan, on='flight_history_id',
            how='left', sort=False)

        return data_with_asdi_est

    def get_most_recent_asdi_time_est(self, day):
        asdi_grouped = day.asdi_flight_plan.groupby('flight_history_id')
        most_recent = asdi_grouped.apply(self.max_time_row)

        return most_recent

    def max_time_row(self, group):
        g_sort = group.sort_index(by='updatetimeutc', ascending=False).reset_index(drop=True)
        return g_sort.ix[0]

    def use_asdi_est(self, data):
        temp = data['estimatedarrivalutc_minutes_after_midnight'].notnull()

        data['ERA_most_recent_minutes_after_midnight'][temp] = \
            (data['estimatedarrivalutc_minutes_after_midnight'][temp] + \
            data['ERA_most_recent_minutes_after_midnight'][temp]) / 2.0

    def ERA_pick_times_in_order(self, row, midnight, cutoff):
        """
        When the ERA is missing go through an list of alternatives:
        """
        # Check for the ERA
        if pd.notnull(row['ERA_most_recent_minutes_after_midnight']):
            return row['ERA_most_recent_minutes_after_midnight']
        # ASDI estimate
        if pd.notnull(row['estimatedarrivalutc_minutes_after_midnight']):
            return row['estimatedarrivalutc_minutes_after_midnight']
        # Check for the actual runway departure and air time
        # and if both exist: add the two together.
        # scheduled_air_time == estimated time from dep runway to arr runway
        elif pd.notnull(row['actual_runway_departure_minutes_after_midnight'])\
            and pd.notnull(row['scheduled_air_time']):
            return row['actual_runway_departure_minutes_after_midnight'] + \
                row['scheduled_air_time']
        # Else us the gate arrival time and subtract the average time to
        # reach the gate for the given airport and airline
        elif pd.notnull(row['EGA_most_recent_minutes_after_midnight']) and \
            pd.notnull(row['gate_delay_seconds']):
            return row['EGA_most_recent_minutes_after_midnight'] - \
                row['gate_delay_seconds'] / float(60)
        # Else use the scheduled time
        elif pd.notnull(
            row['scheduled_runway_arrival_minutes_after_midnight']):
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
