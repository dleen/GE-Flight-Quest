import pandas as pd
from dateutil.tz import tzutc
from datetime import datetime

import date_utilities as dut
import test_data_utils as tdu


class FlightDay:
    """
    A Day class for storing the most basic information we know about one day of flight data i.e.:
    flight_history
    flight_history_events

    flight_predictions: our predictions for the actual arrival times

    cutoff_time_list: this is a list of the times each day where the following is true:
        flight_history["actual_runway_departure"] < cutoff_time:
        flight_history["actual_runway_arrival"] >= cutoff_time:

    cutoff_time: is the value in cutoff_time_list corresponding to the folder containing flight_history

    midnight_time: this is the midnight against which we start counting the minutes until arrival
    """
    def __init__(self, folder_name, data_set_name, mode, cutoff_filename=""):
        self.folder_name = folder_name
        self.data_set_name = data_set_name
        self.mode = mode
        self.cutoff_filename = cutoff_filename

        if mode != "nodata":
            print "\tLoading flight_history.csv...",
            self.flight_history = \
                pd.read_csv("../Data/" + data_set_name + \
                "/" + folder_name + "/" + "FlightHistory/flighthistory.csv",
                converters = dut.get_flight_history_date_converter())
            print "done"

            if data_set_name == "PublicLeaderboardSet":
                conv = dut.parse_datetime_format6
            else:
                conv = dut.parse_datetime_format3

            print "\tLoading flight_history_events.csv...",
            self.flight_history_events = \
                pd.read_csv("../Data/" + data_set_name + "/" + folder_name + "/" + \
                 "FlightHistory/flighthistoryevents.csv",
                converters={"date_time_recorded": conv})
            print "done"            

        self.load_cutoff_times(cutoff_filename)

        self.midnight_time = datetime(self.cutoff_time.year, 
                                      self.cutoff_time.month, 
                                      self.cutoff_time.day, 
                                      tzinfo=tzutc())

        if mode == "leaderboard":
            print "\tLoading test flights data set...",
            self.test_data = \
                pd.read_csv("../Data/" + data_set_name + "/" + folder_name + "/test_flights.csv",
                usecols=[0])
            print "done"            
        elif mode == "training":
            print "\tCreating test flight data set...",
            codes = tdu.get_us_airport_icao_codes()
            self.test_data = tdu.select_valid_rows(self.flight_history, self.cutoff_time, codes)
            print "done"
        else:
            self.test_data = pd.DataFrame(None)
            print "Not a valid option!"

    def save_cutoff_times(self, filename):
        if self.mode == "leaderboard":
            print "You don't need to do this."
        else:
            print "Saving cutoff times to file: {}...".format(filename),
            self.cutoff_time_list.to_csv('{}.csv'.format(filename), index=False)
            print "done"

    def load_cutoff_times(self, filename=""):
        if self.mode == "leaderboard":
            print "\tLoading cutoff times from {}...".format("days.csv"),            
            self.cutoff_time_list = pd.read_csv("../Data/" + self.data_set_name + "/" "days.csv",
                index_col='folder_name', parse_dates=[1])
            print "done"
        elif filename != "":
            print "\tLoading cutoff times from {}...".format(filename),
            self.cutoff_time_list = pd.read_csv(filename, index_col='folder_name', parse_dates=[1])
            print "done"
        else:
            print "\tCreating new cutoff times...",
            self.cutoff_time_list = tdu.generate_cutoff_times()
            print "done"

        self.cutoff_time = self.cutoff_time_list['selected_cutoff_time'].ix[self.folder_name]

    def generate_new_cutoff_times(self):
        """
        Description
        """
        if self.mode == "leaderboard":
            print "You don't need to do this."
        else:
            self.cutoff_time_list = tdu.generate_cutoff_times()
            # Fix folder names, currently static. They need to change?
            self.cutoff_time = cutoff_time_list['selected_cutoff_time'].ix[self.folder_name]

    def generate_new_test_data(self):
        """
        Description
        """
        if self.mode == "leaderboard":
            print "You don't need to do this."
        else:
            codes = tdu.get_us_airport_icao_codes()
            self.test_data = tdu.select_valid_rows(self.flight_history, self.cutoff_time, codes)

    def flight_history_id_grouping(self):
        """
        This function does a "left join" (exactly like SQL join) using the test data flight ids
        as the left data and the flight history events as the right data. We then join the rest
        of the flight history data in a similar manner.
        Maybe this second join will be changed to something smarter?
        """
        joined_data = pd.merge(left=self.test_data, right=self.flight_history_events, 
                               on='flight_history_id', how='left', sort=False)
        joined_data = pd.merge(left=joined_data, right=self.flight_history, 
                               on='flight_history_id', how='left', sort=False)

        grouped_on_fhid = joined_data.groupby('flight_history_id')

        return grouped_on_fhid

class FlightPredictions:
    """
    Holds information for predictions and test data corresponding to the predictions
    """
    def __init__(self):
        self.flight_predictions = pd.DataFrame(None, columns=('flight_history_id',
            'actual_runway_arrival', 
            'actual_gate_arrival'))

        self.test_data = pd.DataFrame(None)

