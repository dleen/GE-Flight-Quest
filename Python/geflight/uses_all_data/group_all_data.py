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

def clean_all_parsed_fhe():
    alld = uadc.AllTrainingData("parsed_fhe")

    for c in del_unneces_cols():
        del alld.parsed_fhe[c]

    alld.parsed_fhe.to_csv('output_csv/all_combined.csv', index=False)

def load_all_parsed_fhe():
    print "Loading combined fhe file...",
    data = \
        pd.read_csv('output_csv/all_combined_test.csv',
        # VVV change
        parse_dates=[4,5,9,10,12,13,15,16,17,18,20,21,33,36,37,40,41,42,43,45])
    print "done"

    return data



# np.asarray