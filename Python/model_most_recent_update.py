import flightday as fd
import date_utilities as dut
import test_data_utils as tdu
import row_helper_functions as rhf

import rmse
import pandas as pd

class MRU:
    """
    Description
    """
    def __repr__(self):
        return "Original model"

    def run_day(self, day, pred):
        """
        All models should have a function like this
        """
        return self.using_most_recent_updates_individual_day(day, pred)

    def using_most_recent_updates_individual_day(self, day, pred):
        """
        Given a day of flights calculates the most recent update for runway and
        gate arrival for each of the flights. Enters this into the flight prediction
        dataframe. Replaces any missing values with just the value of the cutoff time.
        Finally converts the predictions to minutes past midnight.
        """
        flight_events = day.flight_history_id_grouping()

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

        pred.flight_predictions = \
            pred.flight_predictions.fillna(value=day.cutoff_time)

        pred.flight_predictions = \
            dut.convert_predictions_from_datetimes_to_minutes(pred.flight_predictions, day.midnight_time)

        pred.test_data = day.test_data.copy()

        if day.mode == "training": 
            pred.test_data = \
                dut.convert_predictions_from_datetimes_to_minutes(pred.test_data, day.midnight_time)

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

        era_est = self.get_updated_event_arrival(event_list, event_group.ix[event_group.index[0]],
            "runway", offset_str)

        ega_est = self.get_updated_event_arrival(event_list, event_group.ix[event_group.index[0]],
            "gate", offset_str)

        if era_est > ega_est:
            # VV Improves score on Kaggle, worsens training set score
            ega_est = era_est

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
