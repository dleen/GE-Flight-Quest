import flightday as fd
import date_utilities as dut
import test_data_utils as tdu
import row_helper_functions as rhf

import rmse
import pandas as pd

#
# need to have a way to make tiny changes to a model and check
# for improvements
#
def run_model(model_A, model_B, days_list, data_set_name, mode, cutoff_filename=""):
    """
    Runs the most recent update model for each day in the dataset and returns the result to a 
    csv file in the python directory.
    """
    pred = fd.FlightPredictions()

    fin_A = fd.FlightPredictions()
    fin_B = fd.FlightPredictions()

    print "Using mode: {}".format(mode)
    print "Using data from {}".format(data_set_name)

    for i, d in enumerate(days_list):
        if model_B == None:
            print "Running model '{}' on day {} (day {} of {}):".format(model_A, d, i + 1, len(days_list))
        else:
            print "Running models '{}', '{}' on day {} (day {} of {}):".format(model_A, model_B, d, i + 1, len(days_list))

        day = fd.FlightDay(d, data_set_name, mode, cutoff_filename)

        print "\tStarting model: '{}'...".format(model_A),
        pred = model_A.using_most_recent_updates_individual_day(day, pred)
        fin_A.flight_predictions = pd.concat([fin_A.flight_predictions, pred.flight_predictions])
        fin_A.test_data          = pd.concat([fin_A.test_data, pred.test_data])
        print "done"

        if model_B != None:
            print "\tStarting model: '{}'...".format(model_B),
            pred = model_B.using_most_recent_updates_individual_day(day, pred)
            fin_B.flight_predictions = pd.concat([fin_B.flight_predictions, pred.flight_predictions])
            fin_B.test_data          = pd.concat([fin_B.test_data, pred.test_data])
            print "done"

        print "\tDay {} has finished".format(d)
        print ""

    print "All days in {} are done!".format(data_set_name)

    if mode == "leaderboard":
        fin_A.flight_predictions.to_csv('test.csv', index=False)
        print "Predictions written to csv file in Python folder."
        if model_B != None:
            print "Warning: we have disregarded the output of '{}'!".format(model_B)
    elif mode == "training":
        # print to log file rmse score
        score_A = rmse.calculate_rmse_score(fin_A.flight_predictions, fin_A.test_data)

        if model_B != None:
            score_B = rmse.calculate_rmse_score(fin_B.flight_predictions, fin_B.test_data)
        else:
            score_B = None

        return {str(model_A) : score_A, 
                str(model_B) : score_B}
    else:
        print "Not an option!"

class MRU:
    """
    Description
    """
    def __repr__(self):
        return "Original model"

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
            [er, eg] = self.most_recent_update(event_group)
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

    def most_recent_update(self, event_group):
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

        era_est = self.get_updated_arrival(event_list, event_group.ix[event_group.index[0]],
            "runway", offset_str)

        ega_est = self.get_updated_arrival(event_list, event_group.ix[event_group.index[0]],
            "gate", offset_str)

        return [era_est, ega_est]

    def get_updated_arrival(self, event_list, row, arrival_type, offset_str):
        """
        Returns the most recent estimate of the arrival time. If that
        cannot be found resorts to using the scheduled arrival times.
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

class MRU_update(MRU):
    def __repr__(self):
        return "Updated Model"

    def most_recent_update(self, event_group):
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

        era_est = self.get_updated_arrival(event_list, event_group.ix[event_group.index[0]],
            "runway", offset_str)

        ega_est = self.get_updated_arrival(event_list, event_group.ix[event_group.index[0]],
            "gate", offset_str)

        if era_est > ega_est:
            #era_est = ega_est
            ega_est = era_est

        return [era_est, ega_est]

        