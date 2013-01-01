from transforming import flight_history_events as fhe

from utilities import date_utilities as dut

import pandas as pd

from models import flightday as fd

from utilities import folder_names as fn

#
# Fix this file in general
#
#
#

def transform_fhe():
    #mode = "nofiltering"
    mode = "training"
    fn1 = fn.folder_names_init_set()
    data_set_name = "InitialTrainingSet_rev1"
    cutoff_file = "cutoff_time_list_my_cutoff.csv"

    for d in fn1:
        day = fd.FlightDay(d, data_set_name, mode, cutoff_file)    
        create_data(day)

def offset_func(offset):
    if offset>0:
        offset_str = "+" + str(offset)
        return offset_str
    else:
        offset_str = str(offset)
        return offset_str

def create_data(day):

    day.flight_history['departure_airport_timezone_offset'] = \
        day.flight_history['departure_airport_timezone_offset'].apply(offset_func)

    day.flight_history['arrival_airport_timezone_offset'] = \
        day.flight_history['arrival_airport_timezone_offset'].apply(offset_func)

    grouped = day.flight_history_events.groupby('flight_history_id')

    test = grouped.apply(fhe.reduce_fhe_group_to_one_row)
    test = test.reset_index()

    joined = pd.merge(left=day.test_data, right=day.flight_history, on='flight_history_id', how='left', sort=False)
    joined = pd.merge(left=joined, right=test, on='flight_history_id', how='left', sort=False)


    joined['AGA_most_recent'] = joined['AGA_most_recent'] + joined['arrival_airport_timezone_offset']
    joined['ARA_most_recent'] = joined['ARA_most_recent'] + joined['arrival_airport_timezone_offset']
    joined['EGA_most_recent'] = joined['EGA_most_recent'] + joined['arrival_airport_timezone_offset']
    joined['ERA_most_recent'] = joined['ERA_most_recent'] + joined['arrival_airport_timezone_offset']

    joined['AGD_most_recent'] = joined['AGD_most_recent'] + joined['departure_airport_timezone_offset']
    joined['ARD_most_recent'] = joined['ARD_most_recent'] + joined['departure_airport_timezone_offset']

    days_to_parse = ['AGA_most_recent','ARA_most_recent','EGA_most_recent',
    'ERA_most_recent','AGD_most_recent','ARD_most_recent']

    for d in days_to_parse:
        joined[d] = joined[d].fillna(value="MISSING")


    joined['AGA_most_recent'] = joined['AGA_most_recent'].fillna(value="MISSING")
    joined['ARA_most_recent'] = joined['ARA_most_recent'].fillna(value="MISSING")
    joined['EGA_most_recent'] = joined['EGA_most_recent'].fillna(value="MISSING")
    joined['ERA_most_recent'] = joined['ERA_most_recent'].fillna(value="MISSING")
    joined['AGD_most_recent'] = joined['AGD_most_recent'].fillna(value="MISSING")
    joined['ARD_most_recent'] = joined['ARD_most_recent'].fillna(value="MISSING")

    joined['AGA_most_recent'] = joined['AGA_most_recent'].apply(dut.parse_to_utc_w_missing)
    joined['ARA_most_recent'] = joined['ARA_most_recent'].apply(dut.parse_to_utc_w_missing)
    joined['EGA_most_recent'] = joined['EGA_most_recent'].apply(dut.parse_to_utc_w_missing)
    joined['ERA_most_recent'] = joined['ERA_most_recent'].apply(dut.parse_to_utc_w_missing)

    joined['AGD_most_recent'] = joined['AGD_most_recent'].apply(dut.parse_to_utc_w_missing)
    joined['ARD_most_recent'] = joined['ARD_most_recent'].apply(dut.parse_to_utc_w_missing)


    joined['ARA_minutes_after_cutoff'] = \
        joined['ARA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))
    joined['AGA_minutes_after_cutoff'] = \
        joined['AGA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))

    joined['ERA_minutes_after_cutoff'] = \
        joined['ERA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))
    joined['EGA_minutes_after_cutoff'] = \
        joined['EGA_most_recent'].apply(lambda x: dut.minutes_difference_w_missing(x,day.midnight_time))



    joined.to_csv('parsed_fhe_' + fn1[0] + '_test_filtered.csv', index=False)