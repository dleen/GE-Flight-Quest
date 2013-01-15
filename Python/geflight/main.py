from models import flightday as fd


from models import model_Using_New_Data_Format as mundf

from models import model_Using_ASDI_time_est as muate

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

    most_new_data = mundf.Using_New_Data_Format("output_csv")

    asdi_time_est = muate.Using_ASDI_time_est("output_csv")

    if "leaderboard" in modes:

        data_set_name = "PublicLeaderboardSet"

        run_model.run_model(asdi_time_est, None,
            data_set_name, modes)

    elif "training" in modes:

        data_set_name = "InitialTrainingSet_rev1"

        cutoff_file = "cutoff_time_list_my_cutoff.csv"

        temp = run_model.run_model(asdi_time_est, None,
            data_set_name, modes, cutoff_file)
        print temp

    else:
        print "Not a valid option!"


def alld():
    gad.clean_all_parsed_fhe()


def lurn():
    rffi.r_forest()


def agt():
    # uadc.calc_avg_gate_times()
    uadc.calc_avg_gate_airline_times()


def asdi_test():
    from models import extended_asdiday as ead

    fold = fn.folder_names_init_set()
    data_set_name = "InitialTrainingSet_rev1"
    cutoff_file = "cutoff_time_list_my_cutoff.csv"

    ead.ExtendedASDIDay(fold[0], data_set_name,
        "training", cutoff_file)

if __name__ == '__main__':
    main()

    # agt()

    # fhdfm.transform_fhe()

    # alld()

    # lurn()

    # asdi_test()
