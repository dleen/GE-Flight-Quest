import model_MRU_with_improvement as mmwi
import flightday as fd

from utilities import folder_names as fn
from utilities import date_utilities as dut
from utilities import sanity_check as sc


from uses_all_data import using_all_data_calculations as uadc

import numpy as np
import pandas as pd
import datetime

#
# Have to fix to work on test data 
# Use the training data to calc the delays
# and use these on the test data
#
class MRU_with_gate_delay_est(mmwi.MRU_with_improvement):
    """
    This class allows us to make slight changes to our model by "overloading"
    the functions we want to make changes to.
    """
    def __repr__(self):
        """
        This is a descriptive name for the model for use in strings
        """
        return "Avg gate time by airport model"

    def using_most_recent_updates_individual_day(self, day, pred):
        """
        Given a day of flights calculates the most recent update for runway and
        gate arrival for each of the flights. Enters this into the flight prediction
        dataframe. Replaces any missing values with just the value of the cutoff time.
        Finally converts the predictions to minutes past midnight.
        """
        # This is a change from the original:
        uadc.add_column_avg_gate_delays_by_arr_airport(day)

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

        pred.flight_predictions = \
            pred.flight_predictions.fillna(value=day.cutoff_time)

        pred.flight_predictions = \
            dut.convert_predictions_from_datetimes_to_minutes(pred.flight_predictions, day.midnight_time)

        pred.test_data = day.test_data.copy()

        if "training" in day.mode: 
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

        era_est = self.get_updated_event_arrival(event_list, event_group.ix[event_group.index[0]],
            "runway", offset_str)

        ega_est = self.get_updated_event_arrival(event_list, event_group.ix[event_group.index[0]],
            "gate", offset_str)

        gate_delay = event_group["gate_delay_seconds"].ix[event_group.index[0]]

        # Improves score on Kaggle
        if era_est > ega_est:
            if gate_delay >= 0:
                gd = datetime.timedelta(seconds=gate_delay)
                ega_est = era_est + gd
            elif gate_delay < 0:
                gd = datetime.timedelta(seconds=abs(gate_delay))
                ega_est = era_est
                era_est = ega_est - gd
            else:
                ega_est = era_est

        return [era_est, ega_est]

class MRU_with_gate_delay_upd(MRU_with_gate_delay_est):
    """
    This class allows us to make slight changes to our model by "overloading"
    the functions we want to make changes to.
    """
    def __repr__(self):
        """
        This is a descriptive name for the model for use in strings
        """
        return "Avg gate time by airport UPD"

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

        gate_delay = event_group["gate_delay_seconds"].ix[event_group.index[0]]

        # Improves score on Kaggle
        if era_est > ega_est:
            if gate_delay >= 0:
                gd = datetime.timedelta(seconds=gate_delay)
                ega_est = era_est + gd
            elif gate_delay < 0:
                gd = datetime.timedelta(seconds=abs(gate_delay))
                ega_est = era_est
                era_est = ega_est - gd
            else:
                ega_est = era_est

        if gate_delay >= 0:
            gd = datetime.timedelta(seconds=gate_delay)
            if ega_est < era_est + gd:
                ega_est = era_est + gd

        return [era_est, ega_est]