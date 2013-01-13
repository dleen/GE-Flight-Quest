from models import flightday as fd

from utilities import date_utilities as dut
from utilities import test_data_utils as tdu

from dateutil.tz import tzutc
from datetime import datetime

import pandas as pd


class ExtendedFlightDay(fd.FlightDay):
      def __init__(self, folder_name, data_set_name, mode, cutoff_filename=""):
            self.folder_name = folder_name
            self.data_set_name = data_set_name
            self.mode = mode
            self.cutoff_filename = cutoff_filename

            self.load_csv_files()

            self.load_fhe_csv_files()

            self.load_cutoff_times(cutoff_filename)

            self.midnight_time = datetime(self.cutoff_time.year, 
                self.cutoff_time.month, 
                self.cutoff_time.day, 
                tzinfo=tzutc())

            self.load_test_data()

            self.filter_fhe_data()
        
      def load_fhe_csv_files(self):
            if self.data_set_name == "PublicLeaderboardSet":
                  conv = dut.parse_datetime_format6
            else:
                  conv = dut.parse_datetime_format3

            print "\tLoading flight_history_events.csv...",
            self.flight_history_events = \
            pd.read_csv("../Data/" + self.data_set_name + "/" + self.folder_name + "/" + \
                 "FlightHistory/flighthistoryevents.csv",
                 na_values=["MISSING", "HIDDEN", ""], keep_default_na=True,
                 converters={"date_time_recorded": conv})
            print "done"

      def filter_fhe_data(self):
            print "\tFiltering flight history events data set...",
            self.flight_history_events = \
                tdu.filter_data_based_on_cutoff_and_test_ids(self.test_data,
                    self.flight_history_events, 'date_time_recorded', self.cutoff_time)
            print "done"
