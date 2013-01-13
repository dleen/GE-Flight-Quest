import pandas as pd

from dateutil.tz import tzutc
from datetime import datetime

from utilities import date_utilities as dut
from utilities import test_data_utils as tdu


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

        self.load_csv_files()

        self.load_cutoff_times(cutoff_filename)

        self.midnight_time = datetime(self.cutoff_time.year,
                                      self.cutoff_time.month,
                                      self.cutoff_time.day,
                                      tzinfo=tzutc())

        self.load_test_data()

    def load_csv_files(self):
        print "FlightDay Initializing: {}, {} in {} mode".format(self.folder_name, self.data_set_name, self.mode)

        print "\tLoading flight_history.csv...",
        self.flight_history = \
            pd.read_csv("../Data/" + self.data_set_name + \
            "/" + self.folder_name + "/" + "FlightHistory/flighthistory.csv",
            na_values=["MISSING", "HIDDEN", ""], keep_default_na=True,
            converters=dut.get_flight_history_date_converter())
        print "done"

    def load_test_data(self):
        if "leaderboard" in self.mode:

            print "\tLoading leaderboard test flights data set...",
            self.test_data = \
                pd.read_csv("../Data/" + self.data_set_name + "/" + self.folder_name + "/test_flights.csv",
                usecols=[0], na_values=["MISSING", "HIDDEN"], keep_default_na=True)
            print "done"

        elif "training" in self.mode:

            print "\tCreating test flight data set...",
            self.test_data = tdu.select_valid_rows(self.flight_history, self.cutoff_time)
            print "done"

        else:

            self.test_data = pd.DataFrame(None)
            print "\tNot a valid option, test data not created!"

    def load_cutoff_times(self, filename=""):

        if "leaderboard" in self.mode:

            print "\tLoading cutoff times from {}...".format("days.csv"),
            self.cutoff_time_list = pd.read_csv("../Data/" + self.data_set_name + "/" "days.csv",
                index_col='folder_name', parse_dates=[1])
            print "done"

        elif filename != "":

            print "\tLoading cutoff times from {}...".format(filename),
            self.cutoff_time_list = pd.read_csv("input_csv/" + filename, index_col='folder_name', parse_dates=[1])
            print "done"

        else:
            print "\tCreating new cutoff times...",
            self.cutoff_time_list = tdu.generate_cutoff_times()
            print "done"

        self.cutoff_time = self.cutoff_time_list['selected_cutoff_time'].ix[self.folder_name]

        self.midnight_time = datetime(self.cutoff_time.year,
                              self.cutoff_time.month,
                              self.cutoff_time.day,
                              tzinfo=tzutc())

    def save_cutoff_times(self, filename):
        if "leaderboard" in self.mode:
            print "You don't need to do this."
        else:
            print "Saving cutoff times to file: {}...".format(filename),
            self.cutoff_time_list.to_csv('{}.csv'.format(filename), index=False)
            print "done"

    def generate_new_cutoff_times(self):
        if "leaderboard" in self.mode:
            print "You don't need to do this."
        else:
            self.cutoff_time_list = tdu.generate_cutoff_times()

            # Fix folder names, currently static. They need to change?
            self.cutoff_time = self.cutoff_time_list['selected_cutoff_time'].ix[self.folder_name]

            self.midnight_time = datetime(self.cutoff_time.year,
                                          self.cutoff_time.month,
                                          self.cutoff_time.day,
                                          tzinfo=tzutc())

    def generate_new_test_data(self):
        if "leaderboard" in self.mode:
            print "You don't need to do this."
        else:
            self.generate_new_cutoff_times()
            self.load_test_data()


class FlightPredictions:
    """
    Holds information for predictions and test data corresponding to the predictions
    """
    def __init__(self):
        self.flight_predictions = pd.DataFrame(None, columns=('flight_history_id',
            'actual_runway_arrival',
            'actual_gate_arrival'))

        self.test_data = pd.DataFrame(None)

    def get_predictions_from_data(self, data):
        self.flight_predictions = self.flight_predictions.reindex(range(len(data['flight_history_id'])))

        self.flight_predictions['flight_history_id'] = data['flight_history_id']
        self.flight_predictions['actual_runway_arrival'] = data['ERA_most_recent_minutes_after_midnight']
        self.flight_predictions['actual_gate_arrival'] = data['EGA_most_recent_minutes_after_midnight']

    def get_test_from_data(self, data):
        self.test_data = data[['flight_history_id', 'actual_runway_arrival_minutes_after_midnight',
            'actual_gate_arrival_minutes_after_midnight']]

        self.test_data.columns = ['flight_history_id', 'actual_runway_arrival', 'actual_gate_arrival']
