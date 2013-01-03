from uses_all_data import using_all_data_calculations as uadc

import pandas as pd

def del_unneces_cols():
    cols = ['airline_code',
    'departure_airport_code',
    'arrival_airport_code',
    'creator_code',
    'departure_airport_timezone_offset',
    'arrival_airport_timezone_offset',
    'scheduled_aircraft_type',
    'actual_aircraft_type']

    return cols

def non_date_cols_to_str():

    cols_a = ['departure_terminal',
    'departure_gate',
    'arrival_terminal',
    'arrival_gate',
    'flight_number',
    'airline_icao_code',
    'arrival_airport_icao_code',
    'departure_airport_icao_code',
    'icao_aircraft_type_actual',
    'status'
    ]

    cols_b = ['number_of_gate_adjustments',
    'number_of_time_adjustments',
    'scheduled_air_time',
    'scheduled_block_time'
    ]

    a = {x : x_to_str for x in cols_a}
    b = {x : x_to_float for x in cols_b}

    c = dict(a)
    c.update(b)

    return a

def x_to_str(x):
    return str(x)

def x_to_float(x):
    return float(x)

def clean_all_parsed_fhe():
    alld = uadc.AllTrainingData("parsed_fhe_test_no_dates")

    alld.parsed_fhe.to_csv('output_csv/all_combined_test_no_dates_leaderboard.csv', index=False)

def load_all_parsed_fhe(filename):
    print "Loading combined fhe file...",
    data = \
        pd.read_csv('output_csv/' + filename + '.csv',
            na_values=["MISSING"], keep_default_na=True, 
            converters=non_date_cols_to_str())
        # VVV change
    print "done"

    return data