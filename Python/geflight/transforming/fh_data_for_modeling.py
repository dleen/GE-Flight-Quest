from transforming import flight_history_events as fhe
from utilities import date_utilities as dut
from models import flightday as fd
from utilities import folder_names as fn

import pandas as pd

#
# Idea: parse everything in fhe.csv once without cutoff
# Then save, and load it appropriately using cutoff...?
# ^^ Actually, this won't work.
#

def transform_fhe():
    #mode = "nofiltering"
    mode = "training"
    fn1 = fn.folder_names_init_set()
    data_set_name = "InitialTrainingSet_rev1"
    cutoff_file = "cutoff_time_list_my_cutoff.csv"

    for d in fn1:
        mode = "training"
        day = fd.FlightDay(d, data_set_name, mode, cutoff_file)
        print "Running day: {}".format(d)  
        create_data(day, "test_data")

def offset_func(offset):
    if offset>0:
        offset_str = "+" + str(offset)
        return offset_str
    else:
        offset_str = str(offset)
        return offset_str

def create_data(day, data):

    day.flight_history['departure_airport_timezone_offset'] = \
        day.flight_history['departure_airport_timezone_offset'].apply(offset_func)

    day.flight_history['arrival_airport_timezone_offset'] = \
        day.flight_history['arrival_airport_timezone_offset'].apply(offset_func)

    grouped = day.flight_history_events.groupby('flight_history_id')

    test = grouped.apply(fhe.reduce_fhe_group_to_one_row)
    test = test.reset_index()

    for j in ["test_data", "all"]:

        print "\tCreating file: {}".format(j)

        joined = pd.DataFrame(None)

        if j == "test_data":
            joined = pd.merge(left=day.test_data, right=day.flight_history, on='flight_history_id', how='left', sort=False)
            joined = pd.merge(left=joined, right=test, on='flight_history_id', how='left', sort=False)
        elif j == "all":
            joined = pd.merge(left=day.flight_history, right=test, on='flight_history_id', how='left', sort=False)

        days_to_parse_arr = ['AGA_most_recent','ARA_most_recent','EGA_most_recent',
        'ERA_most_recent']

        days_to_parse_dep = ['AGD_most_recent','ARD_most_recent']

        days_to_parse = ['AGA_most_recent','ARA_most_recent','EGA_most_recent',
        'ERA_most_recent','AGD_most_recent','ARD_most_recent']

        for d in days_to_parse_arr:
            joined[d] = joined[d] + joined['arrival_airport_timezone_offset']

        for d in days_to_parse_dep:
            joined[d] = joined[d] + joined['departure_airport_timezone_offset']

        for d in days_to_parse:
            joined[d] = joined[d].fillna(value="MISSING")
            joined[d] = joined[d].apply(dut.parse_to_utc_w_missing)

        joined['ARA_minutes_after_cutoff'] = \
            joined['ARA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))
        joined['AGA_minutes_after_cutoff'] = \
            joined['AGA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))

        joined['ERA_minutes_after_cutoff'] = \
            joined['ERA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))
        joined['EGA_minutes_after_cutoff'] = \
            joined['EGA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))

        joined.to_csv('parsed_fhe_' + day.folder_name + '_' + j + '_filtered.csv', index=False)
