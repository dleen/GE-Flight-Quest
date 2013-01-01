import flightday as fd
from utilities import date_utilities as dut
from utilities import test_data_utils as tdu
from utilities import row_helper_functions as rhf
from utilities import rmse
from utilities import column_functions as cf
from utilities import sanity_check as sc

import pandas as pd

#
# Possible improvement!
#
# Instead of doing a join first then applying functions,
# first group each file by flight id, apply functions to each 
# group and then join? Will this cause some data to be inaccessible?
# Maybe just have the function applied to each group operate as a 
# data transformation type function rather than doing some fancy
# prediction calculation.
#


class MRU:
    """
    Description
    """
    def __repr__(self):
        return "Original model"

    def run_day(self, day, pred):
        """
        All models should have a function like this.
        This says how to run the model/return a prediction
        for a single day.
        """
        return self.using_most_recent_updates_individual_day(day, pred)

    def flight_history_id_grouping(self, day):
        """
        This function does a "left join" (exactly like SQL join) using the test data flight ids
        as the left data and the flight history events as the right data. We then join the rest
        of the flight history data in a similar manner.
        Maybe this second join will be changed to something smarter?
        """
        joined_data = pd.merge(left=day.test_data, right=day.flight_history_events, 
                               on='flight_history_id', how='left', sort=False)
        joined_data = pd.merge(left=joined_data, right=day.flight_history, 
                               on='flight_history_id', how='left', sort=False)

        for c in cf.unnecessary_columns():
            del joined_data[c]

        grouped_on_fhid = joined_data.groupby('flight_history_id')

        return grouped_on_fhid

    def using_most_recent_updates_individual_day(self, day, pred):
        """
        Given a day of flights calculates the most recent update for runway and
        gate arrival for each of the flights. Enters this into the flight prediction
        dataframe. Replaces any missing values with just the value of the cutoff time.
        Finally converts the predictions to minutes past midnight.
        """
        flight_events = self.flight_history_id_grouping(day)

        fid = []; era = []; ega = []

        for flight_id, event_group in flight_events:
            [er, eg] = self.find_most_recent_event_update(event_group)
            fid.append(flight_id)
            era.append(er)
            ega.append(eg)

        pred.flight_predictions = pred.flight_predictions.reindex(range(len(fid)))

        pred.flight_predictions['flight_history_id']     = fid
        pred.flight_predictions['actual_runway_arrival'] = era
        pred.flight_predictions['actual_gate_arrival']   = ega

        # Better na than cutoff?
        pred.flight_predictions = \
            pred.flight_predictions.fillna(value=day.cutoff_time)

        pred.flight_predictions = \
            dut.convert_predictions_from_datetimes_to_minutes(pred.flight_predictions, day.midnight_time)

        pred.test_data = day.test_data.copy()

        if day.mode == "training": 
            pred.test_data = \
                dut.convert_predictions_from_datetimes_to_minutes(pred.test_data, day.midnight_time)

        sc.sanity_check(pred, day.mode)

        return pred

    def find_most_recent_event_update(self, event_group):
        """
        Takes in a group of events corresponding to one flight history id.
        Parses the events looking for estimated runway arrival or gate updates
        and returns the most recent update for each.
        """
        event_group = event_group.sort_index(by='date_time_recorded', ascending=False)

        event_list = event_group['data_updated']

        offset = event_group["arrival_airport_timezone_offset"].ix[event_group.index[0]]
        if offset>0:
            offset_str = "+" + str(offset)
        else:
            offset_str = str(offset)

        era_est = self.get_updated_event_arrival(event_list, 
            event_group.ix[event_group.index[0]], "runway", offset_str)

        ega_est = self.get_updated_event_arrival(event_list, 
            event_group.ix[event_group.index[0]], "gate", offset_str)

        return [era_est, ega_est]

    def get_updated_event_arrival(self, event_list, row, arrival_type, offset_str):
        """
        Returns the most recent estimate of the arrival time. If that
        cannot be found it resorts to using the scheduled arrival times.
        """
        if arrival_type == "runway":
            sig = "ERA"
        elif arrival_type == "gate":
            sig = "EGA"
        else:
            print "Problem with signal type!"

        est_list = event_list.apply(lambda x: rhf.parse_fhe_events(x, sig))
        est = self.get_most_recent(est_list)

        if est:
            est = dut.parse_to_utc(est + offset_str)
        else:
            est = rhf.get_scheduled_arrival(row, arrival_type)

        return est

    def get_most_recent(self, est_list):
        """
        Given an ordered list, with most recent time first,
        pick the first entry which is not None otherwise return None
        """
        for x in est_list:
            if x:
                return x
        return None
