from all_data_agg import using_all_data_calculations as uadc

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
    alld = uadc.AllTrainingData("parsed_fhe_test")

    for c in del_unneces_cols():
        del alld.parsed_fhe[c]

    alld.parsed_fhe.to_csv('output_csv/all_combined.csv', index=False)

def load_all_parsed_fhe():
    data = \
        pd.read_csv('output_csv/all_combined_test.csv',
        # VVV change
        parse_dates=[9,10,11,12,13,14,15,16,17,18,27,28,29,30,31,32,33,34,35,36,37,38,43,47])



# np.asarray