from models import flightday as fd

from models import model_MRU_with_gate_delay_est as mmgd
from models import model_MRU_with_improvement as mmwi
from models import model_most_recent_update as mmru

from models import model_Using_New_Data_Format as mundf

from utilities import folder_names as fn
from models import run_model

from transforming import fh_data_for_modeling as fhdfm

from uses_all_data import group_all_data as gad
from uses_all_data import using_all_data_calculations as uadc

from learning import random_forest_feature_importance as rffi

def main():
    """
    This is not right any more


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

    modes = ["training"]
    # modes = ["leaderboard"]

    # Run model using the most recently updated estimates of 
    # the runway arrival and the gate arrival as the predictions 
    # for the actual arrival times:

    most_new_data = mundf.Using_New_Data_Format()

    most_recent_gdly = mmgd.MRU_with_gate_delay_est()
    most_recent_gdly_upd = mmgd.MRU_with_gate_delay_upd()
    most_recent_imp  = mmwi.MRU_with_improvement()
    most_recent      = mmru.MRU()

    if "leaderboard" in modes:

        fn1 = fn.folder_names_test_set()
        data_set_name = "PublicLeaderboardSet"

        run_model.run_model(most_new_data_upd, None, fn1, data_set_name, modes)

    elif "training" in modes:

        fn1 = fn.folder_names_init_set()
        data_set_name = "InitialTrainingSet_rev1"

        cutoff_file = "cutoff_time_list_my_cutoff.csv"

        temp = run_model.run_model(most_new_data, None, fn1, data_set_name, modes, cutoff_file)
        print temp

    else:
        print "Not a valid option!"
        

def testing_saved_data_model():
    most_new_data = mundf.Using_New_Data_Format()

    mode = ["training"]

    fn1 = fn.folder_names_init_set()
    data_set_name = "InitialTrainingSet_rev1"

    d = fd.FlightDay(fn1[0], data_set_name, mode)

    d.save_cutoff_times("input_csv/cutoff_time_list_my_cutoff_2.csv")

    # cutoff_file = "cutoff_time_list_my_cutoff.csv"

    # temp = run_model.run_model(most_new_data, None, fn1, data_set_name, mode, cutoff_file)

    # print temp

def alld():
    gad.clean_all_parsed_fhe()

def lurn():
    rffi.r_forest()

def agt():
    # uadc.calc_avg_gate_times()
    uadc.calc_avg_gate_airline_times()

if __name__=='__main__':
    main()
    
    # agt()

    # fhdfm.transform_fhe()

    #testo()

    # alld()

    # lurn()




