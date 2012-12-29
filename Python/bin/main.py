from geflight.models import flightday as fd
from models import model_MRU_with_gate_delay_est as mmgd
from models import model_MRU_with_improvement as mmwi
from models import model_most_recent_update as mmru
from models.utilities import folder_names as fn
from run_model import run_model
from all_data_agg import using_all_data_calculations as uadc

import pandas as pd

def main():
    """
    Main file.
    Directory structure is expected to be:
    main_folder/
        Data/
            PublicLeaderboardSet/
                2012_11_26/
                2012_11_27/
                etc...
            InitialTrainingSet_rev1/
                2012_11_12/
                2012_11_13/
                etc...
        Python/
            geflight/
                using_most_recent_update.py
                flightday.py
                date_utilities.py
                etc...
        R/
            R_code_here.R

    The current model uses the most recent arrival update which
    can be found in flight_history_events.csv
    """

    mode = "training"
    #mode = "leaderboard"

    # Run model using the most recently updated estimates of 
    # the runway arrival and the gate arrival as the predictions 
    # for the actual arrival times:

    most_recent_gdly = mmgd.MRU_with_gate_delay_est()
    most_recent_imp  = mmwi.MRU_with_improvement()
    most_recent      = mmru.MRU()

    if mode == "leaderboard":

        fn1 = fn.folder_names_test_set()
        data_set_name = "PublicLeaderboardSet"

        run_model(most_recent_imp, None, fn1, data_set_name, mode)

    elif mode == "training":

        fn1 = fn.folder_names_init_set()
        data_set_name = "InitialTrainingSet_rev1"

        cutoff_file = "cutoff_time_list_my_cutoff.csv"

        temp = run_model(most_recent, most_recent_imp, fn1, data_set_name, mode, cutoff_file)
        #temp = run_model(most_recent_imp, most_recent_gdly, fn1, data_set_name, mode)
        print temp

    else:
        print "Not a valid option!"

def all_data_test(day):
    #test = uadc.AllTrainingData("flight_history")

    #uadc.average_gate_delays_by_arrival_airport(test)

    gaggo = pd.read_csv('output_csv/average_gate_delay_by_arrival_airport.csv')

    mode = "training"
    fn1 = fn.folder_names_init_set()
    data_set_name = "InitialTrainingSet_rev1"
    cutoff_file = "cutoff_time_list_my_cutoff.csv"

    day = fd.FlightDay(fn1[0], data_set_name, mode, cutoff_file)

    day.flight_history = pd.merge(left=day.flight_history, right=gaggo, on='arrival_airport_icao_code', how='left', sort=False)


if __name__=='__main__':
    main()
    #all_data_test()