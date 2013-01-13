from models import flightday as fd

from utilities import date_utilities as dut
from utilities import test_data_utils as tdu

import pandas as pd

from dateutil.tz import tzutc
from datetime import datetime


class ASDIDay(fd.FlightDay):
    """
    Usual day including the ASDI data
    """
    def __init__(self, folder_name, data_set_name, mode, cutoff_filename=""):
        self.folder_name = folder_name
        self.data_set_name = data_set_name
        self.mode = mode
        self.cutoff_filename = cutoff_filename

        self.load_csv_files()

        self.load_asdi_csv_files()

        self.load_cutoff_times(cutoff_filename)

        self.midnight_time = datetime(self.cutoff_time.year, 
            self.cutoff_time.month, 
            self.cutoff_time.day, 
            tzinfo=tzutc())

        self.load_test_data()

        self.filter_asdi_data()

    def load_asdi_csv_files(self):
        print "\tLoading asdiflightplan.csv...",
        self.asdi_flight_plan = \
        pd.read_csv("../Data/" + self.data_set_name + "/" + self.folder_name + "/" + \
            "ASDI/asdiflightplan.csv",
            na_values=["MISSING", "HIDDEN", ""], keep_default_na=True,
            converters = dut.get_asdi_flight_plan_date_converter())
        self.asdi_flight_plan.rename(columns={"flighthistoryid" : "flight_history_id"}, inplace=True)
        print "done"

    def match_asdi_data_with_flight_history_ids(self):
        pass

    def filter_asdi_data(self):
        print "\tFiltering asdi flight plan data set...",
        self.asdi_flight_plan = \
        tdu.filter_data_based_on_cutoff_and_test_ids(self.test_data,
            self.asdi_flight_plan, 'updatetimeutc', self.cutoff_time)
        print "done"

