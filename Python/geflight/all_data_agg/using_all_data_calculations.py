from models.utilities import folder_names as fn
from models.utilities import date_utilities as dut

import pandas as pd
import numpy as np
import datetime

class AllTrainingData:
    def __init__(self, data):
        data_set_name = "InitialTrainingSet_rev1"
        self.flight_history = pd.DataFrame(None)

        if data == "flight_history":
            print "AllTrainingData Initializing: using data {}".format(data)
            for f in fn.folder_names_init_set():
                print "\tLoading flight_history.csv folder {}...".format(f),
                temp = \
                    pd.read_csv("../../Data/" + data_set_name + \
                    "/" + f + "/" + "FlightHistory/flighthistory.csv",
                    converters = dut.get_flight_history_date_converter())
                self.flight_history = pd.concat([self.flight_history, temp])
                print "done"

def average_gate_delays_by_arrival_airport(all_training_data_flight_history):
    """
    Improve this:
        revert to other times if actual are not available
        clean up the return dataframe
    """
    gate_delay = all_training_data_flight_history.flight_history[['arrival_airport_icao_code', 
        'actual_runway_arrival', 'actual_gate_arrival']]

    gate_delay_1 = gate_delay.replace(["MISSING", "HIDDEN"], np.NaN)
    gate_delay_1 = gate_delay_1.dropna(axis=0)


    gate_delay_1['gate_delay_mins'] = (gate_delay_1['actual_gate_arrival'] - \
        gate_delay_1['actual_runway_arrival']).apply(lambda x: x.total_seconds())
    #gate_delay_1['gate_delay_mins'] = gate_delay_1.apply(time_delay, axis=1)
     
    #print gate_delay_1[0:10] 

    gate_delay_2 = gate_delay_1
    gate_delay_1 = gate_delay_1[['arrival_airport_icao_code', 'gate_delay_mins']]

    grouped_by_arrival_airport = gate_delay_1.groupby('arrival_airport_icao_code', as_index=False)

    #print gate_delay_2[['actual_gate_arrival','actual_runway_arrival','gate_delay_mins']].ix[ind]

    gagg = grouped_by_arrival_airport['gate_delay_mins'].aggregate(np.mean)

    gagg.to_csv('output_csv/average_gate_delay_by_arrival_airport.csv', index=False)
    #gagg.to_csv('output_csv/average_gate_delay_by_arrival_airport.csv')

def add_column_avg_gate_delays_by_arr_airport(day):
    """
    Description
    """
    gaggo = pd.read_csv('../output_csv/average_gate_delay_by_arrival_airport.csv')

    day.flight_history = pd.merge(left=day.flight_history, right=gaggo, on='arrival_airport_icao_code', how='left', sort=False)
