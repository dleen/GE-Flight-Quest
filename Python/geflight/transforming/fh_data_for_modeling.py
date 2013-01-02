from transforming import flight_history_events as fhe
from transforming import tf_util as tfu

from models import extended_flightday as efd

from utilities import folder_names as fn
from utilities import date_utilities as dut


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
        day = efd.ExtendedFlightDay(d, data_set_name, mode, cutoff_file)
        print "Running day: {}".format(d)  
        create_data(day)


def create_data(day):

    day.flight_history['departure_airport_timezone_offset'] = \
        day.flight_history['departure_airport_timezone_offset'].apply(tfu.offset_func)

    day.flight_history['arrival_airport_timezone_offset'] = \
        day.flight_history['arrival_airport_timezone_offset'].apply(tfu.offset_func)

    grouped = day.flight_history_events.groupby('flight_history_id')

    reduced_fhe = grouped.apply(fhe.reduce_fhe_group_to_one_row)
    reduced_fhe = reduced_fhe.reset_index()

    print "\tCreating file: all"

    joined = pd.DataFrame(None)

    joined = pd.merge(left=day.flight_history, right=reduced_fhe, on='flight_history_id', how='left', sort=False)

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
        joined[d] = joined[d].apply(dut.parse_to_utc)

    joined['ARA_minutes_after_midnight'] = \
        joined['ARA_most_recent'].apply(lambda x: dut.minutes_difference(x,day.midnight_time))
    joined['AGA_minutes_after_midnight'] = \
        joined['AGA_most_recent'].apply(lambda x: dut.minutes_difference(x,day.midnight_time))

    joined['actual_runway_minutes_after_midnight'] = \
        joined['actual_runway_arrival'].apply(lambda x: dut.minutes_difference(x,day.midnight_time))
    joined['actual_gate_minutes_after_midnight'] = \
        joined['actual_gate_arrival'].apply(lambda x: dut.minutes_difference(x,day.midnight_time))

    joined['ERA_minutes_after_midnight'] = \
        joined['ERA_most_recent'].apply(lambda x: dut.minutes_difference(x,day.midnight_time))
    joined['EGA_minutes_after_midnight'] = \
        joined['EGA_most_recent'].apply(lambda x: dut.minutes_difference(x,day.midnight_time))

    joined.to_csv('output_csv/parsed_fhe_' + day.folder_name + '_' + "all" + '_filtered.csv', index=False)

    joined_test = pd.merge(left=day.test_data[['flight_history_id']], right=joined,
        on='flight_history_id', how='left', sort=False)

    joined_test.to_csv('output_csv/parsed_fhe_' + day.folder_name + '_' + "test" + '_filtered.csv', index=False)
