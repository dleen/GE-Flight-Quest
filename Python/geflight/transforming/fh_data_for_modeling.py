from transforming import flight_history_events as fhe
from transforming import tf_util as tfu

from models import extended_flightday as efd

from utilities import folder_names as fn
from utilities import date_utilities as dut


import pandas as pd
import numpy as np


def transform_fhe():
    # mode = "nofiltering"
    # mode = "leaderboard"
    mode = "training"
    fn1 = fn.folder_names_init_set()
    data_set_name = "InitialTrainingSet_rev1"
    # data_set_name = "PublicLeaderboardSet"

    cutoff_file = "cutoff_time_list_my_cutoff.csv"
    # cutoff_file = "cutoff_time_list_my_cutoff_2.csv"

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

    joined = joined.replace("", np.nan)

    days_to_parse_arr = ['AGA_most_recent', 'ARA_most_recent', 'EGA_most_recent',
    'ERA_most_recent']

    days_to_parse_dep = ['AGD_most_recent', 'ARD_most_recent']

    days_to_parse = ['AGA_most_recent', 'ARA_most_recent', 'EGA_most_recent',
    'ERA_most_recent', 'AGD_most_recent', 'ARD_most_recent']

    for d in days_to_parse_arr:
        joined[d] = joined[d] + joined['arrival_airport_timezone_offset']

    for d in days_to_parse_dep:
        joined[d] = joined[d] + joined['departure_airport_timezone_offset']

    for d in days_to_parse:
        joined[d] = joined[d].apply(dut.parse_to_utc)

    for c in date_columns():
        joined[c + '_minutes_after_midnight'] = \
            joined[c].apply(lambda x: float(dut.minutes_difference(x, day.midnight_time)))

    # for c in date_columns():
    #     del joined[c]

    for d in unneces_cols():
        del joined[d]

    joined = joined.replace("", np.nan)

    joined.to_csv('output_csv/parsed_fhe_' + day.folder_name + '_' + "all" + '_filtered_with_dates.csv',
        index=False, na_rep="MISSING")

    joined_test = pd.merge(left=day.test_data[['flight_history_id']], right=joined,
        on='flight_history_id', how='left', sort=False)

    joined_test.to_csv('output_csv/parsed_fhe_' + day.folder_name + '_' + "test" + '_filtered_with_dates.csv',
        index=False, na_rep="MISSING")


def date_columns():

    cols = ['published_departure',
    'published_arrival',
    'scheduled_gate_departure',
    'actual_gate_departure',
    'scheduled_gate_arrival',
    'actual_gate_arrival',
    'scheduled_runway_departure',
    'actual_runway_departure',
    'scheduled_runway_arrival',
    'actual_runway_arrival',
    'AGA_update_time',
    'AGD_most_recent',
    'AGD_update_time',
    'ARA_update_time',
    'ARD_most_recent',
    'ARD_update_time',
    'EGA_most_recent',
    'EGA_update_time',
    'ERA_most_recent',
    'ERA_update_time',
    'last_update_time',
    'status_update_time'
    ]

    return cols


def unneces_cols():

    cols = ['airline_code',
    'departure_airport_code',
    'arrival_airport_code',
    'creator_code',
    'departure_airport_timezone_offset',
    'arrival_airport_timezone_offset',
    'scheduled_aircraft_type',
    'actual_aircraft_type'
    ]

    return cols


def non_date_columns():

    cols = ['departure_terminal',
    'departure_gate',
    'arrival_terminal',
    'arrival_gate',
    'flight_number',
    'airline_icao_code',
    'arrival_airport_icao_code',
    'departure_airport_icao_code',
    'icao_aircraft_type_actual',
    'number_of_gate_adjustments',
    'number_of_time_adjustments',
    'scheduled_air_time',
    'scheduled_block_time',
    'status',
    'was_gate_adjusted',
    'was_time_adjusted'
    ]

    return cols
